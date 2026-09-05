#!/usr/bin/env python3
"""
setup_kibana_index_patterns.py
---------------------------------
Servicio de inicializacion "kibana-init".

Crea automaticamente, via la API REST de Kibana, un index pattern por cada
fuente del taller (mas uno unificado `taller-*` para la visualizacion
"datos por fuente" que agrega sobre TODOS los indices a la vez).

Esto es un "best effort": si algo falla (por ejemplo, el pattern ya existe
de una ejecucion anterior), se registra como advertencia y se continua con
el resto, sin hacer fallar el contenedor completo — crear los index
patterns manualmente en Kibana toma menos de un minuto por patron y se
documenta paso a paso en el README como alternativa siempre disponible.
"""

from __future__ import annotations

import sys
import time

import requests

from utils.logger import get_logger

logger = get_logger("scripts.setup_kibana_index_patterns")

INDEX_PATTERNS = [
    "taller-ventas-csv*",
    "taller-logs-app*",
    "taller-eventos-json*",
    "taller-eventos-realtime*",
    "taller-mysql-usuarios*",
    "taller-postgres-clientes*",
    "taller-mongo-productos*",
    "taller-*",  # vista unificada: "datos provenientes de las diferentes fuentes"
]


def wait_for_kibana(base_url: str, *, max_attempts: int = 40, delay: float = 3.0) -> bool:
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(f"{base_url}/api/status", timeout=5)
            if resp.status_code == 200:
                logger.info("Kibana listo tras %d intento(s).", attempt)
                return True
        except requests.RequestException as exc:
            logger.debug("Kibana aun no responde (%s)", exc)

        logger.info("Esperando a Kibana... intento %d/%d", attempt, max_attempts)
        time.sleep(delay)

    return False


def create_index_pattern(base_url: str, title: str) -> None:
    url = f"{base_url}/api/index_patterns/index_pattern"
    payload = {"index_pattern": {"title": title, "timeFieldName": "@timestamp"}}
    headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code in (200, 201):
            logger.info("Index pattern creado: '%s'", title)
        elif resp.status_code == 400 and "duplicate" in resp.text.lower():
            logger.info("Index pattern '%s' ya existia, se omite.", title)
        else:
            logger.warning(
                "No se pudo crear el index pattern '%s' (HTTP %d): %s",
                title, resp.status_code, resp.text[:200],
            )
    except requests.RequestException as exc:
        logger.warning("Error de red creando el index pattern '%s': %s", title, exc)


def main() -> int:
    # Dentro de la red interna de docker-compose, el servicio de Kibana
    # siempre se resuelve como "kibana" en el puerto 5601 (nombre de
    # servicio = hostname DNS interno de Docker); no depende de variables
    # de entorno adicionales.
    base_url = "http://kibana:5601"

    if not wait_for_kibana(base_url):
        logger.warning(
            "Kibana no respondio a tiempo. Los index patterns se pueden crear "
            "manualmente despues (ver README, seccion Kibana)."
        )
        return 0  # no bloqueamos el resto del stack por esto

    for pattern in INDEX_PATTERNS:
        create_index_pattern(base_url, pattern)

    logger.info("Inicializacion de index patterns de Kibana finalizada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
