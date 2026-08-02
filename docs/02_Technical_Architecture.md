# Architecture Technique

## Objectif

Cette architecture a été conçue afin de reproduire une plateforme de Data Engineering utilisée dans un contexte industriel.

L'objectif est de centraliser les données environnementales provenant de plusieurs sites de production, de les transformer puis de les rendre exploitables au travers d'un Data Warehouse et de tableaux de bord décisionnels.

---

# Vue d'ensemble

Le schéma ci-dessous présente l'architecture globale de la plateforme.

![Architecture](diagrams/architecture.png)

---

# Description des composants

## 1. Helios Industrial Group

L'entreprise est composée de cinq sites industriels spécialisés dans la fabrication de composants destinés aux infrastructures des énergies renouvelables.

Chaque site produit quotidiennement des données relatives à :

- la consommation d'énergie ;
- la consommation d'eau ;
- les déchets ;
- les émissions de CO₂ ;
- les transports ;
- la production ;
- les fournisseurs.

---

## 2. Générateur de données

Le générateur Python simule les exports quotidiens des différents systèmes d'information de l'entreprise.

Il produit automatiquement des fichiers CSV réalistes qui serviront de source au pipeline ETL.

---

## 3. Incoming

Les fichiers générés sont déposés dans le dossier `incoming`.

Ce dossier représente la zone d'arrivée des données avant leur traitement.

---

## 4. Pipeline ETL

Le pipeline ETL est développé en Python.

Il est responsable de :

- lire les fichiers ;
- contrôler leur qualité ;
- transformer les données ;
- charger les différentes bases MySQL.

---

## 5. Validation et contrôle qualité

Avant tout chargement, plusieurs contrôles sont effectués afin de garantir la qualité des données.

Par exemple :

- valeurs manquantes ;
- doublons ;
- formats invalides ;
- cohérence métier.

---

## 6. Base RAW

La base `industrial_raw` conserve une copie fidèle des données d'origine.

Aucune transformation métier n'y est réalisée.

Cette couche garantit la traçabilité des données et permet de rejouer les traitements si nécessaire.

---

## 7. Base Metadata

La base `industrial_metadata` stocke les informations relatives à l'exécution des pipelines.

Elle permet notamment de conserver :

- les journaux d'exécution ;
- les erreurs ;
- le nombre de lignes chargées ;
- les temps de traitement.

---

## 8. Base STAGING

La base `industrial_staging` contient les données nettoyées et préparées avant leur transformation analytique.

Elle constitue l'intermédiaire entre les données brutes et le Data Warehouse.

---

## 9. dbt Core

dbt est utilisé pour transformer les données présentes dans la couche Staging.

Les modèles dbt permettront de construire :

- les dimensions ;
- les tables de faits ;
- les indicateurs métiers.

---

## 10. Data Warehouse

La base `industrial_dw` contient les données prêtes à être analysées.

Elle est optimisée pour le reporting et l'analyse décisionnelle.

---

## 11. Power BI

Power BI interroge exclusivement le Data Warehouse.

Il permet de construire des tableaux de bord interactifs présentant les principaux indicateurs environnementaux.

---

## 12. Rapport PDF

À terme, la plateforme générera automatiquement un rapport environnemental au format PDF.

Ce rapport présentera :

- les principaux KPI ;
- les alertes ;
- les tendances mensuelles ;
- les graphiques issus des données du Data Warehouse.

---

# Choix techniques

Les principaux choix d'architecture sont les suivants :

- séparation des différentes couches de données (RAW, STAGING, Data Warehouse) ;
- utilisation de MySQL comme système de gestion de base de données ;
- transformation des données avec dbt ;
- orchestration des traitements avec Airflow ;
- visualisation avec Power BI.

Cette architecture reproduit une organisation proche de celle utilisée dans des projets professionnels de Data Engineering.

---

# Évolutions futures

Les prochaines étapes du projet seront :

- conception du modèle de données ;
- développement du générateur de données ;
- création des bases MySQL ;
- développement des pipelines ETL ;
- mise en place de dbt ;
- automatisation avec Airflow ;
- création des tableaux de bord Power BI.