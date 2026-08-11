"""
Point d'entrée principal du pipeline ETL.

Le pipeline exécute les différentes étapes dans l'ordre :

1. Extraction des données depuis les fichiers CSV.
2. Transformation et validation des données.
3. Validation des clés étrangères avec MySQL.
4. Chargement des données dans MySQL.

Le chargement est transactionnel et idempotent.
"""

from __future__ import annotations

from src.etl.extract import extract_all
from src.etl.transform import transform_all
from src.etl.validate import validate_all_references
from src.etl.load import get_mysql_connection, load_all


# ==========================================================
# PIPELINE ETL
# ==========================================================

def run_pipeline() -> dict[str, int]:
    """
    Exécute l'ensemble du pipeline ETL.

    Returns
    -------
    dict[str, int]
        Nombre de lignes traitées pour chaque table.

    Raises
    ------
    Exception
        Si une étape du pipeline échoue.
    """

    print("=" * 60)
    print("DÉMARRAGE DU PIPELINE ETL")
    print("=" * 60)

    # ------------------------------------------------------
    # 1. EXTRACT
    # ------------------------------------------------------

    print("\n[1/4] Extraction des données...")

    raw_data = extract_all()

    for name, df in raw_data.items():
        print(
            f"  ✓ {name}: "
            f"{len(df)} lignes extraites"
        )

    # ------------------------------------------------------
    # 2. TRANSFORM
    # ------------------------------------------------------

    print("\n[2/4] Transformation des données...")

    transformed_data = transform_all(
        raw_data
    )

    for name, df in transformed_data.items():
        print(
            f"  ✓ {name}: "
            f"{len(df)} lignes transformées"
        )

    # ------------------------------------------------------
    # 3. VALIDATION MYSQL
    # ------------------------------------------------------

    print("\n[3/4] Validation des références MySQL...")

    connection = get_mysql_connection()

    try:
        validate_all_references(
            transformed_data,
            connection,
        )

        print(
            "  ✓ Toutes les références MySQL "
            "sont valides."
        )

        # --------------------------------------------------
        # 4. LOAD
        # --------------------------------------------------

        print("\n[4/4] Chargement dans MySQL...")

        result = load_all(
            transformed_data,
            connection,
        )

        for name, count in result.items():
            print(
                f"  ✓ {name}: "
                f"{count} lignes traitées"
            )

    finally:
        connection.close()

    # ------------------------------------------------------
    # RÉSUMÉ
    # ------------------------------------------------------

    total_rows = sum(result.values())

    print("\n" + "=" * 60)
    print("PIPELINE ETL TERMINÉ AVEC SUCCÈS")
    print("=" * 60)

    print("\nRésumé :")

    for name, count in result.items():
        print(
            f"  {name:<12} : {count:>6} lignes"
        )

    print(
        f"  {'TOTAL':<12} : {total_rows:>6} lignes"
    )

    print("=" * 60)

    return result


# ==========================================================
# POINT D'ENTRÉE
# ==========================================================

if __name__ == "__main__":
    run_pipeline()