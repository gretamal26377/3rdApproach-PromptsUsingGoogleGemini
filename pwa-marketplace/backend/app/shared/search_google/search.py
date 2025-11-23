"""
This module implements the search functionality for the customer-facing API,
leveraging Google Search Engine (placeholder implementation)
"""

import os
import requests
from flask import Blueprint, jsonify, request, current_app

search_bp = Blueprint('search_bp', __name__, url_prefix='/api-search')

@search_bp.route('/search', methods=['GET'])
def search_products():
    search_term = request.args.get('q', '').strip()
    if not search_term:
        return jsonify({
            "products_services": [],
            "stores": [],
            "categories": []
        }), 200

    api_key = current_app.config.get("GOOGLE_SEARCH_API_KEY")
    cx = current_app.config.get("GOOGLE_SEARCH_CX")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": api_key,
        "cx": cx,
        "q": search_term,
    }
    try:
        resp = requests.get(url, params=params, timeout=5)
        # Checks the HTTP response status. If it's successful, continues; otherwise raises an error
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        current_app.logger.error(f"Google Search API error: {e}")
        return jsonify({
            "products_services": [],
            "stores": [],
            "categories": []
        }), 200

    products_services = []
    # Google Custom Search returns a list of items, but not in your domain model.
    # We'll map each result to a product_service, using available fields
    for item in data.get("items", []):
        products_services.append({
            "base_product_service_id": item.get("cacheId", 0),
            "name": item.get("title"),
            "thumbnail_url": item.get("pagemap", {}).get("cse_thumbnail", [{}])[0].get("src", "") if item.get("pagemap", {}).get("cse_thumbnail") else None,
            "lowest_price": None,  # Not available from Google
            "category_name": None  # Not available from Google
        })

    # For this integration, stores and categories are left empty
    return jsonify({
        "products_services": products_services,
        "stores": [],
        "categories": []
    }), 200

@search_bp.route('/products_services/<int:base_product_service_id>/listings', methods=['GET'])
def get_product_service_listings(base_product_service_id):
    # Placeholder: Return a mock list of seller offerings for the product/service
    listings = [
        {
            "listing_id": 1001,
            "base_product_service_id": base_product_service_id,
            "seller_name": "Sample Seller",
            "price": 9.99,
            "stock": 10,
            "listing_url": "https://example.com/sample-listing"
        }
    ]
    return jsonify(listings), 200
