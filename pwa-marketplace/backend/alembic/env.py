from logging.config import fileConfig
import os
import sys
import importlib

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

# if sqlalchemy.url is not set, then sqlalchemy.url from alembic.ini will be used by default

# Add your model's MetaData object here for 'autogenerate' support
# Prefer Flask-SQLAlchemy metadata (db.metadata) since this project uses Flask-SQLAlchemy
try:
    # --- START: New dynamic model loading logic ---

    # Get the custom 'models_file' argument from the command line, if provided.
    # The -x flag is used for this: alembic -x models_file=path/to/models.py revision ...
    models_file_path = context.get_x_argument(as_dictionary=True).get('models_file')

    # If not provided via command line, fall back to the value in alembic.ini
    if not models_file_path:
        models_file_path = config.get_main_option('models_file')

    if models_file_path:
        # Convert the file path (e.g., "app/shared/models.py") to a module path
        # (e.g., "app.shared.models") that Python can import. This is OS-agnostic
        # Windows(\) and Linux-Unix(/)
        p = Path(models_file_path)
        # Remove the .py suffix and join the path parts with dots
        module_path = '.'.join(p.with_suffix('').parts)
        
        print(f"Alembic: Loading models from '{module_path}' for autogenerate")
        
        # Dynamically import the models module
        importlib.import_module(module_path)
    else:
        # If you want to keep the old behavior as a final fallback
        print("Alembic: No models_file specified, using default import")
        # (linter false positive, fixed by adding backend/ to sys.path above > ignored)
        import app.shared.models   # type: ignore

    # Now that the models are loaded, get the metadata from the db object
    # Import the Flask-SQLAlchemy `db` instance and ensure models are imported
    # so db.metadata is populated with table objects
    # (linter false positive, fixed by adding backend/ to sys.path above > ignored)
    from app.shared.database import db   # type: ignore
    target_metadata = getattr(db, "metadata", None)

    # --- END: New dynamic model loading logic ---

except Exception as e:
    print(f"Alembic: Failed to load models for autogeneration. Error: {e}")
    target_metadata = None

# Other values from config file , by the needs of env.py,
# can be acquired/defined here:
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
                                     generates SQL statements without executing them
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
