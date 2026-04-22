# Dossier data/

Ce dossier contient toutes les données utilisées et générées par le projet de clustering des joueurs d'échecs Lichess. Les données sont organisées par étapes de traitement, depuis les données brutes collectées jusqu'aux datasets finaux prêts pour l'analyse. Elles sont produites par les notebooks Jupyter dans un ordre spécifique (voir 
otebooks/README.md).

## Structure générale

- player_candidates/ : Liste des joueurs candidats pour l'expansion.
- raw/ : Données brutes collectées depuis l'API Lichess.
- enriched/ : Données enrichies avec des features supplémentaires.
- final/ : Datasets finaux et sorties des modèles.
- final_scaled/ : Données mises à l'échelle pour le clustering.
- selected/ : Données sélectionnées après filtrage.

## Détail par dossier

### player_candidates/

- players.txt : Liste des IDs de joueurs Lichess utilisés comme seeds pour l'expansion. Ces joueurs servent de point de départ pour découvrir d'autres joueurs via leurs adversaires. Format : un ID par ligne. Généré manuellement ou via exploration initiale.

### raw/

- by_player/ : Dossier contenant un fichier JSON par joueur avec ses parties brutes. Chaque fichier est nommé {player_id}.json et contient les données directement récupérées de l'API Berserk.
- failed_players.txt : Liste des IDs de joueurs pour lesquels la collecte de parties a échoué (par exemple, joueurs privés ou erreurs API).
- player_games_raw.json : Dataset consolidé de toutes les parties brutes collectées, sous forme de DataFrame sérialisé. Inclut les métadonnées de parties pour tous les joueurs candidats.

### enriched/

- games_final.json : Dataset enrichi avec des features calculées au niveau partie (par exemple, streaks, sessions, jours, semaines). Construit à partir de 
aw/player_games_raw.json en ajoutant des colonnes temporelles et comportementales.

### final/

- final_dataset.json : Dataset final agrégé au niveau joueur, avec features comportementales (style, endgame, streaks, rythme, etc.) et labels de progression (elo_slope_per_game). Prêt pour l'analyse exploratoire.
- model_outputs/ : Sorties des modèles de clustering.
  - comparison_table.csv : Tableau comparatif des performances des différents modèles (silhouette, inertia, etc.).
  - All_results.pkl : Objet Python sérialisé contenant tous les résultats détaillés des runs (labels, scores, etc.).
  - filter/ : Sous-dossier avec les mêmes fichiers mais filtrés pour les meilleurs modèles (4 retenus).

### final_scaled/

- X_raw_clustering.parquet : Matrice des features brutes pour le clustering, avant transformation.
- X_transformed.parquet : Matrice après transformations (imputation, log, etc.).
- X_scaled.parquet : Matrice finalisée, standardisée (RobustScaler), utilisée comme entrée pour les algorithmes de clustering K-means.

### selected/

- player_games_selected.json : Dataset filtré des parties après sélection des joueurs finaux (basé sur critères comme rating, nombre de parties, etc.). Sous-ensemble de enriched/games_final.json.

## Flux de données

1. **Collecte** : player_candidates/players.txt → API → 
aw/
2. **Enrichissement** : 
aw/player_games_raw.json → calcul features → enriched/games_final.json
3. **Sélection** : enriched/games_final.json → filtrage joueurs → selected/player_games_selected.json
4. **Agrégation** : selected/player_games_selected.json → features joueur + labels → final/final_dataset.json
5. **Préprocessing** : final/final_dataset.json → nettoyage, transformation, scaling → final_scaled/
6. **Clustering** : final_scaled/X_scaled.parquet → K-means → final/model_outputs/

## Notes

- Les fichiers JSON sont volumineux (plusieurs GB) ; ils sont générés par data_creation.ipynb.
- Les fichiers Parquet sont utilisés pour les matrices numériques pour une efficacité de stockage et chargement.
- Pour reproduire, suivre l'ordre des notebooks ; les fichiers d'entrée doivent exister pour les étapes suivantes.
- Les données respectent les termes d'utilisation de Lichess ; elles sont publiques mais anonymisées au niveau des IDs.
