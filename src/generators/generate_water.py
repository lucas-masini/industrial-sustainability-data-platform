"""
Génère les données quotidiennes de consommation d'eau
pour Helios Industrial Group.

Le jeu de données est construit à partir des données de production
générées précédemment afin de conserver une cohérence entre
l'activité industrielle et la consommation d'eau.

Chaque enregistrement correspond à la consommation d'eau
d'un site industriel pour une journée donnée.

Règles métier :
    - aucune activité industrielle le dimanche ;
    - consommation réduite le samedi ;
    - consommation liée au niveau de production ;
    - légère variation saisonnière ;
    - variation aléatoire contrôlée ;
    - coût calculé à partir de la consommation.

Sortie :
    data/raw/water.csv
"""

from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from .config import END_DATE, RAW_DATA_DIR, START_DATE
from .utils import (
    generate_dates,
    get_season,
    is_sunday,
    is_weekend,
    set_random_seed,
)


# ==========================================================
# CONFIGURATION
# ==========================================================

# Consommation d'eau de base par site en m³.
#
# Cette valeur représente les besoins relativement stables
# du site : nettoyage, refroidissement, installations
# industrielles et autres usages indépendants du volume
# de production.

SITE_BASE_WATER_CONSUMPTION = {
    1: 28.0,
    2: 20.0,
    3: 24.0,
    4: 32.0,
    5: 42.0,
}


# Quantité d'eau consommée par unité produite.
#
# Les valeurs sont volontairement différentes selon les sites
# afin de représenter des procédés industriels différents.

SITE_WATER_PER_UNIT = {
    1: 0.12,
    2: 0.08,
    3: 0.15,
    4: 0.10,
    5: 0.18,
}


# Prix indicatif de l'eau en euros par m³.
#
# Cette valeur permet de générer le coût associé à chaque
# consommation journalière.

WATER_PRICE_PER_M3 = 4.20


# Facteurs saisonniers.
#
# Ils représentent une variation modérée des besoins en eau
# selon la saison, notamment pour le refroidissement industriel
# et certains usages liés aux conditions climatiques.

SEASONAL_WATER_FACTORS = {
    "Winter": 0.95,
    "Spring": 1.00,
    "Summer": 1.10,
    "Autumn": 1.00,
}


# ==========================================================
# LECTURE DE LA PRODUCTION
# ==========================================================

def load_production_data() -> pd.DataFrame:
    """
    Charge les données de production générées précédemment.

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
                "quantity_produced": "total_quantity_produced",
                "production_date": "water_date",
            }
        )
    )

    return production_summary


# ==========================================================
# CALCUL DE LA CONSOMMATION
# ==========================================================

def calculate_water_consumption(
    production_quantity: float,
    site_id: int,
    current_date,
) -> float:
    """
    Calcule la consommation d'eau d'un site pour une journée.

    La consommation est composée de deux éléments :

    1. une consommation de base liée au fonctionnement du site ;
    2. une consommation variable liée au volume produit.

    Une variation aléatoire limitée permet de conserver un
    caractère réaliste sans casser la relation entre production
    et consommation.

    Parameters
    ----------
    production_quantity : float
        Quantité totale produite sur le site pendant la journée.

    site_id : int
        Identifiant du site.

    current_date : date
        Date de la consommation.

    Returns
    -------
    float
        Consommation d'eau en m³.
    """

    base_consumption = SITE_BASE_WATER_CONSUMPTION[site_id]

    water_per_unit = SITE_WATER_PER_UNIT[site_id]

    production_consumption = (
        production_quantity
        * water_per_unit
    )

    seasonal_factor = SEASONAL_WATER_FACTORS[
        get_season(current_date)
    ]

    random_variation = random.uniform(
        0.95,
        1.05,
    )

    consumption = (
        (
            base_consumption
            + production_consumption
        )
        * seasonal_factor
        * random_variation
    )

    # Le samedi représente une activité industrielle réduite.
    #
    # Cette règle est cohérente avec le générateur de production
    # et avec le générateur énergétique.

    if is_weekend(current_date):
        consumption *= 0.60

    return round(
        consumption,
        2,
    )


# ==========================================================
# GÉNÉRATION DU JEU DE DONNÉES
# ==========================================================

def generate_water_data(
    production_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Génère les données quotidiennes de consommation d'eau.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données de production.

    Returns
    -------
    pandas.DataFrame
        Données de consommation d'eau.
    """

    production_summary = (
        aggregate_production_by_site_and_date(
            production_df
        )
    )

    rows: list[dict] = []

    dates = generate_dates(
        START_DATE,
        END_DATE,
    )

    for current_date in dates:

        # Aucun enregistrement le dimanche.
        if is_sunday(current_date):
            continue

        for site_id in range(1, 6):

            site_production = production_summary[
                (
                    production_summary["site_id"]
                    == site_id
                )
                & (
                    production_summary["water_date"]
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

            water_consumption = (
                calculate_water_consumption(
                    production_quantity,
                    site_id,
                    current_date,
                )
            )

            water_cost = (
                water_consumption
                * WATER_PRICE_PER_M3
            )

            rows.append(
                {
                    "site_id": site_id,
                    "water_date": current_date,
                    "water_consumption_m3": (
                        water_consumption
                    ),
                    "water_cost": round(
                        water_cost,
                        2,
                    ),
                }
            )

    return pd.DataFrame(rows)


# ==========================================================
# VALIDATION
# ==========================================================

def validate_water_data(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie la conformité des données de consommation d'eau.

    Parameters
    ----------
    df : pandas.DataFrame
        Données de consommation d'eau.

    Raises
    ------
    ValueError
        Lorsqu'une règle de qualité ou une règle métier
        n'est pas respectée.
    """

    required_columns = {
        "site_id",
        "water_date",
        "water_consumption_m3",
        "water_cost",
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
            "Le jeu de données water est vide."
        )

    # Vérification des valeurs NULL.

    if df["site_id"].isna().any():
        raise ValueError(
            "La colonne site_id contient des valeurs NULL."
        )

    if df["water_date"].isna().any():
        raise ValueError(
            "La colonne water_date contient des valeurs NULL."
        )

    if df[
        "water_consumption_m3"
    ].isna().any():
        raise ValueError(
            "La consommation d'eau contient des valeurs NULL."
        )

    if df["water_cost"].isna().any():
        raise ValueError(
            "Le coût de l'eau contient des valeurs NULL."
        )

    # Vérification des valeurs positives.

    if (
        df["water_consumption_m3"] < 0
    ).any():
        raise ValueError(
            "La consommation d'eau ne peut pas être négative."
        )

    if (
        df["water_cost"] < 0
    ).any():
        raise ValueError(
            "Le coût de l'eau ne peut pas être négatif."
        )

    # Vérification de la période.

    dates = pd.to_datetime(
        df["water_date"]
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

    # Aucun dimanche.

    if dates.dt.dayofweek.eq(6).any():
        raise ValueError(
            "Le jeu de données contient des consommations "
            "d'eau le dimanche."
        )

    # Vérification des sites.

    valid_site_ids = set(range(1, 6))

    if not set(
        df["site_id"]
    ).issubset(valid_site_ids):
        raise ValueError(
            "Le jeu de données contient des identifiants "
            "de sites inconnus."
        )

    # Une seule ligne par site et par date.

    duplicates = df.duplicated(
        subset=[
            "site_id",
            "water_date",
        ]
    )

    if duplicates.any():
        raise ValueError(
            "Des doublons existent pour une combinaison "
            "site/date."
        )

    # Chaque site doit couvrir la période complète
    # hors dimanches.

    expected_dates = {
        current_date
        for current_date in generate_dates(
            START_DATE,
            END_DATE,
        )
        if not is_sunday(current_date)
    }

    for site_id in valid_site_ids:

        site_dates = set(
            pd.to_datetime(
                df.loc[
                    df["site_id"] == site_id,
                    "water_date",
                ]
            ).dt.date
        )

        if site_dates != expected_dates:
            raise ValueError(
                f"Le site {site_id} ne couvre pas "
                "correctement la période attendue."
            )

    # Vérification de la cohérence du calcul du coût.
    #
    # Une tolérance de quelques centimes est utilisée afin de
    # tenir compte des arrondis du CSV.

    expected_cost = (
        df["water_consumption_m3"]
        * WATER_PRICE_PER_M3
    )

    if not (
        (df["water_cost"] - expected_cost)
        .abs()
        .le(0.01)
        .all()
    ):
        raise ValueError(
            "Certains coûts d'eau ne correspondent pas "
            "à la consommation et au prix configuré."
        )


# ==========================================================
# EXPORT
# ==========================================================

def export_water_data(
    df: pd.DataFrame,
) -> Path:
    """
    Exporte les données d'eau dans un fichier CSV.

    Parameters
    ----------
    df : pandas.DataFrame
        Données de consommation d'eau.

    Returns
    -------
    pathlib.Path
        Chemin du fichier généré.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / "water.csv"

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
    Génère, valide et exporte les données de consommation d'eau.
    """

    set_random_seed()

    production_df = load_production_data()

    water_df = generate_water_data(
        production_df
    )

    validate_water_data(
        water_df
    )

    output_path = export_water_data(
        water_df
    )

    print(
        "Données de consommation d'eau générées avec succès."
    )

    print(
        f"Nombre de lignes générées : "
        f"{len(water_df):,}"
    )

    print(
        f"Période : "
        f"{water_df['water_date'].min()} "
        f"à "
        f"{water_df['water_date'].max()}"
    )

    print(
        f"Nombre de sites : "
        f"{water_df['site_id'].nunique()}"
    )

    print(
        f"Consommation totale : "
        f"{water_df['water_consumption_m3'].sum():,.2f} m³"
    )

    print(
        f"Coût total : "
        f"{water_df['water_cost'].sum():,.2f} €"
    )

    print(
        f"Fichier généré : {output_path}"
    )


if __name__ == "__main__":
    main()