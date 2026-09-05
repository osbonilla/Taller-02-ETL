"""
extractors/mysql_extractor.py
-------------------------------
Extraccion de la fuente MySQL (tabla `usuarios`).

Por que Python + SQLAlchemy y no el input jdbc de Logstash (aun cuando el
diagrama del taller muestra MySQL "Ship-eando" directo a Logstash):

  - El input jdbc de Logstash requiere descargar y montar manualmente el
    driver JDBC (.jar) de MySQL dentro del contenedor de Logstash. Es un
    paso fragil (URLs de descarga que cambian de version, licencias, y un
    punto de fallo fuera de nuestro control) para un taller que debe
    "funcionar siempre" en la maquina de quien lo ejecute.
  - Con Python ya tenemos control total de la extraccion (reintentos,
    logging, manejo de errores) sin piezas adicionales.
  - Se documenta igualmente el enfoque jdbc como referencia en
    logstash/pipeline/mysql_jdbc.conf.reference, mostrando que se conoce
    la alternativa nativa de Logstash y por que se opto por la otra.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("extractors.mysql")

_engine: Engine | None = None


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        uri = get_settings().mysql.sqlalchemy_uri
        _engine = create_engine(uri, pool_pre_ping=True)
    return _engine


def mysql_is_ready() -> bool:
    """Chequeo de salud usado por utils.wait_for.wait_for()."""
    with _get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def extract_usuarios() -> list[dict[str, Any]]:
    engine = _get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM usuarios"))
        rows = [dict(row._mapping) for row in result]

    logger.info("Extraidas %d filas desde MySQL.usuarios", len(rows))
    return rows
