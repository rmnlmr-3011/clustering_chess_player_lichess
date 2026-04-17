# Code permettant d'évaluer les différents modèles de clustering (différents feature sets, k, seeds).

from asyncio import run

import pandas as pd

import os
import sys
sys.path.append(os.path.abspath(".."))


from src.model.kmeans import *
from src.model.cluster_analyzing import *


def evaluate_single_run(
    X_model: pd.DataFrame,
    final_dataset: pd.DataFrame,
    feature_set_name: str,
    features: list[str],
    k: int,
    seed: int,
    performance_features: list[str],
    progression_labels: list[str],
):
    """
    Évalue un run unique (feature_set, k, seed).
    """
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    model = KMeans(
        n_clusters=k,
        random_state=seed,
        n_init=20,
    )

    labels = model.fit_predict(X_model)

    inertia = model.inertia_
    silhouette = silhouette_score(X_model, labels)

    cluster_sizes_series = pd.Series(labels).value_counts().sort_index()
    cluster_sizes = cluster_sizes_series.to_dict()
    min_cluster_size = int(cluster_sizes_series.min())
    max_cluster_size = int(cluster_sizes_series.max())
    imbalance_ratio = (
        min_cluster_size / max_cluster_size if max_cluster_size > 0 else 0.0
    )

    df_clustered = attach_clusters(final_dataset, labels)

    cluster_tables = build_cluster_profile_tables(
        df=df_clustered,
        clustering_features=features,
        performance_features=performance_features,
        progression_labels=progression_labels,
    )

    progression_metrics = compute_progression_metrics_full(
        df=df_clustered,
        progression_summary=cluster_tables["progression_summary"],
        cluster_col="cluster",
        target_col="elo_slope_per_game",
    )

    return {
        "feature_set_name": feature_set_name,
        "features": features,
        "n_features": len(features),
        "k": k,
        "seed": seed,
        "silhouette": float(silhouette),
        "inertia": float(inertia),
        "cluster_sizes": cluster_sizes,
        "min_cluster_size": min_cluster_size,
        "max_cluster_size": max_cluster_size,
        "imbalance_ratio": float(imbalance_ratio),
        "elo_slope_per_game_range": progression_metrics["elo_slope_per_game_range"],
        "elo_slope_per_game_std_between_clusters": progression_metrics[
            "elo_slope_per_game_std_between_clusters"
        ],
        "elo_slope_per_game_std_between_clusters_weighted": progression_metrics[
            "elo_slope_per_game_std_between_clusters_weighted"
        ],
        "elo_slope_per_game_std_within_clusters_weighted": progression_metrics[
            "elo_slope_per_game_std_within_clusters_weighted"
        ],
    }
#     return {
#         "silhouette": silhouette,
#         "inertia": inertia,
#         "min_cluster_size": min_cluster_size,
#         "max_cluster_size": max_cluster_size,
#         "imbalance_ratio": imbalance_ratio,
#         "elo_slope_per_game_range": progression_metrics["elo_slope_per_game_range"],
#         "elo_slope_per_game_std_between_clusters_weighted": progression_metrics[
#             "elo_slope_per_game_std_between_clusters_weighted"
#         ],
#         "elo_slope_per_game_std_within_clusters_weighted": progression_metrics[
#             "elo_slope_per_game_std_within_clusters_weighted"
#         ],
# }
#     return {
#         "feature_set_name": feature_set_name,
#         "features": features,
#         "n_features": len(features),
#         "k": k,
#         "seed": seed,
#         "silhouette": float(silhouette),
#         "inertia": float(inertia),
#         "cluster_sizes": cluster_sizes,
#         "min_cluster_size": min_cluster_size,
#         "max_cluster_size": max_cluster_size,
#         "imbalance_ratio": float(imbalance_ratio),
#         "labels": labels,
#         "model": model,
#         "clustering_summary": cluster_tables["clustering_summary"],
#         "performance_summary": cluster_tables["performance_summary"],
#         "progression_summary": cluster_tables["progression_summary"],
#         "elo_slope_per_game_range": progression_metrics["elo_slope_per_game_range"],
#         "elo_slope_per_game_std_between_clusters": progression_metrics[
#             "elo_slope_per_game_std_between_clusters"
#         ],
#         "elo_slope_per_game_std_between_clusters_weighted": progression_metrics[
#             "elo_slope_per_game_std_between_clusters_weighted"
#         ],
#         "elo_slope_per_game_std_within_clusters_weighted": progression_metrics[
#             "elo_slope_per_game_std_within_clusters_weighted"
#         ],
#     }

def evaluate_feature_set(
    X_scaled: pd.DataFrame,
    final_dataset: pd.DataFrame,
    feature_set_name: str,
    features: list[str],
    k_values: list[int],
    n_seeds: int,
    performance_features: list[str],
    progression_labels: list[str],
):
    """
    Pour un feature set :
    - lance tous les runs bruts
    - garde le meilleur run par k (meilleur seed selon silhouette)
    """
    X_model = X_scaled[features].copy()

    all_runs = []
    best_by_k = {}

    for k in k_values:
        runs_k = []

        for seed in range(n_seeds):
            run_result = evaluate_single_run(
                X_model=X_model,
                final_dataset=final_dataset,
                feature_set_name=feature_set_name,
                features=features,
                k=k,
                seed=seed,
                performance_features=performance_features,
                progression_labels=progression_labels,
            )
            runs_k.append(run_result)
            all_runs.append(run_result)


        def _safe_minmax_normalize(series):
            min_val = series.min()
            max_val = series.max()

            if max_val == min_val:
                return pd.Series([0.0] * len(series), index=series.index)

            return (series - min_val) / (max_val - min_val)

        runs_k_df = pd.DataFrame([
            {
                "idx": i,
                "elo_slope_per_game_range": run["elo_slope_per_game_range"],
                "elo_slope_per_game_std_between_clusters_weighted": run["elo_slope_per_game_std_between_clusters_weighted"],
                "elo_slope_per_game_std_within_clusters_weighted": run["elo_slope_per_game_std_within_clusters_weighted"],
                "silhouette": run["silhouette"],
            }
            for i, run in enumerate(runs_k)
        ])

        runs_k_df["std_between_weighted_norm"] = _safe_minmax_normalize(
            runs_k_df["elo_slope_per_game_std_between_clusters_weighted"]
        )

        runs_k_df["silhouette_norm"] = _safe_minmax_normalize(
            runs_k_df["silhouette"]
        )

        runs_k_df["run_score"] = (
            0.7 * runs_k_df["std_between_weighted_norm"]
            + 0.3 * runs_k_df["silhouette_norm"]
        )

        best_idx = runs_k_df.sort_values("run_score", ascending=False).iloc[0]["idx"]
        best_run_k = runs_k[int(best_idx)]
        best_by_k[k] = best_run_k

    return {
        "feature_set_name": feature_set_name,
        "features": features,
        "n_features": len(features),
        "all_runs": all_runs,
        "best_by_k": best_by_k,
    }







def evaluate_all_feature_sets(
    X_scaled: pd.DataFrame,
    final_dataset: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    performance_features: list[str],
    progression_labels: list[str],
    k_values: list[int],
    n_seeds: int = 20,
):
    """
    Lance toute la grille d'expérimentation sur tous les feature sets.
    """
    all_results = {}

    for feature_set_name, features in feature_sets.items():
        all_results[feature_set_name] = evaluate_feature_set(
            X_scaled=X_scaled,
            final_dataset=final_dataset,
            feature_set_name=feature_set_name,
            features=features,
            k_values=k_values,
            n_seeds=n_seeds,
            performance_features=performance_features,
            progression_labels=progression_labels,
        )

    return all_results


def build_comparison_table(all_results: dict) -> pd.DataFrame:
    """
    Construit une table globale de comparaison :
    une ligne = meilleur modèle pour un couple (feature_set, k).
    """
    rows = []

    for feature_set_name, fs_result in all_results.items():
        for k, best_run in fs_result["best_by_k"].items():
            rows.append({
                "feature_set_name": feature_set_name,
                "n_features": best_run["n_features"],
                "k": k,
                "best_seed": best_run["seed"],
                "silhouette": best_run["silhouette"],
                "inertia": best_run["inertia"],
                "min_cluster_size": best_run["min_cluster_size"],
                "max_cluster_size": best_run["max_cluster_size"],
                "imbalance_ratio": best_run["imbalance_ratio"],
                "elo_slope_per_game_range": best_run["elo_slope_per_game_range"],
                "elo_slope_per_game_std_between_clusters": best_run[
                    "elo_slope_per_game_std_between_clusters"
                ],
                "elo_slope_per_game_std_between_clusters_weighted": best_run[
                    "elo_slope_per_game_std_between_clusters_weighted"
                ],
                "elo_slope_per_game_std_within_clusters_weighted": best_run[
                    "elo_slope_per_game_std_within_clusters_weighted"
                ],
            })

            
    return pd.DataFrame(rows).sort_values(
        by=["feature_set_name", "k"]
    ).reset_index(drop=True)

def get_best_run_for_feature_set(
    all_results: dict,
    feature_set_name: str,
    chosen_k: int,
):
    """
    Récupère le meilleur run d'un feature set pour un k choisi manuellement.
    """
    return all_results[feature_set_name]["best_by_k"][chosen_k]

def build_feature_set_selection_summary(
    comparison_df: pd.DataFrame,
    feature_set_name: str,
) -> pd.DataFrame:
    """
    Filtre la table de comparaison globale pour un feature set donné.
    Sert à choisir manuellement le meilleur k.
    """
    return (
        comparison_df[comparison_df["feature_set_name"] == feature_set_name]
        .sort_values("k")
        .reset_index(drop=True)
    )






from sklearn.cluster import KMeans

def run_full_analysis_for_model(
    X_scaled,
    final_dataset,
    features,
    feature_set_name,
    k,
    seed,
    performance_features,
    progression_labels,
):
    # 1. Sous-ensemble de features
    X = X_scaled[features].copy()

    # 2. Fit modèle
    model = KMeans(
        n_clusters=k,
        random_state=seed,
        n_init=20,
    )
    labels = model.fit_predict(X)

    # 3. Attacher clusters
    df_with_clusters = attach_clusters(final_dataset, labels)

    # 4. Analyse complète
    full_analysis = build_full_cluster_analysis(
        df=df_with_clusters,
        clustering_features=features,
        performance_features=performance_features,
        progression_labels=progression_labels,
    )

    return {
        "feature_set_name": feature_set_name,
        "k": k,
        "seed": seed,
        "features": features,
        "labels": labels,
        "model": model,
        "df_with_clusters": df_with_clusters,
        "cluster_sizes": full_analysis["cluster_sizes"],
        "clustering_summary_mean": full_analysis["clustering_summary_mean"],
        "clustering_summary_median": full_analysis["clustering_summary_median"],
        "performance_summary_mean": full_analysis["performance_summary_mean"],
        "performance_summary_median": full_analysis["performance_summary_median"],
        "progression_summary_mean": full_analysis["progression_summary_mean"],
        "progression_summary_median": full_analysis["progression_summary_median"],
        "standardized_profiles": full_analysis["standardized_profiles"],
    }
