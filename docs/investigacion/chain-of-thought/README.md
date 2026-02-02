---
layout: default
title: "Chain-of-Thought Prompting"
parent: Investigación
---

# Chain-of-Thought (CoT) Prompting

## Introducción

Chain-of-Thought (CoT) prompting es una técnica de ingeniería de prompts que mejora las capacidades de razonamiento de los LLMs al instruirlos para que "piensen paso a paso" antes de proporcionar una respuesta final.

Esta investigación se realiza en el contexto del **Sprint 6** para implementar la **HU #15: Prompts de Razonamiento**.

---

## Mejores Prácticas

### 1. Separación de Razonamiento y Respuesta

El principio fundamental es **separar el proceso de pensamiento de la respuesta final**:

- El modelo documenta su razonamiento de forma explícita
- Solo después proporciona la respuesta final
- Esto permite transparencia y debugging

### 2. Formato JSON Estructurado

Para aplicaciones en producción, se recomienda usar un esquema JSON con campos separados:

```json
{
  "thinking": "Pasos del razonamiento interno...",
  "answer": "Respuesta final para el usuario"
}
```

**Beneficios:**
- ✅ Permite parsing automático en pipelines
- ✅ Facilita debugging y monitoreo del modelo
- ✅ Previene alucinaciones al hacer el razonamiento explícito
- ✅ Permite mostrar/ocultar el razonamiento según contexto

---

## Técnicas de CoT

| Técnica | Descripción | Caso de Uso |
|---------|-------------|-------------|
| **Explicit CoT** | El razonamiento se muestra al usuario | Educación, transparencia |
| **Hidden CoT** | Razonamiento interno, solo muestra respuesta | Producción, UX limpia |
| **Structured CoT** | JSON schema forzado | APIs, pipelines automatizados |
| **Zero-shot CoT** | Añadir "Let's think step by step" | Prototipado rápido |
| **Few-shot CoT** | Ejemplos de razonamiento | Tareas específicas |

---

## Aplicación en Chatbot Pedagógico

Para un agente educativo, el **CoT explícito** es especialmente valioso:

1. **Modelado de pensamiento**: Muestra al estudiante cómo razonar sobre un problema
2. **Transparencia**: Permite validar el proceso de razonamiento
3. **Valor pedagógico**: El "cómo" es tan importante como el "qué"
4. **Debugging docente**: Los profesores pueden revisar la lógica del agente

### Estructura Propuesta para el Chatbot

```json
{
  "thinking": {
    "steps": [
      "1. Analizo la pregunta del estudiante...",
      "2. Identifico conceptos relevantes...",
      "3. Busco información en la base de conocimiento...",
      "4. Formulo una respuesta adaptada al nivel..."
    ],
    "confidence": 0.85,
    "sources_used": ["documento1.pdf", "documento2.pdf"]
  },
  "answer": {
    "content": "Respuesta formateada para el estudiante",
    "difficulty_level": "intermediate",
    "follow_up_suggestions": ["¿Quieres que profundicemos en...?"]
  }
}
```

---

## Trade-offs a Considerar

### Latencia vs Detalle
- Más razonamiento = respuestas más precisas pero más lentas
- Considerar modo "fast" vs "detailed" según contexto

### Visibilidad del Razonamiento
- **Mostrar siempre**: Máxima transparencia, puede ser verbose
- **Mostrar bajo demanda**: UX más limpia, opción "ver razonamiento"
- **Ocultar**: Solo para logs/debugging

---

## Referencias

- OpenAI Developer Forum: Chain-of-Thought Prompting with JSON Output
- Prompt Engineering Guide: Structured CoT Techniques
- LangChain Documentation: Reasoning with Structured Outputs

---

## Próximos Pasos

1. [ ] Diseñar prompt específico para el chatbot
2. [ ] Definir JSON schema final
3. [ ] Integrar en grafo LangGraph
4. [ ] Crear ADR documentando la decisión

---

*Última actualización: 30 de enero de 2026*
