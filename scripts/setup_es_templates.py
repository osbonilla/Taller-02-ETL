#!/usr/bin/env python3
"""
setup_es_templates.py
------------------------
Servicio de inicializacion "es-init".

Aplica los index templates de elasticsearch/templates/*.json ANTES de que
cualquier otro componente (Logstash, el batch de Python, el productor)
escriba el primer documento.

Por que esto es un paso critico del proyecto: si el primer documento llega
a un indice que todavia no tiene un template asociado, Elasticsearch crea
el indice con MAPEO DINAMICO (adivina el tipo de cada campo a partir del
primer valor que ve). Es exactamente el problema que el taller pide evitar
("Evita problemas de mapping dinamico cuando puedan producir
inconsistencias"): por ejemplo, si el primer "total" que llegara fuera un
numero entero, Elasticsearch podria mapearlo como long en vez de float, y
una venta con decimales fallaria al indexarse despues.

Este script corre UNA SOLA VEZ como servicio one-shot en docker-compose
(`es-init`, con `restart: "no"`), y el resto de servicios usan
`depends_on: es-init: condition: service_completed_successfully` para
garantizar que arrancan DESPUES de que los templates ya existen.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from utils.es_client import es_is_ready, get_es_client
from utils.logger import get_logger
from utils.wait_for import DependencyNotReadyError, wait_for

logger = get_logger("scripts.setup_es_templates")

TEMPLATES_DIR = Path("/app/elasticsearch/templates")


def apply_templates() -> int:
    template_files = sorted(TEMPLATES_DIR.glob("*.json"))
    if not template_files:
        logger.error("No se encontraron archivos de template en %s", TEMPLATES_DIR)
        return 1

    client = get_es_client()
    applied, failed = 0, 0

    for path in template_files:
        template_name = f"taller-{path.stem.replace('_template', '').replace('_', '-')}"
        try:
            body = json.loads(path.read_text(encoding="utf-8"))
            client.indices.put_index_template(
                name=template_name,
                index_patterns=body["index_patterns"],
                priority=body.get("priority"),
                template=body.get("template"),
                meta=body.get("_meta"),
            )
            logger.info("Template aplicado: '%s' (desde %s)", template_name, path.name)
            applied += 1
        except Exception:
            logger.exception("Fallo aplicando el template desde %s", path.name)
            failed += 1

    logger.info("Templates aplicados: %d, fallidos: %d, total: %d", applied, failed, len(template_files))
    return 0 if failed == 0 else 1


def main() -> int:
    try:
        wait_for(es_is_ready, name="elasticsearch", max_attempts=40, initial_delay=2.0, max_delay=15.0)
    except DependencyNotReadyError as exc:
        logger.error("Elasticsearch no estuvo listo: %s", exc)
        return 1

    return apply_templates()


if __name__ == "__main__":
    sys.exit(main())
