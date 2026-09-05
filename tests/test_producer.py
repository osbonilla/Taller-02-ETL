"""
test_producer.py
------------------
Pruebas de la generacion de eventos near real-time (producers/event_producer.py).
build_transaction_event() es una funcion pura -> prueba unitaria directa.
send_event() hace una peticion HTTP real -> se mockea `requests.post`.
"""

from producers.event_producer import build_transaction_event, send_event


class TestBuildTransactionEvent:
    def test_evento_tiene_los_campos_esperados(self):
        event = build_transaction_event()
        assert set(event.keys()) == {
            "transaccion_id", "tienda_id", "metodo_pago", "monto", "event_time",
        }

    def test_monto_es_positivo_y_float(self):
        event = build_transaction_event()
        assert isinstance(event["monto"], float)
        assert event["monto"] > 0

    def test_cada_evento_tiene_un_id_distinto(self):
        e1 = build_transaction_event()
        e2 = build_transaction_event()
        assert e1["transaccion_id"] != e2["transaccion_id"]


class TestSendEvent:
    def test_send_event_true_si_la_respuesta_es_exitosa(self, mocker):
        mock_response = mocker.MagicMock()
        mock_response.raise_for_status.return_value = None
        mocker.patch("producers.event_producer.requests.post", return_value=mock_response)

        ok = send_event("http://logstash:8080", {"transaccion_id": "abc", "monto": 1})
        assert ok is True

    def test_send_event_false_si_hay_excepcion_de_red(self, mocker):
        import requests

        mocker.patch(
            "producers.event_producer.requests.post",
            side_effect=requests.exceptions.ConnectionError("no se pudo conectar"),
        )
        ok = send_event("http://logstash:8080", {"transaccion_id": "abc", "monto": 1})
        assert ok is False
