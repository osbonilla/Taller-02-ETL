"""
utils/es_client.py
-------------------
Punto unico de creacion del cliente de Elasticsearch.

Se centraliza aqui para no repetir `Elasticsearch(host, ...)` en cada
extractor/loader y para poder ajustar timeouts/reintentos en un solo
lugar si el proyecto crece.
"""

from __future__ import annotations

from elasticsearch import Elasticsearch

from config.settings import get_settings

_client: Elasticsearch | None = None


def get_es_client() -> Elasticsearch:
    global _client
    if _client is None:
        settings = get_settings().elasticsearch
        _client = Elasticsearch(
            settings.host,
            request_timeout=settings.request_timeout,
        )
    return _client


def es_is_ready() -> bool:
    """Chequeo de salud usado por utils.wait_for.wait_for().

    Comprobamos el cluster health en vez de solo el ping TCP: un ES que
    responde pero todavia esta inicializando shards internos puede fallar
    bulk inserts. Aceptamos 'yellow' (normal en un cluster de un solo nodo,
    ya que las replicas nunca podran asignarse) y 'green'.
    """
    client = get_es_client()
    health = client.cluster.health(wait_for_status="yellow", timeout="5s")
    return health.get("status") in ("yellow", "green")
