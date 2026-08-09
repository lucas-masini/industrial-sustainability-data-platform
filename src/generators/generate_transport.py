"""
Génère les données quotidiennes de transport pour
Helios Industrial Group.

Les transports représentent les livraisons réalisées entre
les fournisseurs et les cinq sites industriels du groupe.

Les fournisseurs et les entreprises de transport sont des
tables de référence. Le fichier généré utilise donc leurs
identifiants comme clés étrangères.

Règles métier :
    - aucun transport le dimanche ;
    - activité réduite le samedi ;
    - chaque transport est associé à un fournisseur ;
    - chaque transport est associé à une entreprise de transport ;
    - chaque transport est destiné à un site ;
    - la distance dépend du fournisseur et du site ;
    - le poids transporté dépend de l'activité industrielle ;
    - les émissions dépendent de la distance, du poids et du mode ;
    - le coût dépend de la distance, du poids et du mode ;
    - les données sont reproductibles grâce à une graine fixe.

Sortie :
    data/raw/transport.csv
"""

from __future__ import annotations

import random
from datetime import date
from pathlib import Path

import pandas as pd

from .config import END_DATE, RAW_DATA_DIR, START_DATE
from .utils import (
    generate_dates,
    is_sunday,
    set_random_seed,
)


# ==========================================================
# RÉFÉRENCES
# ==========================================================

# Les IDs correspondent directement aux tables de référence
# supplier et transport_company.

SUPPLIER_IDS = list(range(1, 9))

TRANSPORT_COMPANY_IDS = list(range(1, 6))

SITE_IDS = list(range(1, 6))


# ==========================================================
# DISTANCES FOURNISSEUR -> SITE
# ==========================================================

# Distances synthétiques cohérentes avec les pays d'origine
# des fournisseurs et les villes des sites industriels.
#
# Les distances sont exprimées en kilomètres.
#
# Structure :
#     fournisseur -> site -> distance moyenne

SUPPLIER_SITE_DISTANCES = {
    # SUP-001 : France
    1: {
        1: 470,
        2: 540,
        3: 300,
        4: 720,
        5: 620,
    },

    # SUP-002 : Allemagne
    2: {
        1: 720,
        2: 980,
        3: 1050,
        4: 1050,
        5: 650,
    },

    # SUP-003 : Espagne
    3: {
        1: 900,
        2: 620,
        3: 450,
        4: 900,
        5: 1150,
    },

    # SUP-004 : Suède
    4: {
        1: 1850,
        2: 2050,
        3: 2200,
        4: 1950,
        5: 1700,
    },

    # SUP-005 : Italie
    5: {
        1: 900,
        2: 1150,
        3: 950,
        4: 1300,
        5: 1050,
    },

    # SUP-006 : France
    6: {
        1: 470,
        2: 540,
        3: 300,
        4: 720,
        5: 620,
    },

    # SUP-007 : Belgique
    7: {
        1: 750,
        2: 950,
        3: 1050,
        4: 650,
        5: 850,
    },

    # SUP-008 : Danemark
    8: {
        1: 1450,
        2: 1650,
        3: 1800,
        4: 1350,
        5: 1250,
    },
}


# ==========================================================
# CARACTÉRISTIQUES DES TRANSPORTEURS
# ==========================================================

# Les IDs correspondent à la table transport_company :
#
# 1 = Green Logistics France      -> Road
# 2 = Euro Freight Solutions      -> Road
# 3 = Nordic Transport Group      -> Road
# 4 = Eco Rail Cargo              -> Rail
# 5 = Blue Shipping Lines         -> Maritime
#
# Les coefficients représentent des hypothèses synthétiques
# utilisées uniquement pour générer les données.

TRANSPORT_COMPANY_RULES = {
    1: {
        "transport_type": "Road",
        "co2_factor": 0.085,
        "cost_per_km": 1.15,
        "cost_per_kg": 0.012,
    },
    2: {
        "transport_type": "Road",
        "co2_factor": 0.080,
        "cost_per_km": 1.10,
        "cost_per_kg": 0.011,
    },
    3: {
        "transport_type": "Road",
        "co2_factor": 0.075,
        "cost_per_km": 1.05,
        "cost_per_kg": 0.010,
    },
    4: {
        "transport_type": "Rail",
        "co2_factor": 0.025,
        "cost_per_km": 0.85,
        "cost_per_kg": 0.008,
    },
    5: {
        "transport_type": "Maritime",
        "co2_factor": 0.015,
        "cost_per_km": 0.65,
        "cost_per_kg": 0.006,
    },
}


# ==========================================================
# FACTEURS DE TRANSPORT PAR FOURNISSEUR
# ==========================================================

# Certains fournisseurs sont plus naturellement associés
# à certains modes de transport selon leur localisation.
#
# Les listes contiennent uniquement des IDs de la table
# transport_company.

PREFERRED_TRANSPORT_COMPANIES = {
    1: [1, 2, 4],
    2: [2, 3, 4],
    3: [1, 2, 5],
    4: [3, 5],
    5: [1, 2, 4],
    6: [1, 2, 4],
    7: [1, 2, 4],
    8: [3, 5],
}


# ==========================================================
# INTENSITÉ LOGISTIQUE PAR SITE
# ==========================================================

# Facteur permettant d'estimer le poids des marchandises
# entrantes à partir du volume de production.
#
# Les produits des différents sites n'ont pas la même
# intensité matière.

SITE_INPUT_WEIGHT_FACTORS = {
    1: 2.20,
    2: 4.50,
    3: 1.80,
    4: 3.20,
    5: 1.60,
}


# ==========================================================
# LECTURE DE LA PRODUCTION
# ==========================================================

def load_production_data() -> pd.DataFrame:
    """
    Charge les données de production existantes.

    Returns
    -------
    pandas.DataFrame
        Données de production.

    Raises
    ------
    FileNotFoundError
        Si production.csv est introuvable.

    ValueError
        Si des colonnes nécessaires sont absentes.
    """

    production_path = RAW_DATA_DIR / "production.csv"

    if not production_path.exists():
        raise FileNotFoundError(
            "Le fichier production.csv est introuvable. "
            "Générez d'abord les données de production."
        )

    production_df = pd.read_csv(
        production_path,
        parse_dates=["production_date"],
    )

    required_columns = {
        "site_id",
        "production_date",
        "quantity_produced",
    }

    missing_columns = (
        required_columns
        - set(production_df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colonnes manquantes dans production.csv : "
            f"{sorted(missing_columns)}"
        )

    return production_df


# ==========================================================
# AGRÉGATION DE LA PRODUCTION
# ==========================================================

def aggregate_production_by_site_and_date(
    production_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrège la production totale par site et par jour.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données de production détaillées.

    Returns
    -------
    pandas.DataFrame
        Production totale par site et par date.
    """

    production_summary = (
        production_df
        .groupby(
            ["site_id", "production_date"],
            as_index=False,
        )["quantity_produced"]
        .sum()
        .rename(
            columns={
                "production_date": "transport_date",
                "quantity_produced": (
                    "total_quantity_produced"
                ),
            }
        )
    )

    return production_summary


# ==========================================================
# SÉLECTION DU TRANSPORTEUR
# ==========================================================

def select_transport_company(
    supplier_id: int,
) -> int:
    """
    Sélectionne une entreprise de transport adaptée
    au fournisseur.

    Le choix est effectué uniquement parmi les transporteurs
    présents dans la table de référence.

    Parameters
    ----------
    supplier_id : int
        Identifiant du fournisseur.

    Returns
    -------
    int
        Identifiant du transporteur sélectionné.
    """

    preferred_companies = (
        PREFERRED_TRANSPORT_COMPANIES[
            supplier_id
        ]
    )

    return random.choice(
        preferred_companies
    )


# ==========================================================
# CALCUL DE LA DISTANCE
# ==========================================================

def calculate_distance(
    supplier_id: int,
    site_id: int,
) -> float:
    """
    Calcule une distance de transport à partir de la distance
    moyenne fournisseur/site et d'une légère variation.

    Parameters
    ----------
    supplier_id : int
        Identifiant du fournisseur.

    site_id : int
        Identifiant du site.

    Returns
    -------
    float
        Distance en kilomètres.
    """

    base_distance = SUPPLIER_SITE_DISTANCES[
        supplier_id
    ][site_id]

    variation = random.uniform(
        0.95,
        1.05,
    )

    return round(
        base_distance * variation,
        2,
    )


# ==========================================================
# CALCUL DU POIDS TRANSPORTÉ
# ==========================================================

def calculate_transported_weight(
    production_quantity: float,
    site_id: int,
    current_date: date,
) -> float:
    """
    Calcule le poids transporté à partir de l'activité
    industrielle du site.

    Le poids est réparti entre les différents fournisseurs
    qui alimentent le site.

    Parameters
    ----------
    production_quantity : float
        Production totale du site pour la journée.

    site_id : int
        Identifiant du site.

    current_date : date
        Date du transport.

    Returns
    -------
    float
        Poids transporté en kilogrammes.
    """

    input_factor = SITE_INPUT_WEIGHT_FACTORS[
        site_id
    ]

    # Les huit fournisseurs se partagent les besoins
    # d'approvisionnement du site.

    supplier_share = 1 / len(
        SUPPLIER_IDS
    )

    random_variation = random.uniform(
        0.90,
        1.10,
    )

    weight = (
        production_quantity
        * input_factor
        * supplier_share
        * random_variation
    )

    # Le samedi correspond à 60 % de l'activité normale.

    if current_date.weekday() == 5:
        weight *= 0.60

    return round(
        max(weight, 1.0),
        2,
    )


# ==========================================================
# CALCUL DES ÉMISSIONS
# ==========================================================

def calculate_co2_emissions(
    distance_km: float,
    transported_weight_kg: float,
    transport_company_id: int,
) -> float:
    """
    Calcule les émissions de CO₂ du transport.

    Les émissions dépendent :
        - de la distance ;
        - du poids transporté ;
        - du mode de transport.

    Parameters
    ----------
    distance_km : float
        Distance parcourue.

    transported_weight_kg : float
        Poids transporté.

    transport_company_id : int
        Identifiant du transporteur.

    Returns
    -------
    float
        Émissions de CO₂ en kilogrammes.
    """

    company_rule = TRANSPORT_COMPANY_RULES[
        transport_company_id
    ]

    co2_factor = company_rule[
        "co2_factor"
    ]

    emissions = (
        distance_km
        * transported_weight_kg
        / 1000
        * co2_factor
    )

    # Petite variation permettant d'éviter des valeurs
    # totalement déterministes.

    emissions *= random.uniform(
        0.95,
        1.05,
    )

    return round(
        max(emissions, 0.01),
        2,
    )


# ==========================================================
# CALCUL DU COÛT
# ==========================================================

def calculate_transport_cost(
    distance_km: float,
    transported_weight_kg: float,
    transport_company_id: int,
) -> float:
    """
    Calcule le coût du transport.

    Le coût dépend :
        - de la distance ;
        - du poids transporté ;
        - du transporteur.

    Parameters
    ----------
    distance_km : float
        Distance parcourue.

    transported_weight_kg : float
        Poids transporté.

    transport_company_id : int
        Identifiant du transporteur.

    Returns
    -------
    float
        Coût du transport en euros.
    """

    company_rule = TRANSPORT_COMPANY_RULES[
        transport_company_id
    ]

    cost_per_km = company_rule[
        "cost_per_km"
    ]

    cost_per_kg = company_rule[
        "cost_per_kg"
    ]

    cost = (
        distance_km
        * cost_per_km
        + transported_weight_kg
        * cost_per_kg
    )

    cost *= random.uniform(
        0.97,
        1.03,
    )

    return round(
        max(cost, 0.01),
        2,
    )


# ==========================================================
# GÉNÉRATION DU JEU DE DONNÉES
# ==========================================================

def generate_transport_data(
    production_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Génère les opérations quotidiennes de transport.

    Chaque fournisseur réalise une livraison vers chacun
    des cinq sites pendant chaque journée travaillée.

    Les dimanches sont exclus.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données de production.

    Returns
    -------
    pandas.DataFrame
        Données de transport générées.
    """

    production_summary = (
        aggregate_production_by_site_and_date(
            production_df
        )
    )

    rows: list[dict] = []

    transport_id = 1

    dates = generate_dates(
        START_DATE,
        END_DATE,
    )

    for current_date in dates:

        # Aucun transport le dimanche.
        if is_sunday(current_date):
            continue

        for site_id in SITE_IDS:

            site_production = production_summary[
                (
                    production_summary["site_id"]
                    == site_id
                )
                & (
                    production_summary["transport_date"]
                    == pd.Timestamp(current_date)
                )
            ]

            if site_production.empty:
                continue

            production_quantity = float(
                site_production.iloc[0][
                    "total_quantity_produced"
                ]
            )

            for supplier_id in SUPPLIER_IDS:

                transport_company_id = (
                    select_transport_company(
                        supplier_id
                    )
                )

                distance_km = calculate_distance(
                    supplier_id,
                    site_id,
                )

                transported_weight_kg = (
                    calculate_transported_weight(
                        production_quantity,
                        site_id,
                        current_date,
                    )
                )

                co2_emissions_kg = (
                    calculate_co2_emissions(
                        distance_km,
                        transported_weight_kg,
                        transport_company_id,
                    )
                )

                transport_cost = (
                    calculate_transport_cost(
                        distance_km,
                        transported_weight_kg,
                        transport_company_id,
                    )
                )

                rows.append(
                    {
                        "supplier_id": supplier_id,
                        "transport_company_id": (
                            transport_company_id
                        ),
                        "site_id": site_id,
                        "transport_date": current_date,
                        "distance_km": distance_km,
                        "co2_emissions_kg": (
                            co2_emissions_kg
                        ),
                        "transport_cost": (
                            transport_cost
                        ),
                        "transported_weight_kg": (
                            transported_weight_kg
                        ),
                    }
                )

                transport_id += 1

    return pd.DataFrame(rows)


# ==========================================================
# VALIDATION
# ==========================================================

def validate_transport_data(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie la conformité du jeu de données de transport.

    Parameters
    ----------
    df : pandas.DataFrame
        Données de transport.

    Raises
    ------
    ValueError
        Lorsqu'une règle métier ou une contrainte de qualité
        n'est pas respectée.
    """

    required_columns = {
        "supplier_id",
        "transport_company_id",
        "site_id",
        "transport_date",
        "distance_km",
        "co2_emissions_kg",
        "transport_cost",
        "transported_weight_kg",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Colonnes manquantes : "
            f"{sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError(
            "Le jeu de données de transport est vide."
        )

    # ======================================================
    # VALEURS NULL
    # ======================================================

    for column in required_columns:

        if df[column].isna().any():
            raise ValueError(
                f"La colonne {column} contient des valeurs NULL."
            )

    # ======================================================
    # IDENTIFIANTS
    # ======================================================

    if not set(
        df["supplier_id"]
    ).issubset(set(SUPPLIER_IDS)):
        raise ValueError(
            "Le fichier contient des supplier_id inconnus."
        )

    if not set(
        df["transport_company_id"]
    ).issubset(
        set(TRANSPORT_COMPANY_IDS)
    ):
        raise ValueError(
            "Le fichier contient des "
            "transport_company_id inconnus."
        )

    if not set(
        df["site_id"]
    ).issubset(set(SITE_IDS)):
        raise ValueError(
            "Le fichier contient des site_id inconnus."
        )

    # ======================================================
    # VALEURS NUMÉRIQUES
    # ======================================================

    if (
        df["distance_km"] <= 0
    ).any():
        raise ValueError(
            "Les distances doivent être strictement positives."
        )

    if (
        df["co2_emissions_kg"] <= 0
    ).any():
        raise ValueError(
            "Les émissions de CO₂ doivent être strictement positives."
        )

    if (
        df["transport_cost"] <= 0
    ).any():
        raise ValueError(
            "Les coûts de transport doivent être strictement positifs."
        )

    if (
        df["transported_weight_kg"] <= 0
    ).any():
        raise ValueError(
            "Les poids transportés doivent être "
            "strictement positifs."
        )

    # ======================================================
    # DATES
    # ======================================================

    dates = pd.to_datetime(
        df["transport_date"]
    )

    min_date = dates.min().date()
    max_date = dates.max().date()

    if min_date != START_DATE:
        raise ValueError(
            f"La première date est incorrecte : {min_date}"
        )

    if max_date != END_DATE:
        raise ValueError(
            f"La dernière date est incorrecte : {max_date}"
        )

    if dates.dt.dayofweek.eq(6).any():
        raise ValueError(
            "Le fichier contient des transports le dimanche."
        )

    # ======================================================
    # DOUBLONS
    # ======================================================

    duplicates = df.duplicated(
        subset=[
            "supplier_id",
            "site_id",
            "transport_date",
        ]
    )

    if duplicates.any():
        raise ValueError(
            "Des doublons existent pour une combinaison "
            "fournisseur/site/date."
        )

    # ======================================================
    # COUVERTURE DES FOURNISSEURS
    # ======================================================

    expected_dates = {
        current_date
        for current_date in generate_dates(
            START_DATE,
            END_DATE,
        )
        if not is_sunday(current_date)
    }

    for supplier_id in SUPPLIER_IDS:

        supplier_rows = df[
            df["supplier_id"] == supplier_id
        ]

        supplier_dates = set(
            pd.to_datetime(
                supplier_rows["transport_date"]
            ).dt.date
        )

        if supplier_dates != expected_dates:
            raise ValueError(
                f"Le fournisseur {supplier_id} "
                "ne couvre pas correctement la période."
            )

    # ======================================================
    # COUVERTURE DES SITES
    # ======================================================

    for site_id in SITE_IDS:

        site_rows = df[
            df["site_id"] == site_id
        ]

        site_dates = set(
            pd.to_datetime(
                site_rows["transport_date"]
            ).dt.date
        )

        if site_dates != expected_dates:
            raise ValueError(
                f"Le site {site_id} "
                "ne couvre pas correctement la période."
            )

    # ======================================================
    # VÉRIFICATION DES DISTANCES
    # ======================================================

    for supplier_id in SUPPLIER_IDS:

        for site_id in SITE_IDS:

            route_rows = df[
                (
                    df["supplier_id"]
                    == supplier_id
                )
                & (
                    df["site_id"]
                    == site_id
                )
            ]

            base_distance = (
                SUPPLIER_SITE_DISTANCES[
                    supplier_id
                ][site_id]
            )

            minimum_distance = (
                base_distance * 0.94
            )

            maximum_distance = (
                base_distance * 1.06
            )

            if not (
                route_rows["distance_km"]
                .between(
                    minimum_distance,
                    maximum_distance,
                )
                .all()
            ):
                raise ValueError(
                    "Une distance de transport "
                    "est incohérente avec la route fournisseur/site."
                )


# ==========================================================
# EXPORT
# ==========================================================

def export_transport_data(
    df: pd.DataFrame,
) -> Path:
    """
    Exporte les données de transport dans un fichier CSV.

    Parameters
    ----------
    df : pandas.DataFrame
        Données de transport.

    Returns
    -------
    pathlib.Path
        Chemin du fichier généré.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / "transport.csv"

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    return output_path


# ==========================================================
# POINT D'ENTRÉE PRINCIPAL
# ==========================================================

def main() -> None:
    """
    Génère, valide et exporte les données de transport.
    """

    set_random_seed()

    production_df = load_production_data()

    transport_df = generate_transport_data(
        production_df
    )

    validate_transport_data(
        transport_df
    )

    output_path = export_transport_data(
        transport_df
    )

    print(
        "Données de transport générées avec succès."
    )

    print(
        f"Nombre de lignes générées : "
        f"{len(transport_df):,}"
    )

    print(
        f"Période : "
        f"{transport_df['transport_date'].min()} "
        f"à "
        f"{transport_df['transport_date'].max()}"
    )

    print(
        f"Nombre de fournisseurs : "
        f"{transport_df['supplier_id'].nunique()}"
    )

    print(
        f"Nombre de transporteurs : "
        f"{transport_df['transport_company_id'].nunique()}"
    )

    print(
        f"Nombre de sites : "
        f"{transport_df['site_id'].nunique()}"
    )

    print(
        f"Distance totale : "
        f"{transport_df['distance_km'].sum():,.2f} km"
    )

    print(
        f"Poids total transporté : "
        f"{transport_df['transported_weight_kg'].sum():,.2f} kg"
    )

    print(
        f"Émissions totales : "
        f"{transport_df['co2_emissions_kg'].sum():,.2f} kg CO2"
    )

    print(
        f"Coût total : "
        f"{transport_df['transport_cost'].sum():,.2f} €"
    )

    print(
        f"Fichier généré : {output_path}"
    )


if __name__ == "__main__":
    main()