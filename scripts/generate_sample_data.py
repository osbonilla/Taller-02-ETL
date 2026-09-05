#!/usr/bin/env python3
"""
generate_sample_data.py
------------------------
Genera datos sinteticos reproducibles para TODAS las fuentes del taller:

  - data/raw/ventas.csv                 -> fuente CSV (batch)
  - data/raw/application.log            -> fuente LOG (near real-time / batch via Logstash)
  - data/raw/events.json                -> fuente JSON Lines (batch via Logstash)
  - init-scripts/mysql/init.sql         -> semilla para MySQL (tabla usuarios)
  - init-scripts/postgres/init.sql      -> semilla para PostgreSQL (tabla clientes)
  - init-scripts/mongo/init.js          -> semilla para MongoDB (coleccion inventario)

No es necesario volver a ejecutar este script para levantar el proyecto: los
archivos ya quedan generados y versionados en el repositorio. Se incluye por
transparencia y para poder regenerar datos frescos si se desea:

    python scripts/generate_sample_data.py

Usa random.seed(42) para que la salida sea determinista entre ejecuciones,
lo cual facilita comparar resultados y depurar el pipeline.
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
MYSQL_INIT = ROOT / "init-scripts" / "mysql" / "init.sql"
POSTGRES_INIT = ROOT / "init-scripts" / "postgres" / "init.sql"
MONGO_INIT = ROOT / "init-scripts" / "mongo" / "init.js"

NOW = datetime.now(timezone.utc).replace(microsecond=0)


def rand_past_datetime(days_back: int) -> datetime:
    delta_seconds = random.randint(0, days_back * 24 * 3600)
    return NOW - timedelta(seconds=delta_seconds)


# ---------------------------------------------------------------------------
# 1) CSV -> ventas.csv
# ---------------------------------------------------------------------------
PRODUCTOS = [
    ("Laptop Pro 14", "Tecnologia", 1450.00),
    ("Mouse Inalambrico", "Tecnologia", 18.50),
    ("Teclado Mecanico", "Tecnologia", 65.00),
    ("Monitor 27 4K", "Tecnologia", 320.00),
    ("Silla Ergonomica", "Oficina", 210.00),
    ("Escritorio Ajustable", "Oficina", 380.00),
    ("Cuaderno A5", "Papeleria", 3.20),
    ("Set de Boligrafos", "Papeleria", 5.75),
    ("Cafetera Espresso", "Hogar", 145.00),
    ("Aspiradora Robot", "Hogar", 260.00),
    ("Zapatillas Running", "Deporte", 89.90),
    ("Bicicleta Urbana", "Deporte", 540.00),
    ("Mochila Antirrobo", "Accesorios", 47.30),
    ("Audifonos Bluetooth", "Tecnologia", 75.00),
    ("Lampara LED Escritorio", "Oficina", 22.90),
]
REGIONES = ["Quito", "Guayaquil", "Cuenca", "Manta", "Ambato"]
VENDEDORES = ["A. Torres", "M. Salazar", "J. Ramirez", "P. Vega", "L. Ortiz", "C. Nunez"]

ventas_rows = []
for i in range(1, 301):
    producto, categoria, precio = random.choice(PRODUCTOS)
    cantidad = random.randint(1, 12)
    precio_unitario = round(precio * random.uniform(0.95, 1.08), 2)
    total = round(precio_unitario * cantidad, 2)
    fecha = rand_past_datetime(90).date().isoformat()
    ventas_rows.append(
        {
            "venta_id": f"V{i:05d}",
            "fecha": fecha,
            "producto": producto,
            "categoria": categoria,
            "cantidad": cantidad,
            "precio_unitario": precio_unitario,
            "total": total,
            "region": random.choice(REGIONES),
            "vendedor": random.choice(VENDEDORES),
        }
    )

csv_path = RAW_DIR / "ventas.csv"
with csv_path.open("w", encoding="utf-8", newline="") as f:
    header = ventas_rows[0].keys()
    f.write(",".join(header) + "\n")
    for row in ventas_rows:
        f.write(",".join(str(row[k]) for k in header) + "\n")
print(f"[ok] {csv_path} ({len(ventas_rows)} filas)")


# ---------------------------------------------------------------------------
# 2) LOG -> application.log
#    Formato disenado para ser parseado con un patron grok simple y estable:
#    %{TIMESTAMP_ISO8601:log_timestamp} %{LOGLEVEL:log_level}  [%{WORD:service}] %{GREEDYDATA:log_message}
#    y luego un filtro kv para "status=" y "tiempo_ms="
# ---------------------------------------------------------------------------
SERVICES = ["OrderService", "AuthService", "PaymentGateway", "InventoryService", "NotificationWorker"]
LEVELS_WEIGHTED = ["INFO"] * 70 + ["WARN"] * 20 + ["ERROR"] * 10
MESSAGES_OK = [
    "Solicitud procesada correctamente",
    "Pedido creado sin incidencias",
    "Usuario autenticado con exito",
    "Pago confirmado por el proveedor",
    "Stock actualizado correctamente",
    "Notificacion enviada al usuario",
]
MESSAGES_WARN = [
    "Tiempo de respuesta elevado detectado",
    "Reintentando conexion con servicio externo",
    "Cache expirado, recalculando valores",
]
MESSAGES_ERROR = [
    "Fallo al conectar con la base de datos",
    "Timeout esperando respuesta del proveedor de pago",
    "Excepcion no controlada al procesar el pedido",
]

log_lines = []
for _ in range(250):
    ts = rand_past_datetime(30)
    level = random.choice(LEVELS_WEIGHTED)
    service = random.choice(SERVICES)
    if level == "INFO":
        msg = random.choice(MESSAGES_OK)
        status = random.choice([200, 200, 200, 201])
        tiempo_ms = random.randint(15, 220)
    elif level == "WARN":
        msg = random.choice(MESSAGES_WARN)
        status = random.choice([200, 202, 408])
        tiempo_ms = random.randint(220, 900)
    else:
        msg = random.choice(MESSAGES_ERROR)
        status = random.choice([500, 502, 503])
        tiempo_ms = random.randint(500, 3000)

    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z"
    line = f"{ts_str} {level:<5} [{service}] {msg} status={status} tiempo_ms={tiempo_ms}"
    log_lines.append((ts, line))

log_lines.sort(key=lambda t: t[0])
log_path = RAW_DIR / "application.log"
with log_path.open("w", encoding="utf-8") as f:
    for _, line in log_lines:
        f.write(line + "\n")
print(f"[ok] {log_path} ({len(log_lines)} lineas)")


# ---------------------------------------------------------------------------
# 3) JSON -> events.json  (formato JSON Lines: un objeto JSON por linea,
#    requerido por el codec json_lines de Logstash)
# ---------------------------------------------------------------------------
EVENT_TYPES = ["login", "logout", "click", "view_product", "purchase"]
PAGINAS = ["home", "catalogo", "producto/123", "carrito", "checkout", "perfil"]

json_events = []
for i in range(1, 251):
    ts = rand_past_datetime(30)
    event_type = random.choices(
        EVENT_TYPES, weights=[15, 10, 30, 30, 15], k=1
    )[0]
    event = {
        "event_id": f"E{i:06d}",
        "event_type": event_type,
        "user_id": f"U{random.randint(1, 80):04d}",
        "event_time": ts.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ts.microsecond // 1000:03d}Z",
        "pagina": random.choice(PAGINAS) if event_type in ("click", "view_product") else None,
        "monto": round(random.uniform(8, 480), 2) if event_type == "purchase" else None,
        "device": random.choice(["desktop", "mobile", "tablet"]),
    }
    json_events.append((ts, event))

json_events.sort(key=lambda t: t[0])
json_path = RAW_DIR / "events.json"
with json_path.open("w", encoding="utf-8") as f:
    for _, event in json_events:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
print(f"[ok] {json_path} ({len(json_events)} eventos, formato JSON Lines)")


# ---------------------------------------------------------------------------
# 4) MySQL -> init-scripts/mysql/init.sql   (tabla usuarios)
# ---------------------------------------------------------------------------
NOMBRES = ["Ana", "Luis", "Maria", "Carlos", "Sofia", "Diego", "Valentina", "Andres",
           "Camila", "Javier", "Paula", "Ricardo", "Daniela", "Fernando", "Gabriela"]
APELLIDOS = ["Perez", "Gomez", "Rodriguez", "Fernandez", "Lopez", "Martinez", "Sanchez",
             "Torres", "Ramirez", "Flores", "Castro", "Ortega"]
PAISES = ["Ecuador", "Colombia", "Peru", "Chile", "Mexico", "Argentina"]

mysql_rows = []
for i in range(1, 81):
    nombre = f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"
    email = nombre.lower().replace(" ", ".") + f"{i}@correo.com"
    pais = random.choice(PAISES)
    fecha_registro = rand_past_datetime(600).date().isoformat()
    activo = random.choice([1, 1, 1, 0])
    nombre_sql = nombre.replace("'", "''")
    mysql_rows.append(f"('{nombre_sql}', '{email}', '{pais}', '{fecha_registro}', {activo})")

mysql_values_sql = ",\n".join(mysql_rows)
mysql_sql = f"""-- init.sql (MySQL)
-- Se ejecuta automaticamente una sola vez, en el primer arranque del
-- contenedor, gracias al mecanismo docker-entrypoint-initdb.d de la imagen
-- oficial de MySQL. La base de datos y el usuario ya fueron creados por las
-- variables de entorno MYSQL_DATABASE / MYSQL_USER (ver docker-compose.yml).

CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id      INT AUTO_INCREMENT PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL,
    email           VARCHAR(160) NOT NULL,
    pais            VARCHAR(60),
    fecha_registro  DATE,
    activo          TINYINT(1) DEFAULT 1
);

INSERT INTO usuarios (nombre, email, pais, fecha_registro, activo) VALUES
{mysql_values_sql};
"""
MYSQL_INIT.write_text(mysql_sql, encoding="utf-8")
print(f"[ok] {MYSQL_INIT} ({len(mysql_rows)} filas)")


# ---------------------------------------------------------------------------
# 5) PostgreSQL -> init-scripts/postgres/init.sql   (tabla clientes)
# ---------------------------------------------------------------------------
EMPRESAS = ["Andes Software", "Norte Logistica", "Grupo Pichincha Retail", "Litoral Foods",
            "Sierra Textiles", "Amazonia Digital", "Costa Solutions", "Valle Motors",
            "Pacifico Data", "Quito Analytics", "Guayas Trading", "Cuenca Bioagro"]
SECTORES = ["Tecnologia", "Retail", "Logistica", "Manufactura", "Servicios Financieros", "Agroindustria"]
CIUDADES = ["Quito", "Guayaquil", "Cuenca", "Ambato", "Loja", "Manta"]

postgres_rows = []
for i in range(1, 71):
    empresa = f"{random.choice(EMPRESAS)} {i}"
    sector = random.choice(SECTORES)
    ciudad = random.choice(CIUDADES)
    pais = "Ecuador"
    fecha_alta = rand_past_datetime(900).date().isoformat()
    ingresos = round(random.uniform(15000, 950000), 2)
    empresa_sql = empresa.replace("'", "''")
    postgres_rows.append(
        f"('{empresa_sql}', '{sector}', '{ciudad}', '{pais}', '{fecha_alta}', {ingresos})"
    )

postgres_values_sql = ",\n".join(postgres_rows)
postgres_sql = f"""-- init.sql (PostgreSQL)
-- Se ejecuta automaticamente una sola vez, en el primer arranque del
-- contenedor, gracias al mecanismo docker-entrypoint-initdb.d de la imagen
-- oficial de PostgreSQL. La base de datos y el usuario ya fueron creados por
-- las variables de entorno POSTGRES_DB / POSTGRES_USER (ver docker-compose.yml).

CREATE TABLE IF NOT EXISTS clientes (
    cliente_id          SERIAL PRIMARY KEY,
    nombre_empresa       VARCHAR(180) NOT NULL,
    sector               VARCHAR(80),
    ciudad               VARCHAR(80),
    pais                 VARCHAR(80),
    fecha_alta           DATE,
    ingresos_anuales     NUMERIC(12, 2)
);

INSERT INTO clientes (nombre_empresa, sector, ciudad, pais, fecha_alta, ingresos_anuales) VALUES
{postgres_values_sql};
"""
POSTGRES_INIT.write_text(postgres_sql, encoding="utf-8")
print(f"[ok] {POSTGRES_INIT} ({len(postgres_rows)} filas)")


# ---------------------------------------------------------------------------
# 6) MongoDB -> init-scripts/mongo/init.js   (coleccion inventario, documentos
#    con estructura anidada para demostrar el modelo documental de Mongo)
# ---------------------------------------------------------------------------
CATEGORIAS_INV = ["Tecnologia", "Oficina", "Hogar", "Deporte", "Papeleria"]
COLORES = ["negro", "blanco", "gris", "azul", "rojo"]
MARCAS = ["NovaTech", "OfiMax", "HomeLine", "SportPro", "PaperCo"]

mongo_docs = []
for i in range(1, 91):
    categoria = random.choice(CATEGORIAS_INV)
    nombre = f"{categoria} Item {i}"
    stock = random.randint(0, 500)
    precio = round(random.uniform(5, 600), 2)
    fecha_ingreso = rand_past_datetime(400).date().isoformat()
    doc = {
        "producto_id": f"P{i:05d}",
        "nombre": nombre,
        "categoria": categoria,
        "stock": stock,
        "precio": precio,
        "atributos": {
            "color": random.choice(COLORES),
            "peso_kg": round(random.uniform(0.1, 25), 2),
            "marca": random.choice(MARCAS),
        },
        "fecha_ingreso": fecha_ingreso,
    }
    mongo_docs.append(doc)

# Construimos el JS a mano (no json.dumps) para poder usar ISODate(...) nativo de Mongo
def doc_to_js(d: dict) -> str:
    atributos = d["atributos"]
    return (
        "  {\n"
        f'    producto_id: "{d["producto_id"]}",\n'
        f'    nombre: "{d["nombre"]}",\n'
        f'    categoria: "{d["categoria"]}",\n'
        f'    stock: {d["stock"]},\n'
        f'    precio: {d["precio"]},\n'
        "    atributos: {\n"
        f'      color: "{atributos["color"]}",\n'
        f'      peso_kg: {atributos["peso_kg"]},\n'
        f'      marca: "{atributos["marca"]}"\n'
        "    },\n"
        f'    fecha_ingreso: ISODate("{d["fecha_ingreso"]}T00:00:00Z")\n'
        "  }"
    )

MONGO_DB_NAME = "taller_mongo"  # debe coincidir con MONGO_INITDB_DATABASE en .env

mongo_js_docs = ",\n".join(doc_to_js(d) for d in mongo_docs)
mongo_js = f"""// init.js (MongoDB)
// Se ejecuta automaticamente una sola vez, en el primer arranque del
// contenedor, gracias al mecanismo docker-entrypoint-initdb.d de la imagen
// oficial de MongoDB. Se usa getSiblingDB() para apuntar explicitamente a la
// base de datos del taller, sin depender del contexto por defecto del shell.

db = db.getSiblingDB('{MONGO_DB_NAME}');

db.inventario.insertMany([
{mongo_js_docs}
]);

db.inventario.createIndex({{ producto_id: 1 }}, {{ unique: true }});
"""
MONGO_INIT.write_text(mongo_js, encoding="utf-8")
print(f"[ok] {MONGO_INIT} ({len(mongo_docs)} documentos)")

print("\nGeneracion de datos sinteticos completada (seed=42, reproducible).")
