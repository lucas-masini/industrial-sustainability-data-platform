FROM apache/airflow:2.10.4

USER root

RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER airflow

RUN pip install --no-cache-dir \
    "dbt-core==1.7.9" \
    "dbt-mysql==1.7.0" \
    "protobuf<5" \
    pandas \
    mysql-connector-python