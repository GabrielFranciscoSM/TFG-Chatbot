# Changelog

Todos los cambios relevantes entre versiones se verán reflejados en este archivo.

El formato del documento se basa en [keep a changelog](https://keepachangelog.com/en/1.1.0/) y se adiere al [versionado semántico](https://semver.org/).


## [Unreleased]

## [0.1.4] - 2025-10-24

### Fixed

- Fixed Google Pages.

### Changed

- Updated dependency files from `requirements.txt` to `pyproject.toml` and `uv.lock`.

## [0.1.3] - 2025-10-24

### Added

- ADR system: Architecture Decision Records under `docs/ADR` with a template, README and index page.
- Initial ADRs (0001–0009) documenting major decisions: FastAPI, LangChain/LangGraph, Podman, SQLite (graph memory), Pydantic, pytest, vLLM, Ollama (embeddings/RAG), Qdrant (vector store).
- `scripts/new_adr.sh` helper: creates numbered ADRs and now auto-writes `parent: Architecture Decision Records` and a `nav_order` value.
- `docs/ADR/adr-template.md` updated with navigation metadata notes.

### Changed

- Jekyll integration: ADR index page added so ADRs appear under DevLog → Architecture Decision Records in the site navigation; ADR pages include `parent` and `nav_order` front-matter.
- Documentation and navigation updated to reflect ADR listings.

## [0.1.2] - 2025-10-11

### Added

- GitHub Pages website con tema Just the Docs
- Workflow de Jekyll para generación automática de la web
- Badge en README enlazando a la página web del proyecto

### Changed

- Actualizado estado del proyecto de "empty" a "en desarrollo" en badges
- Configuración Jekyll optimizada para evitar duplicación de títulos

## [0.1.1] - 2025-10-11

### Changed

- Modified test configuration and structure
- Updated Docker configuration

### Added

- New infrastructure tests
- Integration test configuration

### Removed

- Removed container tests (replaced with infrastructure tests)

## [0.1.0] - 2025-10-10

### Added

- FastAPI-based backend API (`backend/api.py`) con endpoints `/`, `/health` and `/chat`.
- `GraphAgent`: agente de IA en el backend responsable de la lógica conversacional y manejo de diálogos (implementado en `logic/graph.py`).
- Pruebas: conjunto de tests unitarios y de integración para la API y la lógica del agente (carpeta `tests/`, incluyendo tests de integración para el backend).
- Infraestrutura: Docker compose con vLLM para inferencia del modelo Qwen2.5-1.5b-instruct

