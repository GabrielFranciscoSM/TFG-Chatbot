# Changelog

Todos los cambios relevantes entre versiones se verán reflejados en este archivo.

El formato del documento se basa en [keep a changelog](https://keepachangelog.com/en/1.1.0/) y se adiere al [versionado semántico](https://semver.org/).


## [0.6.0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.6.0...v0.6.0) (2026-02-02)


### ⚠ BREAKING CHANGES

* **chatbot:** The web_search tool and DuckDuckGo integration have been removed. The tool was not being used correctly and added unnecessary complexity.
* **config:** Settings field names changed from UPPERCASE to lowercase

### Features

* [#23](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/23) [#24](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/24) Web search and calculator tools are now available for the graph agent to use. Tests for tools and integration created. ([03aece3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/03aece39e4ee89dfdfd00e344c3b1c2bb186eb80))
* [#25](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/25) Created graph.py basic agent and its tests ([59206be](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/59206beff281b653c7258ef527457bd9b9fe4140))
* Add file loading and management features to RAG service ([fe2db41](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/fe2db4199ccfc2f47fb6d846938e0ff7cb3c276b))
* Add Jekyll deployment workflow to GitHub Pages ([0cd02c6](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/0cd02c62596b00ca82dcb6eaaa7a47c4a2000890))
* add unit tests and refactor backend for dependency injection ([671632c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/671632ce09cf17f58fc89b6dfb68d8de055dd3e9))
* **arch:** merge auth into backend and implement RBAC ([faddaa2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/faddaa2ae55e512a9217fe24020123e297de48bb))
* **arch:** refactor into microservices (Auth, Chatbot, Gateway) ([68f4aed](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/68f4aedbaab436618312f772d5ad9ae3e760c983))
* **auth:** implement role-based navigation and guards ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **backend:** add admin endpoints for stats, users, search, assign and promote ([162f88e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/162f88e6056473b74d80c678279f25c54c3a884e))
* **backend:** add history endpoint and session validation ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **backend:** add professor dashboard API endpoints ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **backend:** add prometheus instrumentation [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([8408c13](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8408c13cd7eb8070db0eb22dcccbc7284e379bd9))
* **backend:** pass user_id to chatbot and add profile analytics endpoints ([070b513](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/070b513f14af48f1874feb0f172fce86946050d5))
* **chatbot:** add adaptive prompts by difficulty level (HU [#17](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/17)) ([c90cb26](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c90cb262612f84e9677935f2a6d8ff206fb1602e))
* **chatbot:** add difficulty classifier module ([4e27b33](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4e27b335e2cec86822b15d17fd2450ecb79aab8c))
* **chatbot:** add history retrieval method ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **chatbot:** add Mistral AI as LLM provider option ([3ea5462](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3ea5462fe5b03b69ebc67b198d034731721289bc))
* **chatbot:** add observability dependencies ([38ba70f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/38ba70f475cfd874fe5dabfa867c459f16e50aee))
* **chatbot:** add Phoenix LLM tracing instrumentation ([1b60a41](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1b60a41566be379aec13848b5b18342d62dd70fb))
* **chatbot:** add ProfileManager for student knowledge tracking ([716126f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/716126f4669548bbd7c1cf23e076d4522d1e50ec))
* **chatbot:** integrate difficulty classifier in agent flow ([cf49616](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cf49616194a608921ca5813d6f76257f2ebf75ef))
* **chatbot:** integrate student profile tracking in /chat endpoint ([862dbfe](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/862dbfe6ebbf7f8ee90dd07b94f4bbf9f71a59ef))
* **chat:** implement chat functionality with optimized API responses ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))
* **ci:** add automated release workflows ([3672529](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/367252912e948121d2eb6b3072be71769d51b2a1))
* complete Sprint 5 observability ([87ce973](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/87ce9735ad3c4b1f951fa52f7742b88858535db5))
* **dashboard:** add professor dashboard with subject management ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **dashboard:** add student progress view for professors (HU [#16](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/16)) ([5eb15c3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5eb15c34751a78d9d9891cffc4126fc8f2167292))
* **dataset:** implement synthetic dataset generation for Sprint 6 ([61773d4](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/61773d41fdaedb667ac34ae09a40089fe9c700f3))
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
* **grafana:** add provisioning configuration ([a95f523](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a95f523f000543fc9c5b7829ed84fbea5710228f))
* **hooks:** add dashboard data fetching hooks ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* implement adaptive reasoning, fix test session errors and improve subject management ([c08bad0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c08bad0190cc52d5c1da1c40103f1cb522b1880e))
* implement comprehensive CI/CD pipeline ([a8319e0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a8319e03fd7f382cd0de5a4fed14b4fbbbea733a))
* implement comprehensive CI/CD pipeline ([e9916d6](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e9916d6d8ca36f5b503ec1deeecf6730090170bb))
* implement comprehensive CI/CD pipeline ([ab8a65a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ab8a65a343fbba7751998286a6e0ef5c31170968))
* implement proactive RAG retrieval in test sessions and fix integration regressions ([8a658c9](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8a658c9b4659957f72585ec39f26a6bc87cde953))
* implement session management and integration with chat ([c9940a0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c9940a0c9e8a896188e1ce52555379efe8673f16))
* Implementación de memoria a corto plazo con sqlite ([f2a72aa](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/f2a72aa04b235146983f90c47ae39193b8bca36f))
* **infra:** add Loki and Promtail for log aggregation [#107](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/107) ([370aa44](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/370aa442b2d301afcff67cabb445118fa0a791e5))
* **infra:** add prometheus service and configuration [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([55780db](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/55780db83c1a00f1e2efabc13ce9d28a363792b6))
* integrate Ollama embeddings (nomic-embed-text) in clustering and topic modeling ([5045cb8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5045cb868e367ea250b318c2d3e022e30d21770d))
* **math:** add t-SNE/UMAP visualization functions ([12b2a09](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/12b2a098109fa54f586fd7d61743aeb2aa9de256))
* **math:** add TF-IDF and NMF topic modeling from scratch ([7a22ed7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/7a22ed77d9bd2a2e2a3e47ce808f684d4266a390))
* **math:** add topic modeling visualizations ([515839f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/515839f895deb7cd8df34cf79457120e72b2cc25))
* New ChatRequest model ([7083303](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/708330359410c1bb83d6a4867a393791d4a13f83))
* New jekyll theme ([ffdd731](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ffdd731cf4f9b161f0c08c5ef1a7d3ad0ace1ffb))
* New tool, Generate adaptive test, implemented closes [#33](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/33) closes [#34](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/34) ([b2be0ab](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b2be0ab2fb1055422ef20ed08806bca1e699d0cc))
* **observability:** add AlertManager for alerting ([#104](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/104), [#105](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/105)) ([6930489](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/6930489c98f9ab1a415278d3c1460366a3a867c7))
* **observability:** configure Grafana and enhance Promtail ([e78f746](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e78f746f630183fbb087ad6a681af5f57cd5ea66))
* **observability:** implement JSON structured logging and correlation ID across services [#102](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/102) ([51a7c3e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/51a7c3e3a493faed7ec027f8409997cd08dce168))
* **rag:** add file deletion endpoint ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **rag:** add prometheus instrumentation [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([9641406](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9641406b0bad978399c008c0279b0aa460d8e2b8))
* Remodelación de graph.py para encapsularlo en una clase ([9dfc5b2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9dfc5b27b4c819f402167f547ca5c060835a2b58))
* **scripts:** add difficulty classifier training tools ([d01aac1](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/d01aac11509d7303ea1622f361be4cc89ac42841))
* **scripts:** add query_student_history.py for session-based history ([73aad15](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/73aad15d2235aeef8e189bb3ff786500bc44198e))
* **scripts:** add run_tests.sh for Docker test execution ([e004791](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e004791ce4782949bf850e9d6bcb9772b48a999d))
* **settings:** create unified settings page for all roles ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* **test:** use RAG context as complementary info in evaluation ([059db74](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/059db74932b832008d77a4c59357549e4b075615))


### Bug Fixes

* [#27](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/27) Actualización del modelo llm para soportar tool-calling ([4a44635](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4a44635757e2e893188241e1eb4a752174ca574a))
* add __main__.py entry points for local development ([3d43fb7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3d43fb707f82737f59e075d505b3155c18a573c0))
* add load: true to docker build-push-action ([8ba3b36](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8ba3b361bda05e091a1d012c7f2daaf65a8eef0b))
* add pytest-cov to backend dev dependencies ([b118862](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b11886277fe4cd8a9845b88cebaf66dfe86e2a7d))
* add pytest-cov to dev dependencies ([aea25d3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/aea25d3da53af17908bcfd48b2392b946a484ced))
* Arreglado link de repositorio en el badge ([753a78a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/753a78a31201b04a76b0615162e4a4ef7997a86e))
* **chatbot:** downgrade Python to 3.12 for compatibility ([a019734](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a019734de9cf4011d325a37cac39ac95dba8f893))
* **chatbot:** include subject context in system prompt ([3ac38da](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3ac38da68078602ad511f0fe6426f9e19ff538b7))
* **ci:** configure Release Please permissions and add setup guide ([bf8870f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bf8870fc453a970cab89c661220e64036ecfca84))
* **ci:** configure Release Please permissions and add setup guide ([bf49012](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bf490122f84340cf5e28102a957f153a687a0283))
* **ci:** correct Docker build context for release workflows ([4dac49d](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4dac49db4725330c3aa7099ab96726db28c713d6))
* **ci:** downgrade Python 3.14 to 3.13 in workflows ([ca9c866](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ca9c866cf24d5427087976a5f303fcbe16182071))
* **ci:** Fix release-please docker images generation permissions ([38925eb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/38925eb9bd6e29203965a14ad30eaf28ce5f18d5))
* **ci:** Fixed Ollama wrong port and hosts for services. ([930cf3c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/930cf3cccc28f70b0773bd43173e2fa71e77c5bc))
* **ci:** install root project dependencies for integration tests ([af26173](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/af2617369450ccbe24aa046124901d156bf634a6))
* **ci:** optimize unit tests to run only on relevant file changes ([e0123d9](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e0123d9be78f9b5327f88224634de6a612e1f1ce))
* **ci:** optimize unit tests to run only on relevant file changes ([55bcbc1](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/55bcbc1ba3b090426de7a001138ab6aeef7332ef))
* **ci:** pin Black version to &lt;26 to avoid bug in 26.1.0 ([01519f3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/01519f30b2483fcae1c73ecb2d61ee673b37deeb))
* corrected parent name of ADRs ([6ca189b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/6ca189b1ddf019f1b0d36c44866429ede891e35f))
* **dependencies:** update passlib and bcrypt version constraints ([2f4e492](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2f4e4923cf2dee8aee3775b7179c770ee2e3f474))
* **docs:** removed unnecesary documentation about please release ([67f0023](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/67f00236a4cb2b31d32cb1e9aedff417d07ee62c))
* **docs:** Sprint retrospective not showing ([b8341cd](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8341cda6bd9f657ee51a6862f97f7526211ee53))
* Duplication of title in pages ([1c0e4c3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1c0e4c3cd29757aaef3307e688a094e969c05ec8))
* ensure environment configuration consistency ([868daad](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/868daad2f2de2e023ae329711f4d6b3061624c15))
* ficed unit tests for backend ([80196ea](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/80196eaa8b900b3aa1e06089d2f2445c5ce54e66))
* Fix title in pages ([11fc09b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/11fc09ba52b22daafaa1977fcb39585dd67fa49e))
* Fixed buged daily scrum and notes showing ([2558ce3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2558ce301ebe9be9f39cf00a0f72cc9dac61d8d5))
* **frontend:** fix Biome linting and TypeScript config for tests ([00706c2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/00706c2086d0cf6266711cbf994ddab9e9f73eb6))
* **frontend:** normalize subject case for session creation ([bf1ac14](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bf1ac147c6404f5bf0147e3020f90f23235f6330))
* **frontend:** update Biome linting and formatting checks in CI and pre-commit hooks ([2ff508f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2ff508fd8bcebc27a97defcb511f9d50d1c7e3f7))
* **math:** correct theme extraction in dataset loader and update clustering results ([e1550aa](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e1550aa3d162426acc1feafe5df0cc1ab74edbd0))
* nav order in ADR page ([db564e2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/db564e25e29e42c9bd95fe2016f7670cfb362d77))
* optimize Dockerfiles with multi-stage builds ([ef591a7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ef591a7790fa3eac9cb12ccf3054b0bee2fad1d6))
* quick fix for ADR jekylls ([88e0afb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/88e0afb90b7da9e2a34604270381c6dad1d7c4c4))
* quickfix for ADR in jekyll ([7a9815b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/7a9815b52510cbab625570588ba731246ef0ae07))
* **rag_service:** create documents directory with correct permissions ([00caed4](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/00caed49f84344e952f2178e6f2a36bdd5318ff7))
* **RAG:** fixed langchain text splitters module ([cfbbced](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cfbbcedd05143cbe1cabbd36404a2d21e070cb26))
* release workflow ([3146426](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/31464264047fb608b34f0c3fc004332b9432d4cb))
* remmoved comment ([e0d23d2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e0d23d2fb3feb30d3e72a0208a09a92072223c4e))
* replace docker-compose with docker compose ([b46afea](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b46afeadb0c4244c90e198fc5331b98e046f0e39))
* resolve rag_service test failures by mocking external services and fixing patches ([2353e36](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2353e36d0b534bcd306fe2760cb5a705b1c4a82d))
* resolve ruff linting errors in compare.py and notebook ([cb8ed00](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cb8ed00344af33f2fde8a624055db37553adb872))
* run rag_service tests excluding integration marker ([d829dc8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/d829dc802230a8197d911871d8652e49ea054b01))
* **tests:** fix failing test_testGraph tests ([1e3e479](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1e3e4792c801a81859dcd3c2fa42182f51eff517))
* **tests:** resolve pytest failures in embedding and RAG tests ([9685923](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9685923fa6629a4bd943193781c226e6faecd4cf))
* try to solve ADRs not showing ([92ff1cb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/92ff1cb55e8638340dbf311a423ef8fd8eb1b04d))
* **ui:** resolve navigation and responsiveness issues ([e7ae665](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e7ae66505e5c2e5cfabe3116f468affef3c0bab8))
* Update Jekyll workflow for GitHub Pages deployment ([d368d02](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/d368d02e54ffb912d46d8532ecdb5e7a5e5d19dd))
* update Python requirement from &gt;=3.14 to &gt;=3.13 ([05cbede](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/05cbede6c99d0862fd25f3469e2c6571b98af2a7))
* update vector store test to mock query_points instead of search ([2ae0e27](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2ae0e275677beab76f7f739303c37cb8fe3cd09f))
* use only Python 3.12 in workflows ([9b74c17](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9b74c17e4547841206bae1c405fba536a20bca16))


### Performance Improvements

* reduce payload size by returning only new message per request ([b8a54f2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b8a54f2b76444f4d976dea164105864f66c3b08d))


### Documentation

* actualización daily scrum ([e936710](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e9367105711a65e088dc4d3a9d92d642b90c7994))
* add ADRs for clustering algorithms and knowledge profiles ([3affc34](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3affc342d406f6dfe464edeb077cbb789ca81bbd))
* add ADRs for observability architecture ([5faea0e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5faea0ef55131c4ec0e91419e88661afaa07fbc9))
* add clustering study plan for future research ([8f18f70](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8f18f7096b341866488ab4a0e6e403c3a628523a))
* Add daily scrum documentation for November 2025 ([96ffb37](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/96ffb37e0d11c560b0930ad767038b261c30192d))
* add daily scrums for December 2025 (09-25) ([5f308fc](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5f308fc67080e681cc569fcaa7ec7eac242e4b83))
* add difficulty classifier documentation ([15aa673](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/15aa673c018a390f94a3ed430c87906e41127a78))
* add frontmatter to ADR documents for consistent formatting ([58150a3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/58150a39bf43c6a4a2991ea925507e63e99d9441))
* add math investigation patterns to copilot instructions ([fbe72e1](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/fbe72e1cdbe038f5837d22a29029dce924587839))
* add mathematical integration proposal for document clustering ([4cf023e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4cf023ecbc316b838af6147f7d785873817cb03c))
* add microservices architecture documentation and OpenAPI export ([b5230a8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b5230a8995a070485908cd5d880c1ef02c43996c))
* add sprint 5 planning and sprint 4 retrospective ([5a72a1d](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5a72a1d72c81f89e9de648eabf7b71458811d3fd))
* add Sprint 5 retrospective ([9b03b88](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9b03b8887590ecf4e8a976ebf21ec16615711a26))
* add Sprint 6 planning document ([fd01583](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/fd015835a22970fd1344ce675336c9baa5d7846c))
* add sprint retrospective 3 ([7c179c8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/7c179c88ba234efd8ba715881fa9dc756679538f))
* added ADR for linters and formaters ([53f90c8](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/53f90c877fe029b997ffeb9fb6f77a864f625f1e))
* ADR for mongoDB to store guia docente JSONs ([bfea364](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bfea3648ead0f6a4af91e2a6c9a96da155dc9865))
* **adr:** add ADR-0033 for Grafana visualization ([bce995a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bce995acdc91400a86cbfa53f4280e06946b1ee6))
* **adr:** add architectural decisions for auth and gateway ([c0ad1ab](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c0ad1ab3fc13ffc44c498cc3ea48f70fef97424b))
* **ADR:** add architecture decision records for frontend technologies (React, Vite, Tailwind CSS, Shadcn/ui, TanStack Query, React Router, Zod, React Hook Form) ([757ea81](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/757ea81d5297528793acff2945c7a0c7c344651f))
* **changelog:** expand 0.1.0 notes (FastAPI, GraphAgent, tests) ([c95cfff](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/c95cfffdd658aabd1a7e1ba7c9865f1f27203add))
* Creación de daily scrum ([1326b0f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1326b0f3d6273906b0f442c622b173f687b404f0))
* Creación de README ([93e712c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/93e712cdfc9dd2563415d900503e1a0d5cf4f17a))
* daily ([9f30670](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9f3067007e22deed4bd8a90f6e6d47b2b476674a))
* Daily scrum upload ([2299bd0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/2299bd0b9f8a99666140e5fe3844f9aceaed73e1))
* Daily scrum upload ([8b51185](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8b511851d3a8523f12ffa0667d67f1348582b0c7))
* **daily-scrum:** add december daily scrums and sprint planning ([8c9daa2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8c9daa28d823e535236b1478a55237fcf10d1cdf))
* **daily:** update progress for 02-02-26 ([448aa74](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/448aa7412ae8d072fd884c742b5fdca060e16d39))
* fix of sprint retrospective 1 not showing ([7a44796](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/7a447969d5eb73b0366a04364318a9e7588cf5dd))
* Incorporación de devLog y notas ([d950a53](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/d950a53ae1216dc3076988ed26f43822c1ec9797))
* ordered scrum dailys ([31e20b2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/31e20b21f76c71e8db40793f9c15849d2ed37a4d))
* **plan:** Created sprint plannification for sprint 3 ([a9643fb](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a9643fb8cd9a8c73cbf31922d720ebd9ea12980e))
* **readme:** add release badge showing latest tag ([82c2aa9](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/82c2aa92f522ac294dccdc21326736779002ea54))
* **Readme:** README actualizado ([6690304](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/6690304567c1e1b05a53c11090f47c580ce51d4b))
* redacción del sprint planning del sprint 1 ([f5694e6](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/f5694e656b355e21435cd4ec12e7b01b6e7f50d6))
* **SCRUM:** add daily scrum entries for November 25-27, 2025 and update Sprint Planning 4 dates ([478a391](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/478a3914dbee22f5583a20ce9d73c8777a119108))
* **scrum:** add daily scrum notes for Dec 28-29 ([472c976](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/472c97671981d6adb4cafa2e4285fc6c618f0c13))
* **SCRUM:** add Sprint Planning 4 documentation for UI Frontend development ([27e2e64](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/27e2e6498eef1141c481cc307930a59e6c6aa6eb))
* **scrum:** update daily scrum 27-12-25 - Prometheus completed [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([259bbd0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/259bbd095d88828abaf70b2f8a16758e540539db))
* Seted up ADR to easily add records in a preconfigured format solves [#38](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/38) ([052b425](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/052b42553117ad14ecd23960b61be1d1d5ec2f13))
* sprint planing ([5c4eb85](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5c4eb8535aa31a836af22a87c2520943bfdc73f5))
* Srum retrospective ([649f52a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/649f52a870525122fdcc7e2a3f25d929bdf4413e))
* update daily scrum entries for Feb 13 and 16 ([8343f9b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8343f9bad4fbc31c942d1be7e28c986bbd01fbb9))
* update daily scrum for Jan 29 with completed tasks and correct themes ([76d0538](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/76d0538ef57f4dc71fed32367ebb219d0de1e1eb))
* update daily scrum with Sprint 4 frontend progress ([4c1e9e0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/4c1e9e0b377fe3e17e17c88738f41d961df91cd4))
* update daily scrums for topic modeling progress ([cf9ebaa](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cf9ebaa8026aa86f3cd6c4acbccab234e4e4f6cc))
* update README for dual degree TFG (CS + Math) ([a1102ed](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a1102ed21eada636158cee70b3f5767ad340731c))
* updated ADR with uv ([32c5083](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/32c5083496bb55ff4093188776fc97a1d6457c40))
* updated daily ([b16db53](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/b16db53d315b0b54684ab6daaef1b1a257d755e7))
* updated docs for rag service ([f046772](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/f0467725c2d30f0891c94996984b2afad79be7e5))
* Updated docstring ([9ce2e07](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9ce2e07bef98c79145ca39cd00c4bc4917824332))
* Uploaded scrum review and updated pages ([be98a87](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/be98a87dc7e2cb8ded5df3c6c4b7c0be0f184ffe))


### Miscellaneous Chores

* force release 0.6.0 ([5981a69](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5981a6998ffef1b5dd3d7ab3309167a9db0560ef))
* release 0.4.1 ([866f71c](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/866f71c6f2da654f23437e251be1af9f93e31acc))
* release 0.4.2 ([47c3a0b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/47c3a0b05dbf22efab47177abf3f216de8e8fb48))


### Code Refactoring

* **chatbot:** remove unused web_search tool ([04cbe09](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/04cbe0932fea620ae7a6743a20b29fdaa4cdc4d5))
* **config:** migrate to pydantic-settings for type-safe configuration ([cf0adfe](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/cf0adfe619a453de028e90aeb4dad2cdcf7542a2))

## [0.4.2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.4.2...v0.4.2) (2026-01-28)


### ⚠ BREAKING CHANGES

* **chatbot:** The web_search tool and DuckDuckGo integration have been removed. The tool was not being used correctly and added unnecessary complexity.

### Features

* **backend:** add prometheus instrumentation [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([8408c13](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/8408c13cd7eb8070db0eb22dcccbc7284e379bd9))
* **chatbot:** add Mistral AI as LLM provider option ([3ea5462](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3ea5462fe5b03b69ebc67b198d034731721289bc))
* **chatbot:** add observability dependencies ([38ba70f](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/38ba70f475cfd874fe5dabfa867c459f16e50aee))
* **chatbot:** add Phoenix LLM tracing instrumentation ([1b60a41](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/1b60a41566be379aec13848b5b18342d62dd70fb))
* complete Sprint 5 observability ([87ce973](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/87ce9735ad3c4b1f951fa52f7742b88858535db5))
* **grafana:** add provisioning configuration ([a95f523](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a95f523f000543fc9c5b7829ed84fbea5710228f))
* **infra:** add Loki and Promtail for log aggregation [#107](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/107) ([370aa44](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/370aa442b2d301afcff67cabb445118fa0a791e5))
* **infra:** add prometheus service and configuration [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([55780db](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/55780db83c1a00f1e2efabc13ce9d28a363792b6))
* **observability:** add AlertManager for alerting ([#104](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/104), [#105](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/105)) ([6930489](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/6930489c98f9ab1a415278d3c1460366a3a867c7))
* **observability:** configure Grafana and enhance Promtail ([e78f746](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/e78f746f630183fbb087ad6a681af5f57cd5ea66))
* **observability:** implement JSON structured logging and correlation ID across services [#102](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/102) ([51a7c3e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/51a7c3e3a493faed7ec027f8409997cd08dce168))
* **rag:** add prometheus instrumentation [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([9641406](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9641406b0bad978399c008c0279b0aa460d8e2b8))


### Bug Fixes

* add __main__.py entry points for local development ([3d43fb7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3d43fb707f82737f59e075d505b3155c18a573c0))
* **chatbot:** downgrade Python to 3.12 for compatibility ([a019734](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a019734de9cf4011d325a37cac39ac95dba8f893))
* **ci:** downgrade Python 3.14 to 3.13 in workflows ([ca9c866](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ca9c866cf24d5427087976a5f303fcbe16182071))
* **ci:** pin Black version to &lt;26 to avoid bug in 26.1.0 ([01519f3](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/01519f30b2483fcae1c73ecb2d61ee673b37deeb))
* ensure environment configuration consistency ([868daad](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/868daad2f2de2e023ae329711f4d6b3061624c15))
* optimize Dockerfiles with multi-stage builds ([ef591a7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ef591a7790fa3eac9cb12ccf3054b0bee2fad1d6))
* **rag_service:** create documents directory with correct permissions ([00caed4](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/00caed49f84344e952f2178e6f2a36bdd5318ff7))
* update Python requirement from &gt;=3.14 to &gt;=3.13 ([05cbede](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/05cbede6c99d0862fd25f3469e2c6571b98af2a7))


### Documentation

* add ADRs for observability architecture ([5faea0e](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5faea0ef55131c4ec0e91419e88661afaa07fbc9))
* add daily scrums for December 2025 (09-25) ([5f308fc](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5f308fc67080e681cc569fcaa7ec7eac242e4b83))
* add sprint 5 planning and sprint 4 retrospective ([5a72a1d](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/5a72a1d72c81f89e9de648eabf7b71458811d3fd))
* add Sprint 5 retrospective ([9b03b88](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/9b03b8887590ecf4e8a976ebf21ec16615711a26))
* **adr:** add ADR-0033 for Grafana visualization ([bce995a](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/bce995acdc91400a86cbfa53f4280e06946b1ee6))
* **scrum:** add daily scrum notes for Dec 28-29 ([472c976](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/472c97671981d6adb4cafa2e4285fc6c618f0c13))
* **scrum:** update daily scrum 27-12-25 - Prometheus completed [#106](https://github.com/GabrielFranciscoSM/TFG-Chatbot/issues/106) ([259bbd0](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/259bbd095d88828abaf70b2f8a16758e540539db))


### Miscellaneous Chores

* release 0.4.2 ([47c3a0b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/47c3a0b05dbf22efab47177abf3f216de8e8fb48))


### Code Refactoring

* **chatbot:** remove unused web_search tool ([04cbe09](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/04cbe0932fea620ae7a6743a20b29fdaa4cdc4d5))

## [0.4.2](https://github.com/GabrielFranciscoSM/TFG-Chatbot/compare/v0.4.1...v0.4.2) (2025-12-22)


### ⚠ BREAKING CHANGES

* **chatbot:** The web_search tool and DuckDuckGo integration have been removed. The tool was not being used correctly and added unnecessary complexity.

### Bug Fixes

* add __main__.py entry points for local development ([3d43fb7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/3d43fb707f82737f59e075d505b3155c18a573c0))
* **chatbot:** downgrade Python to 3.12 for compatibility ([a019734](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/a019734de9cf4011d325a37cac39ac95dba8f893))
* ensure environment configuration consistency ([868daad](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/868daad2f2de2e023ae329711f4d6b3061624c15))
* optimize Dockerfiles with multi-stage builds ([ef591a7](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/ef591a7790fa3eac9cb12ccf3054b0bee2fad1d6))
* **rag_service:** create documents directory with correct permissions ([00caed4](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/00caed49f84344e952f2178e6f2a36bdd5318ff7))


### Miscellaneous Chores

* release 0.4.2 ([47c3a0b](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/47c3a0b05dbf22efab47177abf3f216de8e8fb48))


### Code Refactoring

* **chatbot:** remove unused web_search tool ([04cbe09](https://github.com/GabrielFranciscoSM/TFG-Chatbot/commit/04cbe0932fea620ae7a6743a20b29fdaa4cdc4d5))

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
