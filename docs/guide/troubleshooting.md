---
layout: default
title: Troubleshooting
parent: Developer Guide
nav_order: 6
---

# Troubleshooting

Common issues and their solutions.

---

## Container Issues

### Services Not Starting

**Symptom**: Containers fail to start or stay in "Restarting" state.

```bash
# Check container status
docker compose ps

# View logs for specific service
docker compose logs -f backend
docker compose logs -f chatbot

# Restart specific service
docker compose restart backend

# Full restart
docker compose down && docker compose up -d
```

### Port Already in Use

**Symptom**: Error message about port being in use.

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Container Resource Issues

**Symptom**: Containers are slow or crash.

```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  chatbot:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## Database Issues

### MongoDB Connection Refused

**Symptom**: `Connection refused` or `Authentication failed`.

```bash
# Verify MongoDB is running
docker exec mongo-service mongosh --eval "db.runCommand('ping')"

# Check credentials match .env
cat .env | grep MONGO

# Test connection manually
mongosh "mongodb://root:example@localhost:27017"
```

### MongoDB Data Corruption

**Symptom**: Database errors or missing data.

```bash
# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d

# Re-seed users
python scripts/seed_users.py
```

---

## LLM Issues

### Gemini API Key Invalid

**Symptom**: `401 Unauthorized` or `API key not valid`.

1. Verify your API key at [Google AI Studio](https://aistudio.google.com/)
2. Check the key is set correctly:
   ```bash
   echo $GOOGLE_API_KEY
   ```
3. Ensure no extra spaces or quotes in `.env`

### Ollama Model Not Found

**Symptom**: `model 'nomic-embed-text' not found`.

```bash
# List available models
docker exec ollama-service ollama list

# Pull model manually
docker exec ollama-service ollama pull nomic-embed-text

# Or run init script
./scripts/init_ollama.sh
```

### LLM Response Timeout

**Symptom**: Requests timeout or take too long.

1. Check LLM service health:
   ```bash
   curl http://localhost:11434/api/tags  # Ollama
   ```
2. Increase timeout in configuration
3. Use a faster model for development

---

## Python Issues

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'backend'`.

```bash
# Ensure packages are installed in development mode
uv pip install -e ./backend -e ./rag_service -e ./chatbot -e .

# Verify installation
uv pip list | grep tfg

# Activate virtual environment
source .venv/bin/activate
```

### Version Conflicts

**Symptom**: Dependency conflicts or version mismatches.

```bash
# Recreate virtual environment
rm -rf .venv
uv venv
source .venv/bin/activate
uv pip install -e ./backend -e ./rag_service -e ./chatbot -e ".[test,quality,dev]"
```

### Python Version Too Old

**Symptom**: `Python 3.13 required`.

```bash
# Check Python version
python --version

# Use pyenv to install 3.13
pyenv install 3.13
pyenv local 3.13
```

---

## Frontend Issues

### npm Install Fails

**Symptom**: Dependency installation errors.

```bash
# Clear npm cache
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### Build Errors

**Symptom**: TypeScript or build errors.

```bash
# Check for type errors
cd frontend
npm run check

# Fix linting issues
npm run check:fix
```

### CORS Errors

**Symptom**: `Access-Control-Allow-Origin` errors in browser.

1. Verify backend is running on expected port
2. Check CORS configuration in `backend/api.py`
3. Ensure frontend is using correct API URL

---

## Test Issues

### Tests Not Found

**Symptom**: `no tests ran` or `0 items collected`.

```bash
# Ensure correct directory
pwd  # Should be project root

# Check test discovery
pytest --collect-only tests/

# Verify markers
pytest --markers | grep -E "unit|integration"
```

### Integration Tests Fail

**Symptom**: Tests fail with connection errors.

1. Verify services are running:
   ```bash
   docker compose ps
   curl http://localhost:8000/health
   ```
2. Wait for services to be healthy
3. Check test environment variables

### Fixture Not Found

**Symptom**: `fixture 'xyz' not found`.

```bash
# Check conftest.py exists
ls tests/infrastructure/conftest.py

# View available fixtures
pytest --fixtures tests/infrastructure/
```

---

## Network Issues

### Service Cannot Reach Another Service

**Symptom**: Timeout errors between services.

```bash
# Test connectivity from container
docker exec tfg-chatbot curl http://rag_service:8081/health

# Check network
docker network ls
docker network inspect tfg-chatbot_default
```

### DNS Resolution Fails

**Symptom**: `Could not resolve host`.

```bash
# Use IP instead of hostname for testing
docker inspect rag-service | grep IPAddress

# Restart containers
docker compose down && docker compose up -d
```

---

## Performance Issues

### Slow Startup

**Symptom**: Services take long to start.

1. Pre-pull images:
   ```bash
   docker compose pull
   ```
2. Use `--no-rebuild` flag for testing:
   ```bash
   ./scripts/run_tests.sh all --no-rebuild
   ```

### High Memory Usage

**Symptom**: System becomes slow, OOM errors.

1. Check memory usage:
   ```bash
   docker stats
   ```
2. Reduce parallel test workers
3. Use smaller LLM models for development

---

## Getting Help

### Check Documentation

1. **ADRs**: Architecture decisions in `docs/ADR/`
2. **Copilot Instructions**: Technical details in `.github/copilot-instructions.md`
3. **API Docs**: Run services and visit `/docs` endpoints

### Debug Logging

Enable debug logging for more information:

```bash
export LOG_LEVEL=DEBUG
docker compose up
```

### Report Issues

If you can't resolve an issue:

1. Check [GitHub Issues](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues) for known problems
2. Create a new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - Logs and error messages
   - Environment details (OS, Python version, etc.)
