"""
validators/validators.py
-------------------------
Funciones puras de validacion de datos.

Deliberadamente NO dependen de pandas, SQLAlchemy ni del cliente de
Elasticsearch: reciben y devuelven tipos nativos de Python (dict, str,
float) para poder probarlas con pytest sin necesitar ningun servicio
externo levantado (son las pruebas UNITARIAS del proyecto).

La validacion es la primera etapa del ETL: "garantizar calidad de datos"
significa, en este proyecto, rechazar o marcar registros que no cumplen
reglas minimas ANTES de transformarlos o cargarlos a Elasticsearch.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


class ValidationResult:
    """Resultado de validar un registro: valido/invalido + lista de errores."""

    __slots__ = ("is_valid", "errors")

    def __init__(self, is_valid: bool, errors: list[str]):
        self.is_valid = is_valid
        self.errors = errors

    def __repr__(self) -> str:  # pragma: no cover - solo utilitario
        return f"ValidationResult(is_valid={self.is_valid}, errors={self.errors})"


def validate_required_fields(record: dict[str, Any], required: Iterable[str]) -> list[str]:
    """Devuelve la lista de campos requeridos que faltan o vienen vacios/None."""
    errors = []
    for field_name in required:
        value = record.get(field_name)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            errors.append(f"campo requerido ausente: '{field_name}'")
    return errors


def validate_positive_number(value: Any, field_name: str) -> list[str]:
    """Verifica que value sea numerico y >= 0. Devuelve lista de errores (vacia si OK)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return [f"'{field_name}' no es numerico: {value!r}"]
    if number < 0:
        return [f"'{field_name}' no puede ser negativo: {number}"]
    return []


def validate_iso_date(value: Any, field_name: str) -> list[str]:
    """Verifica que value sea una fecha parseable en formato ISO 8601 (YYYY-MM-DD[...])."""
    if value is None:
        return [f"'{field_name}' es None, se esperaba una fecha ISO 8601"]
    text = str(value)
    # aceptamos tanto 'YYYY-MM-DD' como 'YYYY-MM-DDTHH:MM:SS(.mmm)(Z)'
    candidate = text.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        return [f"'{field_name}' no es una fecha ISO 8601 valida: {value!r}"]
    return []


def validate_allowed_values(value: Any, field_name: str, allowed: Iterable[Any]) -> list[str]:
    allowed_set = set(allowed)
    if value not in allowed_set:
        return [f"'{field_name}'={value!r} no esta en el conjunto permitido {sorted(allowed_set)}"]
    return []


def validate_record(
    record: dict[str, Any],
    *,
    required_fields: Iterable[str] = (),
    positive_number_fields: Iterable[str] = (),
    date_fields: Iterable[str] = (),
) -> ValidationResult:
    """Compone las validaciones anteriores en un unico resultado por registro.

    Disenada para usarse dentro de un extractor/transformador: se valida
    ANTES de transformar, y los registros invalidos se descartan (o se
    envian a un log de "rechazados") en vez de propagarse a Elasticsearch
    con datos corruptos.
    """
    errors: list[str] = []
    errors += validate_required_fields(record, required_fields)

    # Solo validamos tipo/rango si el campo esta presente (evita doble error
    # cuando ya fue reportado como ausente por validate_required_fields).
    for field_name in positive_number_fields:
        if record.get(field_name) is not None:
            errors += validate_positive_number(record[field_name], field_name)

    for field_name in date_fields:
        if record.get(field_name) is not None:
            errors += validate_iso_date(record[field_name], field_name)

    return ValidationResult(is_valid=(len(errors) == 0), errors=errors)
