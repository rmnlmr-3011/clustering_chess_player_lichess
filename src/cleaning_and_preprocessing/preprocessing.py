import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import RobustScaler


def build_clustering_matrix(
    df: pd.DataFrame,
    selected_feature_cols: list[str],
) -> pd.DataFrame:
    """
    Construit X à partir des features retenues pour le clustering.
    """
    missing = [col for col in selected_feature_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le DataFrame : {missing}")

    X = df[selected_feature_cols].copy()
    return X


def impute_missing_values(
    X: pd.DataFrame,
    strategy: str = "median",
) -> tuple[pd.DataFrame, SimpleImputer]:
    """
    Impute les valeurs manquantes.
    Par défaut : médiane, ce qui est robuste aux outliers.
    """
    if X.empty:
        raise ValueError("X est vide.")

    imputer = SimpleImputer(strategy=strategy)
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X),
        columns=X.columns,
        index=X.index,
    )
    return X_imputed, imputer


def apply_log_transformations(
    X: pd.DataFrame,
    features_to_transform: list[str],
) -> pd.DataFrame:
    """
    Applique les transformations décidées à l'étape 5.

    Règles retenues :
    - log1p pour variables positives de type volume / intervalle
    - log(x + 1e-6) pour ratio pouvant être très proche de 0
    """
    X_out = X.copy()

    for col in features_to_transform:
        if col not in X_out.columns:
            raise ValueError(f"La feature '{col}' est absente de X.")

    # Variables positives classiques
    for col in ["cv_games_interval", "mean_games_per_session", "cv_games_per_week", "delay_ratio_when_winstreak"]:
        if col in features_to_transform:
            if (X_out[col] < 0).any():
                raise ValueError(f"La feature '{col}' contient des valeurs négatives, log1p impossible.")
            X_out[col] = np.log1p(X_out[col])

    # Variable de ratio de délai
    # if "delay_ratio_when_winstreak" in features_to_transform:
    #     if (X_out["delay_ratio_when_winstreak"] < 0).any():
    #         raise ValueError("La feature 'delay_ratio_when_winstreak' contient des valeurs négatives, log impossible.")
    #     X_out["delay_ratio_when_winstreak"] = np.log(
    #         X_out["delay_ratio_when_winstreak"] + 1e-6
    #     )

    # Si jamais tu décides finalement de garder et transformer cv_sessions_interval
    if "cv_sessions_interval" in features_to_transform:
        if (X_out["cv_sessions_interval"] < 0).any():
            raise ValueError("La feature 'cv_sessions_interval' contient des valeurs négatives, log1p impossible.")
        X_out["cv_sessions_interval"] = np.log1p(X_out["cv_sessions_interval"])

    return X_out


def scale_features(
    X: pd.DataFrame,
) -> tuple[pd.DataFrame, RobustScaler]:
    """
    Standardise les features avec RobustScaler.
    Choix adapté à KMeans en présence d'asymétrie / outliers.
    """
    if X.empty:
        raise ValueError("X est vide.")

    scaler = RobustScaler()
    X_scaled_array = scaler.fit_transform(X)

    X_scaled = pd.DataFrame(
        X_scaled_array,
        columns=X.columns,
        index=X.index,
    )
    return X_scaled, scaler


def summarize_preprocessing(
    X: pd.DataFrame,
    X_imputed: pd.DataFrame,
    X_transformed: pd.DataFrame,
    X_scaled: pd.DataFrame,
    selected_feature_cols: list[str],
    features_to_transform: list[str],
) -> dict:
    """
    Résumé simple de l'étape 6.
    """
    summary = {
        "n_samples": int(X.shape[0]),
        "n_features": int(X.shape[1]),
        "selected_feature_cols": selected_feature_cols,
        "features_to_transform": features_to_transform,
        "initial_nan_count": int(X.isna().sum().sum()),
        "post_imputation_nan_count": int(X_imputed.isna().sum().sum()),
        "post_transformation_nan_count": int(X_transformed.isna().sum().sum()),
        "post_scaling_nan_count": int(X_scaled.isna().sum().sum()),
    }
    return summary


def check_post_transform_skew(
    X_before: pd.DataFrame,
    X_after: pd.DataFrame,
    features: list[str],
) -> pd.DataFrame:
    """
    Vérifie l'effet des transformations sur la skewness.
    """
    rows = []

    for col in features:
        if col not in X_before.columns or col not in X_after.columns:
            continue

        rows.append({
            "feature": col,
            "skew_before": X_before[col].skew(),
            "skew_after": X_after[col].skew(),
        })

    return pd.DataFrame(rows).sort_values("feature").reset_index(drop=True)