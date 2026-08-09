# Génération des données

## Objectif

Cette étape consiste à générer automatiquement les données opérationnelles de l'Industrial Sustainability Data Platform.

Les données sont produites à partir de règles métier afin de simuler l'activité quotidienne des différents sites industriels de Helios Industrial Group.

Cette approche permet d'obtenir un jeu de données réaliste, cohérent et reproductible destiné à alimenter les pipelines ETL, les transformations dbt ainsi que les tableaux de bord Power BI.

---

# Principe général

Les données sont générées automatiquement à l'aide de scripts Python.

Chaque script produit un fichier CSV correspondant à une table de faits de la base de données.

Le processus de génération est le suivant :

Python

↓

Simulation métier

↓

Génération des fichiers CSV

↓

Chargement dans MySQL (ETL)

↓

Transformation avec dbt

↓

Visualisation dans Power BI

---

# Tables générées

Les tables de référence étant déjà renseignées manuellement, seuls les jeux de données opérationnels sont générés automatiquement.

| Table | Génération |
|--------|------------|
| production | Oui |
| energy | Oui |
| water | Oui |
| waste | Oui |
| transport | Oui |

---

# Période de génération

La première version du projet génère les données correspondant à une année complète d'activité.

| Paramètre | Valeur |
|-----------|--------|
| Début | 01/01/2025 |
| Fin | 31/12/2025 |
| Nombre de jours | 365 |

Cette période pourra être facilement modifiée grâce au fichier de configuration Python.

---

# Règles métier

Les données générées ne sont pas entièrement aléatoires.

Elles respectent des règles métier permettant de simuler le fonctionnement d'un groupe industriel.

Les principales règles sont les suivantes :

- chaque site industriel fabrique uniquement les produits qui lui sont associés ;
- les volumes de production varient selon le type de produit ;
- certaines productions sont influencées par la saison ;
- l'activité est réduite le week-end ;
- la consommation d'énergie dépend du niveau de production ;
- la consommation d'eau dépend de l'activité industrielle ;
- les déchets sont proportionnels aux volumes produits ;
- les opérations de transport sont générées à partir des fournisseurs et des transporteurs référencés.

---

# Architecture Python

Les scripts de génération sont organisés de manière modulaire.

```
src/
│
├── api/
│
├── etl/
│
└── generators/
    ├── config.py
    ├── utils.py
    ├── generate_production.py
    ├── generate_energy.py
    ├── generate_water.py
    ├── generate_waste.py
    └── generate_transport.py
```

---

## Pipeline de génération

Le diagramme ci-dessous présente l'organisation des scripts Python ainsi que le chemin parcouru par les données, depuis leur génération jusqu'à leur exploitation dans Power BI.

![Data Generation Pipeline](diagrams/data_generation_pipeline.png)

---

# Description des scripts

## config.py

Centralise l'ensemble des paramètres de génération :

- période de génération ;
- chemins des fichiers ;
- constantes du projet.

---

## utils.py

Contient les fonctions communes utilisées par l'ensemble des générateurs.

Exemples :

- génération des dates ;
- gestion des saisons ;
- calcul des jours de semaine ;
- fonctions utilitaires.

---

## generate_production.py

Génère les données de production quotidienne.

---

## generate_energy.py

Génère les consommations énergétiques des différents sites.

---

## generate_water.py

Génère les consommations d'eau.

---

## generate_waste.py

Génère les déchets produits quotidiennement.

---

## generate_transport.py

Génère les opérations de transport entre les fournisseurs et les sites industriels.

---

# Structure des données

Les fichiers générés sont enregistrés dans le dossier :

```
data/raw/
```

Chaque générateur produit un fichier CSV.

Exemple :

```
production.csv
energy.csv
water.csv
waste.csv
transport.csv
```

Ces fichiers constituent les données brutes utilisées par les pipelines ETL.

---

# Évolutions prévues

La génération des données pourra être enrichie progressivement grâce à des sources externes.

Les évolutions envisagées sont notamment :

- intégration d'une API météo afin d'influencer certains indicateurs ;
- prise en compte des jours fériés ;
- amélioration des modèles de génération ;
- ajout de nouvelles règles métier.

---

# Conclusion

La génération automatique des données constitue une étape essentielle du projet.

Elle permet de produire un volume important de données cohérentes tout en reproduisant le fonctionnement d'un environnement industriel réaliste.

Les fichiers générés serviront de point d'entrée aux prochaines étapes du projet : les pipelines ETL, les transformations dbt, l'orchestration avec Apache Airflow et la création des tableaux de bord Power BI.