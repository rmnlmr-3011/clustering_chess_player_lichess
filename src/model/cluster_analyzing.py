# Code pour analyser les clusters obtenus, en attachant les labels au DataFrame original, en résumant les caractéristiques de chaque cluster, et en calculant des métriques de progression spécifiques pour évaluer la séparation et l'homogénéité des clusters.

import pandas as pd
import numpy as np


def attach_clusters(df, labels, cluster_col="cluster"):
    df_out = df.copy()
    df_out[cluster_col] = labels
    return df_out


def get_cluster_sizes(df, cluster_col="cluster"):
    return df[cluster_col].value_counts().sort_index().rename("size")


def summarize_clusters(df, features, cluster_col="cluster"):
    cols = [c for c in features if c in df.columns]
    return df.groupby(cluster_col)[cols].mean()


def summarize_clusters_with_global_delta(df, features, cluster_col="cluster"):
    cols = [c for c in features if c in df.columns]

    cluster_means = df.groupby(cluster_col)[cols].mean()
    global_mean = df[cols].mean()

    delta = cluster_means - global_mean
    delta.index.name = cluster_col

    return cluster_means, delta


def build_cluster_profile_tables(
    df,
    clustering_features,
    performance_features,
    progression_labels,
    cluster_col="cluster",
):
    clustering_summary = summarize_clusters(df, clustering_features, cluster_col)
    performance_summary = summarize_clusters(df, performance_features, cluster_col)
    progression_summary = summarize_clusters(df, progression_labels, cluster_col)
    cluster_sizes = get_cluster_sizes(df, cluster_col)

    return {
        "cluster_sizes": cluster_sizes,
        "clustering_summary": clustering_summary,
        "performance_summary": performance_summary,
        "progression_summary": progression_summary,
    }

def compute_progression_metrics(
    progression_summary: pd.DataFrame,
    target_col: str = "elo_slope_per_game",
) -> dict:
    if target_col not in progression_summary.columns:
        return {
            f"{target_col}_range": None,
            f"{target_col}_std_between_clusters": None,
        }

    cluster_means = progression_summary[target_col]

    return {
        f"{target_col}_range": float(cluster_means.max() - cluster_means.min()),
        f"{target_col}_std_between_clusters": float(cluster_means.std(ddof=0)),
    }


def compute_progression_metrics_full(
    df: pd.DataFrame,
    progression_summary: pd.DataFrame,
    cluster_col: str = "cluster",
    target_col: str = "elo_slope_per_game",
) -> dict:
    """
    Calcule les métriques projet-spécifiques de séparation inter-clusters
    et d'homogénéité intra-cluster.

    Retourne :
    - range entre moyennes de clusters
    - std_between_clusters (non pondéré)
    - std_between_clusters_weighted
    - std_within_clusters_weighted
    """
    if target_col not in progression_summary.columns:
        return {
            f"{target_col}_range": None,
            f"{target_col}_std_between_clusters": None,
            f"{target_col}_std_between_clusters_weighted": None,
            f"{target_col}_std_within_clusters_weighted": None,
        }

    if target_col not in df.columns or cluster_col not in df.columns:
        return {
            f"{target_col}_range": None,
            f"{target_col}_std_between_clusters": None,
            f"{target_col}_std_between_clusters_weighted": None,
            f"{target_col}_std_within_clusters_weighted": None,
        }

    cluster_means = progression_summary[target_col]

    # tailles de clusters
    cluster_sizes = df.groupby(cluster_col).size().reindex(cluster_means.index)

    # std_between non pondéré
    std_between = float(cluster_means.std(ddof=0))

    # std_between pondéré
    std_between_weighted = weighted_std(cluster_means, cluster_sizes)

    # std_within pondéré
    grouped = df.groupby(cluster_col)[target_col]
    cluster_stds = grouped.std(ddof=0).reindex(cluster_means.index)

    # sécurité si certains std deviennent NaN
    cluster_stds = cluster_stds.fillna(0.0)

    std_within_weighted = float(
        (cluster_stds * cluster_sizes).sum() / cluster_sizes.sum()
    )

    return {
        f"{target_col}_range": float(cluster_means.max() - cluster_means.min()),
        f"{target_col}_std_between_clusters": std_between,
        f"{target_col}_std_between_clusters_weighted": std_between_weighted,
        f"{target_col}_std_within_clusters_weighted": std_within_weighted,
    }


def weighted_std(values: pd.Series, weights: pd.Series) -> float:
    """
    Écart-type pondéré.
    """
    values = pd.Series(values, dtype="float64")
    weights = pd.Series(weights, dtype="float64")

    if len(values) == 0 or len(weights) == 0 or weights.sum() == 0:
        return np.nan

    mean_weighted = np.average(values, weights=weights)
    variance_weighted = np.average((values - mean_weighted) ** 2, weights=weights)
    return float(np.sqrt(variance_weighted))








def compute_within_cluster_dispersion(
    df: pd.DataFrame,
    cluster_col: str = "cluster",
    target_col: str = "elo_slope_per_game",
) -> dict:
    if target_col not in df.columns or cluster_col not in df.columns:
        return {
            f"{target_col}_std_within_clusters_weighted": None,
        }

    grouped = df.groupby(cluster_col)[target_col]
    cluster_stds = grouped.std(ddof=0)
    cluster_sizes = grouped.size()

    weighted_std = (cluster_stds * cluster_sizes).sum() / cluster_sizes.sum()

    return {
        f"{target_col}_std_within_clusters_weighted": float(weighted_std),
    }





def summarize_clusters_median(df, features, cluster_col="cluster"):
    cols = [c for c in features if c in df.columns]
    return df.groupby(cluster_col)[cols].median()

def standardize_cluster_profiles(cluster_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Standardise les profils de clusters feature par feature
    pour comparer les écarts relatifs indépendamment des échelles.
    """
    std = cluster_summary.std(axis=0, ddof=0)
    std_replaced = std.replace(0, 1.0)

    standardized = (cluster_summary - cluster_summary.mean(axis=0)) / std_replaced
    return standardized

def build_full_cluster_analysis(
    df,
    clustering_features,
    performance_features,
    progression_labels,
    cluster_col="cluster",
):
    clustering_summary_mean = summarize_clusters(df, clustering_features, cluster_col)
    clustering_summary_median = summarize_clusters_median(df, clustering_features, cluster_col)

    performance_summary_mean = summarize_clusters(df, performance_features, cluster_col)
    performance_summary_median = summarize_clusters_median(df, performance_features, cluster_col)

    progression_summary_mean = summarize_clusters(df, progression_labels, cluster_col)
    progression_summary_median = summarize_clusters_median(df, progression_labels, cluster_col)

    cluster_sizes = get_cluster_sizes(df, cluster_col)
    standardized_profiles = standardize_cluster_profiles(clustering_summary_mean)

    return {
        "cluster_sizes": cluster_sizes,
        "clustering_summary_mean": clustering_summary_mean,
        "clustering_summary_median": clustering_summary_median,
        "performance_summary_mean": performance_summary_mean,
        "performance_summary_median": performance_summary_median,
        "progression_summary_mean": progression_summary_mean,
        "progression_summary_median": progression_summary_median,
        "standardized_profiles": standardized_profiles,
    }