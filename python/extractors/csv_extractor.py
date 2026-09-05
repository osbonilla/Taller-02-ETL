"""
extractors/csv_extractor.py
-----------------------------
Extraccion de la fuente CSV (data/raw/ventas.csv).

Responsabilidad UNICA de este modulo: leer el archivo y devolver filas
crudas (dict[str, Any]) tal cual vienen del archivo, vía pandas (la
herramienta estandar de facto para ingestion tabular en Python). La
conversion FINAL de tipos y el enriquecimiento ocurren en
`transformers.normalize_venta`, no aqui — separar extraccion de
transformacion es justamente lo que distingue un pipeline ETL bien
modularizado de un script monolitico.

Nota tecnica: convertimos explicitamente los valores numericos con
int()/float() en transformers.py, lo que además de tipar el dato evita un
problema comun al mezclar pandas con el cliente de Elasticsearch: los
tipos numpy (int64/float64) que produce pandas NO son serializables a
JSON de forma nativa; al pasar por int()/float() quedan como tipos nativos
de Python antes de llegar al bulk loader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from utils.logger import get_logger

logger = get_logger("extractors.csv")


def extract_ventas_csv(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo CSV en {csv_path}. "
            f"Verifica el volumen montado en docker-compose.yml."
        )

    df = pd.read_csv(csv_path, dtype=str)  # dtype=str: la tipificacion "real" es responsabilidad del transformer
    df = df.where(pd.notnull(df), None)  # NaN -> None, mas facil de validar que "nan" como string
    rows = df.to_dict(orient="records")

    logger.info("Extraidas %d filas desde %s", len(rows), csv_path)
    return rows
