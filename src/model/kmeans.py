import numpy as np
import pandas as pd

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def run_kmeans_multiple_seeds(X, k, n_seeds=20, n_init=20):
    results = []

    for seed in range(n_seeds):
        model = KMeans(
            n_clusters=k,
            random_state=seed,
            n_init=n_init,
        )
        labels = model.fit_predict(X)

        inertia = model.inertia_
        silhouette = silhouette_score(X, labels)
        cluster_sizes = pd.Series(labels).value_counts().sort_index().to_dict()

        results.append({
            "seed": seed,
            "k": k,
            "inertia": inertia,
            "silhouette": silhouette,
            "min_cluster_size": min(cluster_sizes.values()),
            "max_cluster_size": max(cluster_sizes.values()),
            "cluster_sizes": cluster_sizes,
            "labels": labels,
            "model": model,
        })

    best = max(results, key=lambda x: x["silhouette"])
    return best, results


def evaluate_k_range(X, k_values, n_seeds=20, n_init=20):
    all_results = []

    for k in k_values:
        best, results = run_kmeans_multiple_seeds(
            X=X,
            k=k,
            n_seeds=n_seeds,
            n_init=n_init,
        )

        all_results.append({
            "k": k,
            "best_seed": best["seed"],
            "best_silhouette": best["silhouette"],
            "best_inertia": best["inertia"],
            "min_cluster_size": best["min_cluster_size"],
            "max_cluster_size": best["max_cluster_size"],
            "cluster_sizes": best["cluster_sizes"],
            "best_model": best["model"],
            "labels": best["labels"],
            "all_seed_results": results,
        })

    return all_results


def results_to_dataframe(results):
    rows = []

    for r in results:
        imbalance_ratio = (
            r["min_cluster_size"] / r["max_cluster_size"]
            if r["max_cluster_size"] > 0 else 0.0
        )

        rows.append({
            "k": r["k"],
            "best_seed": r["best_seed"],
            "best_silhouette": r["best_silhouette"],
            "best_inertia": r["best_inertia"],
            "min_cluster_size": r["min_cluster_size"],
            "max_cluster_size": r["max_cluster_size"],
            "imbalance_ratio": imbalance_ratio,
        })

    return pd.DataFrame(rows).sort_values("k").reset_index(drop=True)