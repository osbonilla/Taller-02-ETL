"""
extractors/mongo_extractor.py
--------------------------------
Extraccion de la fuente MongoDB (coleccion `inventario`).

Por que Python + pymongo y no un input de Logstash: Elastic no mantiene
oficialmente un plugin de input para MongoDB (existe uno de la comunidad,
`logstash-input-mongodb`, sin mantenimiento activo confiable y que exige
instalar un plugin adicional via RubyGems dentro del contenedor). Usar
Python con el driver oficial `pymongo` es la opcion mas solida y es
coherente con el mismo criterio aplicado a MySQL/PostgreSQL.
"""

from __future__ import annotations

from typing import Any

from pymongo import MongoClient

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("extractors.mongo")

_client: MongoClient | None = None


def _get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = get_settings().mongo.connection_uri
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def mongo_is_ready() -> bool:
    """Chequeo de salud usado por utils.wait_for.wait_for()."""
    _get_client().admin.command("ping")
    return True


def extract_inventario() -> list[dict[str, Any]]:
    settings = get_settings().mongo
    client = _get_client()
    db = client[settings.database]
    docs = list(db.inventario.find({}))

    # ObjectId no es serializable a JSON; lo convertimos a str o lo
    # descartamos ya que cada documento trae su propia clave natural
    # (producto_id) que usamos como _id en Elasticsearch.
    for doc in docs:
        doc.pop("_id", None)

    logger.info("Extraidos %d documentos desde MongoDB.inventario", len(docs))
    return docs
