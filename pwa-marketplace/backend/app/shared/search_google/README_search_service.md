# Backend Search Service (GRL: Outdated! Needs review)

This service exposes the search API for the marketplace, leveraging Meilisearch for fast, relevant search results. It is designed to be used by both the customer and admin backends, as well as directly by frontend clients if needed.

## How it works

- The service runs as a standalone Flask app, exposing endpoints under `/api-search` (e.g., `/api-search/search`)
- It connects to Meilisearch using the `MEILISEARCH_URL` and `MEILISEARCH_API_KEY` environment variables
- It is deployed as its own container (`backend-search`) in `docker-compose.yml`

## Usage

- **Customer and Admin backends**: Make HTTP requests to `http://backend-search:5002/api-search/...` for search functionality.
- **Frontend**: Set the Vite environment variable `VITE_SEARCH_API_BASE_URL` to point to the search service (e.g., `http://localhost:5002/api-search`).

## Development

- The entrypoint is `app/shared/search_wsgi.py`
- The Dockerfile for this service is `backend/Dockerfile-search`
- The service is started with Gunicorn on port 5002

## Example docker-compose service

```
backend-search:
  build:
    context: ./backend
    dockerfile: Dockerfile-search
  ports:
    - "5002:5002"
  environment:
    MEILISEARCH_URL: http://meilisearch:7700
    # MEILISEARCH_API_KEY: <your-key>
  depends_on:
    - meilisearch
```

## Example frontend .env

```
VITE_SEARCH_API_BASE_URL=http://localhost:5002/api-search
```

## Example usage in frontend code

```js
import api from "shared-lib/src/services/api";

// For search requests:
const results = await api.getSearch("search?q=shoes");
```

---

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
- The backend will use the Google Search API for requests at url prefix `/api-search/search`

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

The Google Search Engine implementation returns real results from Google Custom Search
