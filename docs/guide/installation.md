---
layout: default
title: Installation
parent: Developer Guide
nav_order: 1
---

# Installation

Complete guide to installing and setting up the TFG-Chatbot project.

---

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| **Python** | 3.13+ | Backend services, math investigation |
| **Node.js** | 20+ | Frontend development |
| **uv** | Latest | Python package manager (recommended) |
| **Podman** or **Docker** | Latest | Container orchestration |
| **Git** | Latest | Version control |

### Installing Prerequisites

#### Python 3.13+

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv

# macOS (with Homebrew)
brew install python@3.13

# Verify installation
python3.13 --version
```

#### uv (Python Package Manager)

```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv

# Verify installation
uv --version
```

#### Podman (or Docker)

```bash
# Ubuntu/Debian (Podman)
sudo apt install podman podman-compose

# macOS
brew install podman podman-compose

# Verify installation
podman --version
podman-compose --version
```

{: .note }
All `docker` and `docker-compose` commands work with Podman. The project uses `podman-compose` but commands are interchangeable.

#### Node.js 20+

```bash
# Using nvm (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
nvm install 20
nvm use 20

# Verify installation
node --version
npm --version
```

### API Keys (Optional)

For LLM functionality, you need at least one:

| Provider | Environment Variable | Notes |
|----------|---------------------|-------|
| **Gemini** (default) | `GOOGLE_API_KEY` | Free tier available |
| **Mistral** | `MISTRAL_API_KEY` | Alternative provider |
| **vLLM** | `VLLM_API_URL` | Self-hosted production |

---

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/GabrielFranciscoSM/TFG-Chatbot.git
cd TFG-Chatbot
```

### 2. Create Python Virtual Environment

```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### 3. Install Python Dependencies

```bash
# Install all packages in development mode
uv pip install -e ./backend -e ./rag_service -e ./chatbot -e .

# For development (with test and quality tools)
uv pip install -e ".[test,quality,dev]"
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example environment file if available
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# ============================================================================
# LLM Configuration
# ============================================================================
LLM_PROVIDER=gemini              # Options: gemini, mistral, vllm
GOOGLE_API_KEY=your-gemini-key   # Required if LLM_PROVIDER=gemini
MISTRAL_API_KEY=your-key         # Required if LLM_PROVIDER=mistral

# ============================================================================
# MongoDB Configuration
# ============================================================================
MONGO_ROOT_USERNAME=root
MONGO_ROOT_PASSWORD=example
MONGO_HOSTNAME=localhost         # Use 'mongo' inside containers

# ============================================================================
# Service URLs (for local development)
# ============================================================================
CHATBOT_SERVICE_URL=http://localhost:8080
RAG_SERVICE_URL=http://localhost:8081
OLLAMA_URL=http://localhost:11434

# ============================================================================
# Security
# ============================================================================
SECRET_KEY=your-secret-key-for-jwt-at-least-32-chars
```

### 6. Pre-commit Hooks (Optional but Recommended)

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

---

## Verify Installation

```bash
# Check Python packages
uv pip list | grep tfg

# Check services can import
python -c "from backend.api import app; print('Backend OK')"
python -c "from chatbot.api import app; print('Chatbot OK')"
python -c "from rag_service.api import app; print('RAG Service OK')"
```

---

## Next Steps

Once installation is complete, proceed to [Quick Start](quickstart.html) to run the services.
