# Backend Search Service

## Google Search API Setup

Use this setup to enable Google-based search for the marketplace backend.

### 1. Obtain credentials

- Create a Programmable Search Engine at https://programmablesearchengine.google.com/
- Enable the Custom Search API in Google Cloud Console
- Create an API key in Google Cloud Console
- Copy your Search Engine ID (CX)

### 2. Set environment variables

Add these values to your environment, Docker Compose file, or deployment configuration:

- `GOOGLE_SEARCH_API_KEY`: your Google API key
- `GOOGLE_SEARCH_CX`: your Programmable Search Engine ID

### 3. Install dependencies

Make sure the `requests` package is available in `requirements.txt`.

### 4. Build and run

Build the backend with the Google search engine enabled:

```sh
docker build --build-arg SEARCH_ENGINE=google -t my-backend:google .
```

The backend will use the Google Search API for requests under `/api-search/search`.

### 5. Response format

The API returns a normalized structure like this:

```json
{
  "products_services": [],
  "stores": [],
  "categories": []
}
```

This implementation returns real results from Google Custom Search and formats them for the marketplace app.
