# Makefile
# Atajos para los comandos de Docker Compose y pruebas mas usados.
# Uso: make <target>   (por ejemplo: make up)

.PHONY: up down restart ps logs logs-batch logs-producer logs-logstash test clean status

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

ps:
	docker compose ps

logs:
	docker compose logs -f

logs-batch:
	docker compose logs -f python-batch

logs-producer:
	docker compose logs -f python-producer

logs-logstash:
	docker compose logs -f logstash

# Verificacion rapida de los conteos de documentos por indice (ver
# scripts/healthcheck_all.sh para el detalle completo)
status:
	bash scripts/healthcheck_all.sh

# Corre la suite de pytest en el host (requiere: pip install -r python/requirements.txt)
test:
	python3 -m pytest

# Baja los contenedores Y elimina los volumenes (¡borra todos los datos indexados!)
clean:
	docker compose down -v
