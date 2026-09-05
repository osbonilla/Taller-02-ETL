"""
airflow/dags/batch_pipeline_dag.py
-------------------------------------
DAG de REFERENCIA — Apache Airflow 3.x (Task SDK / TaskFlow API).

Este DAG NO forma parte del docker-compose.yml principal del taller.
Decision de diseno (ver README, "Decisiones de diseno > Por que Airflow es
opcional"): levantar Airflow completo exige su propio webserver,
scheduler y base de datos de metadatos — varios contenedores y GB de RAM
adicionales — para un taller INDIVIDUAL que ya corre 10 contenedores
(Elasticsearch, Kibana, Logstash, MySQL, PostgreSQL, MongoDB, 2 servicios
Python de aplicacion y 2 de inicializacion). El batch por defecto usa un
orquestador Python simple con su propio loop y reintentos
(python/pipelines/batch_pipeline.py), que cubre el mismo requisito
academico (schedule, retries, logging, tareas separadas) sin ese costo.

Este archivo demuestra COMO se veria la orquestacion de ese MISMO flujo
si Airflow estuviera disponible, reutilizando las funciones existentes de
extractors/transformers/loaders (no se duplica logica de negocio).

Para probarlo (opcional, requiere una instalacion de Airflow 3.x aparte):
  1. Copiar este archivo a $AIRFLOW_HOME/dags/
  2. Incluir el paquete python/ (extractors, transformers, loaders,
     validators, config, utils) en el PYTHONPATH del entorno de Airflow.
  3. Definir en ese entorno las mismas variables de entorno que usa
     python-batch (ver .env.example): ES_HOST, MYSQL_*, POSTGRES_*, MONGO_*.

Nota sobre la API usada: Airflow 3.0 introdujo el Task SDK
(`airflow.sdk`) como interfaz publica recomendada para autoria de DAGs,
reemplazando `from airflow import DAG` / `from airflow.decorators import
dag, task` de Airflow 2.x. Si el entorno destino todavia usa Airflow 2.x,
el equivalente es:
    from airflow import DAG
    from airflow.decorators import dag, task
    from airflow.operators.python import PythonOperator
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.sdk import dag, task

default_args = {
    "owner": "taller-etl",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
}


@dag(
    dag_id="taller02_batch_pipeline",
    description="Batch ETL: CSV + MySQL + PostgreSQL + MongoDB -> Elasticsearch",
    schedule="*/30 * * * *",  # cada 30 minutos; ajustar segun necesidad del curso
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["taller-02-etl", "batch", "etl"],
)
def taller02_batch_pipeline():
    """Cada fuente es una tarea independiente (extraer+validar+transformar+
    cargar, delegado a pipelines.batch_pipeline) para que el fallo de UNA
    fuente no bloquee a las demas ni oculte cual fallo — mismo principio de
    resiliencia que _run_source() en pipelines/batch_pipeline.py, ahora
    expresado como tareas de Airflow con reintentos independientes.

    Los imports van DENTRO de cada tarea (no al inicio del archivo) porque
    Airflow re-parsea los archivos de DAGs frecuentemente para refrescar
    la UI; mantener el "codigo de nivel superior" liviano es una practica
    recomendada explicitamente por la documentacion de Airflow.
    """

    @task
    def run_csv() -> dict:
        from pipelines.batch_pipeline import run_csv_batch
        stats = run_csv_batch()
        if stats.error:
            raise RuntimeError(f"Fuente CSV fallo: {stats.error}")
        return {"source": stats.source, "loaded": stats.loaded, "errors": stats.load_errors}

    @task
    def run_mysql() -> dict:
        from pipelines.batch_pipeline import run_mysql_batch
        stats = run_mysql_batch()
        if stats.error:
            raise RuntimeError(f"Fuente MySQL fallo: {stats.error}")
        return {"source": stats.source, "loaded": stats.loaded, "errors": stats.load_errors}

    @task
    def run_postgres() -> dict:
        from pipelines.batch_pipeline import run_postgres_batch
        stats = run_postgres_batch()
        if stats.error:
            raise RuntimeError(f"Fuente PostgreSQL fallo: {stats.error}")
        return {"source": stats.source, "loaded": stats.loaded, "errors": stats.load_errors}

    @task
    def run_mongo() -> dict:
        from pipelines.batch_pipeline import run_mongo_batch
        stats = run_mongo_batch()
        if stats.error:
            raise RuntimeError(f"Fuente MongoDB fallo: {stats.error}")
        return {"source": stats.source, "loaded": stats.loaded, "errors": stats.load_errors}

    @task
    def summarize(resultados: list) -> None:
        import logging

        logger = logging.getLogger("taller02_batch_pipeline.summarize")
        total_cargados = sum(r["loaded"] for r in resultados)
        logger.info("Resumen del ciclo batch: %s (total documentos cargados=%d)", resultados, total_cargados)

    resultados = [run_csv(), run_mysql(), run_postgres(), run_mongo()]
    summarize(resultados)


taller02_batch_pipeline()
