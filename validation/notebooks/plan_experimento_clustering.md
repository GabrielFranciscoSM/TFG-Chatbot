# Plan detallado para crear el notebook de experimentación

## 1. Objetivo del notebook

Construir un notebook único y reproducible para comparar formalmente cuatro algoritmos de clustering implementados en `validation/clustering.py` sobre tres representaciones textuales (BoW, TF-IDF, Nomic embeddings), evaluándolos con las métricas de `validation/metrics/metrics.py` y apoyando el análisis con visualizaciones 2D (UMAP/t-SNE).

## 2. Alcance experimental

### 2.1 Algoritmos a comparar

1. `GenericKMeans(algorithm="kmeans", distance="euclidean")`
2. `GenericKMeans(algorithm="kmeans", distance="cosine")` (equivalente conceptual a spherical k-means)
3. `GenericKMeans(algorithm="fcm", distance="euclidean")`
4. `GenericKMeans(algorithm="fcm", distance="cosine")` (equivalente conceptual a spherical FCM)

### 2.2 Representaciones textuales

1. BoW (`CountVectorizer`)
2. TF-IDF (`TfidfVectorizer`)
3. Nomic embeddings (por API/local model según entorno disponible)

### 2.3 Datasets

Usar `DatasetLoader` de `validation/datasets.py`:

1. DialogSum (EN)
2. StackOverflow subset (EN)
3. ESQAD (ES)

## 3. Estructura del notebook (sección por sección)

## Sección A. Contexto y configuración

### Celda 1 (Markdown) - Título y resumen

Incluir:

1. Título formal del experimento.
2. Objetivo general.
3. Preguntas de investigación.
4. Hipótesis iniciales.

### Celda 2 (Markdown) - Diseño metodológico

Describir diseño factorial: 4 algoritmos x 3 representaciones x 3 datasets x N semillas.

### Celda 3 (Code) - Imports y configuración global

Incluir:

1. Imports de numpy, pandas, matplotlib, seaborn.
2. Imports de sklearn (vectorizadores, optional TruncatedSVD, métricas externas opcionales).
3. Imports de UMAP y t-SNE.
4. Imports locales: `validation/clustering.py`, `validation/metrics/metrics.py`, `validation/datasets.py`.
5. Semillas globales (`np.random.seed`) y constantes del experimento.

### Celda 4 (Code) - Configuración de logging y rutas de salida

Definir:

1. Carpeta de resultados: `validation/results/clustering_experiment/`.
2. Subcarpetas: `tables/`, `figures/`, `artifacts/`, `logs/`.
3. Función auxiliar para guardar tablas y gráficos.

## Sección B. Carga y validación de datos

### Celda 5 (Code) - Carga de datasets

1. Instanciar `DatasetLoader`.
2. Cargar los tres datasets.
3. Homogeneizar columnas (`text`, `label`).
4. Añadir columna `dataset`.

### Celda 6 (Code) - Limpieza y control de calidad

Aplicar:

1. Eliminación de nulos.
2. Eliminación de textos vacíos.
3. Eliminación de duplicados.
4. Filtrado opcional por longitud mínima.

### Celda 7 (Markdown + tabla mostrada) - Reporte de muestra

Mostrar por dataset:

1. Número de documentos.
2. Longitud media del texto.
3. Número de etiquetas reales (si aplica).

## Sección C. Construcción de representaciones

### Celda 8 (Code) - Funciones de representación

Definir funciones:

1. `build_bow(texts, params)`
2. `build_tfidf(texts, params)`
3. `build_nomic_embeddings(texts, batch_size, model_name)`

Notas:

1. Devolver siempre `np.ndarray` o matriz compatible.
2. Registrar dimensión final y tiempo de cómputo.

### Celda 9 (Code) - Configuración por representación

Definir un diccionario de configuración, por ejemplo:

1. BoW: `max_features`, `ngram_range`, `min_df`.
2. TF-IDF: mismo esquema para comparabilidad.
3. Nomic: modelo, endpoint, lote.

### Celda 10 (Code) - Construcción efectiva y cache

1. Generar representaciones por dataset.
2. Guardar artefactos en `artifacts/` para reuso.
3. Aplicar normalización L2 cuando corresponda (especialmente para distancia coseno).

## Sección D. Definición de protocolo de clustering

### Celda 11 (Markdown) - Política de hiperparámetros

Declarar formalmente:

1. Rango de `k` (por ejemplo 2..15, ajustado a tamaño).
2. Número de semillas (p.ej. 5 o 10).
3. `max_iter`, `tol`, y `m` para FCM.

### Celda 12 (Code) - Grid experimental

Construir tabla de combinaciones:

1. dataset
2. representación
3. algoritmo
4. distancia
5. `k`
6. semilla

## Sección E. Ejecución del experimento

### Celda 13 (Code) - Runner principal

Implementar función `run_single_experiment(...)` que:

1. Entrene el modelo (`GenericKMeans`).
2. Obtenga etiquetas y/o membresías.
3. Calcule métricas con `evaluate_hard_clustering` o `evaluate_fuzzy_clustering`.
4. Devuelva registro plano (dict) con resultados y metadatos.

### Celda 14 (Code) - Bucle completo

1. Iterar sobre todas las combinaciones.
2. Acumular resultados en `DataFrame`.
3. Guardar CSV maestro en `tables/raw_results.csv`.
4. Guardar logs de errores sin interrumpir el barrido completo.

## Sección F. Análisis estadístico y tablas académicas

### Celda 15 (Code) - Agregación por condición

Calcular por grupo:

1. Media
2. Desviación estándar
3. Intervalo de confianza (95%)

Para métricas: ASW, CH, PC, PE, XB, tiempo, iteraciones.

### Celda 16 (Code) - Ranking y selección

1. Ranking por dataset y representación.
2. Ranking global ponderado (explicar criterio).
3. Exportar tablas finales a `tables/summary_*.csv`.

### Celda 17 (Code) - Pruebas estadísticas

1. Comparaciones pareadas (Wilcoxon o alternativa no paramétrica).
2. Prueba global (Friedman si aplica).
3. Corrección por comparaciones múltiples (Holm/Bonferroni).
4. Guardar resultados en `tables/stat_tests.csv`.

## Sección G. Visualizaciones

### Celda 18 (Code) - Curvas de métrica vs k

Generar por dataset/representación:

1. ASW vs k
2. CH vs k
3. XB/PC/PE para algoritmos difusos

### Celda 19 (Code) - Boxplots de estabilidad

Mostrar dispersión entre semillas por algoritmo.

### Celda 20 (Code) - UMAP

1. Reducir a 2D desde cada representación.
2. Panel por algoritmo (mismo dataset y representación).
3. Colorear por cluster predicho.
4. Figura paralela coloreada por etiqueta real para inspección.

### Celda 21 (Code) - t-SNE

Repetir esquema de UMAP para contraste cualitativo.

### Celda 22 (Code) - Incertidumbre difusa

Para FCM:

1. Entropía de membresía por punto.
2. Histograma de `max_membership`.

## Sección H. Discusión y conclusiones en notebook

### Celda 23 (Markdown) - Discusión guiada

Responder:

1. Qué algoritmo gana por dataset y representación.
2. Si coseno supera euclídea en texto.
3. Cuándo FCM aporta valor frente a hard clustering.
4. Efecto de BoW/TF-IDF/Nomic en separabilidad.

### Celda 24 (Markdown) - Amenazas a la validez

1. Dependencia de hiperparámetros.
2. Sesgo por tamaño de muestra.
3. Sensibilidad de UMAP/t-SNE a parámetros.
4. Coste computacional diferencial entre representaciones.

### Celda 25 (Markdown) - Conclusiones y trabajo futuro

1. Conclusiones accionables.
2. Próximos pasos (HDBSCAN, validación externa adicional, robustez cross-domain).

## 4. Checklist de calidad académica (antes de cerrar el notebook)

1. ¿Está fijada la semilla en todos los puntos estocásticos?
2. ¿Se documentan todas las configuraciones y versiones?
3. ¿Hay tablas de media + desviación + IC95?
4. ¿Se reportan pruebas estadísticas y tamaño de efecto?
5. ¿Se guardan figuras y tablas en disco?
6. ¿Se distingue claramente análisis cuantitativo y cualitativo?
7. ¿La discusión responde explícitamente a las hipótesis?

## 5. Entregables esperados

1. Notebook final ejecutable con narrativa académica.
2. CSV maestro de resultados crudos.
3. Tablas agregadas y de pruebas estadísticas.
4. Figuras UMAP/t-SNE y gráficas de métricas.
5. Resumen final para incluir en memoria/TFG.

## 6. Convención de nombres sugerida

1. Notebook: `validation/notebooks/clustering_experiment.ipynb`
2. Resultados: `validation/results/clustering_experiment/`
3. Plan (este documento): `validation/notebooks/plan_experimento_clustering.md`

## 7. Nota operativa para implementación

Si hay limitaciones de tiempo/cómputo:

1. Ejecutar primero una fase piloto con menos muestras y menos semillas.
2. Validar pipeline extremo a extremo.
3. Lanzar después la versión completa sin cambiar metodología.
