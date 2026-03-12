# Backend Deployment Guide

Complete guide for deploying the Backend service to production.

## Deployment Overview

The Backend service can be deployed in multiple environments:

1. **Docker Compose** (Development/Staging)
2. **Docker Container** (Kubernetes/Cloud)
3. **Traditional Server** (VPS/Bare Metal)

This guide covers each approach.

---

## Prerequisites

- Git repository cloned
- `.env` file configured with production values
- Docker installed (for container deployments)
- Access to target environment
- Domain name (for HTTPS)

---

## Pre-Deployment Checklist

### Configuration Review

- [ ] `SECRET_KEY` changed to secure value
- [ ] `MONGO_URI` points to production database
- [ ] `CHATBOT_SERVICE_URL` correct for environment
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` appropriate
- [ ] `LOG_LEVEL` set to INFO or WARNING
- [ ] All sensitive values in `.env` (not in code)

### Code Review

- [ ] All tests passing: `uv run pytest tests/`
- [ ] No debug code or print statements
- [ ] Linting passes: `uv run ruff check .`
- [ ] No hardcoded passwords or secrets
- [ ] Documentation up-to-date

### Database Preparation

- [ ] MongoDB instance running and accessible
- [ ] Database indexes created
- [ ] Backup procedure in place
- [ ] Initial data seeded

### Security Review

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Security headers added
- [ ] Monitoring configured

---

## Deployment Method 1: Docker Compose

### Best For
- Development environments
- Staging servers
- Testing full stack locally
- Simple deployments

### Setup

1. **Navigate to project root:**
```bash
cd /path/to/TFG-Chatbot
```

2. **Create production `.env`:**
```bash
cat > .env.prod << 'EOF'
# Services
CHATBOT_SERVICE_URL=http://chatbot:8080
RAG_SERVICE_URL=http://rag_service:8081

# MongoDB
MONGO_HOSTNAME=mongo
MONGO_PORT=27017
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=your-secure-password
MONGO_AUTH_DB=admin
DB_NAME=tfg_chatbot

# JWT
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
EOF

chmod 600 .env.prod  # Secure file permissions
```

3. **Update docker-compose.yml** (if needed):
```yaml
services:
  backend:
    image: tfg-backend:latest
    ports:
      - "8000:8000"
    environment:
      CHATBOT_SERVICE_URL: http://chatbot:8080
      RAG_SERVICE_URL: http://rag_service:8081
    depends_on:
      - mongo
      - chatbot
      - rag_service
    restart: unless-stopped

  mongo:
    image: mongo:latest
    environment:
      MONGO_INITDB_ROOT_USERNAME: root
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```

4. **Build images:**
```bash
docker compose build
```

5. **Start services:**
```bash
docker compose up -d
```

6. **Verify deployment:**
```bash
curl http://localhost:8000/health
docker compose logs backend
```

### Monitoring

```bash
# View logs
docker compose logs -f backend

# Check status
docker compose ps

# View resource usage
docker stats tfg-backend
```

### Updating

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker compose build backend
docker compose up -d backend

# Verify
curl http://localhost:8000/health
```

---

## Deployment Method 2: Docker Container (Cloud)

### Best For
- Production environments
- Kubernetes deployments
- Scalable cloud platforms
- Multi-environment setups

### Building Docker Image

1. **Build image locally:**
```bash
cd backend
docker build -t tfg-backend:1.0.0 .
```

2. **Tag for registry:**
```bash
# Docker Hub
docker tag tfg-backend:1.0.0 yourname/tfg-backend:1.0.0
docker tag tfg-backend:1.0.0 yourname/tfg-backend:latest

# Or your own registry
docker tag tfg-backend:1.0.0 registry.example.com/tfg-backend:1.0.0
```

3. **Push to registry:**
```bash
# Docker Hub
docker login
docker push yourname/tfg-backend:1.0.0

# Or your registry
docker push registry.example.com/tfg-backend:1.0.0
```

### Running Container

**Basic:**
```bash
docker run -d \
  --name tfg-backend \
  -p 8000:8000 \
  --env-file .env.prod \
  --network backend-network \
  tfg-backend:1.0.0
```

**With health check:**
```bash
docker run -d \
  --name tfg-backend \
  -p 8000:8000 \
  --env-file .env.prod \
  --network backend-network \
  --health-cmd='curl -f http://localhost:8000/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  tfg-backend:1.0.0
```

**With volume mount (for logs):**
```bash
docker run -d \
  --name tfg-backend \
  -p 8000:8000 \
  --env-file .env.prod \
  -v /var/log/tfg-backend:/app/logs \
  tfg-backend:1.0.0
```

### Kubernetes Deployment

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tfg-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tfg-backend
  template:
    metadata:
      labels:
        app: tfg-backend
    spec:
      containers:
      - name: tfg-backend
        image: yourname/tfg-backend:1.0.0
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: backend-secrets
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1024Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: tfg-backend
spec:
  selector:
    app: tfg-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Deploy:**
```bash
# Create secrets
kubectl create secret generic backend-secrets \
  --from-literal=SECRET_KEY=<your-secret>

# Create config
kubectl create configmap backend-config \
  --from-literal=CHATBOT_SERVICE_URL=http://chatbot:8080

# Deploy
kubectl apply -f deployment.yaml

# Verify
kubectl get pods
kubectl get service tfg-backend
```

---

## Deployment Method 3: Traditional Server

### Best For
- VPS deployments
- On-premise hosting
- Simple setups without Docker
- Cost-effective hosting

### Setup

1. **Connect to server:**
```bash
ssh user@server.example.com
```

2. **Install Python 3.13:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.13 python3.13-venv

# RHEL/CentOS
sudo yum install python3.13
```

3. **Install uv:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

4. **Clone repository:**
```bash
cd /opt
sudo git clone https://github.com/GabrielFranciscoSM/TFG-Chatbot.git
sudo chown -R $USER:$USER TFG-Chatbot
cd TFG-Chatbot
```

5. **Install dependencies:**
```bash
cd backend
uv sync
```

6. **Configure environment:**
```bash
# Create .env with production values
nano .env
```

7. **Create systemd service:**
```bash
sudo tee /etc/systemd/system/tfg-backend.service > /dev/null << EOF
[Unit]
Description=TFG Chatbot Backend Service
After=network.target mongodb.service

[Service]
Type=notify
User=tfg-user
Group=tfg-user
WorkingDirectory=/opt/TFG-Chatbot/backend
Environment="PATH=/opt/TFG-Chatbot/backend/.venv/bin"
ExecStart=/opt/TFG-Chatbot/backend/.venv/bin/python -m backend
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tfg-backend
sudo systemctl start tfg-backend
```

8. **Setup Nginx reverse proxy:**
```bash
sudo tee /etc/nginx/sites-available/tfg-backend > /dev/null << EOF
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name backend.example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/tfg-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

9. **Setup HTTPS with Let's Encrypt:**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d backend.example.com
```

10. **Verify service:**
```bash
sudo systemctl status tfg-backend
curl https://backend.example.com/health
```

---

## HTTPS Setup

### Let's Encrypt (Free)

**With certbot:**
```bash
sudo certbot certonly --standalone \
  -d backend.example.com \
  -d www.backend.example.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

**Nginx configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name backend.example.com;

    ssl_certificate /etc/letsencrypt/live/backend.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/backend.example.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name backend.example.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Database Deployment

### MongoDB Atlas (Recommended for Production)

1. **Create cluster:**
   - Visit https://www.mongodb.com/cloud/atlas
   - Sign up or login
   - Create cluster (M10 or larger for production)

2. **Configure connection:**
```bash
# Connection string from Atlas
MONGO_URI=mongodb+srv://user:password@cluster.mongodb.net/tfg_chatbot?retryWrites=true&w=majority
```

3. **Create indexes:**
```bash
mongosh "mongodb+srv://user:password@cluster.mongodb.net/tfg_chatbot"

use tfg_chatbot
db.users.createIndex({"username": 1}, {unique: true})
db.users.createIndex({"email": 1}, {unique: true})
db.sessions.createIndex({"user_id": 1})
```

### Self-Hosted MongoDB

**Docker:**
```bash
docker run -d \
  --name mongo \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=secure_password \
  -v mongo_data:/data/db \
  -p 27017:27017 \
  mongo:latest
```

**Traditional:**
```bash
# Install
sudo apt-get install mongodb

# Secure
sudo systemctl restart mongod
sudo mongosh
> use admin
> db.createUser({user: "root", pwd: "password", roles: ["root"]})

# Configure replication (recommended)
# Edit /etc/mongod.conf
replication:
  replSetName: rs0

# Initialize replica set
mongosh
> rs.initiate()
```

---

## Monitoring & Logging

### Application Logs

**View logs:**
```bash
# Docker Compose
docker compose logs -f backend

# Systemd
sudo journalctl -u tfg-backend -f

# Log files
tail -f /var/log/tfg-backend/app.log
```

### Prometheus Metrics

**Access metrics:**
```bash
curl http://localhost:8000/metrics
```

**Prometheus config:**
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'tfg-backend'
    static_configs:
      - targets: ['localhost:8000']
```

### Health Checks

```bash
# Quick check
curl http://localhost:8000/health

# Detailed check
curl http://localhost:8000/system/info

# Monitor continuously
watch -n 5 "curl -s http://localhost:8000/health"
```

### Error Alerts

Set up alerts for:
- Service down (no response)
- High error rate (>5% 5xx errors)
- Slow responses (>1s)
- Database connection failures

---

## Database Backup

### Automated Backup

**Backup script:**
```bash
#!/bin/bash
# backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/tfg-chatbot"
mkdir -p "$BACKUP_DIR"

# Backup MongoDB
mongodump --uri "mongodb://root:password@localhost:27017" \
  --db tfg_chatbot \
  --out "$BACKUP_DIR/tfg_chatbot_$TIMESTAMP"

# Compress
tar -czf "$BACKUP_DIR/tfg_chatbot_$TIMESTAMP.tar.gz" \
  "$BACKUP_DIR/tfg_chatbot_$TIMESTAMP"

# Upload to S3
aws s3 cp "$BACKUP_DIR/tfg_chatbot_$TIMESTAMP.tar.gz" \
  s3://my-backups/tfg-chatbot/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

**Cron schedule:**
```bash
# Daily backup at 2 AM
0 2 * * * /opt/scripts/backup.sh
```

### Restore from Backup

```bash
# Extract backup
tar -xzf tfg_chatbot_20240115_020000.tar.gz

# Restore
mongorestore --uri "mongodb://root:password@localhost:27017" \
  --db tfg_chatbot \
  tfg_chatbot_20240115_020000/tfg_chatbot
```

---

## Performance Tuning

### Uvicorn Workers

**Configure workers:**
```bash
# In docker-compose.yml or systemd service
uv run uvicorn backend.api:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4  # Use 2-4 * CPU cores
```

### Connection Pooling

**MongoDB pooling:**
```python
# In config.py
mongo_uri = "mongodb://.../?maxPoolSize=50&minPoolSize=10"
```

### Caching

Consider implementing:
- Redis for session caching
- Browser caching headers
- CDN for static files

---

## Scaling

### Load Balancing

**Nginx upstream:**
```nginx
upstream backend {
    least_conn;  # Load balancing algorithm
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    keepalive 32;
}
```

### Horizontal Scaling

**Docker Compose scaling:**
```bash
docker compose up -d --scale backend=3
```

**Kubernetes scaling:**
```bash
kubectl scale deployment tfg-backend --replicas=5
```

---

## Rollback

### Docker Compose

```bash
# View image history
docker images | grep tfg-backend

# Rollback to previous version
docker compose down
docker compose pull tfg-backend:1.0.0
docker compose up -d
```

### Kubernetes

```bash
# View rollout history
kubectl rollout history deployment/tfg-backend

# Rollback to previous version
kubectl rollout undo deployment/tfg-backend

# Rollback to specific revision
kubectl rollout undo deployment/tfg-backend --to-revision=2
```

---

## Security Hardening

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw deny 8000/tcp  # Block direct access
```

### Network Security

```bash
# Limit connections
# In /etc/security/limits.conf
*  soft  nofile  65535
*  hard  nofile  65535
```

### Regular Updates

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade

# Update Python packages
cd backend
uv pip install --upgrade pip
uv sync
```

---

## Troubleshooting

### Service Not Starting

```bash
# Check logs
sudo journalctl -u tfg-backend -n 50

# Test configuration
uv run python -c "from backend.config import settings; print(settings)"

# Manual start
cd /opt/TFG-Chatbot/backend
uv run python -m backend
```

### High Memory Usage

```bash
# Check memory
docker stats tfg-backend

# Reduce worker count
# Increase timeout in monitoring
```

### Database Connection Errors

```bash
# Test connection
mongosh $MONGO_URI

# Check credentials
echo $MONGO_URI

# Verify firewall
nc -zv mongodb.example.com 27017
```

---

## Related Documentation

- [Configuration](./configuration.md) - Environment setup
- [Database](./database.md) - MongoDB administration
- [Development](./development.md) - Local development
