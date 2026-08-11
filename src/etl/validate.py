"""
Validation des données transformées par rapport aux tables
de référence présentes dans MySQL.

Ce module vérifie que les identifiants utilisés dans les
tables de faits correspondent réellement aux identifiants
présents dans les tables de référence.

Aucune donnée n'est modifiée ou insérée dans MySQL.
"""

from __future__ import annotations

import pandas as pd
from mysql.connector import MySQLConnection


# ==========================================================
# VALIDATION DES CLÉS ÉTRANGÈRES
# ==========================================================

def validate_foreign_key(
    df: pd.DataFrame,
    dataframe_column: str,
    reference_table: str,
    reference_column: str,
    connection: MySQLConnection,
    dataset_name: str,
) -> None:
    """
    Vérifie qu'une colonne d'un DataFrame contient uniquement
    des identifiants existant dans une table de référence MySQL.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame à contrôler.

    dataframe_column : str
        Colonne contenant la clé étrangère.

    reference_table : str
        Table MySQL contenant les identifiants valides.

    reference_column : str
        Colonne MySQL contenant les identifiants valides.

    connection : MySQLConnection
        Connexion active à MySQL.

    dataset_name : str
        Nom du dataset utilisé dans les messages d'erreur.

    Raises
    ------
    ValueError
        Si un identifiant présent dans le DataFrame
        n'existe pas dans la table de référence.
    """

    query = f"""
        SELECT `{reference_column}`
        FROM `{reference_table}`
    """

    cursor = connection.cursor()

    try:
        cursor.execute(query)

        valid_ids = {
            int(row[0])
            for row in cursor.fetchall()
        }

    finally:
        cursor.close()

    actual_ids = set(
        df[dataframe_column]
        .astype(int)
        .unique()
        .tolist()
    )

    invalid_ids = actual_ids - valid_ids

    if invalid_ids:
        raise ValueError(
            f"{dataset_name} : identifiants inconnus "
            f"dans {dataframe_column} pour "
            f"{reference_table}.{reference_column} : "
            f"{sorted(invalid_ids)}"
        )
# ==========================================================
# PRODUCTION
# ==========================================================

def validate_production_references(
    df: pd.DataFrame,
    connection: MySQLConnection,
) -> None:
    """
    Valide les références utilisées par production.
    """

    validate_foreign_key(
        df,
        "site_id",
        "site",
        "site_id",
        connection,
        "production",
    )

    validate_foreign_key(
        df,
        "product_id",
        "product",
        "product_id",
        connection,
        "production",
    )


# ==========================================================
# ÉNERGIE
# ==========================================================

def validate_energy_references(
    df: pd.DataFrame,
    connection: MySQLConnection,
) -> None:
    """
    Valide les références utilisées par energy.
    """

    validate_foreign_key(
        df,
        "site_id",
        "site",
        "site_id",
        connection,
        "energy",
    )

    validate_foreign_key(
        df,
        "energy_source_id",
        "energy_source",
        "energy_source_id",
        connection,
        "energy",
    )


# ==========================================================
# EAU
# ==========================================================

def validate_water_references(
    df: pd.DataFrame,
    connection: MySQLConnection,
) -> None:
    """
    Valide les références utilisées par water.
    """

    validate_foreign_key(
        df,
        "site_id",
        "site",
        "site_id",
        connection,
        "water",
    )


# ==========================================================
# DÉCHETS
# ==========================================================

def validate_waste_references(
    df: pd.DataFrame,
    connection: MySQLConnection,
) -> None:
    """
    Valide les références utilisées par waste.
    """

    validate_foreign_key(
        df,
        "site_id",
        "site",
        "site_id",
        connection,
        "waste",
    )


# ==========================================================
# TRANSPORT
# ==========================================================

def validate_transport_references(
    df: pd.DataFrame,
    connection: MySQLConnection,
) -> None:
    """
    Valide les références utilisées par transport.
    """

    validate_foreign_key(
        df,
        "site_id",
        "site",
        "site_id",
        connection,
        "transport",
    )

    validate_foreign_key(
        df,
        "supplier_id",
        "supplier",
        "supplier_id",
        connection,
        "transport",
    )

    validate_foreign_key(
        df,
        "transport_company_id",
        "transport_company",
        "transport_company_id",
        connection,
        "transport",
    )


# ==========================================================
# VALIDATION COMPLÈTE
# ==========================================================

def validate_all_references(
    data: dict[str, pd.DataFrame],
    connection: MySQLConnection,
) -> None:
    """
    Valide les clés étrangères de tous les datasets.

    Parameters
    ----------
    data : dict[str, pandas.DataFrame]
        DataFrames transformés.

    connection : MySQLConnection
        Connexion active à MySQL.
    """

    validate_production_references(
        data["production"],
        connection,
    )

    validate_energy_references(
        data["energy"],
        connection,
    )

    validate_water_references(
        data["water"],
        connection,
    )

    validate_waste_references(
        data["waste"],
        connection,
    )

    validate_transport_references(
        data["transport"],
        connection,
    )