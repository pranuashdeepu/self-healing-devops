# Self-Healing Infrastructure (Prometheus + Alertmanager + Ansible)

This project demonstrates auto-healing: if **NGINX** goes down, **Prometheus** (via **Blackbox Exporter**) fires an alert; **Alertmanager** calls a **webhook** which runs an **Ansible playbook** to restart the NGINX container.

## Prerequisites
- Docker + Docker Compose installed
- Ports available: 8080, 8081, 9090, 9093, 9115, 5001

## Quick Start
```bash
# 1) Start the stack
docker compose up -d

# 2) Open UIs
# NGINX
http://localhost:8080

# Prometheus
http://localhost:9090

# Alertmanager
http://localhost:9093

# Blackbox (optional)
http://localhost:9115/probe?module=http_2xx&target=http://nginx:80

# Webhook health
http://localhost:5001/health
```

## How it Works
- **Blackbox Exporter** probes `http://nginx:80` every 15s.
- If probe fails for 30s, the `NginxDown` alert fires.
- **Alertmanager** sends a POST to `http://webhook:5001/alert`.
- The **webhook** runs `ansible-playbook` which restarts the `nginx` container via the Docker socket.

## Trigger a Failure & Watch Auto-Heal
```bash
# Stop NGINX (simulate failure)
docker stop nginx

# Follow webhook logs to see Ansible running
docker logs -f webhook

# Within ~30-60s the playbook restarts the container
# Confirm it's back:
docker ps | grep nginx
curl -I http://localhost:8080
```

## Files to submit (deliverables)
- `prometheus/prometheus.yml` (Prometheus config)
- `prometheus/rules.yml` (alert rules)
- `alertmanager/alertmanager.yml` (webhook receiver)
- `ansible/playbooks/heal_nginx.yml` (Ansible playbook)
- Demo screenshots of the alert firing and the container being restarted (from `docker logs -f webhook` and Prometheus/Alertmanager UI)

## Troubleshooting
- If alerts never fire, open Prometheus → **Status → Targets** and ensure all targets are **UP** (except the nginx probe **after you stop NGINX**).
- If the webhook logs show error about Docker socket, ensure `webhook` service has:
  ```yaml
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  ```
- If you changed the nginx port, update the `prometheus.yml` blackbox target and `rules.yml` accordingly.