#!/usr/bin/env bash
# healthcheck_all.sh
# ---------------------------------------------------------------------------
# Verificacion rapida de que TODO el pipeline esta funcionando: estado de
# contenedores, salud de Elasticsearch/Kibana/Logstash, y conteo de
# documentos por indice (evidencia concreta de que los datos llegaron).
#
# Uso:  bash scripts/healthcheck_all.sh     (o simplemente: make status)
# ---------------------------------------------------------------------------
set -uo pipefail

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

ES_PORT="${ES_PORT:-9200}"
KIBANA_PORT="${KIBANA_PORT:-5601}"
LOGSTASH_MONITOR_PORT="${LOGSTASH_MONITOR_PORT:-9600}"

echo "============================================================"
echo " 1) Estado de los contenedores"
echo "============================================================"
docker compose ps

echo
echo "============================================================"
echo " 2) Salud del cluster de Elasticsearch"
echo "============================================================"
curl -s "http://localhost:${ES_PORT}/_cluster/health?pretty" \
  || echo "[!] No se pudo contactar a Elasticsearch en el puerto ${ES_PORT}"

echo
echo "============================================================"
echo " 3) Indices 'taller-*' y conteo de documentos por fuente"
echo "    (evidencia directa de cuantos registros llegaron de cada origen)"
echo "============================================================"
curl -s "http://localhost:${ES_PORT}/_cat/indices/taller-*?v&h=index,docs.count,store.size" \
  || echo "[!] No se pudieron listar los indices 'taller-*'"

echo
echo "============================================================"
echo " 4) Kibana"
echo "============================================================"
curl -s "http://localhost:${KIBANA_PORT}/api/status" | head -c 300
echo
echo "Abrir en el navegador: http://localhost:${KIBANA_PORT}"

echo
echo "============================================================"
echo " 5) Logstash (API de monitoreo: eventos in/out por pipeline)"
echo "============================================================"
curl -s "http://localhost:${LOGSTASH_MONITOR_PORT}/_node/stats/pipelines?pretty" \
  | grep -E '"events"|"in"|"out"|"filtered"' \
  || echo "[!] No se pudo contactar a Logstash en el puerto ${LOGSTASH_MONITOR_PORT}"

echo
echo "============================================================"
echo " 6) Actividad reciente de los servicios Python"
echo "============================================================"
echo "--- python-batch (ultimas 5 lineas) ---"
docker compose logs --tail=5 python-batch 2>/dev/null
echo
echo "--- python-producer (ultimas 5 lineas) ---"
docker compose logs --tail=5 python-producer 2>/dev/null

echo
echo "Listo. Si algo aparece vacio o con error, revisa: docker compose logs -f <servicio>"
