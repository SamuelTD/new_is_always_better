

 
# 🎬 New is Always Better – Outil d’aide à la programmation cinématographique

## 📑 Sommaire

1. [Introduction](#introduction)
2. [📦 Scraping](#scraping)
3. [📊 Modélisation](#-modélisation)
   - [🔬 Approche retenue](#-approche-retenue)
   - [⚙️ Entraînement et validation](#-entraînement-et-validation)
4. [🚀 API de Prédiction](#api-de-prédiction-daffluence-pour-films)
   - [Aperçu](#aperçu)
   - [Architecture](#architecture)
   - [Installation](#installation)
   - [Utilisation](#utilisation)
   - [Modèle de données](#modèle-de-données)
   - [Personnalisation](#personnalisation)
5. [🖥️ Django](#django)

## Introduction

New is Always Better est un projet de data science et développement web visant à accompagner le gérant d’un cinéma indépendant dans sa prise de décision hebdomadaire concernant la programmation de films. L’objectif principal est de prédire la fréquentation des films en première semaine de sortie, afin de sélectionner les deux œuvres les plus prometteuses à projeter dans les deux salles du cinéma.

Le projet combine machine learning, scraping automatisé, développement d’API et application web dans un environnement cloud, et s’inscrit dans une méthodologie agile avec des livrables répartis sur 4 sprints.

Grâce à cet outil, le gérant peut maximiser son chiffre d’affaires en allouant les films les plus attractifs aux salles en fonction de leur capacité, tout en réduisant le temps consacré à la veille manuelle et aux paris risqués sur les nouveautés.
Structure du projet GitHub

Le projet est organisé en quatre grands dossiers, chacun correspondant à une étape ou composante clé du pipeline de production et disposant de son propre requirements.txt pour gérer les dépendances spécifiques.

## 📦 scrapping

Ce dossier contient l’ensemble des scripts dédiés à la collecte automatisée de données à partir de sources telles qu’Allociné, JB Box Office et le CNC. Plusieurs sous-dossiers (allo_cine, jb_boxoffice, cnc, imdb) permettent de structurer le scraping selon la source.

## 📊 modelisation

Contient plusieurs notebooks Jupyter dédiés à la préparation des données (cleaning), à l’analyse exploratoire (EDA), et à la modélisation prédictive (régression).

## 🚀 api

Ce dossier contient l’API développée avec FastAPI qui expose le modèle de machine learning sous forme de service REST. Cette API est consommée par l’application Django. Le dossier inclut également un fichier requirements.txt spécifique et un script deploy.sh pour faciliter le déploiement du service.

## 🖥️ django

C’est l’application web front-end, développée avec Django et stylisée avec TailwindCSS. Elle permet au gérant du cinéma de visualiser les prédictions, consulter les estimations de chiffre d’affaires, suivre l’historique des performances et accéder aux métriques. Le dossier contient aussi un requirements.txt ainsi qu’un deploy.sh pour automatiser le déploiement.

# Scraping

# 🧠 Modélisation

La partie modélisation constitue le cœur du projet, avec pour objectif de prédire le nombre d’entrées en salle d’un film dès sa première semaine d’exploitation. Plusieurs approches ont été explorées et comparées afin de répondre au mieux aux besoins spécifiques du client : maximiser l’occupation des salles tout en tenant compte des contraintes de capacité et de rentabilité.

Le modèle final est une architecture hybride en deux étapes :

Prédiction du box-office national :
Un modèle SARIMA (Seasonal AutoRegressive Integrated Moving Average) a été utilisé pour modéliser les séries temporelles du box-office national hebdomadaire. Il permet de produire une estimation fiable du nombre d'entrée tout cinéma confondue en France.

La prédiction locale à partir de la prédiction nationale
La prédiction SARIMA est ensuite intégrée comme une feature dans un modèle de régression basé sur XGBoost, entraîné pour estimer plus précisément le nombre d’entrées potentielles dans le cinéma concerné (1/2000e du national). Ce modèle prend également en compte des variables explicatives comme :

Les genres du film

Sa nationalité

Le casting et le réalisateur

Le studio

Les langues disponibles

La longueur ...



 Entraînement et validation

L’entraînement du modèle XGBoost repose sur des splits train/test personnalisés afin de respecter les temporalités réelles et éviter tout target leakage.

Une métrique de performance personnalisée a été définie afin de pénaliser davantage les erreurs sur les films à fort potentiel (essentiel pour maximiser les recettes hebdomadaires du cinéma).

Un travail approfondi de feature engineering a été réalisé pour enrichir les données, y compris l’ajout de variables exogènes issues du scraping web (Twitter, IMDb, etc.).

# API de Prédiction d'Affluence pour Films

Cette API permet de prédire l'affluence de nouveaux films en se basant sur diverses caractéristiques comme les acteurs, les réalisateurs, le genre, etc. Elle utilise un modèle préentraîné stocké dans un fichier pkl pour faire des prédictions.

## Aperçu

L'API de prédiction d'affluence pour films est construite avec FastAPI et permet de prédire l'affluence de nouveaux films en fonction de leurs caractéristiques. L'API prend en entrée des métadonnées de films comme les acteurs, la date de sortie, les réalisateurs, etc., et retourne une prédiction d'affluence basée sur un modèle préentraîné.

## Architecture

L'API est construite avec les technologies suivantes :

- **FastAPI** : Framework API moderne et performant
- **Pandas** : Manipulation des données
- **Scikit-learn** : Pour le modèle de prédiction
- **Docker** : Containerisation de l'application

Les fichiers de données (acteurs et affluence nationale) sont intégrés directement dans le conteneur Docker, ce qui élimine la nécessité d'une connexion à Azure ML Studio.

## Installation

### Prérequis

- Python 3.10+
- Docker (optionnel, mais recommandé)

### Installation locale

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/api-prediction-film.git
   cd api-prediction-film
   ```

2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Lancer l'API :
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Installation avec Docker

1. Construire l'image Docker :
   ```bash
   docker build -t api-prediction-film .
   ```

2. Exécuter le conteneur :
   ```bash
   docker run -p 8000:8000 api-prediction-film
   ```

## Utilisation

### Endpoint de prédiction

L'API expose un endpoint `/predict` qui accepte des requêtes POST contenant une liste de films.

#### Format de la requête

```json
{
  "films": [
    {
      "actors": ["Monica Bellucci", "Vincent Cassel"],
      "date": "2023-05-10T00:00:00",
      "directors": ["Gaspar Noé"],
      "editor": "Carlotta Films",
      "genre": ["Drame", "Thriller"],
      "langage": ["Anglais", "Francais", "Italien", "Espagnol"],
      "length": 90.0,
      "nationality": ["France"],
      "title": "Film Exemple"
    },
    {
      "actors": ["Brad Pitt", "Marion Cotillard"],
      "date": "2023-06-15T00:00:00",
      "directors": ["Quentin Tarantino"],
      "editor": "Sony Pictures",
      "genre": ["Action", "Guerre"],
      "langage": ["Anglais"],
      "length": 120.0,
      "nationality": ["USA"],
      "title": "Autre Film"
    }
  ]
}
```

#### Format de la réponse

```json
{
  "predictions": [
    {
      "title": "Film Exemple",
      "predicted_affluence": 1234567.89,
      "shap_values": shap en binaire,
      "predicted_affluence_2": 1334567.89,
      "shap_values_2": shap en binaire
    },
    {
      "title": "Autre Film",
      "predicted_affluence": 9876543.21,
      "shap_values": shap en binaire,
      "predicted_affluence_2": 1334567.89,
      "shap_values_2": shap en binaire
    }
  ]
}
```

### Documentation de l'API

Une documentation interactive de l'API est disponible aux URLs suivantes après le démarrage du serveur :

- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## Structure du projet

```
├── app/
│   ├── __init__.py
│   ├── main.py           # Point d'entrée de l'API
│   ├── schemas.py        # Définition des modèles de données (Pydantic)
│   ├── predict.py        # Service de prédiction
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_processing.py   # Transformation des données
│   │   └── azure_ml.py        # Gestion des fichiers de données locaux(il faudra changer le nom)
├── data/
│   ├── actors_data.parquet      # Données sur les acteurs
│   └── national_affluence_data.parquet  # Données d'affluence nationale
├── model/
│   └── model.pkl         # Modèle de prédiction
├── requirements.txt
└── Dockerfile
```

## Modèle de données

### Entrée (FilmInput)

- `actors` : Liste des acteurs du film
- `date` : Date de sortie du film
- `directors` : Liste des réalisateurs
- `editor` : Éditeur/distributeur du film
- `genre` : Liste des genres du film
- `langage` : Liste des langues du film
- `length` : Durée du film en minutes
- `nationality` : Liste des nationalités de production
- `title` : Titre du film (optionnel)

### Transformation des données

L'API transforme les données d'entrée en caractéristiques utilisées par le modèle.

## Personnalisation

### Modifier le modèle de prédiction

Pour utiliser un modèle différent, remplacez le fichier `model/best_model.pkl` par votre propre modèle. Assurez-vous que le nouveau modèle accepte les mêmes caractéristiques d'entrée.
On peut également choisir un deuxième model. `model/best_model_tuned.pkl`

### Mise à jour des données

Pour mettre à jour les données des acteurs ou d'affluence nationale, remplacez les fichiers parquet correspondants dans le dossier `data/` :

1. `data/actors_data.parquet` : Données sur les acteurs
2. `data/national_affluence_data.parquet` : Données d'affluence nationale

# Django
message.txt
11 Ko