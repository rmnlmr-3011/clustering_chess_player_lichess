# Code pour effectuer une analyse univariée des features, identifier les features à transformer, calculer les corrélations avec les targets de progression, visualiser les relations entre features et targets, détecter les paires de features fortement corrélées, et construire un résumé des décisions de sélection et de transformation des features.

import pandas as pd
import matplotlib.pyplot as plt

def univariate_analysis(df, features, low_variance_threshold=1e-6, skew_threshold=1.0):
    stats = []

    for col in features:
        x = df[col].dropna()

        if len(x) == 0:
            stats.append({
                "feature": col,
                "nan_ratio": 1.0,
                "n_unique": 0,
                "variance": None,
                "skew": None,
                "q1": None,
                "q3": None,
                "iqr": None,
                "min": None,
                "max": None,
                "decision": "drop_all_nan",
                "suggested_transform": "check_transform",
            })
            continue

        q1 = x.quantile(0.25)
        q3 = x.quantile(0.75)
        iqr = q3 - q1

        decision = "keep"
        suggested_transform = None

        if x.nunique() <= 1:
            decision = "drop_constant"
        elif x.var() <= low_variance_threshold or iqr == 0:
            decision = "drop_low_variance"
        elif abs(x.skew()) > skew_threshold:
            suggested_transform = "log_or_robust_treatment"

        stats.append({
            "feature": col,
            "nan_ratio": df[col].isna().mean(),
            "n_unique": x.nunique(),
            "variance": x.var(),
            "skew": x.skew(),
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "min": x.min(),
            "max": x.max(),
            "decision": decision,
            "suggested_transform": suggested_transform,
        })
        

    return pd.DataFrame(stats).sort_values("feature").reset_index(drop=True)


def suggest_features_for_transform(univariate_df):
    mask = (
        (univariate_df["decision"] == "keep") &
        (univariate_df["suggested_transform"] == "log_or_robust_treatment")
    )
    return univariate_df.loc[mask, "feature"].tolist()


def correlation_with_progression(df, features, targets):
    results = []

    for f in features:
        for t in targets:
            pearson = df[f].corr(df[t], method="pearson")
            spearman = df[f].corr(df[t], method="spearman")

            results.append({
                "feature": f,
                "target": t,
                "pearson": pearson,
                "spearman": spearman,
            })

    return pd.DataFrame(results)

def summarize_progression_correlations(corr_df):
    tmp = (
        corr_df
        .assign(
            abs_pearson=lambda d: d["pearson"].abs(),
            abs_spearman=lambda d: d["spearman"].abs(),
            max_abs_corr=lambda d: d[["abs_pearson", "abs_spearman"]].max(axis=1),
        )
    )

    idx = tmp.groupby("feature")["max_abs_corr"].idxmax()

    summary = (
        tmp.loc[idx, ["feature", "target", "abs_pearson", "abs_spearman", "max_abs_corr"]]
        .rename(columns={
            "target": "best_target",
            "abs_pearson": "max_abs_pearson",
            "abs_spearman": "max_abs_spearman",
        })
        .sort_values("max_abs_corr", ascending=False)
        .reset_index(drop=True)
    )

    return summary

def plot_feature_vs_target(df, feature, target):
    tmp = df[[feature, target]].dropna()

    plt.figure(figsize=(6, 4))
    plt.scatter(tmp[feature], tmp[target], alpha = 0.7)
    plt.xlabel(feature)
    plt.ylabel(target)
    plt.title(f"{feature} vs {target}")
    plt.grid(True, alpha=0.3)
    plt.show()

def find_correlated_pairs(df, features, threshold=0.8, method="spearman"):
    corr = df[features].corr(method=method)

    pairs = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            value = corr.iloc[i, j]
            if abs(value) > threshold:
                pairs.append({
                    "feature_1": corr.index[i],
                    "feature_2": corr.columns[j],
                    "correlation": value,
                    "abs_correlation": abs(value),
                })

    return (
        pd.DataFrame(pairs)
        .sort_values("abs_correlation", ascending=False)
        .reset_index(drop=True)
        if pairs else
        pd.DataFrame(columns=["feature_1", "feature_2", "correlation", "abs_correlation"])
    )


def choose_feature_to_drop(pair_row, univariate_df, corr_summary_df):
    f1 = pair_row["feature_1"]
    f2 = pair_row["feature_2"]

    uni = univariate_df.set_index("feature")
    corr = corr_summary_df.set_index("feature")

    score1 = (
        (1 - uni.loc[f1, "nan_ratio"]) +
        corr.loc[f1, "max_abs_corr"]
    )
    score2 = (
        (1 - uni.loc[f2, "nan_ratio"]) +
        corr.loc[f2, "max_abs_corr"]
    )

    return f2 if score1 >= score2 else f1

def validate_features(df, features):
    available = [f for f in features if f in df.columns]
    missing = [f for f in features if f not in df.columns]
    return available, missing

def build_step5_summary(selected_features, dropped_features, log_features):
    return {
        "selected_feature_cols": selected_features,
        "dropped_features": dropped_features,
        "features_to_log": log_features,
    }
