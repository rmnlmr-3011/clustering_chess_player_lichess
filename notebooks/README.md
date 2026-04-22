# Dossier notebooks/

Ce dossier contient les notebooks Jupyter qui constituent le pipeline exécutable du projet de clustering des joueurs d'échecs Lichess. Ils permettent de reproduire l'ensemble du processus depuis la collecte des données jusqu'à l'analyse des résultats. L'ordre d'exécution recommandé est présenté ci-dessous pour assurer la reproductibilité.

## Ordre d'exécution recommandé

1. **berserk_api_test.ipynb** : Tests initiaux de l'API et des transformations.
2. **data_creation.ipynb** : Collecte et préparation des données brutes.
3. **cleaning_preprocess_data.ipynb** : Nettoyage et prétraitement des features.
4. **clustering_kmeans_evaluation.ipynb** : Exécution et évaluation des modèles de clustering.
5. **full_results_deep_dive.ipynb** : Analyse approfondie des meilleurs résultats.

## Détail de chaque notebook

### 1. berserk_api_test.ipynb

**Rôle** : Notebook de test pour vérifier la configuration de l'API Berserk et expérimenter les transformations de données des parties et joueurs.

**Contenu** :
- Importation des libraries nécessaires (berserk, pandas, etc.).
- Chargement du token API depuis le fichier .env.
- Connexion à l'API et récupération du profil utilisateur.
- Requêtes pour obtenir les parties d'un joueur spécifique.
- Analyse des ouvertures (ECO codes), résultats, et visualisation basique.
- Tests de transformation des données (par exemple, calcul de streaks, analyse temporelle).

**Reproductibilité** :
- Nécessite un fichier .env avec LICHESS_API_TOKEN.
- Aucun fichier d'entrée spécifique requis ; utilise des appels API directs.
- Produit des outputs temporaires (affichages, graphiques) pour validation.
- Pertinent pour tester la connectivité API avant de lancer la collecte massive.

### 2. data_creation.ipynb

**Rôle** : Première étape du pipeline, responsable de la collecte des données brutes depuis l'API Lichess et de la construction des datasets initiaux.

**Contenu** :
- Sampling des joueurs candidats : utilise un fichier players.txt (dans data/player_candidates/) contenant des IDs de joueurs seeds pour expansion.
- Collecte des parties : pour chaque joueur, récupère l'historique des parties via l'API.
- Construction des tables : transforme les données brutes en DataFrames structurés (player_games_raw, enriched, etc.).
- Sauvegarde des données : exporte vers data/raw/, data/enriched/, data/final/.

**Reproductibilité** :
- Entrée : data/player_candidates/players.txt (liste d'IDs de joueurs pour commencer l'expansion).
- Sortie : data/raw/player_games_raw.json, data/enriched/games_final.json, data/final/final_dataset.json, etc.
- Pour tester avec d'autres joueurs : modifier players.txt avec de nouveaux IDs de joueurs Lichess. Le notebook utilise une expansion à partir de ces seeds (joueurs qui ont joué contre eux), avec un préfiltrage (rating 900-1600, etc.). Ajuster les paramètres dans src/ingestion/player_sampling.py si nécessaire.
- Temps d'exécution : Long (collecte API), dépend du nombre de joueurs et parties.

### 3. cleaning_preprocess_data.ipynb

**Rôle** : Seconde étape, effectue le nettoyage, la validation et le prétraitement des features pour préparer la matrice de clustering.

**Contenu** :
- Chargement du dataset final (data/final/final_dataset.json).
- Analyse univariée des features : statistiques, visualisation, détection de corrélations.
- Validation des features sélectionnées (présence, types).
- Construction de la matrice X : imputation, transformations (log, etc.), standardisation.
- Sauvegarde des données prétraitées : data/final_scaled/X_raw.parquet, X_transformed.parquet, X_scaled.parquet.

**Reproductibilité** :
- Entrée : data/final/final_dataset.json (produit par data_creation.ipynb).
- Sortie : Fichiers dans data/final_scaled/.
- Utilise les définitions de features dans src/features/features_groups.py.
- Pertinent pour ajuster les transformations ou features sans re-collecter les données.

### 4. clustering_kmeans_evaluation.ipynb

**Rôle** : Troisième étape, exécute les modèles de clustering K-means avec différents paramètres, évalue les performances et conserve les meilleurs runs.

**Contenu** :
- Chargement des données scalées (data/final_scaled/X_scaled.parquet).
- Définition des feature sets (minimal, principal, etc.).
- Exécution de K-means avec multiples seeds et k (clusters).
- Évaluation : silhouette score, inertia, tailles de clusters.
- Sauvegarde des résultats : data/final/model_outputs/comparison_table.csv, All_results.pkl.

**Reproductibilité** :
- Entrée : data/final_scaled/X_scaled.parquet (produit par cleaning_preprocess_data.ipynb).
- Sortie : data/final/model_outputs/.
- Les runs sont déterministes avec seeds fixes ; pour explorer plus, ajuster les paramètres dans le notebook.
- Filtre les meilleurs modèles pour l'analyse suivante.

### 5. full_results_deep_dive.ipynb

**Rôle** : Dernière étape, analyse approfondie des meilleurs runs de clustering, génération de graphiques et résumés.

**Contenu** :
- Chargement des résultats filtrés (data/final/model_outputs/filter/).
- Analyse par modèle : distributions des clusters, caractéristiques moyennes, métriques de progression.
- Visualisations : graphiques de clusters, comparaisons.
- Sauvegarde des analyses : analysis_outputs/full_results_deep_dive/.

**Reproductibilité** :
- Entrée : data/final/model_outputs/filter/all_results.pkl et comparison_table.csv (produit par clustering_kmeans_evaluation.ipynb).
- Sortie : analysis_outputs/full_results_deep_dive/.
- Génère automatiquement des rapports pour tous les modèles candidats (23 runs) et les 4 retenus.
- Utile pour explorer les insights sans re-exécuter les modèles.

## Notes générales

- Tous les notebooks utilisent les modules de src/ pour les fonctions réutilisables.
- Assurer que l'environnement virtuel est activé et les dépendances installées (pip install -r requirements.txt).
- Pour la reproductibilité complète, exécuter dans l'ordre ; sinon, utiliser les fichiers de sortie comme entrées.
- Les notebooks ne sont pas exécutés par défaut ; lancer cellule par cellule pour contrôler.
