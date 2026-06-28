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

# Kafka (Redpanda)
kubectl apply -f k8s/kafka/redpanda.yaml

# Wait for Redpanda to be ready before starting services
echo "Waiting for Redpanda to start..."
sleep 60
kubectl wait --for=condition=ready pod -l app=redpanda -n trading --timeout=180s || true

# Monitoring stack
kubectl apply -f k8s/monitoring/prometheus.yaml
kubectl apply -f k8s/dashboards/dashboard-configmap.yaml
kubectl apply -f k8s/monitoring/grafana.yaml

# Trading services (images pulled from GHCR)
kubectl apply -f k8s/services/tick-ingestion.yaml
kubectl apply -f k8s/services/signal-processor.yaml
kubectl apply -f k8s/services/order-execution.yaml

echo "=== All manifests applied ==="
echo "Grafana: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):30300"
echo "Prometheus: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):30090"
echo "Bootstrap complete at: $(date)"
