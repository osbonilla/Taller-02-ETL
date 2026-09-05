"""
test_transformers.py
----------------------
Pruebas UNITARIAS de transformers/transformers.py: verifican tipado,
generacion de @timestamp/ingested_at y que el id devuelto sea el esperado
(clave para la idempotencia del pipeline).
"""

from datetime import datetime

from transformers.transformers import (
    normalize_cliente_postgres,
    normalize_producto_mongo,
    normalize_usuario_mysql,
    normalize_venta,
)


class TestNormalizeVenta:
    def test_tipa_correctamente_los_campos_numericos(self):
        row = {
            "venta_id": "V00001",
            "fecha": "2026-08-09",
            "producto": "Laptop Pro 14",
            "categoria": "Tecnologia",
            "cantidad": "2",
            "precio_unitario": "85.7",
            "total": "171.4",
            "region": "Quito",
            "vendedor": "A. Torres",
        }
        doc_id, doc = normalize_venta(row)

        assert doc_id == "V00001"
        assert isinstance(doc["cantidad"], int) and doc["cantidad"] == 2
        assert isinstance(doc["precio_unitario"], float) and doc["precio_unitario"] == 85.7
        assert isinstance(doc["total"], float)

    def test_agrega_campos_comunes(self):
        row = {
            "venta_id": "V00002", "fecha": "2026-08-09", "producto": "X",
            "categoria": "Y", "cantidad": "1", "precio_unitario": "1.0",
            "total": "1.0", "region": "Quito", "vendedor": "A",
        }
        _, doc = normalize_venta(row)
        assert doc["source"] == "csv"
        assert doc["@timestamp"] == "2026-08-09T00:00:00.000Z"
        assert "ingested_at" in doc
        # ingested_at debe ser una fecha ISO parseable (verificamos formato)
        datetime.fromisoformat(doc["ingested_at"].replace("Z", "+00:00"))

    def test_mismo_venta_id_produce_mismo_doc_id_idempotencia(self):
        row = {
            "venta_id": "V00099", "fecha": "2026-08-09", "producto": "X",
            "categoria": "Y", "cantidad": "1", "precio_unitario": "1.0",
            "total": "1.0", "region": "Quito", "vendedor": "A",
        }
        id1, _ = normalize_venta(row)
        id2, _ = normalize_venta(row)
        assert id1 == id2 == "V00099"


class TestNormalizeUsuarioMysql:
    def test_convierte_activo_a_booleano(self):
        row = {
            "usuario_id": 5, "nombre": "Ana Perez", "email": "ana@correo.com",
            "pais": "Ecuador", "fecha_registro": "2026-01-01", "activo": 1,
        }
        doc_id, doc = normalize_usuario_mysql(row)
        assert doc_id == "5"
        assert doc["activo"] is True
        assert doc["source"] == "mysql"

    def test_soporta_objeto_date_nativo(self):
        import datetime as dt

        row = {
            "usuario_id": 7, "nombre": "Luis Gomez", "email": "luis@correo.com",
            "pais": "Ecuador", "fecha_registro": dt.date(2026, 3, 10), "activo": 0,
        }
        _, doc = normalize_usuario_mysql(row)
        assert doc["fecha_registro"] == "2026-03-10"
        assert doc["activo"] is False


class TestNormalizeClientePostgres:
    def test_tipa_ingresos_como_float(self):
        row = {
            "cliente_id": 3, "nombre_empresa": "Andes Software",
            "sector": "Tecnologia", "ciudad": "Quito", "pais": "Ecuador",
            "fecha_alta": "2025-05-01", "ingresos_anuales": "125000.50",
        }
        doc_id, doc = normalize_cliente_postgres(row)
        assert doc_id == "3"
        assert isinstance(doc["ingresos_anuales"], float)
        assert doc["source"] == "postgres"


class TestNormalizeProductoMongo:
    def test_aplana_atributos_anidados(self):
        raw_doc = {
            "producto_id": "P00001",
            "nombre": "Item 1",
            "categoria": "Tecnologia",
            "stock": 10,
            "precio": 99.9,
            "atributos": {"color": "negro", "peso_kg": 1.2, "marca": "NovaTech"},
            "fecha_ingreso": "2026-01-01",
        }
        doc_id, doc = normalize_producto_mongo(raw_doc)

        assert doc_id == "P00001"
        assert doc["atributos_color"] == "negro"
        assert doc["atributos_peso_kg"] == 1.2
        assert doc["atributos_marca"] == "NovaTech"
        assert "atributos" not in doc  # el objeto anidado original no debe quedar duplicado
        assert doc["source"] == "mongo"

    def test_maneja_atributos_ausentes_sin_lanzar_excepcion(self):
        raw_doc = {
            "producto_id": "P00002", "nombre": "Item 2", "categoria": "Hogar",
            "stock": 5, "precio": 10.0, "fecha_ingreso": "2026-01-01",
        }
        _, doc = normalize_producto_mongo(raw_doc)
        assert doc["atributos_color"] is None
