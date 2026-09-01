"""
DAG Airflow - Industrial Sustainability Data Platform

Orchestration du pipeline :

1. Exécution du pipeline ETL Python
2. Exécution des transformations dbt
3. Exécution des tests dbt
"""

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from src.etl.pipeline import run_pipeline


# ==========================================================
# CONFIGURATION DU DAG
# ==========================================================

default_args = {
    "owner": "helios",
    "retries": 2,
}


with DAG(
    dag_id="sustainability_pipeline",
    description="Pipeline de données de Helios Industrial Group",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["helios", "sustainability", "etl"],
) as dag:

    # ------------------------------------------------------
    # 1. ETL PYTHON
    # ------------------------------------------------------

    run_etl = PythonOperator(
        task_id="run_etl",
        python_callable=run_pipeline,
    )

    # ------------------------------------------------------
    # 2. DBT RUN
    # ------------------------------------------------------

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command="cd /opt/airflow/dbt && dbt run",
    )

    # ------------------------------------------------------
    # 3. DBT TEST
    # ------------------------------------------------------

    test_dbt = BashOperator(
        task_id="test_dbt",
        bash_command="cd /opt/airflow/dbt && dbt test",
    )

    # ------------------------------------------------------
    # PIPELINE
    # ------------------------------------------------------

    run_etl >> run_dbt >> test_dbt