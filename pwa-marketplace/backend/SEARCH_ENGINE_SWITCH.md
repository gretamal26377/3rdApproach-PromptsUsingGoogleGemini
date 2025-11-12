# Search Engine Build-Time Switch (Meilisearch vs Google) (GRL: Outdated: It must be reviewed!!)

This backend supports two search engine implementations:

- **Meilisearch** (default, production-ready)
- **Google Search Engine** (placeholder, for future integration)

## How It Works

- Both implementations live in:
  - `app/shared/search_meili/` (Meilisearch)
  - `app/shared/search_google/` (Google Search Engine)
- At build time, Docker uses the `SEARCH_ENGINE` build argument to copy the selected implementation to `app/shared/search/`.
- All backend code imports `search_bp` from `app.shared.search`, which is a build-time mount point for the selected engine.

## Usage

### Build with Meilisearch (default)

```sh
# From backend directory
# This is the default, but you can be explicit:
docker build --build-arg SEARCH_ENGINE=meili -t my-backend:meili .
```

### Build with Google Search Engine (placeholder)

```sh
docker build --build-arg SEARCH_ENGINE=google -t my-backend:google .
```

### Run

- The backend will use the selected search engine logic at runtime.
- All code should import the search blueprint as:
  ```python
  from app.shared.search import search_bp
  ```

## Directory Structure

```
app/shared/
  search_meili/    # Meilisearch implementation
  search_google/   # Google Search Engine implementation
  search/          # Build-time mount point (selected engine)
```

## Notes

- The Google Search Engine implementation is a placeholder and returns 501 Not Implemented.
- To add a new engine, create a new directory under `app/shared/`, implement `search.py` and `search_wsgi.py`, and update the Dockerfile if needed.
- The Dockerfile will fail the build if an unknown `SEARCH_ENGINE` is provided.
