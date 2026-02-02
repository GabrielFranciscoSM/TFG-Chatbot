---
layout: default
title: Monitoring Guide
parent: Developer Guide
nav_order: 6
---

# Monitoring Guide

The TFG-Chatbot uses a comprehensive observability stack with **Grafana** for metrics/logs and **Phoenix** for LLM tracing.

---

## Monitoring Stack Overview

| Service | Purpose | Port | URL |
|---------|---------|------|-----|
| **Grafana** | Dashboards & visualization | 3001 | `http://localhost:3001` |
| **Phoenix** | LLM observability & tracing | 6006 | `http://localhost:6006` |
| **Prometheus** | Metrics collection | 9093 | `http://localhost:9093` |
| **Loki** | Log aggregation | 3100 | `http://localhost:3100` |
| **Alertmanager** | Alert routing | 9094 | `http://localhost:9094` |

---

## Starting the Monitoring Stack

All monitoring services are included in docker-compose:

```bash
# Start all services including monitoring
docker compose up -d

# Verify monitoring services
docker compose ps | grep -E "grafana|phoenix|prometheus|loki"
```

---

## Phoenix - LLM Observability

Phoenix (by Arize AI) provides detailed tracing for LangChain/LangGraph operations.

### Accessing Phoenix

Open [http://localhost:6006](http://localhost:6006) in your browser.

### What Phoenix Tracks

- **LLM Calls**: Every call to Gemini/vLLM with prompts and responses
- **Chain Execution**: Full LangGraph node execution traces
- **Tool Calls**: RAG searches, guía docente lookups, web searches
- **Token Usage**: Input/output token counts per request
- **Latency**: Time spent in each component

### Phoenix Dashboard Features

1. **Traces View**: See all LLM interactions with full context
2. **Spans**: Drill down into individual operations
3. **Latency Distribution**: Identify slow operations
4. **Error Tracking**: Find failed LLM calls

### Example Trace

A typical chat interaction shows:

```
📦 Chat Request
├── 🔗 LangGraph: should_continue
├── 🤖 LLM Call: Gemini (tool selection)
├── 🔧 Tool: rag_search
│   └── 📊 Embedding: nomic-embed-text
├── 🤖 LLM Call: Gemini (response generation)
└── ✅ Response returned
```

### Configuration

Phoenix is configured via environment variables in `docker-compose.yml`:

```yaml
chatbot:
  environment:
    PHOENIX_HOST: phoenix
    PHOENIX_PORT: "6006"
    PHOENIX_PROJECT_NAME: tfg-chatbot
```

To disable Phoenix tracing:

```bash
PHOENIX_ENABLED=false docker compose up -d chatbot
```

---

## Grafana - Metrics & Logs

Grafana provides unified dashboards for system metrics and logs.

### Accessing Grafana

1. Open [http://localhost:3001](http://localhost:3001)
2. Login with:
   - **Username**: `admin`
   - **Password**: `admin` (or `GRAFANA_ADMIN_PASSWORD` from `.env`)

### Pre-configured Datasources

| Datasource | Purpose |
|------------|---------|
| **Prometheus** | Service metrics (HTTP requests, latency, errors) |
| **Loki** | Aggregated container logs |

### Available Dashboards

#### System Health Dashboard

Located at: `Dashboards > System Health`

Panels include:
- **Service Status**: Up/down status for all services
- **Request Rate**: HTTP requests per second by service
- **Error Rate**: 5xx errors percentage
- **Latency (P95)**: 95th percentile response times

#### Logs Dashboard

Located at: `Dashboards > Logs`

Features:
- **Log Stream**: Real-time logs from all containers
- **Filter by Service**: `{container_name="tfg-chatbot"}`
- **Search**: Full-text search across logs
- **Error Highlighting**: Automatic error detection

### Useful Queries

#### Prometheus (Metrics)

```promql
# Request rate by service
sum(rate(http_requests_total[5m])) by (job)

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)
/ sum(rate(http_requests_total[5m])) by (job) * 100

# P95 latency
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job)
)
```

#### Loki (Logs)

```logql
# All chatbot logs
{container_name="tfg-chatbot"}

# Error logs only
{container_name=~"tfg-.*"} |= "ERROR"

# Search for specific user
{container_name="tfg-gateway"} |~ "user_id=estudiante"

# JSON parsing (structured logs)
{container_name="tfg-chatbot"} | json | level="error"
```

### Creating Custom Dashboards

1. Click **+** → **New Dashboard**
2. Add a panel
3. Select datasource (Prometheus or Loki)
4. Write your query
5. Configure visualization
6. Save dashboard

---

## Prometheus - Metrics Collection

Prometheus scrapes metrics from all services.

### Accessing Prometheus

Open [http://localhost:9093](http://localhost:9093) for the Prometheus UI.

### Scraped Targets

Configured in `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'backend-gateway'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'rag-service'
    static_configs:
      - targets: ['rag-service:8081']

  - job_name: 'chatbot'
    static_configs:
      - targets: ['tfg-chatbot:8080']
```

### Checking Target Health

1. Go to **Status** → **Targets**
2. All targets should show `UP` in green

---

## Alerting

Alerts are configured in `alertmanager/alert_rules.yml`.

### Pre-configured Alerts

| Alert | Condition | Severity |
|-------|-----------|----------|
| **ServiceDown** | Service unreachable for 1 min | Critical |
| **HighErrorRate** | Error rate > 1% for 5 min | Warning |
| **HighLatency** | P95 latency > 2s for 5 min | Warning |

### Viewing Active Alerts

1. **Prometheus**: Alerts tab → shows firing alerts
2. **Alertmanager**: [http://localhost:9094](http://localhost:9094) → alert routing

### Customizing Alerts

Edit `alertmanager/alert_rules.yml`:

```yaml
groups:
  - name: custom_alerts
    rules:
      - alert: ChatbotHighLatency
        expr: |
          histogram_quantile(0.95, 
            sum(rate(http_request_duration_seconds_bucket{job="chatbot"}[5m])) by (le)
          ) > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Chatbot latency is high"
```

---

## Log Collection with Promtail

Promtail collects Docker container logs and sends them to Loki.

### Configuration

See `promtail-config.yml`:

```yaml
scrape_configs:
  - job_name: containers
    static_configs:
      - targets:
          - localhost
        labels:
          job: containerlogs
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
```

### Troubleshooting Logs

```bash
# Check Promtail is collecting logs
docker logs promtail

# Verify Loki is receiving logs
curl http://localhost:3100/ready
```

---

## Monitoring Best Practices

### For Development

1. **Use Phoenix** for debugging LLM behavior
2. Check **Grafana logs** when errors occur
3. Monitor **latency panels** during testing

### For Production

1. Set up **alert notifications** (email, Slack)
2. Create **SLO dashboards** (availability, latency)
3. Enable **long-term storage** for Prometheus
4. Configure **log retention** in Loki

### Quick Health Check

```bash
# Check all monitoring services
curl -s http://localhost:9093/-/healthy && echo "Prometheus OK"
curl -s http://localhost:3100/ready && echo "Loki OK"
curl -s http://localhost:3001/api/health && echo "Grafana OK"
curl -s http://localhost:6006 > /dev/null && echo "Phoenix OK"
```

---

## Troubleshooting

### Phoenix not receiving traces

1. Check chatbot can reach Phoenix:
   ```bash
   docker exec tfg-chatbot curl -s http://phoenix:6006
   ```

2. Verify instrumentation is enabled:
   ```bash
   docker logs tfg-chatbot | grep -i phoenix
   ```

### Grafana shows no data

1. Check Prometheus targets are UP
2. Verify datasource configuration in Grafana
3. Ensure time range includes recent data

### Logs not appearing in Loki

1. Check Promtail has access to Docker socket
2. Verify containers are producing logs:
   ```bash
   docker logs tfg-chatbot --tail 10
   ```

3. Test Loki query in Grafana Explore
