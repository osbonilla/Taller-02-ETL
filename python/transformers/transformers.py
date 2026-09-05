"""
transformers/transformers.py
------------------------------
Transformaciones "puras" (dict -> dict) de cada fuente hacia un documento
listo para indexar en Elasticsearch.

Decisiones de diseno importantes (ver README, seccion "Decisiones de
diseno" para la justificacion completa ante el profesor):

1. IDs deterministas: cada documento recibe un `_id` calculado a partir de
   una clave natural del origen (venta_id, usuario_id, cliente_id,
   producto_id). Esto hace que volver a correr el batch NO genere
   duplicados: Elasticsearch simplemente sobre-escribe el documento con el
   mismo _id (idempotencia). Es la misma razon por la que, en Logstash,
   usamos `document_id` en el output de Elasticsearch (ver logstash/pipeline).

2. Campos comunes (source, ingested_at, @timestamp): TODAS las fuentes
   comparten estos tres campos. `source` permite construir en Kibana una
   visualizacion "eventos por fuente" agregando sobre el alias unificado
   `taller-*`. `@timestamp` es el campo de tiempo *de negocio* (cuando
   ocurrio el evento en el mundo real) y `ingested_at` es el momento en que
   el pipeline lo proceso; comparar ambos permite medir latencia
   aproximada del pipeline (requisito de observabilidad del taller).

3. Este modulo NO transforma los datos de LOG ni de JSON: esas dos fuentes
   se procesan directamente en Logstash (filtros grok/json), por eso no
   tienen una funcion equivalente aqui. Ver logstash/pipeline/*.conf.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
        f"{datetime.now(timezone.utc).microsecond // 1000:03d}Z"


def _stable_id(*parts: str) -> str:
    """Genera un id deterministico a partir de una o mas partes.

    Se usa como red de seguridad cuando no hay una clave natural 100%
    confiable (por ejemplo si dos filas llegaran con el mismo id de
    negocio pero de ejecuciones distintas). No se usa actualmente porque
    todas las fuentes ya traen una clave natural, pero queda documentada
    y probada por si una fuente futura no la trajera.
    """
    joined = "|".join(parts)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()  # noqa: S324 (no es criptografico)


def attach_common_fields(doc: dict[str, Any], *, source: str, timestamp: str) -> dict[str, Any]:
    """Adjunta los campos compartidos por TODAS las fuentes del proyecto."""
    enriched = dict(doc)
    enriched["source"] = source
    enriched["@timestamp"] = timestamp
    enriched["ingested_at"] = _now_iso()
    return enriched


def normalize_venta(row: dict[str, str]) -> tuple[str, dict[str, Any]]:
    """CSV (ventas.csv) -> documento Elasticsearch.

    Todo llega como string desde el csv.DictReader; aqui es donde se hace
    el "transform tipos de datos" pedido en el taller (ETL: la
    transformacion ocurre en Python, ANTES de llegar a Elasticsearch).
    """
    doc = {
        "venta_id": row["venta_id"],
        "producto": row["producto"],
        "categoria": row["categoria"],
        "cantidad": int(row["cantidad"]),
        "precio_unitario": float(row["precio_unitario"]),
        "total": float(row["total"]),
        "region": row["region"],
        "vendedor": row["vendedor"],
    }
    timestamp = f"{row['fecha']}T00:00:00.000Z"
    doc = attach_common_fields(doc, source="csv", timestamp=timestamp)
    return row["venta_id"], doc


def normalize_usuario_mysql(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Fila de MySQL (tabla usuarios) -> documento Elasticsearch."""
    usuario_id = str(row["usuario_id"])
    fecha_registro = row["fecha_registro"]
    fecha_str = fecha_registro.isoformat() if hasattr(fecha_registro, "isoformat") else str(fecha_registro)
    doc = {
        "usuario_id": usuario_id,
        "nombre": row["nombre"],
        "email": row["email"],
        "pais": row["pais"],
        "fecha_registro": fecha_str,
        "activo": bool(row["activo"]),
    }
    timestamp = f"{fecha_str}T00:00:00.000Z"
    doc = attach_common_fields(doc, source="mysql", timestamp=timestamp)
    return usuario_id, doc


def normalize_cliente_postgres(row: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Fila de PostgreSQL (tabla clientes) -> documento Elasticsearch."""
    cliente_id = str(row["cliente_id"])
    fecha_alta = row["fecha_alta"]
    fecha_str = fecha_alta.isoformat() if hasattr(fecha_alta, "isoformat") else str(fecha_alta)
    doc = {
        "cliente_id": cliente_id,
        "nombre_empresa": row["nombre_empresa"],
        "sector": row["sector"],
        "ciudad": row["ciudad"],
        "pais": row["pais"],
        "fecha_alta": fecha_str,
        "ingresos_anuales": float(row["ingresos_anuales"]),
    }
    timestamp = f"{fecha_str}T00:00:00.000Z"
    doc = attach_common_fields(doc, source="postgres", timestamp=timestamp)
    return cliente_id, doc


def normalize_producto_mongo(raw_doc: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Documento de MongoDB (coleccion inventario) -> documento Elasticsearch.

    Decision de transformacion: MongoDB permite estructuras anidadas
    (`atributos: {color, peso_kg, marca}`), pero para que Kibana pueda
    agregar/filtrar facilmente sobre esos campos sin configurar un mapping
    `nested` (mas costoso y menos intuitivo para agregaciones simples),
    "aplanamos" el objeto anidado a `atributos_color`, `atributos_peso_kg`,
    `atributos_marca`. Este es un ejemplo concreto de transformacion
    ELT-vs-ETL discutido en el README.
    """
    producto_id = raw_doc["producto_id"]
    atributos = raw_doc.get("atributos", {}) or {}
    fecha_ingreso = raw_doc.get("fecha_ingreso")
    fecha_str = fecha_ingreso.isoformat() if hasattr(fecha_ingreso, "isoformat") else str(fecha_ingreso)

    doc = {
        "producto_id": producto_id,
        "nombre": raw_doc["nombre"],
        "categoria": raw_doc["categoria"],
        "stock": int(raw_doc["stock"]),
        "precio": float(raw_doc["precio"]),
        "atributos_color": atributos.get("color"),
        "atributos_peso_kg": float(atributos["peso_kg"]) if atributos.get("peso_kg") is not None else None,
        "atributos_marca": atributos.get("marca"),
    }
    timestamp = f"{fecha_str}T00:00:00.000Z" if "T" not in fecha_str else fecha_str
    doc = attach_common_fields(doc, source="mongo", timestamp=timestamp)
    return str(producto_id), doc
