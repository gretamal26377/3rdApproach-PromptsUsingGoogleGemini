# Search Engine Build-Time Switch (Meilisearch vs Google) (GRL: Outdated: It must be reviewed!!)

This backend supports two search engine implementations:

- **Meilisearch** (default, production-ready)
- **Google Search Engine**

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


## Google Search API Setup

To use the Google Search JSON API integration:

1. **Obtain Credentials:**
  - Create a Programmable Search Engine at https://programmablesearchengine.google.com/
  - Get your Search Engine ID (CX) and enable the Custom Search API in Google Cloud Console
  - Create an API key in Google Cloud Console

2. **Set Environment Variables:**
  - `GOOGLE_SEARCH_API_KEY`: Your Google API key
  - `GOOGLE_SEARCH_CX`: Your Programmable Search Engine ID
  - Set these in your environment, Docker Compose, or deployment config

3. **Install Dependencies:**
  - Ensure `requests` is present in `requirements.txt`

4. **Build and Run:**
  - Build with `SEARCH_ENGINE=google` as shown above
  - The backend will use the Google Search API for `/api-search/search` requests

5. **Response Format:**
  - The API will always return a normalized structure:
    ```json
    {
     "products_services": [...],
     "stores": [],
     "categories": []
    }
    ```

---
*The Google Search Engine implementation now returns real results from Google Custom Search*
