"""
test_es_loader_mocked.py
---------------------------
Prueba de integracion ligera del loader hacia Elasticsearch: se mockea el
helper `bulk` de la libreria oficial (no un servidor Elasticsearch real),
para verificar que:
  - se construyen las acciones bulk con el `_id` correcto (idempotencia),
  - el nombre de indice final incluye el prefijo configurado,
  - se contabilizan correctamente exitos/errores.
"""

import loaders.es_loader as mod


def test_load_to_elasticsearch_construye_acciones_con_id_correcto(mocker):
    captured_actions = []

    def fake_bulk(client, actions, **kwargs):
        captured_actions.extend(list(actions))
        return len(captured_actions), []

    mocker.patch("loaders.es_loader.bulk", side_effect=fake_bulk)
    mocker.patch("loaders.es_loader.get_es_client", return_value=mocker.MagicMock())

    records = [
        ("V001", {"producto": "Laptop", "total": 100.0}),
        ("V002", {"producto": "Mouse", "total": 20.0}),
    ]

    success, errors = mod.load_to_elasticsearch("ventas-csv", records)

    assert success == 2
    assert errors == 0
    assert captured_actions[0]["_id"] == "V001"
    assert captured_actions[0]["_op_type"] == "index"
    assert captured_actions[0]["_source"]["producto"] == "Laptop"
    # el indice final debe llevar el prefijo configurado (por defecto "taller")
    assert captured_actions[0]["_index"].endswith("ventas-csv")
    assert captured_actions[0]["_index"].startswith("taller")


def test_load_to_elasticsearch_reporta_errores(mocker):
    def fake_bulk(client, actions, **kwargs):
        list(actions)
        return 1, [{"index": {"_id": "V002", "error": "mapper_parsing_exception"}}]

    mocker.patch("loaders.es_loader.bulk", side_effect=fake_bulk)
    mocker.patch("loaders.es_loader.get_es_client", return_value=mocker.MagicMock())

    records = [
        ("V001", {"producto": "Laptop"}),
        ("V002", {"producto": "Mouse"}),
    ]
    success, errors = mod.load_to_elasticsearch("ventas-csv", records)

    assert success == 1
    assert errors == 1
