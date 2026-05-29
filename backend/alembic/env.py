import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

# Cargar variables de entorno desde .env.local
load_dotenv(Path(__file__).parent.parent.parent / ".env.local")

# Agregar backend/ al path para importar modelos
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.base import Base  # noqa: E402
import models  # noqa: E402 — importar todos los modelos para que Alembic los detecte

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# DATABASE_URL del entorno; fallback a SQLite local para desarrollo
database_url = os.environ.get("DATABASE_URL") or "sqlite:///./dev.db"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
# Usar sqlite fallback en config para satisfacer Alembic; la URL real se usa en run_migrations_online
_url_for_config = "sqlite:///./dev.db" if not database_url.startswith("sqlite") else database_url
config.set_main_option("sqlalchemy.url", _url_for_config)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy import create_engine as _create_engine
    connectable = _create_engine(database_url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
