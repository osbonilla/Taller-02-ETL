# python/Dockerfile
# ---------------------------------------------------------------------------
# Una unica imagen Python reutilizada por CUATRO servicios distintos en
# docker-compose.yml (python-batch, python-producer, es-init, kibana-init).
# Se construye una sola imagen -en vez de 4 Dockerfiles casi identicos-
# porque comparten exactamente las mismas dependencias; lo unico que cambia
# entre servicios es el COMANDO (`command:`) que se ejecuta, no el contenido
# de la imagen. Esto es justamente lo que evita "sobre-ingenieria" pedido
# en el enunciado del taller.
#
# IMPORTANTE: el contexto de build es la RAIZ del repositorio (ver
# docker-compose.yml: `context: . / dockerfile: python/Dockerfile`), no
# python/, porque esta imagen tambien necesita los templates de
# Elasticsearch y los scripts de inicializacion, que viven fuera de python/.
# ---------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# Solo copiamos requirements.txt primero para aprovechar la cache de Docker:
# si el codigo cambia pero las dependencias no, `pip install` no se repite.
COPY python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Codigo de la aplicacion (extractors, transformers, loaders, producers,
# pipelines, config, utils) directo bajo /app
COPY python/ ./

# Scripts de inicializacion one-shot (es-init, kibana-init) y los templates
# de Elasticsearch que esos scripts necesitan leer
COPY scripts/setup_es_templates.py ./scripts/setup_es_templates.py
COPY scripts/setup_kibana_index_patterns.py ./scripts/setup_kibana_index_patterns.py
COPY elasticsearch/templates/ ./elasticsearch/templates/

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DATA_RAW_DIR=/app/data/raw

# Comando por defecto; cada servicio en docker-compose.yml lo sobre-escribe
# explicitamente con `command:` segun su rol.
CMD ["python", "-m", "pipelines.batch_pipeline"]
