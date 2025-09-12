from logging.config import fileConfig
import os
import sys
import importlib

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically
# config_file_name: Filesystem path to the .ini file used by Alembic
if config.config_file_name is not None:
    # Set up logger from the config file (.ini file)
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
# for 'autogenerate' support
# eg:
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Ensure the backend package (project) is on sys.path so imports work
# Alembic env.py lives in backend/alembic; add backend/ to path
# __file__: Path to the current file (env.py)
here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if here not in sys.path:
    # 0: Insert at front of sys.path to take precedence over other packages.
    # All other paths are moved one position to the right, starting at index 1.
    # This change is in effect only for the duration of this script
    sys.path.insert(0, here)

# If a database URL is set in the environment (Docker Compose friendly),
# prefer that over the value in alembic.ini. Project's env vars used are
# DATABASE_URL and SQLALCHEMY_DATABASE_URI
db_url = (
    os.environ.get('DATABASE_URL')
    or os.environ.get('SQLALCHEMY_DATABASE_URI')
    or os.environ.get('DATABASE_URI')
)
if db_url:
    # Override the sqlalchemy.url setting in the .ini file with
    # db_url value
    config.set_main_option('sqlalchemy.url', db_url)
# else: sqlalchemy.url from alembic.ini will be used

# Add your model's MetaData object here for 'autogenerate' support
# Try to import the project's Base object (app.shared.models.Base)
try:
    # importlib used to avoid hard fail during some CI environments
    proj = importlib.import_module('app.shared.models')
    Base = getattr(proj, 'Base')
    # getattr reads 'Base' attribute named metadata, if it doesn't
    # exist, return None instead of raising an exception
    target_metadata = getattr(Base, 'metadata', None)
except Exception:
    target_metadata = None

# Other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    # with: Introduces a context manager
    # context manager: An object that defines the runtime context 
    #                  to be established
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode

    In this scenario we need to create an Engine
    and associate a connection with the context

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
