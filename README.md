# TFG-Chatbot

[![state: empty](https://img.shields.io/badge/state-empty-lightgrey)](README.md) [![license](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![GitHub](https://img.shields.io/badge/GitHub-Repo-black?logo=github&logoColor=white)](https://github.com/usuario/TFG-Chatbot)

## Resumen

Proyecto para el Trabajo de Fin de Grado (TFG) que investiga y desarrolla un agente de IA tipo chatbot orientado a entornos educativos. El objetivo es combinar los beneficios de los LLM con directrices pedagógicas que reduzcan alucinaciones y favorezcan el aprendizaje del estudiante. El repositorio está en una fase inicial (prácticamente vacío) y actúa como contenedor del TFG: documentación, experimentos y código.

## Table of Contents

- [TFG-Chatbot](#tfg-chatbot)
  - [Resumen](#resumen)
  - [Table of Contents](#table-of-contents)
  - [Motivación](#motivación)
  - [Desarrollo agil](#desarrollo-agil)
  - [Estado del proyecto](#estado-del-proyecto)
  - [Tecnologías (planificadas)](#tecnologías-planificadas)
  - [Instalación mínima (proyecto vacío)](#instalación-mínima-proyecto-vacío)
  - [Quick start (demo/ejecución)](#quick-start-demoejecución)
  - [Arquitectura (plan)](#arquitectura-plan)
  - [Evaluación y consideraciones éticas](#evaluación-y-consideraciones-éticas)
  - [Roadmap / Milestones](#roadmap--milestones)
  - [Cómo contribuir](#cómo-contribuir)
  - [Licencia](#licencia)
  - [Contacto](#contacto)
  - [Agradecimientos](#agradecimientos)

## Motivación

Hoy en día los LLM, y más específicamente los chatbots, han revolucionado la sociedad. Como evidencia de esto, chatbots como chatGPT alcanzó los 100 millones de usuarios a solo 60 días de su lanzamiento, y este número no para de crecer, junto con el de sus competidores.

Estas nuevas herramientas pueden aportar a la docencia, sobretodo como apoyo a profesores y métodos más clásicos. Es más, han existido durante decadas Intelligent Tutoring Systems, que han usado técnicas de machine learning y NLP para poder simular chatbots educacionales, con el objetivo de alcanzar el ratio de profesores-alumnos 1:1. Los LLM son un cambio de paradigma en este campo.

Sin embargo, estudios demuestran que el uso no adecuado de estos LLM puede llevar a los estudiantes a empeorar su aprendizaje. Por ejemplo, si el agente alucina una respuesta falsea, o da un respuesta directa en vez de razonarla junto con el estudiante.

De estos y otros problemas surge la necesidad de desarrollar un agente chatbot que aporte los beneficios de los LLM, pero adaptando su uso al entorno educativo, dandole directrizes pedagógicas y especializandolos.

## Desarrollo agil

Como metodología para desarrollar este proyecto he elegido SCRUM.

Para ello he creado un Product Backlog compuesto de historias de usuario en los Issues de este repositorio, así como diferentes Mileston que los agrupa y definen Prodúctos Mínimamente Viables que entregar después de cada sprint.

## Estado del proyecto

Actualmente este repositorio está en una fase inicial: no hay código ni modelos entrenados incluidos. Se usan las Issues y Milestones del repositorio para planificar el Product Backlog y los sprints del TFG.

## Tecnologías (planificadas)

- Lenguaje: Python (versión mínima recomendada: 3.10)
- Modelos/Frameworks: Transformers (Hugging Face), LangChain o similar (según necesidades), herramientas de evaluación (nltk, sacrebleu) y librerías para despliegue (FastAPI, Streamlit o similar)
- Experimentos y notebooks: Jupyter / Colab

## Instalación mínima (proyecto vacío)

1. Clonar el repositorio.
2. Crear un entorno virtual (venv/conda) y activar.
3. Añadir dependencias en `requirements.txt` en futuras fases.

Ejemplo (básico):

- Crear entorno (recomendado): `python -m venv .venv && source .venv/bin/activate`
- Instalar dependencias cuando estén definidas: `pip install -r requirements.txt`

## Quick start (demo/ejecución)

Este proyecto aún no contiene una demo ejecutable. En próximas versiones se añadirá una sección con ejemplos de uso, scripts para lanzar el servidor y capturas de conversaciones.

## Arquitectura (plan)

- interfaz (web / CLI) para interacción con el estudiante
- backend que gestiona la sesión y la memoria pedagógica
- capa de integración con LLMs y filtros de seguridad/validez
- módulo de políticas pedagógicas que guía las respuestas (scaffolding, hinting, preguntas socráticas)
- registro de logs y métricas para evaluación

## Evaluación y consideraciones éticas

- Se documentarán métricas de evaluación (evaluación humana, exactitud, medidas de coherencia y robustez frente a alucinaciones).
- Se incluirá un apartado de privacidad y uso de datos: origen de datos, licencias y medidas para preservar privacidad del alumnado.

## Roadmap / Milestones

- Milestone 1: API de un agente React básico para un chatbot
- Milestone 2: Agente con herramientas específicas
- Milestone 3: Autenticación de usuarios
- Milestone 4: Interfaz Educativa
- Milestone 5: Logs y Monitorización
- Milestone 6: Métricas y Dashboard
- Milestone 7: Chatbot con herramientas avanzadas
- Milestone 8: Evaluación y documentación

## Cómo contribuir

- Abrir Issues para bugs, ideas y tareas del TFG.
- Proponer Pull Requests con pequeñas unidades de trabajo.
- En próximas versiones se añadirá un `CONTRIBUTING.md` con normas de estilo, testing y workflow.

## Licencia

Este repositorio incluye un fichero `LICENSE`. Revisa ese fichero para conocer los términos exactos.

## Contacto

Autor: Gabriel Francisco Sánchez Muñoz
Tutor / Afiliación: (añadir nombre del tutor y la afiliación de la universidad)

## Agradecimientos

- Referencias y bibliografía relevantes se añadirán en la sección de Referencias.