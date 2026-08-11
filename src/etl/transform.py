"""
Transformation et validation des données extraites.

Ce module prépare les DataFrames issus des fichiers CSV avant
leur chargement dans MySQL.

Responsabilités :
    - vérifier la structure des données ;
    - convertir les types ;
    - vérifier les dates ;
    - vérifier les valeurs NULL ;
    - vérifier les valeurs numériques ;
    - détecter les doublons ;
    - vérifier les identifiants utilisés par les tables de faits ;
    - préparer les données pour le chargement MySQL.

Aucune écriture en base de données n'est effectuée ici.
"""

from __future__ import annotations

from datetime import date

import pandas as pd


# ==========================================================
# CONFIGURATION
# ==========================================================

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

EXPECTED_SITE_IDS = set(range(1, 6))
EXPECTED_PRODUCT_IDS = set(range(1, 11))
EXPECTED_SUPPLIER_IDS = set(range(1, 9))
EXPECTED_TRANSPORT_COMPANY_IDS = set(range(1, 6))
EXPECTED_ENERGY_SOURCE_IDS = set(range(1, 6))


# ==========================================================
# UTILITAIRES GÉNÉRIQUES
# ==========================================================

def validate_required_columns(
    df: pd.DataFrame,
    expected_columns: set[str],
    dataset_name: str,
) -> None:
    """
    Vérifie que toutes les colonnes attendues sont présentes.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    expected_columns : set[str]
        Colonnes obligatoires.

    dataset_name : str
        Nom du jeu de données utilisé dans les messages d'erreur.

    Raises
    ------
    ValueError
        Si une ou plusieurs colonnes sont absentes.
    """

    missing_columns = (
        expected_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"{dataset_name} : colonnes manquantes : "
            f"{sorted(missing_columns)}"
        )


def validate_not_empty(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:
    """
    Vérifie qu'un DataFrame n'est pas vide.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si le DataFrame est vide.
    """

    if df.empty:
        raise ValueError(
            f"{dataset_name} : le DataFrame est vide."
        )


def validate_no_nulls(
    df: pd.DataFrame,
    dataset_name: str,
) -> None:
    """
    Vérifie l'absence de valeurs NULL.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si une valeur NULL est détectée.
    """

    null_counts = df.isna().sum()

    columns_with_nulls = (
        null_counts[
            null_counts > 0
        ]
        .index
        .tolist()
    )

    if columns_with_nulls:
        details = {
            column: int(null_counts[column])
            for column in columns_with_nulls
        }

        raise ValueError(
            f"{dataset_name} : valeurs NULL détectées : "
            f"{details}"
        )


def validate_no_duplicates(
    df: pd.DataFrame,
    columns: list[str],
    dataset_name: str,
) -> None:
    """
    Vérifie l'absence de doublons selon une clé logique.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    columns : list[str]
        Colonnes utilisées pour identifier un doublon.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si des doublons sont détectés.
    """

    duplicates = df.duplicated(
        subset=columns
    )

    if duplicates.any():
        duplicate_count = int(
            duplicates.sum()
        )

        raise ValueError(
            f"{dataset_name} : {duplicate_count} "
            f"doublon(s) détecté(s) pour la clé "
            f"{columns}."
        )


def validate_date_range(
    df: pd.DataFrame,
    date_column: str,
    dataset_name: str,
) -> None:
    """
    Vérifie que les dates sont comprises dans la période
    du projet.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    date_column : str
        Nom de la colonne contenant la date.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si une date est hors de la période configurée.
    """

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce",
    )

    if dates.isna().any():
        raise ValueError(
            f"{dataset_name} : dates invalides dans "
            f"{date_column}."
        )

    minimum_date = dates.min().date()
    maximum_date = dates.max().date()

    if minimum_date < START_DATE:
        raise ValueError(
            f"{dataset_name} : date antérieure à "
            f"{START_DATE} détectée."
        )

    if maximum_date > END_DATE:
        raise ValueError(
            f"{dataset_name} : date postérieure à "
            f"{END_DATE} détectée."
        )


def validate_no_sundays(
    df: pd.DataFrame,
    date_column: str,
    dataset_name: str,
) -> None:
    """
    Vérifie qu'aucune donnée ne correspond à un dimanche.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    date_column : str
        Colonne contenant la date.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si un dimanche est détecté.
    """

    dates = pd.to_datetime(
        df[date_column]
    )

    sunday_rows = dates.dt.dayofweek.eq(6)

    if sunday_rows.any():
        sunday_count = int(
            sunday_rows.sum()
        )

        raise ValueError(
            f"{dataset_name} : {sunday_count} "
            "ligne(s) correspondent à un dimanche."
        )


def validate_positive_values(
    df: pd.DataFrame,
    columns: list[str],
    dataset_name: str,
) -> None:
    """
    Vérifie que les colonnes numériques contiennent
    uniquement des valeurs positives ou nulles.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    columns : list[str]
        Colonnes numériques à contrôler.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si une valeur négative est détectée.
    """

    for column in columns:

        if not pd.api.types.is_numeric_dtype(
            df[column]
        ):
            raise ValueError(
                f"{dataset_name} : la colonne "
                f"{column} n'est pas numérique."
            )

        negative_values = (
            df[column] < 0
        )

        if negative_values.any():
            count = int(
                negative_values.sum()
            )

            raise ValueError(
                f"{dataset_name} : {count} valeur(s) "
                f"négative(s) détectée(s) dans {column}."
            )


def validate_ids(
    df: pd.DataFrame,
    column: str,
    valid_ids: set[int],
    dataset_name: str,
) -> None:
    """
    Vérifie qu'une colonne d'identifiants contient uniquement
    des IDs autorisés.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à vérifier.

    column : str
        Colonne d'identifiants.

    valid_ids : set[int]
        Ensemble des IDs autorisés.

    dataset_name : str
        Nom du jeu de données.

    Raises
    ------
    ValueError
        Si un identifiant inconnu est détecté.
    """

    actual_ids = set(
        df[column].astype(int).unique()
    )

    invalid_ids = (
        actual_ids
        - valid_ids
    )

    if invalid_ids:
        raise ValueError(
            f"{dataset_name} : identifiants inconnus "
            f"dans {column} : {sorted(invalid_ids)}"
        )


# ==========================================================
# PRODUCTION
# ==========================================================

def transform_production(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforme et valide les données de production.

    Returns
    -------
    pandas.DataFrame
        Données de production préparées.
    """

    dataset_name = "production"

    expected_columns = {
        "site_id",
        "product_id",
        "production_date",
        "quantity_produced",
        "production_duration_minutes",
    }

    validate_not_empty(
        df,
        dataset_name,
    )

    validate_required_columns(
        df,
        expected_columns,
        dataset_name,
    )

    result = df.copy()

    result["site_id"] = pd.to_numeric(
        result["site_id"],
        errors="raise",
    ).astype(int)

    result["product_id"] = pd.to_numeric(
        result["product_id"],
        errors="raise",
    ).astype(int)

    result["production_date"] = pd.to_datetime(
        result["production_date"],
        errors="raise",
    )

    result["quantity_produced"] = pd.to_numeric(
        result["quantity_produced"],
        errors="raise",
    )

    result["production_duration_minutes"] = pd.to_numeric(
        result["production_duration_minutes"],
        errors="raise",
    )

    validate_no_nulls(
        result,
        dataset_name,
    )

    validate_date_range(
        result,
        "production_date",
        dataset_name,
    )

    validate_no_sundays(
        result,
        "production_date",
        dataset_name,
    )

    validate_ids(
        result,
        "site_id",
        EXPECTED_SITE_IDS,
        dataset_name,
    )

    validate_ids(
        result,
        "product_id",
        EXPECTED_PRODUCT_IDS,
        dataset_name,
    )

    validate_positive_values(
        result,
        [
            "quantity_produced",
            "production_duration_minutes",
        ],
        dataset_name,
    )

    validate_no_duplicates(
        result,
        [
            "site_id",
            "product_id",
            "production_date",
        ],
        dataset_name,
    )

    return result


# ==========================================================
# ÉNERGIE
# ==========================================================

def transform_energy(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforme et valide les données énergétiques.

    Returns
    -------
    pandas.DataFrame
        Données énergétiques préparées.
    """

    dataset_name = "energy"

    expected_columns = {
        "site_id",
        "energy_source_id",
        "energy_date",
        "energy_consumption_kwh",
        "energy_cost",
    }

    validate_not_empty(
        df,
        dataset_name,
    )

    validate_required_columns(
        df,
        expected_columns,
        dataset_name,
    )

    result = df.copy()

    result["site_id"] = pd.to_numeric(
        result["site_id"],
        errors="raise",
    ).astype(int)

    result["energy_source_id"] = pd.to_numeric(
        result["energy_source_id"],
        errors="raise",
    ).astype(int)

    result["energy_date"] = pd.to_datetime(
        result["energy_date"],
        errors="raise",
    )

    result["energy_consumption_kwh"] = pd.to_numeric(
        result["energy_consumption_kwh"],
        errors="raise",
    )

    result["energy_cost"] = pd.to_numeric(
        result["energy_cost"],
        errors="raise",
    )

    validate_no_nulls(
        result,
        dataset_name,
    )

    validate_date_range(
        result,
        "energy_date",
        dataset_name,
    )

    validate_no_sundays(
        result,
        "energy_date",
        dataset_name,
    )

    validate_ids(
        result,
        "site_id",
        EXPECTED_SITE_IDS,
        dataset_name,
    )

    validate_ids(
        result,
        "energy_source_id",
        EXPECTED_ENERGY_SOURCE_IDS,
        dataset_name,
    )

    validate_positive_values(
        result,
        [
            "energy_consumption_kwh",
            "energy_cost",
        ],
        dataset_name,
    )

    validate_no_duplicates(
        result,
        [
            "site_id",
            "energy_source_id",
            "energy_date",
        ],
        dataset_name,
    )

    return result


# ==========================================================
# EAU
# ==========================================================

def transform_water(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforme et valide les données de consommation d'eau.

    Returns
    -------
    pandas.DataFrame
        Données d'eau préparées.
    """

    dataset_name = "water"

    expected_columns = {
        "site_id",
        "water_date",
        "water_consumption_m3",
        "water_cost",
    }

    validate_not_empty(
        df,
        dataset_name,
    )

    validate_required_columns(
        df,
        expected_columns,
        dataset_name,
    )

    result = df.copy()

    result["site_id"] = pd.to_numeric(
        result["site_id"],
        errors="raise",
    ).astype(int)

    result["water_date"] = pd.to_datetime(
        result["water_date"],
        errors="raise",
    )

    result["water_consumption_m3"] = pd.to_numeric(
        result["water_consumption_m3"],
        errors="raise",
    )

    result["water_cost"] = pd.to_numeric(
        result["water_cost"],
        errors="raise",
    )

    validate_no_nulls(
        result,
        dataset_name,
    )

    validate_date_range(
        result,
        "water_date",
        dataset_name,
    )

    validate_no_sundays(
        result,
        "water_date",
        dataset_name,
    )

    validate_ids(
        result,
        "site_id",
        EXPECTED_SITE_IDS,
        dataset_name,
    )

    validate_positive_values(
        result,
        [
            "water_consumption_m3",
            "water_cost",
        ],
        dataset_name,
    )

    validate_no_duplicates(
        result,
        [
            "site_id",
            "water_date",
        ],
        dataset_name,
    )

    return result


# ==========================================================
# DÉCHETS
# ==========================================================

def transform_waste(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforme et valide les données de déchets.

    Returns
    -------
    pandas.DataFrame
        Données de déchets préparées.
    """

    dataset_name = "waste"

    expected_columns = {
        "site_id",
        "waste_date",
        "waste_type",
        "waste_quantity_kg",
        "recyclable",
    }

    validate_not_empty(
        df,
        dataset_name,
    )

    validate_required_columns(
        df,
        expected_columns,
        dataset_name,
    )

    result = df.copy()

    result["site_id"] = pd.to_numeric(
        result["site_id"],
        errors="raise",
    ).astype(int)

    result["waste_date"] = pd.to_datetime(
        result["waste_date"],
        errors="raise",
    )

    result["waste_type"] = (
        result["waste_type"]
        .astype(str)
        .str.strip()
    )

    result["waste_quantity_kg"] = pd.to_numeric(
        result["waste_quantity_kg"],
        errors="raise",
    )

    # Conversion explicite des valeurs booléennes.
    result["recyclable"] = result[
        "recyclable"
    ].astype(str).str.lower().map(
        {
            "true": True,
            "false": False,
        }
    )

    validate_no_nulls(
        result,
        dataset_name,
    )

    validate_date_range(
        result,
        "waste_date",
        dataset_name,
    )

    validate_no_sundays(
        result,
        "waste_date",
        dataset_name,
    )

    validate_ids(
        result,
        "site_id",
        EXPECTED_SITE_IDS,
        dataset_name,
    )

    validate_positive_values(
        result,
        [
            "waste_quantity_kg",
        ],
        dataset_name,
    )

    validate_no_duplicates(
        result,
        [
            "site_id",
            "waste_date",
            "waste_type",
        ],
        dataset_name,
    )

    return result


# ==========================================================
# TRANSPORT
# ==========================================================

def transform_transport(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforme et valide les données de transport.

    Returns
    -------
    pandas.DataFrame
        Données de transport préparées.
    """

    dataset_name = "transport"

    expected_columns = {
        "supplier_id",
        "transport_company_id",
        "site_id",
        "transport_date",
        "distance_km",
        "co2_emissions_kg",
        "transport_cost",
        "transported_weight_kg",
    }

    validate_not_empty(
        df,
        dataset_name,
    )

    validate_required_columns(
        df,
        expected_columns,
        dataset_name,
    )

    result = df.copy()

    result["supplier_id"] = pd.to_numeric(
        result["supplier_id"],
        errors="raise",
    ).astype(int)

    result["transport_company_id"] = pd.to_numeric(
        result["transport_company_id"],
        errors="raise",
    ).astype(int)

    result["site_id"] = pd.to_numeric(
        result["site_id"],
        errors="raise",
    ).astype(int)

    result["transport_date"] = pd.to_datetime(
        result["transport_date"],
        errors="raise",
    )

    result["distance_km"] = pd.to_numeric(
        result["distance_km"],
        errors="raise",
    )

    result["co2_emissions_kg"] = pd.to_numeric(
        result["co2_emissions_kg"],
        errors="raise",
    )

    result["transport_cost"] = pd.to_numeric(
        result["transport_cost"],
        errors="raise",
    )

    result["transported_weight_kg"] = pd.to_numeric(
        result["transported_weight_kg"],
        errors="raise",
    )

    validate_no_nulls(
        result,
        dataset_name,
    )

    validate_date_range(
        result,
        "transport_date",
        dataset_name,
    )

    validate_no_sundays(
        result,
        "transport_date",
        dataset_name,
    )

    validate_ids(
        result,
        "supplier_id",
        EXPECTED_SUPPLIER_IDS,
        dataset_name,
    )

    validate_ids(
        result,
        "transport_company_id",
        EXPECTED_TRANSPORT_COMPANY_IDS,
        dataset_name,
    )

    validate_ids(
        result,
        "site_id",
        EXPECTED_SITE_IDS,
        dataset_name,
    )

    validate_positive_values(
        result,
        [
            "distance_km",
            "co2_emissions_kg",
            "transport_cost",
            "transported_weight_kg",
        ],
        dataset_name,
    )

    validate_no_duplicates(
        result,
        [
            "supplier_id",
            "site_id",
            "transport_date",
        ],
        dataset_name,
    )

    return result


# ==========================================================
# TRANSFORMATION COMPLÈTE
# ==========================================================

def transform_all(
    data: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """
    Transforme et valide tous les jeux de données extraits.

    Parameters
    ----------
    data : dict[str, pandas.DataFrame]
        Données extraites par extract_all().

    Returns
    -------
    dict[str, pandas.DataFrame]
        Données transformées et validées.
    """

    required_datasets = {
        "production",
        "energy",
        "water",
        "waste",
        "transport",
    }

    missing_datasets = (
        required_datasets
        - set(data.keys())
    )

    if missing_datasets:
        raise ValueError(
            "Jeux de données manquants : "
            f"{sorted(missing_datasets)}"
        )

    return {
        "production": transform_production(
            data["production"]
        ),
        "energy": transform_energy(
            data["energy"]
        ),
        "water": transform_water(
            data["water"]
        ),
        "waste": transform_waste(
            data["waste"]
        ),
        "transport": transform_transport(
            data["transport"]
        ),
    }