# Industrial Sustainability Data Platform

> Plateforme de Data Engineering permettant de centraliser, transformer et analyser les données environnementales d'un groupe industriel.

---

# Présentation

L'Industrial Sustainability Data Platform est un projet de Data Engineering conçu pour reproduire une plateforme de données utilisée dans un contexte industriel réel.

L'objectif est de centraliser automatiquement les données provenant de plusieurs sites de production afin de suivre leurs performances environnementales.

Cette plateforme permet de collecter, nettoyer, transformer et stocker les données avant de les restituer sous forme de tableaux de bord et de rapports décisionnels.

Le projet est développé dans une logique de production afin de reproduire les différentes étapes d'une architecture Data moderne.

---

# Contexte métier

EcoManufacture est une entreprise industrielle fictive possédant cinq usines de production réparties en Europe.

Chaque jour, ces usines génèrent de nombreuses données concernant :

- la consommation d'énergie ;
- la consommation d'eau ;
- la production ;
- les déchets ;
- les émissions de CO₂ ;
- les transports ;
- les fournisseurs.

Aujourd'hui, ces informations sont réparties dans différents fichiers et systèmes, ce qui rend leur exploitation complexe.

L'objectif de cette plateforme est de centraliser ces données afin de fournir une vision globale de la performance environnementale de l'entreprise.

---

# Objectifs du projet

Ce projet a pour objectif de concevoir une plateforme complète de Data Engineering capable de :

- centraliser les données de plusieurs usines ;
- automatiser leur ingestion ;
- garantir leur qualité ;
- transformer les données en indicateurs exploitables ;
- alimenter un Data Warehouse ;
- produire des tableaux de bord Power BI ;
- simuler une architecture utilisée en entreprise.

---

# Fonctionnalités

À terme, la plateforme permettra notamment de :

- générer des données réalistes ;
- ingérer automatiquement des fichiers quotidiens ;
- contrôler la qualité des données ;
- alimenter plusieurs couches de stockage (Raw, Staging, Data Warehouse) ;
- transformer les données avec dbt ;
- orchestrer les traitements avec Airflow ;
- produire des KPI environnementaux ;
- générer des rapports automatisés.

---

# Stack technique

- Python
- MySQL
- dbt Core
- Apache Airflow
- Docker
- Power BI Desktop
- Git
- GitHub
- GitHub Actions

---

# Architecture

L'architecture complète du projet sera disponible dans la documentation technique.

```
Usines
    │
    ▼
Générateur de données
    │
    ▼
Incoming
    │
    ▼
ETL Python
    │
    ▼
RAW
    │
    ▼
STAGING
    │
    ▼
dbt
    │
    ▼
Data Warehouse
    │
    ▼
Power BI
```

---

# Roadmap

- Analyse métier
- Architecture technique
- Génération des données
- Base de données MySQL
- Développement des pipelines ETL
- Transformation avec dbt
- Dashboard Power BI
- Orchestration avec Airflow
- Dockerisation
- Tests
- CI/CD
- Documentation

---

# Documentation

La documentation complète du projet sera disponible dans le dossier `docs`.

Elle décrira notamment :

- l'analyse métier ;
- l'architecture ;
- le modèle de données ;
- les pipelines ETL ;
- les transformations dbt ;
- le déploiement.

---

# Auteur

Projet réalisé par Lucas Masini dans le cadre d'un projet personnel de Data Engineering.
