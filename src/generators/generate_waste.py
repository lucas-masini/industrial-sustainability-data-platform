"""
Génère les données quotidiennes de déchets pour
Helios Industrial Group.

Les données sont générées à partir des volumes de production
afin de conserver une cohérence entre l'activité industrielle
et les déchets produits.

Chaque enregistrement représente une catégorie de déchets
produite par un site industriel pendant une journée donnée.

Règles métier :
    - aucune production ni aucun déchet le dimanche ;
    - activité réduite le samedi ;
    - quantité de déchets liée au volume de production ;
    - plusieurs catégories de déchets par site ;
    - certaines catégories sont recyclables ;
    - variation aléatoire contrôlée ;
    - données reproductibles grâce à la graine aléatoire.

Sortie :
    data/raw/waste.csv
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
# CONFIGURATION DES DÉCHETS
# ==========================================================

# Les quatre catégories utilisées dans le jeu de données.
#
# La table SQL utilise un champ VARCHAR pour le type de déchet.
# Les valeurs restent donc suffisamment génériques pour être
# exploitées facilement dans Power BI et dbt.

WASTE_TYPES = {
    "Metal Scrap": {
        "recyclable": True,
        "waste_rate": 0.035,
    },
    "Plastic Waste": {
        "recyclable": True,
        "waste_rate": 0.018,
    },
    "Electrical Waste": {
        "recyclable": True,
        "waste_rate": 0.008,
    },
    "Packaging Waste": {
        "recyclable": False,
        "waste_rate": 0.012,
    },
}


# Facteur spécifique à chaque site.
#
# Il permet de représenter des procédés industriels différents.
# Un site ayant un facteur élevé génère davantage de déchets
# pour un même volume de production.

SITE_WASTE_FACTORS = {
    1: 1.00,
    2: 0.85,
    3: 1.10,
    4: 0.95,
    5: 1.20,
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
    Agrège les volumes de production par site et par date.

    Cette agrégation permet de relier les déchets à l'activité
    industrielle réelle de chaque site.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données détaillées de production.

    Returns
    -------
    pandas.DataFrame
        Production totale par site et par jour.
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
                "production_date": "waste_date",
                "quantity_produced": "total_quantity_produced",
            }
        )
    )

    return production_summary


# ==========================================================
# CALCUL DES DÉCHETS
# ==========================================================

def calculate_waste_quantity(
    production_quantity: float,
    site_id: int,
    waste_rate: float,
    current_date: date,
) -> float:
    """
    Calcule la quantité de déchets produite.

    La quantité dépend :
        - du volume de production ;
        - du facteur propre au site ;
        - du taux propre au type de déchet ;
        - d'une variation aléatoire contrôlée.

    Le samedi, l'activité industrielle étant réduite,
    la quantité de déchets est également réduite.

    Parameters
    ----------
    production_quantity : float
        Quantité totale produite par le site.

    site_id : int
        Identifiant du site industriel.

    waste_rate : float
        Taux de déchets associé à la catégorie.

    current_date : date
        Date de production des déchets.

    Returns
    -------
    float
        Quantité de déchets en kilogrammes.
    """

    site_factor = SITE_WASTE_FACTORS[site_id]

    random_variation = random.uniform(
        0.90,
        1.10,
    )

    quantity = (
        production_quantity
        * waste_rate
        * site_factor
        * random_variation
    )

    # Le samedi correspond à 60 % de l'activité normale.
    if current_date.weekday() == 5:
        quantity *= 0.60

    return round(
        quantity,
        2,
    )


# ==========================================================
# GÉNÉRATION DU JEU DE DONNÉES
# ==========================================================

def generate_waste_data(
    production_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Génère le jeu complet de données de déchets.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données de production.

    Returns
    -------
    pandas.DataFrame
        Jeu de données de déchets généré.
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

        # Aucun déchet industriel le dimanche car aucune
        # production n'est réalisée ce jour-là.
        if is_sunday(current_date):
            continue

        for site_id in range(1, 6):

            site_production = production_summary[
                (
                    production_summary["site_id"]
                    == site_id
                )
                & (
                    production_summary["waste_date"]
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

            for waste_type, waste_rule in WASTE_TYPES.items():

                waste_quantity = calculate_waste_quantity(
                    production_quantity=production_quantity,
                    site_id=site_id,
                    waste_rate=waste_rule["waste_rate"],
                    current_date=current_date,
                )

                rows.append(
                    {
                        "site_id": site_id,
                        "waste_date": current_date,
                        "waste_type": waste_type,
                        "waste_quantity_kg": waste_quantity,
                        "recyclable": waste_rule["recyclable"],
                    }
                )

    return pd.DataFrame(rows)


# ==========================================================
# VALIDATION DES DONNÉES
# ==========================================================

def validate_waste_data(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie la conformité du jeu de données de déchets.

    Parameters
    ----------
    df : pandas.DataFrame
        Jeu de données de déchets.

    Raises
    ------
    ValueError
        Lorsqu'une règle métier ou une contrainte de qualité
        n'est pas respectée.
    """

    required_columns = {
        "site_id",
        "waste_date",
        "waste_type",
        "waste_quantity_kg",
        "recyclable",
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
            "Le jeu de données de déchets est vide."
        )

    # ======================================================
    # VALEURS NULL
    # ======================================================

    if df["site_id"].isna().any():
        raise ValueError(
            "La colonne site_id contient des valeurs NULL."
        )

    if df["waste_date"].isna().any():
        raise ValueError(
            "La colonne waste_date contient des valeurs NULL."
        )

    if df["waste_type"].isna().any():
        raise ValueError(
            "La colonne waste_type contient des valeurs NULL."
        )

    if df["waste_quantity_kg"].isna().any():
        raise ValueError(
            "La quantité de déchets contient des valeurs NULL."
        )

    if df["recyclable"].isna().any():
        raise ValueError(
            "La colonne recyclable contient des valeurs NULL."
        )

    # ======================================================
    # QUANTITÉS
    # ======================================================

    if (
        df["waste_quantity_kg"] <= 0
    ).any():
        raise ValueError(
            "Les quantités de déchets doivent être "
            "strictement positives."
        )

    # ======================================================
    # TYPES DE DÉCHETS
    # ======================================================

    valid_waste_types = set(
        WASTE_TYPES.keys()
    )

    if not set(
        df["waste_type"]
    ).issubset(valid_waste_types):
        raise ValueError(
            "Le jeu de données contient des types "
            "de déchets inconnus."
        )

    # ======================================================
    # SITES
    # ======================================================

    valid_site_ids = set(range(1, 6))

    if not set(
        df["site_id"]
    ).issubset(valid_site_ids):
        raise ValueError(
            "Le jeu de données contient des identifiants "
            "de sites inconnus."
        )

    # ======================================================
    # DATES
    # ======================================================

    dates = pd.to_datetime(
        df["waste_date"]
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
            "Le jeu de données contient des déchets "
            "le dimanche."
        )

    # ======================================================
    # RECYCLABILITÉ
    # ======================================================

    for waste_type, waste_rule in WASTE_TYPES.items():

        waste_rows = df[
            df["waste_type"] == waste_type
        ]

        expected_recyclable = (
            waste_rule["recyclable"]
        )

        if not (
            waste_rows["recyclable"]
            == expected_recyclable
        ).all():
            raise ValueError(
                f"Le statut recyclable du type "
                f"'{waste_type}' est incorrect."
            )

    # ======================================================
    # DOUBLONS
    # ======================================================

    duplicates = df.duplicated(
        subset=[
            "site_id",
            "waste_date",
            "waste_type",
        ]
    )

    if duplicates.any():
        raise ValueError(
            "Des doublons existent pour une combinaison "
            "site/date/type de déchet."
        )

    # ======================================================
    # COUVERTURE DES DONNÉES
    # ======================================================

    expected_dates = {
        current_date
        for current_date in generate_dates(
            START_DATE,
            END_DATE,
        )
        if not is_sunday(current_date)
    }

    for site_id in valid_site_ids:

        site_rows = df[
            df["site_id"] == site_id
        ]

        site_dates = set(
            pd.to_datetime(
                site_rows["waste_date"]
            ).dt.date
        )

        if site_dates != expected_dates:
            raise ValueError(
                f"Le site {site_id} ne couvre pas "
                "correctement la période attendue."
            )

        site_waste_types = set(
            site_rows["waste_type"]
        )

        if site_waste_types != valid_waste_types:
            raise ValueError(
                f"Le site {site_id} ne possède pas "
                "toutes les catégories de déchets attendues."
            )

    # ======================================================
    # TYPES DE DONNÉES
    # ======================================================

    valid_recyclable_values = {
        True,
        False,
    }

    if not set(
        df["recyclable"].unique()
    ).issubset(valid_recyclable_values):
        raise ValueError(
            "La colonne recyclable contient des valeurs "
            "autres que TRUE ou FALSE."
        )


# ==========================================================
# EXPORT
# ==========================================================

def export_waste_data(
    df: pd.DataFrame,
) -> Path:
    """
    Exporte les données de déchets dans un fichier CSV.

    Parameters
    ----------
    df : pandas.DataFrame
        Jeu de données de déchets.

    Returns
    -------
    pathlib.Path
        Chemin du fichier CSV généré.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / "waste.csv"

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
    Génère, valide et exporte les données de déchets.
    """

    set_random_seed()

    production_df = load_production_data()

    waste_df = generate_waste_data(
        production_df
    )

    validate_waste_data(
        waste_df
    )

    output_path = export_waste_data(
        waste_df
    )

    print(
        "Données de déchets générées avec succès."
    )

    print(
        f"Nombre de lignes générées : "
        f"{len(waste_df):,}"
    )

    print(
        f"Période : "
        f"{waste_df['waste_date'].min()} "
        f"à "
        f"{waste_df['waste_date'].max()}"
    )

    print(
        f"Nombre de sites : "
        f"{waste_df['site_id'].nunique()}"
    )

    print(
        f"Nombre de catégories de déchets : "
        f"{waste_df['waste_type'].nunique()}"
    )

    print(
        f"Quantité totale de déchets : "
        f"{waste_df['waste_quantity_kg'].sum():,.2f} kg"
    )

    recyclable_quantity = waste_df.loc[
        waste_df["recyclable"] == True,
        "waste_quantity_kg",
    ].sum()

    total_quantity = waste_df[
        "waste_quantity_kg"
    ].sum()

    recycling_rate = (
        recyclable_quantity / total_quantity * 100
    )

    print(
        f"Taux de déchets recyclables : "
        f"{recycling_rate:.2f} %"
    )

    print(
        f"Fichier généré : {output_path}"
    )


if __name__ == "__main__":
    main()