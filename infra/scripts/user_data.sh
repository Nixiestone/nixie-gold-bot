#!/bin/bash
set -euo pipefail
exec > >(tee /var/log/user-data.log) 2>&1

echo "=== Nixie Gold Bot Bootstrap ==="
echo "Started at: $(date)"

# ── 1. Swap (4 GB) — critical for running Redpanda + services on 1 GB RAM ────
if [ ! -f /swapfile ]; then
  fallocate -l 4G /swapfile
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
  echo 'vm.swappiness=10' >> /etc/sysctl.conf
  sysctl -p
  echo "Swap: 4 GB created"
fi

# ── 2. System packages ─────────────────────────────────────────────────────────
dnf update -y
dnf install -y git curl

# ── 3. Docker (for building images locally if needed) ─────────────────────────
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# ── 4. k3s — lightweight Kubernetes ──────────────────────────────────────────
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--disable traefik --disable servicelb" sh -
# Wait for k3s to be ready
sleep 20
until kubectl get nodes | grep -q Ready; do sleep 5; done
echo "k3s ready"

# Copy kubeconfig for ec2-user
mkdir -p /home/ec2-user/.kube
cp /etc/rancher/k3s/k3s.yaml /home/ec2-user/.kube/config
chown ec2-user:ec2-user /home/ec2-user/.kube/config
chmod 600 /home/ec2-user/.kube/config

# ── 5. Clone the repository ───────────────────────────────────────────────────
git clone https://github.com/nixiestone/nixie-gold-bot.git /opt/nixie-gold-bot
cd /opt/nixie-gold-bot
git checkout claude/trading-infra-architecture-0k877c || git checkout main

# ── 6. Inject secrets into k8s/configmaps/trading-config.yaml ────────────────
cat > /opt/nixie-gold-bot/k8s/configmaps/secrets-values.env <<EOF
ALPHA_VANTAGE_KEY=${alpha_vantage_key}
TELEGRAM_BOT_TOKEN=${telegram_bot_token}
TELEGRAM_CHAT_ID=${telegram_chat_id}
NEON_DATABASE_URL=${neon_database_url}
ACCOUNT_BALANCE=${account_balance}
EOF

# Create the k8s secret from injected values
kubectl create secret generic trading-secrets \
  --namespace trading \
  --from-env-file=/opt/nixie-gold-bot/k8s/configmaps/secrets-values.env \
  --dry-run=client -o yaml | kubectl apply -f - || true

# ── 7. Apply Kubernetes manifests in order ────────────────────────────────────
cd /opt/nixie-gold-bot

# Namespaces first
kubectl apply -f k8s/namespaces.yaml

# Wait a moment for namespaces
sleep 5

# ConfigMaps and Secrets
kubectl apply -f k8s/configmaps/trading-config.yaml

# GHCR image-pull secret (only needed if the GHCR packages are private).
# Harmless to create even for public images; deployments reference it by name.
if [ -n "${github_token}" ]; then
  kubectl create secret docker-registry ghcr-pull \
    --namespace trading \
    --docker-server=ghcr.io \
    --docker-username="${github_user}" \
    --docker-password="${github_token}" \
    --dry-run=client -o yaml | kubectl apply -f -
  echo "Created ghcr-pull secret for private image pulls."
else
  echo "No github_token provided — assuming public GHCR images."
fi

# NetworkPolicies (default-deny ingress + allowlist)
kubectl apply -f k8s/network-policies.yaml

# Kafka (Redpanda)
kubectl apply -f k8s/kafka/redpanda.yaml

# Wait for Redpanda to be ready before starting services
echo "Waiting for Redpanda to start..."
sleep 60
kubectl wait --for=condition=ready pod -l app=redpanda -n trading --timeout=180s || true

# Monitoring stack
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/dashboards/dashboard-configmap.yaml

# Generate a random Grafana admin password and store it as a Secret (never hardcoded)
GRAFANA_PASS=$(head -c 18 /dev/urandom | base64 | tr -dc 'A-Za-z0-9' | head -c 20)
kubectl create secret generic grafana-admin \
  --namespace monitoring \
  --from-literal=admin-password="$GRAFANA_PASS" \
  --dry-run=client -o yaml | kubectl apply -f -
echo "Grafana admin password (save this): $GRAFANA_PASS"

kubectl apply -f k8s/monitoring/grafana.yaml

# Trading services (images pulled from GHCR).
# Pin the image tag to the exact commit deployed (CI publishes <sha> tags).
IMAGE_TAG=$(git rev-parse HEAD)
for svc in tick-ingestion signal-processor order-execution; do
  sed "s/__IMAGE_TAG__/$IMAGE_TAG/g" "k8s/services/$svc.yaml" | kubectl apply -f -
done

echo "=== All manifests applied ==="
# IMDSv2 requires a session token
IMDS_TOKEN=$(curl -sX PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" \
  http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Grafana: http://$PUBLIC_IP:30300"
echo "Prometheus: http://$PUBLIC_IP:30090"
echo "Bootstrap complete at: $(date)"
