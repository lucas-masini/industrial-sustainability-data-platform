# Industrial Sustainability Data Platform

## Présentation

L'Industrial Sustainability Data Platform est un projet personnel de Data Engineering visant à reproduire une plateforme de données utilisée dans un contexte industriel.

Le projet simule l'architecture complète d'une plateforme capable de centraliser, transformer et analyser les données environnementales provenant de plusieurs sites de production.

L'objectif est de construire une solution proche des standards utilisés en entreprise, depuis la génération des données jusqu'à leur exploitation dans Power BI.

---

# Objectifs

Cette plateforme permet de :

- centraliser les données provenant de plusieurs usines ;
- automatiser leur ingestion ;
- garantir leur qualité ;
- transformer les données en indicateurs métiers ;
- alimenter un Data Warehouse ;
- produire des tableaux de bord Power BI ;
- automatiser l'ensemble du pipeline de données.

---

# Contexte

Helios Industrial Group est une entreprise industrielle fictive spécialisée dans la fabrication de composants destinés aux infrastructures des énergies renouvelables.

Le groupe possède cinq sites de production répartis en France.

Chaque jour, ces sites génèrent des données concernant :

- la production ;
- la consommation d'énergie ;
- la consommation d'eau ;
- les déchets ;
- les émissions de CO₂ ;
- les transports ;
- les fournisseurs.

Ces informations sont produites par différents systèmes et doivent être centralisées afin de permettre un pilotage fiable de la performance environnementale.

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

# Principaux KPI

Le projet permettra notamment de suivre :

- consommation énergétique par site ;
- consommation énergétique par produit ;
- consommation d'eau ;
- émissions de CO₂ ;
- taux de recyclage ;
- production industrielle ;
- performance des fournisseurs ;
- comparaison des performances entre les sites.

---

# Roadmap

- [x] Analyse métier
- [x] Architecture technique
- [ ] Modélisation des données
- [ ] Générateur de données
- [ ] Base de données MySQL
- [ ] Pipelines ETL
- [ ] Data Warehouse (dbt)
- [ ] Dashboard Power BI
- [ ] Airflow
- [ ] Docker
- [ ] GitHub Actions