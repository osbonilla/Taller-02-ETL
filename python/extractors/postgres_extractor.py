"""
extractors/postgres_extractor.py
-----------------------------------
Extraccion de la fuente PostgreSQL (tabla `clientes`).

Misma logica que mysql_extractor.py (Python + SQLAlchemy en vez de
Logstash jdbc input) — ver el docstring de ese modulo para la
justificacion completa. Se mantiene un extractor separado, aunque el
codigo es similar, porque en un proyecto real cada fuente relacional
suele tener su propio esquema, tipos de datos especificos del motor
(NUMERIC en Postgres vs DECIMAL en MySQL, por ejemplo) y reglas de
negocio propias; forzarlos a un extractor generico "para ahorrar lineas"
suele complicar el mantenimiento mas de lo que ahorra.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("extractors.postgres")

_engine: Engine | None = None


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        uri = get_settings().postgres.sqlalchemy_uri
        _engine = create_engine(uri, pool_pre_ping=True)
    return _engine


def postgres_is_ready() -> bool:
    """Chequeo de salud usado por utils.wait_for.wait_for()."""
    with _get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    return True


def extract_clientes() -> list[dict[str, Any]]:
    engine = _get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM clientes"))
        rows = [dict(row._mapping) for row in result]

    logger.info("Extraidas %d filas desde PostgreSQL.clientes", len(rows))
    return rows
