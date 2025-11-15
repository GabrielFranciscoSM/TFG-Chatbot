# Changelog

Todos los cambios relevantes entre versiones se verán reflejados en este archivo.

El formato del documento se basa en [keep a changelog](https://keepachangelog.com/en/1.1.0/) y se adiere al [versionado semántico](https://semver.org/).


## [0.2.0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.1.4...v0.2.0) (2025-11-15)


### Features

* **ci:** add automated release workflows ([3672529](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/367252912e948121d2eb6b3072be71769d51b2a1))
* implement comprehensive CI/CD pipeline ([a8319e0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a8319e03fd7f382cd0de5a4fed14b4fbbbea733a))
* implement comprehensive CI/CD pipeline ([e9916d6](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e9916d6d8ca36f5b503ec1deeecf6730090170bb))
* implement comprehensive CI/CD pipeline ([ab8a65a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ab8a65a343fbba7751998286a6e0ef5c31170968))
* New tool, Generate adaptive test, implemented closes [#33](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/33) closes [#34](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/34) ([b2be0ab](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b2be0ab2fb1055422ef20ed08806bca1e699d0cc))


### Bug Fixes

* add load: true to docker build-push-action ([8ba3b36](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8ba3b361bda05e091a1d012c7f2daaf65a8eef0b))
* add pytest-cov to dev dependencies ([aea25d3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/aea25d3da53af17908bcfd48b2392b946a484ced))
* **ci:** configure Release Please permissions and add setup guide ([bf8870f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bf8870fc453a970cab89c661220e64036ecfca84))
* **ci:** configure Release Please permissions and add setup guide ([bf49012](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bf490122f84340cf5e28102a957f153a687a0283))
* **ci:** install root project dependencies for integration tests ([af26173](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/af2617369450ccbe24aa046124901d156bf634a6))
* replace docker-compose with docker compose ([b46afea](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b46afeadb0c4244c90e198fc5331b98e046f0e39))
* run rag_service tests excluding integration marker ([d829dc8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/d829dc802230a8197d911871d8652e49ea054b01))
* use only Python 3.12 in workflows ([9b74c17](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9b74c17e4547841206bae1c405fba536a20bca16))


### Documentation

* Add daily scrum documentation for November 2025 ([96ffb37](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/96ffb37e0d11c560b0930ad767038b261c30192d))
* added ADR for linters and formaters ([53f90c8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/53f90c877fe029b997ffeb9fb6f77a864f625f1e))
* ADR for mongoDB to store guia docente JSONs ([bfea364](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bfea3648ead0f6a4af91e2a6c9a96da155dc9865))
* Srum retrospective ([649f52a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/649f52a870525122fdcc7e2a3f25d929bdf4413e))
* updated ADR with uv ([32c5083](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/32c5083496bb55ff4093188776fc97a1d6457c40))
* Updated docstring ([9ce2e07](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9ce2e07bef98c79145ca39cd00c4bc4917824332))

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
