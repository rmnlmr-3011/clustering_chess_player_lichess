# Clustering Chess Player Lichess

## Objectif du projet

Comment progresser rapidement aux échecs ? Une réponse rapide serait de simplement jouer plus. Cependant, ce projet tente de répondre à cette question en identifiant des schémas comportementaux associés à la progression des joueurs d'échecs en ligne. Les données utilisées proviennent de la plateforme d'échecs en ligne Lichess, dont l'historique complet des parties est disponible en ligne. L'objectif est d'explorer et d'exploiter qualitativement ces données dans l'optique de segmenter les joueurs selon leurs comportements, en identifiant des groupes liés à la profondeur de jeu et à la résilience.

## Résumé de la méthodologie

Sélection d'un ensemble de joueurs débutants ayant suffisamment joué dans une fenêtre temporelle commune. Nettoyage et enrichissement des parties. Construction d'un ensemble de variables comportementales couvrant le style, la fréquence et l'intensité de jeu. Application du modèle de clustering K-means pour identifier des groupes de joueurs. Analyse des résultats pour comprendre les mécanismes d'apprentissage des échecs en ligne.

## Structure du dépôt

- `README.md` : Ce fichier.
- `requirements.txt` : Liste des dépendances Python.
- `RapportFinal.pdf` : Rapport académique détaillé du projet.
- `analysis_outputs/` : Résultats des analyses.
  - `final_results/` : Analyses des 3 modèles retenus (ModèleMinimal, ModèlePsychologique, ModèleRythme).
  - `full_results_deep_dive/` : Analyses des 23 runs candidats, incluant des comparaisons et résumés.
- `data/` : Données du projet.
  - `enriched/` : Données enrichies.
  - `final/` : Jeu de données final et sorties des modèles.
  - `final_scaled/` : Données mises à l'échelle pour le clustering.
  - `player_candidates/` : Candidats de joueurs.
  - `raw/` : Données brutes et échecs de récupération.
  - `selected/` : Données sélectionnées.
- `notebooks/` : Notebooks Jupyter exécutant l'ensemble du projet.
  - `berserk_api_test.ipynb` : Test de l'API Berserk.
  - `data_creation.ipynb` : Création et ingestion des données.
  - `cleaning_preprocess_data.ipynb` : Nettoyage et prétraitement.
  - `clustering_kmeans_evaluation.ipynb` : Clustering et évaluation.
  - `full_results_deep_dive.ipynb` : Analyse approfondie des résultats.
- `src/` : Code source Python modulaire.
  - `cleaning_and_preprocessing/` : Nettoyage et prétraitement.
  - `dataset/` : Gestion des données.
  - `features/` : Définition des caractéristiques.
  - `ingestion/` : Ingestion des données depuis l'API.
  - `labels/` : Étiquettes et cibles.
  - `model/` : Modèles de clustering et analyse.

## Procédure d'installation

1. Cloner le dépôt.
2. Créer un environnement virtuel : `python -m venv venv`
3. Activer l'environnement : `venv\Scripts\activate` (Windows)
4. Installer les dépendances : `pip install -r requirements.txt`

## Configuration API

1. Obtenir un token API depuis Lichess (https://lichess.org/account/oauth/token).
2. Créer un fichier `.env` à la racine du projet.
3. Ajouter la ligne : `LICHESS_API_TOKEN=votre_token_ici`

## Ordre recommandé d'exécution

Exécuter les notebooks dans l'ordre suivant pour reproduire le projet :

1. `berserk_api_test.ipynb` : Vérifier l'accès à l'API.
2. `data_creation.ipynb` : Collecter et préparer les données brutes.
3. `cleaning_preprocess_data.ipynb` : Nettoyer et prétraiter les données.
4. `clustering_kmeans_evaluation.ipynb` : Appliquer le clustering et évaluer les modèles.
5. `full_results_deep_dive.ipynb` : Analyser en profondeur tous les résultats.

## Emplacement des résultats

- Résultats finaux : `analysis_outputs/final_results/`
- Analyse complète : `analysis_outputs/full_results_deep_dive/`

## Lien vers le rapport

Consulter `RapportFinal.pdf` pour une présentation académique complète du projet.

## Limites connues

- Dépendance à la disponibilité de l'API Lichess, qui peut limiter les requêtes.
- Sélection de joueurs limitée aux débutants dans une plage de rating spécifique (1000-1400).
- Potentiel biais dans les données dues à la nature auto-sélectionnée des joueurs sur Lichess.
- Le clustering K-means peut être sensible à l'initialisation et ne capture que des clusters convexes.
- Analyse limitée aux caractéristiques comportementales définies ; d'autres facteurs (psychologiques, externes) ne sont pas inclus.

## Python

Python 3.12 recommandé