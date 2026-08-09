"""
Génère les données quotidiennes de consommation énergétique
pour Helios Industrial Group.

Le jeu de données couvre la période configurée et est cohérent
avec les données de production générées précédemment.

Chaque enregistrement correspond à la consommation d'une source
d'énergie donnée pour un site industriel et une date donnée.

Règles principales :
    - aucune activité énergétique le dimanche ;
    - activité réduite le samedi ;
    - consommation liée au niveau réel de production ;
    - chaque site utilise les cinq sources d'énergie référencées ;
    - les sources renouvelables représentent une partie de
      l'énergie consommée ;
    - le coût est calculé à partir de la consommation énergétique.

Sortie :
    data/raw/energy.csv
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
# CONFIGURATION ÉNERGÉTIQUE
# ==========================================================

# Répartition indicative de l'énergie consommée par source.
#
# Les proportions sont propres à chaque site afin de créer
# un jeu de données réaliste et exploitable pour les analyses
# de mix énergétique.
#
# La somme des proportions pour chaque site est égale à 1.

ENERGY_MIX = {
    1: {
        "Electricity": 0.50,
        "Natural Gas": 0.25,
        "Solar": 0.10,
        "Wind": 0.05,
        "Hydroelectric": 0.10,
    },
    2: {
        "Electricity": 0.40,
        "Natural Gas": 0.15,
        "Solar": 0.10,
        "Wind": 0.20,
        "Hydroelectric": 0.15,
    },
    3: {
        "Electricity": 0.35,
        "Natural Gas": 0.10,
        "Solar": 0.35,
        "Wind": 0.10,
        "Hydroelectric": 0.10,
    },
    4: {
        "Electricity": 0.50,
        "Natural Gas": 0.20,
        "Solar": 0.10,
        "Wind": 0.05,
        "Hydroelectric": 0.15,
    },
    5: {
        "Electricity": 0.35,
        "Natural Gas": 0.20,
        "Solar": 0.10,
        "Wind": 0.10,
        "Hydroelectric": 0.25,
    },
}


# Prix indicatifs en euros par kWh.
#
# Ces valeurs sont utilisées uniquement pour générer les coûts
# du jeu de données.
ENERGY_PRICES = {
    "Electricity": 0.18,
    "Natural Gas": 0.09,
    "Solar": 0.05,
    "Wind": 0.06,
    "Hydroelectric": 0.07,
}


# Facteurs permettant de convertir l'activité de production
# en consommation énergétique.
#
# Plus le facteur est élevé, plus le site consomme d'énergie
# pour un même niveau de production.

SITE_ENERGY_FACTORS = {
    1: 2.40,
    2: 3.20,
    3: 1.80,
    4: 2.20,
    5: 1.50,
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
        Si le fichier production.csv n'existe pas.
    ValueError
        Si les colonnes nécessaires sont absentes.
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

    missing_columns = required_columns - set(production_df.columns)

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
    Agrège les quantités produites par site et par date.

    Cette agrégation permet de relier directement la consommation
    énergétique à l'activité industrielle réelle du site.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données de production détaillées.

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
                "quantity_produced": "total_quantity_produced",
                "production_date": "energy_date",
            }
        )
    )

    return production_summary


# ==========================================================
# CONSOMMATION ÉNERGÉTIQUE
# ==========================================================

def calculate_site_energy_consumption(
    production_quantity: float,
    site_id: int,
) -> float:
    """
    Calcule la consommation énergétique totale d'un site
    à partir de son niveau de production.

    Parameters
    ----------
    production_quantity : float
        Quantité totale produite par le site pendant la journée.

    site_id : int
        Identifiant du site industriel.

    Returns
    -------
    float
        Consommation énergétique totale en kWh.
    """

    energy_factor = SITE_ENERGY_FACTORS[site_id]

    # Une légère variation aléatoire permet d'éviter des valeurs
    # parfaitement déterministes tout en conservant une relation
    # claire entre production et consommation.
    random_variation = random.uniform(0.95, 1.05)

    consumption = (
        production_quantity
        * energy_factor
        * random_variation
    )

    return round(consumption, 2)


def calculate_source_consumption(
    total_consumption: float,
    site_id: int,
    energy_source: str,
) -> float:
    """
    Répartit la consommation totale du site entre les différentes
    sources d'énergie selon le mix énergétique du site.

    Parameters
    ----------
    total_consumption : float
        Consommation énergétique totale du site.

    site_id : int
        Identifiant du site.

    energy_source : str
        Source d'énergie.

    Returns
    -------
    float
        Consommation de la source en kWh.
    """

    source_ratio = ENERGY_MIX[site_id][energy_source]

    return round(
        total_consumption * source_ratio,
        2,
    )


# ==========================================================
# GÉNÉRATION DU JEU DE DONNÉES
# ==========================================================

def generate_energy_data(
    production_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Génère les données quotidiennes de consommation énergétique.

    La consommation est directement liée aux volumes de production
    des différents sites.

    Parameters
    ----------
    production_df : pandas.DataFrame
        Données de production.

    Returns
    -------
    pandas.DataFrame
        Jeu de données énergétique généré.
    """

    production_summary = aggregate_production_by_site_and_date(
        production_df
    )

    rows: list[dict] = []

    dates = generate_dates(
        START_DATE,
        END_DATE,
    )

    for current_date in dates:

        # Aucune activité énergétique le dimanche.
        if is_sunday(current_date):
            continue

        for site_id in range(1, 6):

            site_production = production_summary[
                (
                    production_summary["site_id"] == site_id
                )
                & (
                    production_summary["energy_date"]
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

            total_consumption = calculate_site_energy_consumption(
                production_quantity,
                site_id,
            )

            for energy_source in ENERGY_MIX[site_id]:

                source_consumption = calculate_source_consumption(
                    total_consumption,
                    site_id,
                    energy_source,
                )

                energy_cost = (
                    source_consumption
                    * ENERGY_PRICES[energy_source]
                )

                rows.append(
                    {
                        "site_id": site_id,
                        "energy_source_id": (
                            list(ENERGY_PRICES.keys()).index(
                                energy_source
                            ) + 1
                        ),
                        "energy_date": current_date,
                        "energy_consumption_kwh": round(
                            source_consumption,
                            2,
                        ),
                        "energy_cost": round(
                            energy_cost,
                            2,
                        ),
                    }
                )

    return pd.DataFrame(rows)


# ==========================================================
# VALIDATION DES DONNÉES
# ==========================================================

def validate_energy_data(
    df: pd.DataFrame,
) -> None:
    """
    Vérifie la conformité du jeu de données énergétique.

    Parameters
    ----------
    df : pandas.DataFrame
        Jeu de données énergétique.

    Raises
    ------
    ValueError
        Lorsqu'une règle métier n'est pas respectée.
    """

    required_columns = {
        "site_id",
        "energy_source_id",
        "energy_date",
        "energy_consumption_kwh",
        "energy_cost",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Colonnes manquantes : {sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError(
            "Le jeu de données énergétique est vide."
        )

    if df[
        "energy_consumption_kwh"
    ].isna().any():
        raise ValueError(
            "La consommation énergétique contient "
            "des valeurs NULL."
        )

    if (
        df["energy_consumption_kwh"] < 0
    ).any():
        raise ValueError(
            "La consommation énergétique ne peut pas "
            "être négative."
        )

    if df["energy_cost"].isna().any():
        raise ValueError(
            "Le coût énergétique contient des valeurs NULL."
        )

    if (df["energy_cost"] < 0).any():
        raise ValueError(
            "Le coût énergétique ne peut pas être négatif."
        )

    # Vérification de la période.
    min_date = pd.to_datetime(
        df["energy_date"]
    ).min().date()

    max_date = pd.to_datetime(
        df["energy_date"]
    ).max().date()

    if min_date != START_DATE:
        raise ValueError(
            f"La première date est incorrecte : {min_date}"
        )

    if max_date != END_DATE:
        raise ValueError(
            f"La dernière date est incorrecte : {max_date}"
        )

    # Aucun enregistrement ne doit exister le dimanche.
    if (
        pd.to_datetime(df["energy_date"])
        .dt.dayofweek
        .eq(6)
        .any()
    ):
        raise ValueError(
            "Le jeu de données contient des enregistrements "
            "énergétiques le dimanche."
        )

    # Les identifiants de sites doivent être valides.
    valid_site_ids = set(range(1, 6))

    if not set(df["site_id"]).issubset(valid_site_ids):
        raise ValueError(
            "Le jeu de données contient des identifiants "
            "de sites inconnus."
        )

    # Les identifiants de sources doivent être valides.
    valid_energy_source_ids = set(range(1, 6))

    if not set(
        df["energy_source_id"]
    ).issubset(valid_energy_source_ids):
        raise ValueError(
            "Le jeu de données contient des identifiants "
            "de sources d'énergie inconnus."
        )

    # Chaque site doit utiliser les cinq sources.
    for site_id in valid_site_ids:

        site_sources = set(
            df.loc[
                df["site_id"] == site_id,
                "energy_source_id",
            ]
        )

        if site_sources != valid_energy_source_ids:
            raise ValueError(
                f"Le site {site_id} ne possède pas exactement "
                "les cinq sources d'énergie attendues."
            )

    # Une combinaison site/date/source ne doit apparaître
    # qu'une seule fois.
    duplicates = df.duplicated(
        subset=[
            "site_id",
            "energy_source_id",
            "energy_date",
        ]
    )

    if duplicates.any():
        raise ValueError(
            "Des doublons existent pour une combinaison "
            "site/date/source d'énergie."
        )


# ==========================================================
# EXPORT
# ==========================================================

def export_energy_data(
    df: pd.DataFrame,
) -> Path:
    """
    Exporte les données énergétiques dans un fichier CSV.

    Parameters
    ----------
    df : pandas.DataFrame
        Jeu de données énergétique.

    Returns
    -------
    pathlib.Path
        Chemin du fichier CSV généré.
    """

    RAW_DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RAW_DATA_DIR / "energy.csv"

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
    Génère, valide et exporte les données énergétiques.
    """

    set_random_seed()

    production_df = load_production_data()

    energy_df = generate_energy_data(
        production_df
    )

    validate_energy_data(
        energy_df
    )

    output_path = export_energy_data(
        energy_df
    )

    print(
        "Données énergétiques générées avec succès."
    )

    print(
        f"Nombre de lignes générées : "
        f"{len(energy_df):,}"
    )

    print(
        f"Période : "
        f"{energy_df['energy_date'].min()} "
        f"à "
        f"{energy_df['energy_date'].max()}"
    )

    print(
        f"Nombre de sites : "
        f"{energy_df['site_id'].nunique()}"
    )

    print(
        f"Nombre de sources d'énergie : "
        f"{energy_df['energy_source_id'].nunique()}"
    )

    print(
        f"Consommation totale : "
        f"{energy_df['energy_consumption_kwh'].sum():,.2f} kWh"
    )

    print(
        f"Coût énergétique total : "
        f"{energy_df['energy_cost'].sum():,.2f} €"
    )

    print(
        f"Fichier généré : {output_path}"
    )


if __name__ == "__main__":
    main()