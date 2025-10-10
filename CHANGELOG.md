# Changelog

Todos los cambios relevantes entre versiones se verán reflejados en este archivo.

El formato del documento se basa en [keep a changelog](https://keepachangelog.com/en/1.1.0/) y se adiere al [versionado semántico](https://semver.org/).


## [Unreleased]

- Nothing yet.

## [0.1.0] - 2025-10-10

### Added

- FastAPI-based backend API (`backend/api.py`) con endpoints `/`, `/health` and `/chat`.
- `GraphAgent`: agente de IA en el backend responsable de la lógica conversacional y manejo de diálogos (implementado en `logic/graph.py`).
- Pruebas: conjunto de tests unitarios y de integración para la API y la lógica del agente (carpeta `tests/`, incluyendo tests de integración para el backend).
- Infraestrutura: Docker compose con vLLM para inferencia del modelo Qwen2.5-1.5b-instruct

