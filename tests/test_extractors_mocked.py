"""
test_extractors_mocked.py
----------------------------
Pruebas de INTEGRACION LIGERA (mockeadas): validan la logica de cada
extractor (parseo, forma de los datos devueltos, manejo de errores) SIN
requerir MySQL/PostgreSQL/MongoDB reales corriendo. Los drivers
(SQLAlchemy, pymongo) se sustituyen por dobles de prueba.

Estas pruebas complementan, pero no reemplazan, la verificacion manual
contra los servicios reales levantados con `docker compose up -d`
(descrita en el README, seccion de observabilidad/pruebas).
"""

import pytest

from extractors.csv_extractor import extract_ventas_csv


# ---------------------------------------------------------------------------
# CSV: usamos un archivo temporal real (pytest tmp_path), no un mock, porque
# la extraccion de CSV no tiene una dependencia externa que mockear.
# ---------------------------------------------------------------------------
class TestCsvExtractor:
    def test_extrae_filas_correctamente(self, tmp_path):
        csv_file = tmp_path / "ventas.csv"
        csv_file.write_text(
            "venta_id,fecha,producto,cantidad\n"
            "V001,2026-01-01,Laptop,2\n"
            "V002,2026-01-02,Mouse,5\n",
            encoding="utf-8",
        )
        rows = extract_ventas_csv(csv_file)
        assert len(rows) == 2
        assert rows[0]["venta_id"] == "V001"
        assert rows[1]["producto"] == "Mouse"

    def test_lanza_error_claro_si_no_existe_el_archivo(self, tmp_path):
        missing = tmp_path / "no-existe.csv"
        with pytest.raises(FileNotFoundError):
            extract_ventas_csv(missing)


# ---------------------------------------------------------------------------
# MySQL: se mockea sqlalchemy.create_engine para no requerir un MySQL real.
# ---------------------------------------------------------------------------
class FakeRow:
    """Simula una fila devuelta por SQLAlchemy (expone `_mapping`)."""

    def __init__(self, mapping: dict):
        self._mapping = mapping


class TestMysqlExtractorMocked:
    def test_extract_usuarios_convierte_filas_a_dicts(self, mocker):
        import extractors.mysql_extractor as mod

        mod._engine = None  # forzar recreacion del engine mockeado

        fake_rows = [
            FakeRow({"usuario_id": 1, "nombre": "Ana", "email": "ana@correo.com"}),
            FakeRow({"usuario_id": 2, "nombre": "Luis", "email": "luis@correo.com"}),
        ]

        mock_conn = mocker.MagicMock()
        mock_conn.execute.return_value = fake_rows
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = False

        mock_engine = mocker.MagicMock()
        mock_engine.connect.return_value = mock_conn

        mocker.patch("extractors.mysql_extractor.create_engine", return_value=mock_engine)

        rows = mod.extract_usuarios()

        assert len(rows) == 2
        assert rows[0] == {"usuario_id": 1, "nombre": "Ana", "email": "ana@correo.com"}
        mock_conn.execute.assert_called_once()

    def test_mysql_is_ready_devuelve_true_si_select_1_no_lanza_excepcion(self, mocker):
        import extractors.mysql_extractor as mod

        mod._engine = None
        mock_conn = mocker.MagicMock()
        mock_conn.__enter__.return_value = mock_conn
        mock_conn.__exit__.return_value = False

        mock_engine = mocker.MagicMock()
        mock_engine.connect.return_value = mock_conn

        mocker.patch("extractors.mysql_extractor.create_engine", return_value=mock_engine)

        assert mod.mysql_is_ready() is True


# ---------------------------------------------------------------------------
# MongoDB: se mockea pymongo.MongoClient para no requerir un Mongo real.
# ---------------------------------------------------------------------------
class TestMongoExtractorMocked:
    def test_extract_inventario_elimina_objectid(self, mocker):
        import extractors.mongo_extractor as mod

        mod._client = None

        fake_docs = [
            {"_id": "507f1f77bcf86cd799439011", "producto_id": "P001", "nombre": "Item"},
            {"_id": "507f1f77bcf86cd799439012", "producto_id": "P002", "nombre": "Item 2"},
        ]

        mock_collection = mocker.MagicMock()
        mock_collection.find.return_value = fake_docs

        mock_db = mocker.MagicMock()
        mock_db.inventario = mock_collection

        mock_client = mocker.MagicMock()
        mock_client.__getitem__.return_value = mock_db

        mocker.patch("extractors.mongo_extractor.MongoClient", return_value=mock_client)

        docs = mod.extract_inventario()

        assert len(docs) == 2
        assert "_id" not in docs[0]
        assert docs[0]["producto_id"] == "P001"
