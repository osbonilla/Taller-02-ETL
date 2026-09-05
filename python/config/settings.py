"""
config/settings.py
-------------------
Punto unico de lectura de configuracion (variables de entorno).

Decision de diseno: en vez de leer os.environ desperdigado por todo el
codigo, centralizamos aqui todas las variables. Esto facilita:
  - saber de un vistazo que variables usa el proyecto,
  - evitar strings de conexion hardcodeados en el codigo (requisito de
    seguridad del taller),
  - cambiar de entorno (local / CI / otra maquina) solo tocando el .env.

Usa dataclasses + valores por defecto explicitos para que, si falta una
variable, el fallo sea temprano y claro (fail fast) en vez de silencioso.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Si existe python-dotenv, lo usamos para cargar un .env local cuando el
# script se ejecuta FUERA de Docker (dentro de Docker las variables ya
# vienen inyectadas por docker-compose y esto simplemente no encuentra
# archivo .env y no hace nada).
try:
    from dotenv import load_dotenv

    _ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
    if _ENV_PATH.exists():
        load_dotenv(_ENV_PATH)
except ImportError:  # pragma: no cover - dotenv es opcional
    pass


def _get(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria '{name}'. "
            f"Revisa tu archivo .env (usa .env.example como referencia)."
        )
    return value


@dataclass(frozen=True)
class ElasticsearchSettings:
    host: str = field(default_factory=lambda: _get("ES_HOST", "http://elasticsearch:9200"))
    index_prefix: str = field(default_factory=lambda: _get("ES_INDEX_PREFIX", "taller"))
    bulk_chunk_size: int = field(default_factory=lambda: int(_get("ES_BULK_CHUNK_SIZE", "500")))
    request_timeout: int = field(default_factory=lambda: int(_get("ES_REQUEST_TIMEOUT", "30")))


@dataclass(frozen=True)
class MySQLSettings:
    host: str = field(default_factory=lambda: _get("MYSQL_HOST", "mysql"))
    port: int = field(default_factory=lambda: int(_get("MYSQL_PORT", "3306")))
    database: str = field(default_factory=lambda: _get("MYSQL_DATABASE", "taller_mysql"))
    user: str = field(default_factory=lambda: _get("MYSQL_USER", "taller_user"))
    password: str = field(default_factory=lambda: _get("MYSQL_PASSWORD", ""))

    @property
    def sqlalchemy_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@dataclass(frozen=True)
class PostgresSettings:
    host: str = field(default_factory=lambda: _get("POSTGRES_HOST", "postgres"))
    port: int = field(default_factory=lambda: int(_get("POSTGRES_PORT", "5432")))
    database: str = field(default_factory=lambda: _get("POSTGRES_DB", "taller_postgres"))
    user: str = field(default_factory=lambda: _get("POSTGRES_USER", "taller_user"))
    password: str = field(default_factory=lambda: _get("POSTGRES_PASSWORD", ""))

    @property
    def sqlalchemy_uri(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )


@dataclass(frozen=True)
class MongoSettings:
    host: str = field(default_factory=lambda: _get("MONGO_HOST", "mongodb"))
    port: int = field(default_factory=lambda: int(_get("MONGO_PORT", "27017")))
    database: str = field(default_factory=lambda: _get("MONGO_INITDB_DATABASE", "taller_mongo"))
    user: str = field(default_factory=lambda: _get("MONGO_INITDB_ROOT_USERNAME", ""))
    password: str = field(default_factory=lambda: _get("MONGO_INITDB_ROOT_PASSWORD", ""))

    @property
    def connection_uri(self) -> str:
        return (
            f"mongodb://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}?authSource=admin"
        )


@dataclass(frozen=True)
class LogstashSettings:
    http_host: str = field(default_factory=lambda: _get("LOGSTASH_HTTP_HOST", "logstash"))
    http_port: int = field(default_factory=lambda: int(_get("LOGSTASH_HTTP_PORT", "8080")))

    @property
    def http_endpoint(self) -> str:
        return f"http://{self.http_host}:{self.http_port}"


@dataclass(frozen=True)
class PipelineSettings:
    batch_interval_seconds: int = field(
        default_factory=lambda: int(_get("BATCH_INTERVAL_SECONDS", "120"))
    )
    producer_interval_seconds: float = field(
        default_factory=lambda: float(_get("PRODUCER_INTERVAL_SECONDS", "5"))
    )
    run_once: bool = field(
        default_factory=lambda: _get("BATCH_RUN_ONCE", "false").lower() in ("1", "true", "yes")
    )
    log_level: str = field(default_factory=lambda: _get("LOG_LEVEL", "INFO"))
    data_raw_dir: Path = field(
        default_factory=lambda: Path(_get("DATA_RAW_DIR", "/app/data/raw"))
    )


@dataclass(frozen=True)
class Settings:
    elasticsearch: ElasticsearchSettings = field(default_factory=ElasticsearchSettings)
    mysql: MySQLSettings = field(default_factory=MySQLSettings)
    postgres: PostgresSettings = field(default_factory=PostgresSettings)
    mongo: MongoSettings = field(default_factory=MongoSettings)
    logstash: LogstashSettings = field(default_factory=LogstashSettings)
    pipeline: PipelineSettings = field(default_factory=PipelineSettings)


def get_settings() -> Settings:
    """Fabrica simple; si en el futuro se requiere cache, se agrega aqui."""
    return Settings()
