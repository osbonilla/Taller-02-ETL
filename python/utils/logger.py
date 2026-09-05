"""
utils/logger.py
----------------
Configuracion centralizada de logging.

Por que un modulo dedicado y no logging.basicConfig() disperso: queremos
el MISMO formato (con nombre de componente y nivel) en extractores,
transformadores, cargadores, productor y orquestador batch, para que los
logs de `docker compose logs -f` sean faciles de correlacionar entre
servicios durante la demo/observabilidad.
"""

from __future__ import annotations

import logging
import os
import sys


_CONFIGURED_LOGGERS: set[str] = set()


def get_logger(name: str) -> logging.Logger:
    """Devuelve un logger configurado de forma consistente.

    Idempotente: si se llama varias veces con el mismo nombre no duplica
    handlers (problema comun al reconfigurar logging en loops).
    """
    logger = logging.getLogger(name)

    if name in _CONFIGURED_LOGGERS:
        return logger

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03dZ %(levelname)-7s [%(name)s] %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False

    _CONFIGURED_LOGGERS.add(name)
    return logger
