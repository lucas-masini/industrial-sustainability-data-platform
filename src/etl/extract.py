"""
Extraction des données brutes utilisées par le pipeline ETL.

Ce module lit les fichiers CSV générés dans data/raw/
et les charge dans des DataFrames Pandas.

Aucune transformation métier ni écriture en base de données
n'est effectuée dans ce module.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import PROJECT_ROOT


# ==========================================================
# CHEMIN DES DONNÉES BRUTES
# ==========================================================

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"


# ==========================================================
# FONCTION GÉNÉRIQUE DE LECTURE
# ==========================================================

def extract_csv(
    filename: str,
    date_columns: list[str] | None = None,
) -> pd.DataFrame:
    """
    Lit un fichier CSV depuis le dossier data/raw/.

    Parameters
    ----------
    filename : str
        Nom du fichier CSV à lire.

    date_columns : list[str] | None
        Colonnes à convertir automatiquement en dates.

    Returns
    -------
    pandas.DataFrame
        Données extraites du fichier CSV.

    Raises
    ------
    FileNotFoundError
        Si le fichier demandé n'existe pas.
    """

    file_path = RAW_DATA_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {file_path}"
        )

    return pd.read_csv(
        file_path,
        parse_dates=date_columns,
    )


# ==========================================================
# PRODUCTION
# ==========================================================

def extract_production() -> pd.DataFrame:
    """
    Extrait les données de production.

    Returns
    -------
    pandas.DataFrame
        Données du fichier production.csv.
    """

    return extract_csv(
        "production.csv",
        date_columns=["production_date"],
    )


# ==========================================================
# ÉNERGIE
# ==========================================================

def extract_energy() -> pd.DataFrame:
    """
    Extrait les données de consommation énergétique.

    Returns
    -------
    pandas.DataFrame
        Données du fichier energy.csv.
    """

    return extract_csv(
        "energy.csv",
        date_columns=["energy_date"],
    )


# ==========================================================
# EAU
# ==========================================================

def extract_water() -> pd.DataFrame:
    """
    Extrait les données de consommation d'eau.

    Returns
    -------
    pandas.DataFrame
        Données du fichier water.csv.
    """

    return extract_csv(
        "water.csv",
        date_columns=["water_date"],
    )


# ==========================================================
# DÉCHETS
# ==========================================================

def extract_waste() -> pd.DataFrame:
    """
    Extrait les données de déchets.

    Returns
    -------
    pandas.DataFrame
        Données du fichier waste.csv.
    """

    return extract_csv(
        "waste.csv",
        date_columns=["waste_date"],
    )


# ==========================================================
# TRANSPORT
# ==========================================================

def extract_transport() -> pd.DataFrame:
    """
    Extrait les données de transport.

    Returns
    -------
    pandas.DataFrame
        Données du fichier transport.csv.
    """

    return extract_csv(
        "transport.csv",
        date_columns=["transport_date"],
    )


# ==========================================================
# EXTRACTION COMPLÈTE
# ==========================================================

def extract_all() -> dict[str, pd.DataFrame]:
    """
    Extrait l'ensemble des données brutes du projet.

    Returns
    -------
    dict[str, pandas.DataFrame]
        Dictionnaire contenant un DataFrame par table de faits.
    """

    return {
        "production": extract_production(),
        "energy": extract_energy(),
        "water": extract_water(),
        "waste": extract_waste(),
        "transport": extract_transport(),
    }