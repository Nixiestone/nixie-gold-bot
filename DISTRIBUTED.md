# Distributed Trading Infrastructure

A Kafka-driven, asyncio-microservice deployment of the Nixie gold strategy, running
on single-node k3s with full IaC (OpenTofu) and observability (Prometheus + Grafana).
The existing monolithic bot (`main.py`, `data/`, MT5 integration) is unchanged — this
is an alternative, cloud-native runtime that reuses the same strategy logic.

```
Alpha Vantage (intraday -> daily+quote -> simulation fallback)
        |
        v   Kafka topics: raw.ticks -> processed.signals -> executed.orders
        |
  tick-ingestion -> signal-processor -> order-execution
                                            |
                                            +-> Telegram + Neon PostgreSQL

  Prometheus scrape -> Grafana dashboards
```

## Components

| Component | Tech | Notes |
|---|---|---|
| Broker | Redpanda (Kafka API) | single broker, ~250 MB RAM |
| Services | Python asyncio | `services/{tick-ingestion,signal-processor,order-execution}` |
| Strategy | reused from `services/shared/` | indicators/structural/signal logic, MT5 removed |
| DB | Neon PostgreSQL (free) | `signals` + `orders` tables (`infra/schema.sql`) |
| Observability | Prometheus + Grafana | dashboard in `k8s/dashboards/` |
| Orchestration | k3s | `--disable traefik --disable servicelb` |
| IaC | OpenTofu | `infra/` |
| Images | GHCR via GitHub Actions | `.github/workflows/build-images.yml` |

## Deploy

1. **Create free accounts**: AWS, Alpha Vantage, Neon, a Telegram bot.
2. **Run the DB schema** once against Neon: `psql "$NEON_DATABASE_URL" -f infra/schema.sql`.
3. **Set variables** — create `infra/terraform.tfvars` (git-ignored):
   ```hcl
   key_pair_name      = "my-keypair"
   allowed_ssh_cidr   = "203.0.113.4/32"   # YOUR IP — required, /32
   allowed_ui_cidr    = "203.0.113.4/32"   # YOUR IP — required, /32
   alpha_vantage_key  = "..."
   telegram_bot_token = "..."
   telegram_chat_id   = "..."
   neon_database_url  = "postgresql://...?sslmode=require"
   github_token       = "ghp_..."        # optional: only if GHCR packages are private (scope read:packages)
   ```
4. **Deploy**: `cd infra && tofu init && tofu apply`.
5. Outputs give the Grafana/Prometheus URLs; the Grafana admin password is
   generated on the box and printed to `/var/log/user-data.log`.

### Local smoke test

```bash
cp .env.example .env   # fill in keys
docker compose up --build
# Grafana at http://localhost:3000  (admin / trading2024 locally)
```

## Security notes

- **SSH and the Grafana/Prometheus NodePorts are locked to `allowed_ssh_cidr` /
  `allowed_ui_cidr`.** Terraform refuses `0.0.0.0/0` for either.
- **No secrets in git.** Terraform state, `*.tfvars`, and `.env` are git-ignored;
  k8s secrets are created at deploy time (`kubectl create secret`), never committed.
- **IMDSv2 required**, root EBS volume encrypted, default-deny ingress NetworkPolicies.
- **Grafana admin password** is randomly generated per deploy and stored in a k8s Secret.

## Free-tier data caveat

`FX_INTRADAY` is a **premium** Alpha Vantage function and `XAU` may not be supported on
every plan. `tick-ingestion` degrades gracefully:
1. FX_INTRADAY 5-min bars (if your key allows it),
2. else FX_DAILY seed + `CURRENCY_EXCHANGE_RATE` realtime quote polling (free),
3. else pure random-walk simulation (keeps the pipeline flowing with no API).

Check `kubectl logs deploy/tick-ingestion -n trading` to see which tier is active.

## Legacy monolith warning

The original `config.py` sets `AUTO_TRADE = True` (line 74). The **cloud services do
not execute live trades** — `order-execution` only sends Telegram alerts and writes to
the DB. But if you run the legacy `main.py` / `launcher.py` directly against a funded MT5
account, it **will place real orders**. Set `AUTO_TRADE = False` (and use a demo account)
before running the monolith.
