# Analysis Outputs

## Contenu

Ce dossier contient les résultats du clustering K-means des profils de joueurs d'échecs Lichess et l'analyse détaillée de tous les runs d'expérimentation.

### Structure

```
final_results/              Trois modèles optimaux sélectionnés
├── ModèleMinimal/         K-means avec 3 features (silhouette: 0.246)
├── ModèlePsychologique/   K-means avec 5 features comportementales
└── ModèleRythme/          K-means avec 5 features temporelles

full_results_deep_dive/     Résultats détaillés de 24 runs testés
├── all_model_summaries.csv
├── selected_models_comparison.csv
└── COMBO_*_k*_s*_*/       Dossiers pour chaque run (n=24)
```

---

## final_results/

### ModèleMinimal

Features: `mean_ply_count`, `entropy_sessions_interval`, `mean_games_per_session`

K=5 clusters. Silhouette score: 0.246. Meilleur modèle par équilibre rigueur/simplicité.

Contenu: `model_summary.json`, `plots/`, `tables/`, `data/`

### ModèlePsychologique

Features comportementales: moyenne des coups, entropie temporelle, ratios de délai, variation fréquence de jeu, sessions par intervalle.

K=5 clusters. Analyse des patterns psychologiques.

### ModèleRythme

Features temporelles: profondeur moyenne, ratios de délai, variabilité quotidienne/hebdomadaire, régularité.

K=5 clusters. Analyse des cycles de jeu.

---

## full_results_deep_dive/

### Fichiers synthétiques

**all_model_summaries.csv**: 24 runs. Colonnes: `feature_set_name`, `k`, `best_seed`, `silhouette`, `inertia`, `imbalance_ratio`, `elo_slope_*` (métriques de validation)

**selected_models_comparison.csv**: Top 5 modèles selon les critères d'évaluation

### Structure des runs individuels

Chaque dossier `COMBO_N_feature1_feature2_..._kK_sS_hash/` (où N=nombre de features, K=clusters, S=seed):

- `model_summary.json`: Métriques du run
- `plots/`: 5 visualisations clés (cluster sizes, boxplots Elo, heatmap profils)
- `tables/`: 8 fichiers CSV (cluster sizes, résumés statistiques, profils standardisés)
- `data/`: Données utilisées

---

## Métriques de validation

- **Silhouette**: -1 à 1 (>0.2 = acceptable pour ce dataset)
- **Inertia**: Somme distances intra-clusters (minimisation K-means)
- **Imbalance ratio**: Ratio max/min cluster size (proche de 1 = équilibré)
- **ELO slope metrics**: Mesure de séparation des profils de progression entre clusters

## Résumé

24 runs testés (COMBO_3: 3 runs, COMBO_4: 7 runs, COMBO_5: 10 runs). Trois modèles optimaux sélectionnés dans `final_results/` sur base de silhouette, équilibre et interprétabilité.
