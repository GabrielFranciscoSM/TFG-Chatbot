import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score

# Asegurarse de estar en el directorio correcto y agregar al path
sys.path.append(os.path.abspath("/home/gabriel/clase/TFG/TFG-Chatbot/validation/"))
sys.path.append(os.path.abspath("/home/gabriel/clase/TFG/TFG-Chatbot/"))

from clustering import GenericKMeans
from metrics.metrics import evaluate_fuzzy_clustering
from representation.ollama_embeddings import OllamaEmbeddings


def run():
    print("Cargando dataset...")
    df = pd.read_csv(
        "/home/gabriel/clase/TFG/TFG-Chatbot/validation/results/banking77_eda/tables/banking77_similar8_subset.csv"
    )
    texts = df["text"].tolist()
    true_labels = df["label"].tolist()
    label_to_idx = {label: idx for idx, label in enumerate(np.unique(true_labels))}
    true_labels_idx = np.array([label_to_idx[label] for label in true_labels])

    print("Generando embeddings (nomic)...")
    embedder = OllamaEmbeddings(model="nomic-embed-text", host="localhost", port=11434)
    embeddings = embedder.embed_batch(texts, normalize=True)

    m_values = [1.1, 1.2, 1.3, 1.5, 1.8, 2.0]
    k = 8
    seed = 42

    print(f"\n--- Probando FCM Coseno (Esférico) para k={k} con varias m ---")
    print(f"{'m':<5} | {'PC':<8} | {'PE':<8} | {'XB':<12} | {'ARI':<8} | {'NMI':<8}")
    print("-" * 60)

    for m in m_values:
        model = GenericKMeans(
            n_clusters=k,
            algorithm="fcm",
            distance="cosine",
            max_iter=300,
            random_state=seed,
            m=m,
        )
        model.fit(embeddings)

        # Evaluar
        metrics = evaluate_fuzzy_clustering(
            embeddings, model.membership_, model.centroids_, m=m, distance="cosine"
        )
        predicted_labels = np.argmax(model.membership_, axis=1)

        ari = adjusted_rand_score(true_labels_idx, predicted_labels)
        nmi = normalized_mutual_info_score(true_labels_idx, predicted_labels)

        print(
            f"{m:<5.1f} | {metrics.pc:<8.4f} | {metrics.pe:<8.4f} | {metrics.xb:<12.4e} | {ari:<8.4f} | {nmi:<8.4f}"
        )


if __name__ == "__main__":
    run()
