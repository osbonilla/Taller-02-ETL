"""
utils/wait_for.py
------------------
Espera activa con reintentos y backoff para dependencias externas.

Paso critico del proyecto: docker-compose con `depends_on: condition:
service_healthy` garantiza el ORDEN de arranque de contenedores, pero NO
garantiza que el servicio este 100% listo para el caso de uso concreto que
necesitamos (p.ej. Elasticsearch puede reportarse 'healthy' antes de que
nuestros index templates esten aplicados, o Logstash puede tener su API de
monitoreo arriba en el puerto 9600 antes de que el pipeline HTTP en el
puerto 8080 este cargado). Por eso, ademas de los healthchecks de Docker,
cada componente Python vuelve a comprobar su propia dependencia antes de
operar, con reintentos.
"""

from __future__ import annotations

import time
from typing import Callable

from utils.logger import get_logger

logger = get_logger("utils.wait_for")


class DependencyNotReadyError(RuntimeError):
    """Se agotaron los reintentos esperando a que una dependencia este lista."""


def wait_for(
    check_fn: Callable[[], bool],
    *,
    name: str,
    max_attempts: int = 30,
    initial_delay: float = 2.0,
    max_delay: float = 20.0,
) -> None:
    """Reintenta `check_fn` hasta que devuelva True o se agoten los intentos.

    Usa backoff exponencial acotado (initial_delay -> max_delay) para no
    saturar al servicio dependiente ni esperar indefinidamente.
    """
    delay = initial_delay
    for attempt in range(1, max_attempts + 1):
        try:
            if check_fn():
                logger.info("Dependencia lista: %s (intento %d/%d)", name, attempt, max_attempts)
                return
        except Exception as exc:  # noqa: BLE001 - queremos capturar cualquier error de red/driver
            logger.debug("Chequeo de '%s' fallo (intento %d/%d): %s", name, attempt, max_attempts, exc)

        logger.info(
            "Esperando a '%s'... intento %d/%d (reintento en %.1fs)",
            name, attempt, max_attempts, delay,
        )
        time.sleep(delay)
        delay = min(delay * 1.4, max_delay)

    raise DependencyNotReadyError(
        f"'{name}' no estuvo listo tras {max_attempts} intentos. "
        f"Revisa 'docker compose logs {name}'."
    )
