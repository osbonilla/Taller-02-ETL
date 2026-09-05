"""
producers/event_producer.py
------------------------------
Productor NEAR REAL-TIME del taller.

Genera una "transaccion" sintetica (compra en punto de venta) cada
PRODUCER_INTERVAL_SECONDS y la envia por HTTP POST al input `http` de
Logstash (logstash/pipeline/realtime_http.conf), que la parsea, la
enriquece y la indexa en Elasticsearch casi inmediatamente.

Por que HTTP y no Kafka/RabbitMQ: el input `http` viene incluido de
fabrica en Logstash (no requiere levantar un broker adicional ni instalar
plugins extra), y para el volumen y el proposito academico de este taller
(demostrar que Kibana refleja datos en near real-time, con latencia de
segundos) es una solucion suficiente, simple y facil de defender. Un
broker de mensajeria seria la eleccion correcta en un escenario productivo
con miles de eventos por segundo y necesidad de garantias de entrega mas
fuertes — se documenta como mejora futura en el README.

Por que esto NO corre en Airflow: Airflow esta pensado para orquestar
tareas discretas con inicio y fin (batch), no para mantener un proceso
generando eventos de forma continua. Forzar un "productor infinito" dentro
de un DAG de Airflow (p.ej. con un sensor en loop) es un anti-patron
conocido en la comunidad de Airflow.
"""

from __future__ import annotations

import random
import sys
import time
import uuid
from datetime import datetime, timezone

import requests

from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger("producers.event_producer")

TIENDAS = ["TIENDA-QUITO-01", "TIENDA-GYE-02", "TIENDA-CUENCA-01", "TIENDA-MANTA-01"]
METODOS_PAGO = ["tarjeta", "efectivo", "transferencia"]


def _now_iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"


def build_transaction_event() -> dict:
    return {
        "transaccion_id": str(uuid.uuid4()),
        "tienda_id": random.choice(TIENDAS),
        "metodo_pago": random.choice(METODOS_PAGO),
        "monto": round(random.uniform(3.5, 320.0), 2),
        "event_time": _now_iso(),
    }


def send_event(endpoint: str, event: dict, *, timeout: float = 5.0) -> bool:
    try:
        response = requests.post(endpoint, json=event, timeout=timeout)
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        logger.warning("No se pudo enviar el evento %s a Logstash: %s", event["transaccion_id"], exc)
        return False


def wait_for_logstash_http(endpoint: str, *, max_attempts: int = 30, delay: float = 3.0) -> bool:
    """Logstash puede tardar en cargar el pipeline http aunque el proceso ya
    este arriba (ver utils/wait_for.py para la explicacion general de por
    que no basta con el healthcheck de docker-compose). Aqui hacemos un
    POST de "warm-up" real: si Logstash aun no cargo el input http, la
    conexion sera rechazada o dara timeout, y reintentamos.
    """
    warmup_event = {"warmup": True, "event_time": _now_iso()}
    for attempt in range(1, max_attempts + 1):
        if send_event(endpoint, warmup_event, timeout=3.0):
            logger.info("Logstash (input http) listo tras %d intento(s).", attempt)
            return True
        logger.info("Esperando a que Logstash cargue el input http... intento %d/%d", attempt, max_attempts)
        time.sleep(delay)
    return False


def main() -> int:
    settings = get_settings()
    endpoint = settings.logstash.http_endpoint
    interval = settings.pipeline.producer_interval_seconds

    logger.info("Productor near real-time iniciando. Destino: %s cada %.1fs", endpoint, interval)

    if not wait_for_logstash_http(endpoint):
        logger.error("Logstash no respondio a tiempo. Abortando productor.")
        return 1

    sent, failed = 0, 0
    try:
        while True:
            event = build_transaction_event()
            if send_event(endpoint, event):
                sent += 1
                logger.info(
                    "Evento enviado: %s | tienda=%s | monto=$%.2f | total_enviados=%d",
                    event["transaccion_id"][:8], event["tienda_id"], event["monto"], sent,
                )
            else:
                failed += 1
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Productor detenido manualmente. Enviados=%d Fallidos=%d", sent, failed)
        return 0


if __name__ == "__main__":
    sys.exit(main())
