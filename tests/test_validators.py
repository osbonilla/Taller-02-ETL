"""
test_validators.py
-------------------
Pruebas UNITARIAS (sin red, sin base de datos, sin Elasticsearch) de
validators/validators.py.
"""

from validators.validators import (
    validate_allowed_values,
    validate_iso_date,
    validate_positive_number,
    validate_record,
    validate_required_fields,
)


class TestValidateRequiredFields:
    def test_ok_cuando_todos_los_campos_presentes(self):
        record = {"a": "1", "b": "2"}
        assert validate_required_fields(record, ["a", "b"]) == []

    def test_detecta_campo_ausente(self):
        record = {"a": "1"}
        errors = validate_required_fields(record, ["a", "b"])
        assert len(errors) == 1
        assert "b" in errors[0]

    def test_detecta_campo_vacio_como_ausente(self):
        record = {"a": "  ", "b": "2"}
        errors = validate_required_fields(record, ["a", "b"])
        assert len(errors) == 1
        assert "a" in errors[0]

    def test_detecta_none_como_ausente(self):
        record = {"a": None, "b": "2"}
        errors = validate_required_fields(record, ["a", "b"])
        assert len(errors) == 1


class TestValidatePositiveNumber:
    def test_numero_valido(self):
        assert validate_positive_number(42, "cantidad") == []
        assert validate_positive_number("42.5", "precio") == []

    def test_numero_negativo_es_invalido(self):
        errors = validate_positive_number(-5, "cantidad")
        assert len(errors) == 1
        assert "negativo" in errors[0]

    def test_no_numerico_es_invalido(self):
        errors = validate_positive_number("abc", "cantidad")
        assert len(errors) == 1
        assert "no es numerico" in errors[0]

    def test_cero_es_valido(self):
        assert validate_positive_number(0, "stock") == []


class TestValidateIsoDate:
    def test_fecha_simple_valida(self):
        assert validate_iso_date("2026-01-15", "fecha") == []

    def test_fecha_con_hora_valida(self):
        assert validate_iso_date("2026-01-15T10:30:00.000Z", "fecha") == []

    def test_fecha_invalida(self):
        errors = validate_iso_date("15/01/2026", "fecha")
        assert len(errors) == 1

    def test_none_es_invalido(self):
        errors = validate_iso_date(None, "fecha")
        assert len(errors) == 1


class TestValidateAllowedValues:
    def test_valor_permitido(self):
        assert validate_allowed_values("INFO", "nivel", ["INFO", "WARN", "ERROR"]) == []

    def test_valor_no_permitido(self):
        errors = validate_allowed_values("DEBUG", "nivel", ["INFO", "WARN", "ERROR"])
        assert len(errors) == 1


class TestValidateRecord:
    def test_registro_completamente_valido(self):
        record = {
            "venta_id": "V001",
            "fecha": "2026-01-15",
            "cantidad": "3",
            "total": "45.5",
        }
        result = validate_record(
            record,
            required_fields=("venta_id", "fecha"),
            positive_number_fields=("cantidad", "total"),
            date_fields=("fecha",),
        )
        assert result.is_valid is True
        assert result.errors == []

    def test_registro_con_multiples_errores(self):
        record = {"venta_id": "", "cantidad": "-5", "fecha": "no-es-fecha"}
        result = validate_record(
            record,
            required_fields=("venta_id",),
            positive_number_fields=("cantidad",),
            date_fields=("fecha",),
        )
        assert result.is_valid is False
        assert len(result.errors) == 3  # ausente, negativo, fecha invalida

    def test_no_duplica_error_de_tipo_si_ya_esta_ausente(self):
        # si el campo esta ausente, no debe ademas reportarse como "no numerico"
        record = {}
        result = validate_record(
            record,
            required_fields=("cantidad",),
            positive_number_fields=("cantidad",),
        )
        assert len(result.errors) == 1
