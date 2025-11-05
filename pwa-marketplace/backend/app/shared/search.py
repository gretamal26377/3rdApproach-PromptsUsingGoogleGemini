"""
This module implements the search functionality for the customer-facing API,
leveraging Meilisearch for fast and relevant search results
"""

import meilisearch
from flask import Blueprint, request, jsonify, current_app

# A dedicated blueprint for search functionality
search_bp = Blueprint('search_bp', __name__, url_prefix='/api')

INDEX_NAME = 'products_services'

# No need of sanitisation here as Meilisearch client handles that internally
@search_bp.route('/search', methods=['GET'])
def search_products():
    """
    Performs a search query against the Meilisearch 'products_services' index

    This endpoint is designed to handle typeahead search from the frontend.
    It uses Meilisearch's faceting and filtering capabilities to return one
    result per unique base product, featuring the seller with the lowest price

    Query Parameters:
        q (str): The search term

    Returns:
        JSON: A list of aggregated search results or an error message
    """
    # '': Default value if no 'q' parameter is provided
    search_term = request.args.get('q', '').strip()

    if not search_term:
        return jsonify([]) # Return empty list if no query

    try:
        client = meilisearch.Client(
            url=current_app.config['MEILISEARCH_URL'],
            api_key=current_app.config['MEILISEARCH_API_KEY']
        )
        index = client.index(INDEX_NAME)

        # 1. Perform an initial search to get all matching product/ service listings
        #    and get a facet distribution for base_product_service_id
        search_results = index.search(
            search_term,
            {
                'facets': ['base_product_service_id']
            }
        )

        facet_distribution = search_results.facet_distribution
        if not facet_distribution or 'base_product_service_id' not in facet_distribution:
            return jsonify([])

        # 2. For each unique base product/service, find the listing with the lowest price
        aggregated_results = []
        # Sequence unpacking where 2nd value is not needed (_), named this way following Python convention
        for base_product_id_iterator, _ in facet_distribution['base_product_service_id'].items():
            # Perform a filtered and sorted search to find the best-priced item
            # for this specific base product/service
            product_service_specific_results = index.search(
                search_term,
                {
                    'filter': f'base_product_service_id = {base_product_id_iterator}',
                    'sort': ['price:asc'],
                    'limit': 1 # We only need the top result (the one with the lowest price)
                }
            )

            if product_service_specific_results.hits:
                best_hit = product_service_specific_results.hits[0]
                # 3. Structure the lightweight JSON for the frontend
                aggregated_results.append({
                    'base_product_service_id': best_hit['base_product_service_id'],
                    'name': best_hit['product_service_name'],
                    'thumbnail_url': best_hit.get('product_service_pic_path'),
                    'lowest_price': best_hit['price'],
                    'category_name': best_hit.get('category_name')
                })

        return jsonify(aggregated_results), 200

    except Exception as e:
        current_app.logger.error(f"Meilisearch query failed: {e}")
        return jsonify({'message': 'Search service is currently unavailable'}), 503

# No need of sanitisation here as Flask allows only integers for base_product_service_id
# Milisearch also cooperates with it as we're using its filtering capabilities
@search_bp.route('/products_services/<int:base_product_service_id>/listings', methods=['GET'])
def get_product_service_listings(base_product_service_id):
    """
    Fetches all seller listings for a specific base product/service ID from Meilisearch

    Args:
        base_product_service_id (int): The ID of the base product/service

    Returns:
        JSON: A list of all seller offerings for the product/service, or an error message
    """
    try:
        client = meilisearch.Client(
            url=current_app.config['MEILISEARCH_URL'],
            api_key=current_app.config['MEILISEARCH_API_KEY']
        )
        index = client.index(INDEX_NAME)

        # Search for all documents matching the base_product_service_id
        # We sort by price to show the cheapest options first
        search_results = index.search(
            '', # Empty query string to match all documents
            {
                'filter': f'base_product_service_id = {base_product_service_id}',
                'sort': ['price:asc'],
                # 'limit': 100 # Adjust limit as needed
            }
        )

        if not search_results.hits:
            return jsonify({'message': 'No listings found for this product/service'}), 404

        # The hits are already the detailed listings we need
        return jsonify(search_results.hits), 200

    except Exception as e:
        current_app.logger.error(f"Meilisearch product listings query failed: {e}")
        return jsonify({'message': 'Search service is currently unavailable'}), 503
