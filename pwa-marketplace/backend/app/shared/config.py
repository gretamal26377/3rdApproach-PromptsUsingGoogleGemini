import os

class Config:
    # SECRET_KEY is used for session management and should be kept secret in production.
    # It's different from DB password
    _secret_key_file = os.environ.get('SECRET_KEY_FILE', '/run/secrets/secret_key')
    _secret_key = None
    if _secret_key_file and os.path.exists(_secret_key_file):
        try:
            with open(_secret_key_file, 'r', encoding='utf-8') as f:
                _secret_key = f.read().strip()
        except Exception:
            pass
    if not _secret_key:
        _secret_key = os.environ.get('SECRET_KEY', 'dev-secret')
    SECRET_KEY = _secret_key

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

    if os.environ.get('SEARCH_ENGINE') == 'meili':
        # Meilisearch configuration. Port: 7700 is the default associated with Meilisearch
        MEILISEARCH_URL = os.environ.get('MEILISEARCH_URL', 'http://localhost:7700')

        # Read Meilisearch API key from Docker secret if available
        _meili_api_key_file = os.environ.get('MEILISEARCH_API_KEY_FILE')
        _meili_api_key = None
        if _meili_api_key_file and os.path.exists(_meili_api_key_file):
            try:
                with open(_meili_api_key_file, 'r', encoding='utf-8') as f:
                    _meili_api_key = f.read().strip()
            except Exception:
                pass
        if not _meili_api_key:
            _meili_api_key = os.environ.get('MEILISEARCH_API_KEY', None)
        MEILISEARCH_API_KEY = _meili_api_key
    else: # SEARCH_ENGINE == 'google'
       # Google Search CX configuration
        GOOGLE_SEARCH_CX = os.environ.get('GOOGLE_SEARCH_CX', None)

        # Read Google API key from Docker secret if available
        _google_api_key_file = os.environ.get('GOOGLE_SEARCH_API_KEY_FILE')
        _google_api_key = None
        if _google_api_key_file and os.path.exists(_google_api_key_file):
            try:
                with open(_google_api_key_file, 'r', encoding='utf-8') as f:
                    _google_api_key = f.read().strip()
            except Exception:
                pass
        if not _google_api_key:
            _google_api_key = os.environ.get('GOOGLE_SEARCH_API_KEY', None)
        GOOGLE_SEARCH_API_KEY = _google_api_key
 





