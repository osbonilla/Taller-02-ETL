"""
loaders/es_loader.py
----------------------
Carga masiva (bulk) de documentos a Elasticsearch.

Usa el helper oficial `elasticsearch.helpers.bulk`, que agrupa las
operaciones en lotes (chunk_size configurable via ES_BULK_CHUNK_SIZE) en
vez de hacer una peticion HTTP por documento — esto es lo que en la
practica hace viable indexar miles de documentos sin saturar la red ni la
CPU de Elasticsearch con overhead de conexiones.

Cada elemento de `records` es una tupla (doc_id, doc). El `doc_id` se usa
como `_id` de Elasticsearch: reindexar el mismo `doc_id` SOBRESCRIBE el
documento en vez de duplicarlo (idempotencia — ver transformers.py).
"""

from __future__ import annotations

from typing import Any, Iterable

from elasticsearch.helpers import bulk

from config.settings import get_settings
from utils.es_client import get_es_client
from utils.logger import get_logger

logger = get_logger("loaders.es_loader")


def load_to_elasticsearch(
    index_name: str,
    records: Iterable[tuple[str, dict[str, Any]]],
) -> tuple[int, int]:
    """Indexa `records` en `index_name`. Devuelve (exitosos, fallidos)."""
    settings = get_settings().elasticsearch
    client = get_es_client()
    full_index_name = f"{settings.index_prefix}-{index_name}"

    actions = (
        {
            "_op_type": "index",
            "_index": full_index_name,
            "_id": doc_id,
            "_source": doc,
        }
        for doc_id, doc in records
    )

    success, errors = bulk(
        client,
        actions,
        chunk_size=settings.bulk_chunk_size,
        raise_on_error=False,
        stats_only=False,
    )

    error_count = len(errors) if isinstance(errors, list) else errors
    if error_count:
        logger.warning(
            "Carga a '%s': %d exitosos, %d con error. Primeros errores: %s",
            full_index_name, success, error_count,
            errors[:3] if isinstance(errors, list) else "N/A",
        )
    else:
        logger.info("Carga a '%s': %d documentos indexados correctamente", full_index_name, success)

    return success, error_count
