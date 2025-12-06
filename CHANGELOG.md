# Changelog

Todos los cambios relevantes entre versiones se verán reflejados en este archivo.

El formato del documento se basa en [keep a changelog](https://keepachangelog.com/en/1.1.0/) y se adiere al [versionado semántico](https://semver.org/).


## [0.4.1](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.4.0...v0.4.1) (2025-12-06)


### ⚠ BREAKING CHANGES

* **config:** Settings field names changed from UPPERCASE to lowercase

### Documentation

* add frontmatter to ADR documents for consistent formatting ([58150a3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/58150a39bf43c6a4a2991ea925507e63e99d9441))
* add microservices architecture documentation and OpenAPI export ([b5230a8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b5230a8995a070485908cd5d880c1ef02c43996c))


### Miscellaneous Chores

* release 0.4.1 ([866f71c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/866f71c6f2da654f23437e251be1af9f93e31acc))


### Code Refactoring

* **config:** migrate to pydantic-settings for type-safe configuration ([cf0adfe](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cf0adfe619a453de028e90aeb4dad2cdcf7542a2))

## [0.4.0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.3.0...v0.4.0) (2025-12-06)


### Features

* **auth:** implement role-based navigation and guards ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **backend:** add admin endpoints for stats, users, search, assign and promote ([162f88e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/162f88e6056473b74d80c678279f25c54c3a884e))
* **backend:** add history endpoint and session validation ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **backend:** add professor dashboard API endpoints ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **chatbot:** add history retrieval method ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **chat:** implement chat functionality with optimized API responses ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **dashboard:** add professor dashboard with subject management ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **frontend:** add advanced students table with search, sort, and pagination ([69484a5](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/69484a51f57314f58cf7f6e220e77bf864de4e01))
* **frontend:** add advanced users table with search, filter, and pagination ([f751d64](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/f751d64784b9af7fdfd3aeae5e94a5384caa7559))
* **frontend:** add autocomplete to admin dialogs ([a0643cd](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a0643cd9e2e7462e0d2fbdef3ea6b009e068db5f))
* **frontend:** add Biome for linting and formatting ([42f660f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/42f660f5d4f024adba4c49d5fd2aa2678e66d342))
* **frontend:** add chat types and hooks ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **frontend:** add chat UI components ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **frontend:** add containerization with Nginx ([4c091bb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4c091bb984096292bcfd09b568965c985617106c))
* **frontend:** add enroll/unenroll functionality to StudentList ([49f9060](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/49f90605732e28cef79876e486acea86d67169dc))
* **frontend:** add markdown rendering for chat messages ([56d4f4e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/56d4f4e5fd6aa5cf27d55b8507071e6fed242d51))
* **frontend:** add professor dashboard and role-based access ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **Frontend:** implement core layout and authentication features ([1912e47](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1912e47b58d1debce3ac0e02496f8eb254af3dcb))
* **frontend:** implement layout, routing and route guards ([8a8584e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8a8584efc0108be84603c344d34f8bbdf4ee9d56))
* **frontend:** integrate admin dialogs and update dashboard UI ([1e1bc54](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1e1bc543026ef172ae5cb63265eaf4ff78fed77e))
* **frontend:** integrate auth forms with backend API ([fb77597](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/fb77597c2f7812006ca96a02b07d31b3dec123b3))
* **hooks:** add dashboard data fetching hooks ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **rag:** add file deletion endpoint ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **settings:** create unified settings page for all roles ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))


### Bug Fixes

* **chatbot:** include subject context in system prompt ([3ac38da](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3ac38da68078602ad511f0fe6426f9e19ff538b7))
* **dependencies:** update passlib and bcrypt version constraints ([2f4e492](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2f4e4923cf2dee8aee3775b7179c770ee2e3f474))
* **frontend:** fix Biome linting and TypeScript config for tests ([00706c2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/00706c2086d0cf6266711cbf994ddab9e9f73eb6))
* **frontend:** normalize subject case for session creation ([bf1ac14](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bf1ac147c6404f5bf0147e3020f90f23235f6330))
* **frontend:** update Biome linting and formatting checks in CI and pre-commit hooks ([2ff508f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2ff508fd8bcebc27a97defcb511f9d50d1c7e3f7))
* **ui:** resolve navigation and responsiveness issues ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))


### Performance Improvements

* reduce payload size by returning only new message per request ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))


### Documentation

* add sprint retrospective 3 ([7c179c8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/7c179c88ba234efd8ba715881fa9dc756679538f))
* **ADR:** add architecture decision records for frontend technologies (React, Vite, Tailwind CSS, Shadcn/ui, TanStack Query, React Router, Zod, React Hook Form) ([757ea81](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/757ea81d5297528793acff2945c7a0c7c344651f))
* **daily-scrum:** add december daily scrums and sprint planning ([8c9daa2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8c9daa28d823e535236b1478a55237fcf10d1cdf))
* **SCRUM:** add daily scrum entries for November 25-27, 2025 and update Sprint Planning 4 dates ([478a391](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/478a3914dbee22f5583a20ce9d73c8777a119108))
* **SCRUM:** add Sprint Planning 4 documentation for UI Frontend development ([27e2e64](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/27e2e6498eef1141c481cc307930a59e6c6aa6eb))
* update daily scrum with Sprint 4 frontend progress ([4c1e9e0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4c1e9e0b377fe3e17e17c88738f41d961df91cd4))

## [0.3.0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.2.1...v0.3.0) (2025-11-23)


### Features

* add unit tests and refactor backend for dependency injection ([671632c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/671632ce09cf17f58fc89b6dfb68d8de055dd3e9))
* **arch:** merge auth into backend and implement RBAC ([faddaa2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/faddaa2ae55e512a9217fe24020123e297de48bb))
* **arch:** refactor into microservices (Auth, Chatbot, Gateway) ([68f4aed](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/68f4aedbaab436618312f772d5ad9ae3e760c983))
* implement session management and integration with chat ([c9940a0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c9940a0c9e8a896188e1ce52555379efe8673f16))


### Bug Fixes

* add pytest-cov to backend dev dependencies ([b118862](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b11886277fe4cd8a9845b88cebaf66dfe86e2a7d))
* **ci:** Fix release-please docker images generation permissions ([38925eb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/38925eb9bd6e29203965a14ad30eaf28ce5f18d5))
* **docs:** removed unnecesary documentation about please release ([67f0023](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/67f00236a4cb2b31d32cb1e9aedff417d07ee62c))
* resolve rag_service test failures by mocking external services and fixing patches ([2353e36](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2353e36d0b534bcd306fe2760cb5a705b1c4a82d))
* update vector store test to mock query_points instead of search ([2ae0e27](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2ae0e275677beab76f7f739303c37cb8fe3cd09f))


### Documentation

* **adr:** add architectural decisions for auth and gateway ([c0ad1ab](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c0ad1ab3fc13ffc44c498cc3ea48f70fef97424b))

## [0.2.1](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.2.0...v0.2.1) (2025-11-18)


### Bug Fixes

* **ci:** correct Docker build context for release workflows ([4dac49d](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4dac49db4725330c3aa7099ab96726db28c713d6))
* **ci:** Fixed Ollama wrong port and hosts for services. ([930cf3c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/930cf3cccc28f70b0773bd43173e2fa71e77c5bc))
* **ci:** optimize unit tests to run only on relevant file changes ([e0123d9](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e0123d9be78f9b5327f88224634de6a612e1f1ce))
* **ci:** optimize unit tests to run only on relevant file changes ([55bcbc1](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/55bcbc1ba3b090426de7a001138ab6aeef7332ef))
* **docs:** Sprint retrospective not showing ([b8341cd](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8341cda6bd9f657ee51a6862f97f7526211ee53))
* **RAG:** fixed langchain text splitters module ([cfbbced](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cfbbcedd05143cbe1cabbd36404a2d21e070cb26))


### Documentation

* **plan:** Created sprint plannification for sprint 3 ([a9643fb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a9643fb8cd9a8c73cbf31922d720ebd9ea12980e))

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
