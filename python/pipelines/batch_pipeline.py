"""
pipelines/batch_pipeline.py
------------------------------
Orquestador del flujo BATCH del taller.

Cubre 4 de las fuentes del diagrama: CSV, MySQL, PostgreSQL y MongoDB.
(LOG y JSON se procesan aparte, directamente en Logstash; el evento
near-real-time lo genera producers/event_producer.py.)

Este modulo es, en terminos del taller, donde ocurre el ETL:

    EXTRACT  -> extractors.*  (leer el dato crudo de la fuente)
    TRANSFORM-> validators + transformers  (limpiar, tipar, enriquecer)
    LOAD     -> loaders.es_loader  (bulk insert a Elasticsearch)

Es ETL y no ELT porque la transformacion ocurre en Python ANTES de que el
dato toque Elasticsearch. (Contraste: en el pipeline near-real-time,
Logstash hace "ship" del dato con transformaciones minimas y el filtro
vive junto al transporte; para LOG/JSON el parseo grok/json en Logstash
tambien es, estrictamente, T-antes-de-L, pero mas acoplado al transporte
que en este modulo. La discusion completa esta en el README.)

Diseno de resiliencia: cada fuente se procesa en su propio try/except.
Si MySQL estuviera caido, por ejemplo, el batch de CSV/Postgres/Mongo
igual se ejecuta y se reporta claramente cual fuente fallo, en vez de que
una excepcion en una fuente tumbe todo el proceso.

Este orquestador puede ejecutarse:
  - en loop (comportamiento por defecto en el contenedor python-batch,
    simulando un batch programado cada BATCH_INTERVAL_SECONDS), o
  - una sola vez, con BATCH_RUN_ONCE=true (util para pruebas manuales o
    para ejecutarlo bajo Airflow, ver airflow/dags/batch_pipeline_dag.py).
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from config.settings import get_settings
from extractors.csv_extractor import extract_ventas_csv
from extractors.mongo_extractor import extract_inventario, mongo_is_ready
from extractors.mysql_extractor import extract_usuarios, mysql_is_ready
from extractors.postgres_extractor import extract_clientes, postgres_is_ready
from loaders.es_loader import load_to_elasticsearch
from transformers.transformers import (
    normalize_cliente_postgres,
    normalize_producto_mongo,
    normalize_usuario_mysql,
    normalize_venta,
)
from utils.es_client import es_is_ready
from utils.logger import get_logger
from utils.wait_for import DependencyNotReadyError, wait_for
from validators.validators import validate_record

logger = get_logger("pipelines.batch")


@dataclass
class SourceRunStats:
    source: str
    extracted: int = 0
    valid: int = 0
    invalid: int = 0
    loaded: int = 0
    load_errors: int = 0
    error: str | None = None
    validation_errors_sample: list[str] = field(default_factory=list)

    def log_summary(self) -> None:
        if self.error:
            logger.error("[%s] FALLO: %s", self.source, self.error)
            return
        logger.info(
            "[%s] extraidos=%d validos=%d invalidos=%d cargados=%d errores_carga=%d",
            self.source, self.extracted, self.valid, self.invalid, self.loaded, self.load_errors,
        )
        if self.validation_errors_sample:
            logger.warning(
                "[%s] ejemplo de errores de validacion: %s",
                self.source, self.validation_errors_sample[:3],
            )


def _run_source(
    source_name: str,
    index_name: str,
    extract_fn,
    normalize_fn,
    *,
    required_fields: tuple[str, ...],
    positive_number_fields: tuple[str, ...] = (),
    date_fields: tuple[str, ...] = (),
) -> SourceRunStats:
    stats = SourceRunStats(source=source_name)
    try:
        raw_rows = extract_fn()
        stats.extracted = len(raw_rows)

        to_load = []
        for row in raw_rows:
            result = validate_record(
                row,
                required_fields=required_fields,
                positive_number_fields=positive_number_fields,
                date_fields=date_fields,
            )
            if result.is_valid:
                stats.valid += 1
                to_load.append(normalize_fn(row))
            else:
                stats.invalid += 1
                if len(stats.validation_errors_sample) < 5:
                    stats.validation_errors_sample.extend(result.errors)

        if to_load:
            loaded, errors = load_to_elasticsearch(index_name, to_load)
            stats.loaded = loaded
            stats.load_errors = errors if isinstance(errors, int) else len(errors)

    except Exception as exc:  # noqa: BLE001 - un fallo por fuente no debe tumbar el batch completo
        stats.error = f"{type(exc).__name__}: {exc}"
        logger.exception("Error procesando la fuente '%s'", source_name)

    return stats


def run_csv_batch() -> SourceRunStats:
    settings = get_settings().pipeline
    csv_path = settings.data_raw_dir / "ventas.csv"
    return _run_source(
        "csv-ventas",
        "ventas-csv",
        lambda: extract_ventas_csv(csv_path),
        normalize_venta,
        required_fields=("venta_id", "fecha", "producto", "categoria", "cantidad", "precio_unitario", "total"),
        positive_number_fields=("cantidad", "precio_unitario", "total"),
        date_fields=("fecha",),
    )


def run_mysql_batch() -> SourceRunStats:
    return _run_source(
        "mysql-usuarios",
        "mysql-usuarios",
        extract_usuarios,
        normalize_usuario_mysql,
        required_fields=("usuario_id", "nombre", "email"),
        date_fields=("fecha_registro",),
    )


def run_postgres_batch() -> SourceRunStats:
    return _run_source(
        "postgres-clientes",
        "postgres-clientes",
        extract_clientes,
        normalize_cliente_postgres,
        required_fields=("cliente_id", "nombre_empresa"),
        positive_number_fields=("ingresos_anuales",),
        date_fields=("fecha_alta",),
    )


def run_mongo_batch() -> SourceRunStats:
    return _run_source(
        "mongo-inventario",
        "mongo-productos",
        extract_inventario,
        normalize_producto_mongo,
        required_fields=("producto_id", "nombre", "categoria"),
        positive_number_fields=("stock", "precio"),
    )


def run_batch_cycle(cycle_number: int) -> list[SourceRunStats]:
    logger.info("===== Iniciando ciclo de batch #%d =====", cycle_number)
    results = [
        run_csv_batch(),
        run_mysql_batch(),
        run_postgres_batch(),
        run_mongo_batch(),
    ]
    for stats in results:
        stats.log_summary()

    total_loaded = sum(r.loaded for r in results)
    total_errors = sum(1 for r in results if r.error is not None)
    logger.info(
        "===== Ciclo #%d finalizado: %d documentos cargados en total, %d fuentes con fallo =====",
        cycle_number, total_loaded, total_errors,
    )
    return results


def wait_for_dependencies() -> None:
    logger.info("Verificando dependencias antes de iniciar el batch...")
    wait_for(es_is_ready, name="elasticsearch")
    wait_for(mysql_is_ready, name="mysql")
    wait_for(postgres_is_ready, name="postgres")
    wait_for(mongo_is_ready, name="mongodb")
    logger.info("Todas las dependencias estan listas.")


def main() -> int:
    settings = get_settings().pipeline

    try:
        wait_for_dependencies()
    except DependencyNotReadyError as exc:
        logger.error("No se pudo iniciar el batch: %s", exc)
        return 1

    cycle = 0
    while True:
        cycle += 1
        run_batch_cycle(cycle)

        if settings.run_once:
            logger.info("BATCH_RUN_ONCE=true -> el proceso termina aqui (codigo de salida 0).")
            return 0

        logger.info("Durmiendo %ds antes del siguiente ciclo de batch...", settings.batch_interval_seconds)
        time.sleep(settings.batch_interval_seconds)


if __name__ == "__main__":
    sys.exit(main())
