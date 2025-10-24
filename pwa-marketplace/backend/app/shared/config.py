import os

class Config:
    # SECRET_KEY is used for session management and should be kept secret in production.
    # It's different from DB password
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

    # Prefer an explicit DATABASE_URL if provided (useful for tests/CI).
    _env_database_url = os.environ.get('DATABASE_URL')
    if _env_database_url:
        SQLALCHEMY_DATABASE_URI = _env_database_url
    else:
        # Determine path to the password file (compose provides this via secrets)
        pw_file = (
            os.environ.get('MYSQL_PASSWORD_FILE')
            or '/run/secrets/mysql_db_user_password'
        )

        # Try to read password from env var, if not set fallback to an empty string
        password = os.environ.get('MYSQL_DB_USER_PASSWORD', '')
        try:
            # If path exists, read the password from the file
            if os.path.exists(pw_file):
                with open(pw_file, 'r', encoding='utf-8') as f:
                    password = f.read().strip()
        except Exception:
            # If reading the secret fails, fall back to password from env var/default
            pass # This command does nothing, it's Python syntax, it's used as a placeholder
                 # to indicate that we are intentionally ignoring exceptions here

        user = os.environ.get('MYSQL_USER', 'db_user')
        host = os.environ.get('MYSQL_HOST', 'localhost')
        dbname = os.environ.get('MYSQL_DATABASE', 'marketplace_db')
        # This var is reserved and used by SQLAlchemy internally (do not change it)
        # to connect the DB with db setting in database.py when init_extensions(app) is called
        SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{user}:{password}@{host}:3306/{dbname}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
