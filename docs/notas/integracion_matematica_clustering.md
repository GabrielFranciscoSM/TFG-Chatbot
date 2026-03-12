# Propuesta de Integración Matemática: Document Clustering en Chatbot Educativo

**Fecha:** 20 de Enero de 2026
**Contexto:** TFG Conjunto (Informática + Matemáticas)
**Objetivo:** Integrar y validar técnicas de clustering (k-means, FCM, NMF) en el proyecto TFG-Chatbot sin disponer de datos reales de usuarios.

---

## 1. El Reto: Validación sin Datos Reales
La principal barrera para la parte matemática del TFG es la ausencia de logs de chat reales o documentos de usuarios.
**Solución Estratégica:** Generación de Datos Sintéticos ("Synthetic Ground Truth").
Utilizaremos el LLM (Gemini/Ollama) no solo como parte del chatbot, sino como un **generador de datos estocásticos** que simule el comportamiento de estudiantes y la estructura de documentos. Esto nos permite crear un "escenario controlado" donde conocemos la respuesta correcta (las etiquetas reales), permitiendo una validación matemática rigurosa.

---

## 2. Propuestas de Integración y Algoritmos

### A. Descubrimiento de Tópicos Latentes (Topic Modeling)
**Concepto:** Analizar los documentos de la base de conocimiento (RAG) para descubrir automáticamente la estructura temática de la asignatura sin supervisión humana.

*   **Datos de Entrada:** Matriz Documento-Término (TF-IDF) construida a partir de los "chunks" de texto en Qdrant.
*   **Algoritmo Principal:** **NMF (Non-negative Matrix Factorization)**.
    *   *Justificación Matemática:* A diferencia de PCA, NMF garantiza componentes no negativos, lo que hace que los "tópicos" sean interpretables como sumas aditivas de palabras (no hay "palabras negativas").
    *   *Variante:* Probar con diferentes funciones de coste (Norma Frobenius vs Divergencia Kullback-Leibler).
*   **Aplicación Práctica:**
    *   Generar un "Mapa de Conceptos" automático para el profesor.
    *   Etiquetado automático de nuevos documentos subidos.
*   **Validación:**
    *   **Coherencia Semántica (UCI/UMass):** Medir si las palabras top de cada tópico suelen aparecer juntas en el corpus.
    *   **Comparación con Guía Docente:** Calcular la similitud de coseno entre los vectores de los tópicos generados y los vectores de los temas oficiales de la asignatura.

### B. Clustering de Preguntas Frecuentes (FAQ Generation)
**Concepto:** Anticiparse a las dudas de los alumnos agrupando preguntas sintéticas.

*   **Pipeline de Datos Sintéticos:**
    1.  Muestreo estratificado de chunks de la base de datos.
    2.  Prompt al LLM: *"Actúa como un estudiante confuso y genera 5 preguntas sobre este concepto: {texto_chunk}"*.
    3.  Embedding de las preguntas usando el modelo del RAG (ej: `text-embedding-3-small` o local).
*   **Algoritmos:**
    *   **K-Means:** Como baseline robusto. Usar inicialización **K-Means++** para mejorar la convergencia.
    *   **Fuzzy C-Means (FCM):**
        *   *Justificación:* Muchas preguntas son ambiguas y pueden pertenecer a varios temas (ej: una duda sobre "implementación de redes neuronales" toca tanto "teoría" como "práctica"). FCM asigna grados de pertenencia ($u_{ij} \in [0,1]$).
*   **Aplicación Práctica:**
    *   Los centroides de los clústeres se convierten en las "Preguntas Sugeridas" en la interfaz del chat.
*   **Validación:**
    *   **Silhouette Score:** Para evaluar la compacidad y separación de los clústeres.
    *   **Elbow Method:** Para justificar matemáticamente la elección del número óptimo de preguntas ($k$).

### C. Diversificación de Resultados en RAG (Maximal Marginal Relevance via Clustering)
**Concepto:** Mejorar la calidad de las respuestas del chatbot evitando que el contexto sea redundante.

*   **Problema:** Si recuperamos 5 chunks y los 5 dicen lo mismo, el LLM no tiene variedad de información.
*   **Algoritmo:** Clustering Jerárquico Aglomerativo.
    1.  Recuperar un exceso de candidatos (ej: $N=20$).
    2.  Agruparlos en $k=5$ clústeres basados en su similitud semántica.
    3.  Seleccionar el documento más representativo (centroide) de cada clúster.
*   **Beneficio:** Garantiza que el contexto pasado al LLM cubra diferentes aspectos de la query original.

---

## 3. Plan de Validación Matemática (El "Experimento")

Para el TFG de Matemáticas, es crucial tener una sección de "Resultados Numéricos". Diseñaremos el siguiente experimento:

### Fase 1: Generación del Dataset de Control
Seleccionaremos 3 temas disjuntos de la asignatura (ej: "Tema A", "Tema B", "Tema C").
Usaremos el LLM para generar 100 documentos sintéticos para cada tema.
*   **Etiqueta Real:** Sabemos a qué tema pertenece cada documento.
*   **Ruido Controlado:** Introduciremos documentos "trampa" que mezclen vocabulario de dos temas para probar la robustez de FCM.

### Fase 2: Ejecución Ciega
Ejecutaremos los algoritmos (K-Means, FCM, NMF) sobre el dataset sin proporcionar las etiquetas.

### Fase 3: Métricas de Evaluación
Compararemos el resultado del clustering con las etiquetas reales usando:
1.  **ARI (Adjusted Rand Index):** Mide la similitud entre dos particiones de datos, ajustado por azar. Es la métrica estándar de oro para validación externa.
    $$ARI = \frac{\sum_{ij} \binom{n_{ij}}{2} - [\sum_i \binom{a_i}{2} \sum_j \binom{b_j}{2}] / \binom{n}{2}}{ \frac{1}{2} [\sum_i \binom{a_i}{2} + \sum_j \binom{b_j}{2}] - [\sum_i \binom{a_i}{2} \sum_j \binom{b_j}{2}] / \binom{n}{2} }$$
2.  **NMI (Normalized Mutual Information):** Mide la información compartida entre las etiquetas reales y los clústeres.
3.  **Coeficiente de Partición (FCM):** Para medir cuánta "borrosidad" (fuzziness) hay en la partición.

---

## 4. Roadmap de Implementación

1.  **Script de Generación (`scripts/math/generate_dataset.py`):**
    *   Usa `chatbot.logic` para invocar al LLM.
    *   Guarda los datos en `data/synthetic_dataset.json`.
2.  **Notebook de Análisis (`notebooks/math_clustering.ipynb`):**
    *   Carga el JSON.
    *   Implementa pipelines con `scikit-learn` (KMeans, NMF) y `scikit-fuzzy` (FCM).
    *   Genera visualizaciones 2D con **t-SNE** o **UMAP** para mostrar la separación de los clústeres en la memoria.
