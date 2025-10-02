from logging.config import fileConfig
import os
import sys
# import importlib

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from pathlib import Path

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically
# config_file_name: Filesystem path to the .ini file used by Alembic
if config.config_file_name is not None:
    # Set up logger from the config file (.ini file)
    fileConfig(config.config_file_name)

# Ensure the backend package (project) is on sys.path so imports work
# Alembic env.py lives in backend/alembic; add backend/ to path
# __file__: Path to the current file (env.py)
here = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if here not in sys.path:
    # 0: Insert at front of sys.path to take precedence over other packages.
    # All other paths are moved one position to the right, starting at index 1.
    # This change is in effect only for the duration of this script
    sys.path.insert(0, here)

if config.get_main_option("sqlalchemy.url") != 'sqlite:///:memory:':
    # If a database URL is set in the environment (Docker Compose friendly),
    # prefer that over the value in alembic.ini
    db_url = (
        os.environ.get('DATABASE_URL')
        or os.environ.get('SQLALCHEMY_DATABASE_URI')
        or os.environ.get('DATABASE_URI')
    )

    if db_url:
        # Override the sqlalchemy.url setting in the .ini file with
        # db_url value
        config.set_main_option('sqlalchemy.url', db_url)
    else:
        # Try to build db_url from environment variables and secret file
        here_path = Path(__file__).resolve().parent.parent
        secret_path = here_path.parent.joinpath("database", "secrets", "mysql_db_user_password.txt")
        if secret_path.exists():
            password = secret_path.read_text().strip()
            mysql_user = os.environ.get("MYSQL_USER", "db_user")
            mysql_host = os.environ.get("MYSQL_HOST", "localhost")
            mysql_db = os.environ.get("MYSQL_DATABASE", "marketplace_db")
            tmp_db_url = f"mysql+pymysql://{mysql_user}:{password}@{mysql_host}:3306/{mysql_db}"
            config.set_main_option('sqlalchemy.url', tmp_db_url)

# if sqlalchemy.url is not set, then sqlalchemy.url from alembic.ini will be used

# Add your model's MetaData object here for 'autogenerate' support
# Prefer Flask-SQLAlchemy metadata (db.metadata) since this project uses Flask-SQLAlchemy
try:
    # Import the Flask-SQLAlchemy `db` instance and ensure models are imported
    # so db.metadata is populated with table objects.
    from app.shared.database import db
    import app.shared.models  # noqa: F401  (side-effect: registers models on db.metadata)
    target_metadata = getattr(db, "metadata", None)
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
    script output (stdout by default)

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        # dialect_opts={"paramstyle": "named"},
        # compare_type=True,
        # compare_server_default=True,
        dialect_name='mysql',
        as_sql=True,
    )

    """
     The "with" statement works with objects that support context manager protocol, which means
     they have __enter__() and __exit__() methods.
      __enter__(): Called when execution flow enters the context of the "with" statement
       __exit__(): Called when execution leaves the context of the "with" statement
     This particular case:   
        with: Introduces a context manager
        context manager: An object that defines the runtime context to be established
        begin_transaction(): Start a new transaction block
        run_migrations() in offline: Run migrations in 'offline' mode. That is,
                                     generate SQL statements without executing them
    """
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
        # This with indentation is right, it's acting on previous with context, that is, using same connection
        with context.begin_transaction():
            context.run_migrations()


# is_offline_mode() is true when --sql flag is passed to alembic command.
# See alembic/README file for details.
# Offline Mode: Generates the SQL statements for the migration without
#               applying them to the database. The SQL is printed to the standard output
#               or can be redirected to a file. This mode is useful for reviewing the SQL
#               statements before applying them
# Online Mode:  Applies the migration directly to the database specified
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
