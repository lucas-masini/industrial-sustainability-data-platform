"""
Génère les données quotidiennes de production pour Helios Industrial Group.

Le jeu de données couvre la période configurée et respecte
les règles métier définies pour chaque produit industriel.

Sortie :
    data/raw/production.csv
"""

from __future__ import annotations

import random
from datetime import date
from pathlib import Path

import pandas as pd

from .config import END_DATE, RAW_DATA_DIR, START_DATE
from .utils import (
    apply_saturday_factor,
    generate_dates,
    get_season,
    is_sunday,
    set_random_seed,
)


# ==========================================================
# RÈGLES DE PRODUCTION DES PRODUITS
# ==========================================================

PRODUCT_RULES = {
    1: {
        "site_id": 1,
        "product_name": "Industrial Battery",
        "category": "Energy Storage",
        "min_quantity": 80,
        "max_quantity": 140,
        "units_per_hour": 20,
    },
    2: {
        "site_id": 1,
        "product_name": "Residential Battery",
        "category": "Energy Storage",
        "min_quantity": 140,
        "max_quantity": 240,
        "units_per_hour": 35,
    },
    3: {
        "site_id": 2,
        "product_name": "Wind Turbine Blade",
        "category": "Wind Energy",
        "min_quantity": 4,
        "max_quantity": 10,
        "units_per_hour": 1,
    },
    4: {
        "site_id": 2,
        "product_name": "Wind Turbine Hub",
        "category": "Wind Energy",
        "min_quantity": 6,
        "max_quantity": 14,
        "units_per_hour": 2,
    },
    5: {
        "site_id": 3,
        "product_name": "Photovoltaic Structure",
        "category": "Solar Energy",
        "min_quantity": 160,
        "max_quantity": 300,
        "units_per_hour": 45,
    },
    6: {
        "site_id": 3,
        "product_name": "Solar Panel Support",
        "category": "Solar Energy",
        "min_quantity": 250,
        "max_quantity": 450,
        "units_per_hour": 70,
    },
    7: {
        "site_id": 4,
        "product_name": "Electrical Cabinet",
        "category": "Electrical Systems",
        "min_quantity": 45,
        "max_quantity": 90,
        "units_per_hour": 15,
    },
    8: {
        "site_id": 4,
        "product_name": "Electrical Distribution Panel",
        "category": "Electrical Systems",
        "min_quantity": 70,
        "max_quantity": 140,
        "units_per_hour": 20,
    },
    9: {
        "site_id": 5,
        "product_name": "Recycled Aluminum Pellets",
        "category": "Recycling",
        "min_quantity": 700,
        "max_quantity": 1300,
        "units_per_hour": 180,
    },
    10: {
        "site_id": 5,
        "product_name": "Recycled Steel",
        "category": "Recycling",
        "min_quantity": 500,
        "max_quantity": 1000,
        "units_per_hour": 150,
    },
}


# ==========================================================
# GÉNÉRATION DE LA PRODUCTION
# ==========================================================

def generate_base_quantity(product_rule: dict) -> int:
    """
    Génère une quantité de production de base aléatoire.

    Paramètres
    ----------
    product_rule : dict
        Paramètres de production du produit.

    Retourne
    --------
    int
        Quantité de production de base.
    """
    return random.randint(
        product_rule["min_quantity"],
        product_rule["max_quantity"],
    )


def apply_day_factor(
    quantity: int,
    current_date: date,
) -> int | None:
    """
    Applique les ajustements de production en fonction
    du jour de la semaine.

    Aucune production n'est réalisée le dimanche.
    Le samedi, la production correspond à 60 % de la
    production normale.

    Paramètres
    ----------
    quantity : int
        Quantité de production de base.

    current_date : date
        Date de production.

    Retourne
    --------
    int | None
        Quantité ajustée, ou None lorsqu'aucune production
        n'est réalisée.
    """
    if is_sunday(current_date):
        return None

    if current_date.weekday() == 5:
        quantity = apply_saturday_factor(quantity)

    return max(1, round(quantity))


def apply_seasonal_factor(
    quantity: int,
    season: str,
    category: str,
) -> int:
    """
    Applique les ajustements saisonniers de production.

    Les produits solaires bénéficient d'une augmentation
    de production au printemps et en été.

    Les produits éoliens bénéficient d'une augmentation
    de production en automne et en hiver.

    Paramètres
    ----------
    quantity : int
        Quantité de production actuelle.

    season : str
        Saison actuelle.

    category : str
        Catégorie du produit.

    Retourne
    --------
    int
        Quantité de production ajustée selon la saison.
    """
    factor = 1.0

    if category == "Solar Energy":
        if season == "Spring":
            factor = 1.10
        elif season == "Summer":
            factor = 1.20

    elif category == "Wind Energy":
        if season in ("Autumn", "Winter"):
            factor = 1.10

    return max(1, round(quantity * factor))


def calculate_production_duration(
    quantity: int,
    units_per_hour: int,
) -> int:
    """
    Calcule la durée de production à partir de la quantité produite.

    Paramètres
    ----------
    quantity : int
        Quantité produite.

    units_per_hour : int
        Capacité de production en unités par heure.

    Retourne
    --------
    int
        Durée de production en minutes.
    """
    duration_hours = quantity / units_per_hour

    return max(1, round(duration_hours * 60))


# ==========================================================
# GÉNÉRATION DU JEU DE DONNÉES
# ==========================================================

def generate_production_data() -> pd.DataFrame:
    """
    Génère l'ensemble du jeu de données de production.

    Retourne
    --------
    pandas.DataFrame
        Jeu de données de production généré.
    """
    rows: list[dict] = []

    dates = generate_dates(START_DATE, END_DATE)

    for current_date in dates:

        season = get_season(current_date)

        for product_id, product_rule in PRODUCT_RULES.items():

            base_quantity = generate_base_quantity(product_rule)

            quantity = apply_day_factor(
                base_quantity,
                current_date,
            )

            # Aucune production le dimanche.
            if quantity is None:
                continue

            quantity = apply_seasonal_factor(
                quantity,
                season,
                product_rule["category"],
            )

            production_duration = calculate_production_duration(
                quantity,
                product_rule["units_per_hour"],
            )

            rows.append(
                {
                    "site_id": product_rule["site_id"],
                    "product_id": product_id,
                    "production_date": current_date,
                    "quantity_produced": quantity,
                    "production_duration_minutes": production_duration,
                }
            )

    return pd.DataFrame(rows)


# ==========================================================
# VALIDATION DES DONNÉES
# ==========================================================

def validate_production_data(df: pd.DataFrame) -> None:
    """
    Vérifie la conformité du jeu de données de production généré.

    Lève
    ----
    ValueError
        Lorsqu'une des règles métier n'est pas respectée.
    """
    required_columns = {
        "site_id",
        "product_id",
        "production_date",
        "quantity_produced",
        "production_duration_minutes",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError(
            "Le jeu de données de production est vide."
        )

    if df["quantity_produced"].isna().any():
        raise ValueError(
            "Les quantités de production contiennent des valeurs NULL."
        )

    if (df["quantity_produced"] <= 0).any():
        raise ValueError(
            "Les quantités de production doivent être strictement positives."
        )

    if df["production_duration_minutes"].isna().any():
        raise ValueError(
            "Les durées de production contiennent des valeurs NULL."
        )

    if (df["production_duration_minutes"] <= 0).any():
        raise ValueError(
            "Les durées de production doivent être strictement positives."
        )

    if pd.to_datetime(
        df["production_date"]
    ).dt.dayofweek.eq(6).any():
        raise ValueError(
            "Le jeu de données contient des enregistrements le dimanche."
        )

    valid_product_ids = set(PRODUCT_RULES.keys())

    if not set(df["product_id"]).issubset(valid_product_ids):
        raise ValueError(
            "Le jeu de données contient des identifiants de produits inconnus."
        )

    for product_id, product_rule in PRODUCT_RULES.items():

        product_rows = df[df["product_id"] == product_id]

        if not (
            product_rows["site_id"] == product_rule["site_id"]
        ).all():
            raise ValueError(
                f"Le produit {product_id} est associé "
                f"à un site incorrect."
            )


# ==========================================================
# EXPORT
# ==========================================================

def export_production_data(df: pd.DataFrame) -> Path:
    """
    Exporte les données de production dans un fichier CSV.

    Paramètres
    ----------
    df : pandas.DataFrame
        Jeu de données de production.

    Retourne
    --------
    pathlib.Path
        Chemin vers le fichier CSV généré.
    """
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RAW_DATA_DIR / "production.csv"

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
    Génère, valide et exporte le jeu de données de production.
    """
    set_random_seed()

    production_df = generate_production_data()

    validate_production_data(production_df)

    output_path = export_production_data(production_df)

    print("Données de production générées avec succès.")
    print(f"Nombre de lignes générées : {len(production_df):,}")
    print(
        f"Période : "
        f"{production_df['production_date'].min()} "
        f"à "
        f"{production_df['production_date'].max()}"
    )
    print(f"Fichier généré : {output_path}")


if __name__ == "__main__":
    main()