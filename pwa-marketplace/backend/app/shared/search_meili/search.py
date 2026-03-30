"""
This module implements the search functionality for the customer-facing API,
leveraging Meilisearch for fast and relevant search results
"""

import meilisearch
from flask import Blueprint, request, jsonify, current_app

# A dedicated blueprint for search functionality
search_bp = Blueprint('search_bp', __name__, url_prefix='/api-search')

INDEX_NAME = 'products_services_stores_categories'

# No need of sanitisation here as Meilisearch client handles that internally
@search_bp.route('/search', methods=['GET'])
def search_products_services():
    """
    Performs a search query against the Meilisearch 'products_services_stores_categories' index

    This endpoint is designed to handle typeahead search from the frontend.
    It returns results grouped by document type (Products/Services, Stores, Categories).
    For Products/Services, it aggregates results to show one entry per base
    product/service, featuring the seller with the lowest price

    Query Parameters:
        q (str): The search term

    Returns:
        JSON: A dictionary of search results grouped by type, or an error message
    """
    # '': Default value if no 'q' parameter is provided
    search_term = request.args.get('q', '').strip()

    # --- Normalized Response Format ---
    # {
    #   "products_services": [
    #     {
    #       "base_product_service_id": int,
    #       "name": str,
    #       "thumbnail_url": str | null,
    #       "lowest_price": float,
    #       "category_name": str | null
    #     }, ...
    #   ],
    #   "stores": [
    #     {
    #       "id": int,
    #       "name": str,
    #       "description": str
    #     }, ...
    #   ],
    #   "categories": [
    #     {
    #       "id": int,
    #       "name": str,
    #       "description": str
    #     }, ...
    #   ]
    # }

    if not search_term:
        return jsonify({})  # Return empty object if no query

    try:
        client = meilisearch.Client(
            url=current_app.config['MEILISEARCH_URL'],
            api_key=current_app.config['MEILISEARCH_API_KEY']
        )
        index = client.index(INDEX_NAME)

        # --- Main Search Logic ---
        # 1. Perform a broad search and get facet distribution for each document type
        #    search_results = Contains all data details categorized by document type
        search_results = index.search(
            search_term,
            {'facets': ['document_type']}
        )

        # 2. Initialize structure for the final grouped results
        grouped_results = {
            "products_services": [],
            "stores": [],
            "categories": []
        }

        # facet_distribution: Contains counts of each document type found in the search
        facet_distribution = search_results.facet_distribution
        if not facet_distribution or 'document_type' not in facet_distribution:
            # jsonify({}): Return empty object and automatically sets/add/return status code 200 despite explicitly not setting it 
            # return jsonify({})
            # Best Practice: Changed to return object with empty keys
            return jsonify(grouped_results), 200

        # 3. Process each document type found in the search.
        #    Sequence unpacking where 2nd value is not needed (_), named this way following Python convention
        #    facet_distribution['document_type'].items(): Contains document types and their counts. In this case it
        #    contains counts for three document types: 'Product/Service', 'Store', 'Category'
        for doc_type, _ in facet_distribution['document_type'].items():
            if doc_type == 'Product/Service':
                # For products/services, we need to find the best-priced item for each unique base product/service.
                # This is a more complex aggregation
                product_service_facet_search = index.search(
                    search_term,
                    {
                        'filter': 'document_type = "Product/Service"',
                        'facets': ['base_product_service_id']
                    }
                )
                product_service_facets = product_service_facet_search.facet_distribution
                if product_service_facets and 'base_product_service_id' in product_service_facets:
                    for base_id, _ in product_service_facets['base_product_service_id'].items():
                        # For each unique product/service, find the listing with the lowest price
                        best_price_search = index.search(
                            search_term,
                            {
                                'filter': f'base_product_service_id = {base_id}',
                                'sort': ['price:asc'],
                                'limit': 1
                            }
                        )
                        if best_price_search.hits:
                            best_hit = best_price_search.hits[0]
                            grouped_results["products_services"].append({
                                'base_product_service_id': best_hit['base_product_service_id'],
                                'name': best_hit['product_service_name'],
                                'thumbnail_url': best_hit.get('product_service_pic_path'),
                                'lowest_price': best_hit['price'],
                                'category_name': best_hit.get('category_name')
                            })

            elif doc_type in ['Store', 'Category']:
                # For stores and categories, the logic is simpler: just get the search hits
                type_search_results = index.search(
                    search_term,
                    {
                        'filter': f'document_type = "{doc_type}"',
                        'limit': 5  # Limit to 5 best matches per document type ranked by Milisearch
                                    # internal algorithm based on defined ranking rules
                    }
                )
                
                # Map to a cleaner structure for the frontend
                if doc_type == 'Store':
                    for hit in type_search_results.hits:
                        grouped_results["stores"].append({
                            'id': hit['store_id'],
                            'name': hit['store_name'],
                            # '': It's a default value used when 'store_description' is missing,
                            # that is, when store_description key doesn't exist in the hit dictionary
                            'description': hit.get('store_description', '')
                        })
                elif doc_type == 'Category':
                    for hit in type_search_results.hits:
                        grouped_results["categories"].append({
                            'id': hit['category_id'],
                            'name': hit['category_name'],
                            'description': hit.get('category_description', '')
                        })

        return jsonify(grouped_results), 200

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
        current_app.logger.error(f"Meilisearch product/service listings query failed: {e}")
        return jsonify({'message': 'Search service is currently unavailable'}), 503
