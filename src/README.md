# Dossier src/

Ce dossier contient le code source modulaire du projet de clustering des joueurs d'�checs Lichess. Il est organis� en sous-modules th�matiques pour faciliter la maintenance et la r�utilisabilit�.

## Structure g�n�rale

- __init__.py : Fichier d'initialisation vide du module src.
- cleaning_and_preprocessing/ : Modules pour le nettoyage et le pr�traitement des donn�es.
- dataset/ : Gestion des datasets, IO et s�lection des joueurs.
- features/ : D�finition et calcul des caract�ristiques (features) des joueurs et parties.
- ingestion/ : Ingestion des donn�es depuis l'API Lichess.
- labels/ : Calcul des �tiquettes de progression.
- model/ : Mod�les de clustering et analyse.

## D�tail par dossier

### cleaning_and_preprocessing/

- __init__.py : Initialisation du sous-module.
- data_cleaning.py : Effectue une analyse univari�e des features, identifie les features � transformer, calcule les corr�lations avec les targets de progression, visualise les relations, d�tecte les paires de features fortement corr�l�es, et construit un r�sum� des d�cisions de s�lection et transformation.
- preprocessing.py : Construit la matrice de clustering X � partir des features s�lectionn�es, impute les valeurs manquantes, applique les transformations d�cid�es, standardise les features, et construit un r�sum� de l'�tape de pr�processing. Inclut des v�rifications pour s'assurer que les transformations ont l'effet escompt� sur la skewness.

### dataset/

- __init__.py : Initialisation du sous-module.
- build_final_dataset.py : Construit le dataset final en combinant les features des joueurs et les labels de progression, en s'assurant que les donn�es sont align�es correctement sur les identifiants des joueurs. Le r�sultat est un DataFrame pr�t pour l'analyse de clustering et l'�valuation.
- io.py : G�re l'IO des donn�es, notamment la sauvegarde et le chargement des parties brutes par joueur, ainsi que la construction du DataFrame player_games_raw � partir du dump brut API.
- select_players.py : S�lectionne les joueurs retenus pour l'�tude � partir du DataFrame player_games brut.

### features/

- __init__.py : Initialisation du sous-module.
- day_features.py : Ajoute des features 'quotidiennes' au niveau partie (par exemple, nombre de parties par jour, etc.).
- features_groups.py : Regroupe les features par th�me, liste celles retenues pour le clustering, celles �cart�es, et celles gard�es pour l'analyse.
- game_features.py : Regroupe toutes les fonctions pour les features temporelles des parties (utilise les autres modules de features).
- player_features.py : Calcule les features du joueur, d�compos�es en 7 cat�gories : style de jeu (mean_ply_count, openings), comportement en fin de partie, streaks, rythme, sessions, jours, semaines.
- session_features.py : Ajoute des features de session aux donn�es de parties (identification des sessions par seuil de temps, features par session).
- 	emporal_features.py : D�finit les features partie induisant une notion temporelle, notamment le calcul de streaks cumulatifs (win/lose streaks).
- week_features.py : Ajoute des features 'hebdomadaires' au niveau partie (par exemple, nombre de parties par semaine, etc.).

### ingestion/

- __init__.py : Initialisation du sous-module.
- build_player_games.py : Construit la table player_games � partir d'une liste de parties brutes Berserk.
- flatten_games.py : Convertit une partie brute en une structure plate (dictionnaire avec champs aplatis).
- opening.py : G�re la normalisation du code ECO et le mapping vers la famille d'ouverture.
- player_sampling.py : Construit le pool de joueurs candidats via une expansion � partir de seeds et un pr�filtrage l�ger.
- player_view.py : Convertit une partie applatie en une partie du point de vue d'un joueur (r�sultat, couleur, etc.).

### labels/

- __init__.py : Initialisation du sous-module.
- progression.py : D�finit plusieurs m�triques de progression, principalement elo_slope_per_game (pente de l'ELO par partie).

### model/

- cluster_analyzing.py : Analyse les clusters obtenus : attache les labels au DataFrame, r�sume les caract�ristiques de chaque cluster, calcule des m�triques de progression pour �valuer la s�paration et l'homog�n�it�.
- kmeans.py : Ex�cute KMeans avec plusieurs seeds pour chaque k, compare les r�sultats en termes de silhouette score, inertia, et taille des clusters. Organise les r�sultats dans un DataFrame.
- model_evaluation.py : �value les diff�rents mod�les de clustering (diff�rents feature sets, k, seeds).
