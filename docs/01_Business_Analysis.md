# Analyse métier

## Contexte

Helios Industrial Group est un groupe industriel européen spécialisé dans la fabrication de composants destinés aux infrastructures des énergies renouvelables.

L'entreprise possède cinq sites de production répartis sur le territoire français.

Chaque site génère quotidiennement plusieurs milliers de données relatives à la production industrielle et à la performance environnementale.

Ces données sont actuellement réparties dans différents fichiers (CSV, Excel...) et ne permettent pas un pilotage global de l'activité.

Le projet consiste à concevoir une plateforme Data Engineering capable de centraliser automatiquement ces informations afin de produire des indicateurs fiables pour les différents métiers de l'entreprise.

---

# Les utilisateurs

## Responsable Développement Durable

Suivi des indicateurs environnementaux :

- consommation énergétique ;
- consommation d'eau ;
- émissions de CO₂ ;
- déchets ;
- taux de recyclage.

---

## Directeur Industriel

Pilotage des performances de production :

- production ;
- rendement ;
- coûts énergétiques ;
- consommation par produit.

---

## Responsable Logistique

Suivi :

- transports ;
- fournisseurs ;
- émissions liées au transport.

---

## Direction Générale

Vision globale de l'entreprise :

- comparaison des sites ;
- évolution des KPI ;
- performance environnementale ;
- aide à la décision.

---

# Questions métier

La plateforme devra notamment répondre aux questions suivantes.

## Énergie

- Quelle usine consomme le plus d'énergie ?
- Quelle est la consommation par produit fabriqué ?
- Comment évolue la consommation énergétique au fil du temps ?

## Eau

- Quelle usine consomme le plus d'eau ?
- Quelle est la consommation d'eau par produit ?

## Déchets

- Quel site produit le plus de déchets ?
- Quel est le taux global de recyclage ?

## CO₂

- Quelle usine génère le plus d'émissions ?
- Quel est l'impact du transport ?

## Production

- Quelle est la production de chaque site ?
- Quel site présente les meilleures performances ?

## Fournisseurs

- Quel pourcentage est certifié ISO 14001 ?
- Quels fournisseurs présentent le meilleur score environnemental ?

---

# Hypothèses

Le projet repose sur les hypothèses suivantes :

- chaque usine transmet ses données quotidiennement ;
- les données sont reçues au format CSV ;
- les KPI sont recalculés chaque jour ;
- les tableaux de bord sont mis à jour après chaque exécution du pipeline.

---

# Sources de données

Les principales données manipulées sont :

- sites industriels ;
- production ;
- énergie ;
- eau ;
- déchets ;
- transports ;
- fournisseurs.

Ces données alimenteront l'ensemble du pipeline de Data Engineering.