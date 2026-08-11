"""
Fonctions responsables du chargement des données transformées
dans les tables de faits MySQL.

Les tables de référence sont déjà présentes dans MySQL et ne
sont pas modifiées par ce module.

Le chargement est idempotent :
une même donnée peut être chargée plusieurs fois sans créer
de doublon grâce aux contraintes UNIQUE présentes dans MySQL.
"""

from __future__ import annotations

from typing import Sequence

import mysql.connector
import pandas as pd
from mysql.connector import MySQLConnection

from .config import (
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)


# ==========================================================
# CONNEXION MYSQL
# ==========================================================

def get_mysql_connection() -> MySQLConnection:
    """
    Établit une connexion avec la base MySQL du projet.

    Returns
    -------
    MySQLConnection
        Connexion active à MySQL.
    """

    connection = mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )

    return connection


# ==========================================================
# INSERTION / MISE À JOUR GÉNÉRIQUE
# ==========================================================

def insert_dataframe(
    connection: MySQLConnection,
    df: pd.DataFrame,
    table_name: str,
    columns: Sequence[str],
    update_columns: Sequence[str],
) -> int:
    """
    Insère ou met à jour les données d'un DataFrame dans MySQL.

    Si une ligne possède déjà une combinaison de valeurs
    correspondant à une contrainte UNIQUE, les colonnes de
    données sont mises à jour au lieu de créer un doublon.

    Parameters
    ----------
    connection : MySQLConnection
        Connexion active à MySQL.

    df : pandas.DataFrame
        Données transformées à charger.

    table_name : str
        Nom de la table cible.

    columns : Sequence[str]
        Colonnes à insérer.

    update_columns : Sequence[str]
        Colonnes à mettre à jour en cas de doublon.

    Returns
    -------
    int
        Nombre de lignes traitées.

    Raises
    ------
    ValueError
        Si une colonne attendue est absente du DataFrame.
    """

    missing_columns = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{table_name} : colonnes manquantes : "
            f"{missing_columns}"
        )

    invalid_update_columns = [
        column
        for column in update_columns
        if column not in columns
    ]

    if invalid_update_columns:
        raise ValueError(
            f"{table_name} : colonnes de mise à jour invalides : "
            f"{invalid_update_columns}"
        )

    if df.empty:
        return 0

    column_list = ", ".join(
        f"`{column}`"
        for column in columns
    )

    placeholders = ", ".join(
        ["%s"] * len(columns)
    )

    update_clause = ", ".join(
        f"`{column}` = VALUES(`{column}`)"
        for column in update_columns
    )

    query = f"""
        INSERT INTO `{table_name}`
        ({column_list})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
        {update_clause}
    """

    rows = [
        tuple(row)
        for row in df[list(columns)].itertuples(
            index=False,
            name=None,
        )
    ]

    cursor = connection.cursor()

    try:
        cursor.executemany(
            query,
            rows,
        )

    finally:
        cursor.close()

    return len(rows)


# ==========================================================
# PRODUCTION
# ==========================================================

def load_production(
    connection: MySQLConnection,
    df: pd.DataFrame,
) -> int:
    """
    Charge les données de production dans MySQL.
    """

    columns = [
        "site_id",
        "product_id",
        "production_date",
        "quantity_produced",
        "production_duration_minutes",
    ]

    update_columns = [
        "quantity_produced",
        "production_duration_minutes",
    ]

    return insert_dataframe(
        connection,
        df,
        "production",
        columns,
        update_columns,
    )


# ==========================================================
# ÉNERGIE
# ==========================================================

def load_energy(
    connection: MySQLConnection,
    df: pd.DataFrame,
) -> int:
    """
    Charge les données énergétiques dans MySQL.
    """

    columns = [
        "site_id",
        "energy_source_id",
        "energy_date",
        "energy_consumption_kwh",
        "energy_cost",
    ]

    update_columns = [
        "energy_consumption_kwh",
        "energy_cost",
    ]

    return insert_dataframe(
        connection,
        df,
        "energy",
        columns,
        update_columns,
    )


# ==========================================================
# EAU
# ==========================================================

def load_water(
    connection: MySQLConnection,
    df: pd.DataFrame,
) -> int:
    """
    Charge les données de consommation d'eau dans MySQL.
    """

    columns = [
        "site_id",
        "water_date",
        "water_consumption_m3",
        "water_cost",
    ]

    update_columns = [
        "water_consumption_m3",
        "water_cost",
    ]

    return insert_dataframe(
        connection,
        df,
        "water",
        columns,
        update_columns,
    )


# ==========================================================
# DÉCHETS
# ==========================================================

def load_waste(
    connection: MySQLConnection,
    df: pd.DataFrame,
) -> int:
    """
    Charge les données de déchets dans MySQL.
    """

    columns = [
        "site_id",
        "waste_date",
        "waste_type",
        "waste_quantity_kg",
        "recyclable",
    ]

    update_columns = [
        "waste_quantity_kg",
        "recyclable",
    ]

    return insert_dataframe(
        connection,
        df,
        "waste",
        columns,
        update_columns,
    )


# ==========================================================
# TRANSPORT
# ==========================================================

def load_transport(
    connection: MySQLConnection,
    df: pd.DataFrame,
) -> int:
    """
    Charge les données de transport dans MySQL.
    """

    columns = [
        "supplier_id",
        "transport_company_id",
        "site_id",
        "transport_date",
        "distance_km",
        "co2_emissions_kg",
        "transport_cost",
        "transported_weight_kg",
    ]

    update_columns = [
        "transport_company_id",
        "distance_km",
        "co2_emissions_kg",
        "transport_cost",
        "transported_weight_kg",
    ]

    return insert_dataframe(
        connection,
        df,
        "transport",
        columns,
        update_columns,
    )


# ==========================================================
# CHARGEMENT COMPLET
# ==========================================================

def load_all(
    data: dict[str, pd.DataFrame],
    connection: MySQLConnection,
) -> dict[str, int]:
    """
    Charge tous les jeux de données dans MySQL.

    Une transaction unique est utilisée pour l'ensemble
    du chargement.

    Si une erreur survient, toutes les opérations sont
    annulées avec un rollback.

    Parameters
    ----------
    data : dict[str, pandas.DataFrame]
        DataFrames transformés et validés.

    connection : MySQLConnection
        Connexion active à MySQL.

    Returns
    -------
    dict[str, int]
        Nombre de lignes traitées par table.

    Raises
    ------
    Exception
        Si une erreur survient pendant le chargement.
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

    processed_rows: dict[str, int] = {}

    try:
        processed_rows["production"] = load_production(
            connection,
            data["production"],
        )

        processed_rows["energy"] = load_energy(
            connection,
            data["energy"],
        )

        processed_rows["water"] = load_water(
            connection,
            data["water"],
        )

        processed_rows["waste"] = load_waste(
            connection,
            data["waste"],
        )

        processed_rows["transport"] = load_transport(
            connection,
            data["transport"],
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    return processed_rows