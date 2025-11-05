"""
This script fetches product data from the application's database and indexes it
into a Meilisearch instance. It's designed to be run as a one-off task or
on a schedule to keep the search index in sync with the database.

The script structures the data to solve the "same product, different seller"
problem by creating a document for each unique seller's listing but linking
them via a common 'base_product_service_id'.

Usage (from backend/):
  python -m scripts.index_products_services
"""

import os
import sys
import meilisearch
# import time

# --- Path Setup ---
# Add the project's root directory (backend/) to the Python path
# This allows the script to import modules from the 'app' package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- End Path Setup ---

from app.shared.database import db
from app.shared.models_sql2orm_flask_sqlalchemy import StoreProductsServices, ProductsServices, Stores, Categories
from app import create_app

# --- Configuration ---
INDEX_NAME = 'products_services'
# --- End Configuration ---

def run_indexing():
    """
    Connects to the database and Meilisearch, fetches product listings,
    and indexes them
    """
    print("Starting product indexing process...")

    # Create a Flask app context to access the database and config
    app = create_app()
    with app.app_context():
        # 1. Initialize Meilisearch Client
        try:
            client = meilisearch.Client(
                url=app.config['MEILISEARCH_URL'],
                api_key=app.config['MEILISEARCH_API_KEY']
            )
            print(f"Successfully connected to Meilisearch at {app.config['MEILISEARCH_URL']}")
        except Exception as e:
            print(f"Error: Could not connect to Meilisearch. Please ensure it is running. Details: {e}")
            return

        # 2. Fetch Data from Database
        # We query the 'StoreProductsServices' table which represents a single product
        # listing by a specific store. We join with ProductsServices and Stores to get
        # all the details we need for the search document
        print("Fetching product/service listings from the database...")
        try:
            listings = db.session.query(
                StoreProductsServices,
                ProductsServices,
                Stores,
                Categories
            ).join(
                ProductsServices, StoreProductsServices.product_service_id == ProductsServices.product_service_id
            ).join(
                Stores, StoreProductsServices.store_id == Stores.store_id
            ).join(
                Categories, ProductsServices.product_service_category_id == Categories.category_id
            ).all()
            print(f"Found {len(listings)} product/service listings to index")
        except Exception as e:
            print(f"Error: Failed to fetch data from the database. Details: {e}")
            return

        if not listings:
            print("No product/service listings found in the database. Exiting")
            return

        # 3. Structure Documents for Meilisearch
        documents = []
        # Iterate and unpack the listings into these four variables
        for listing, product_service, store, category in listings:
            doc = {
                # Use the unique ID of the listing as the document ID
                'id': listing.id,
                'document_type': 'Product/Service',
                # This is the key for grouping results by the base product/service
                'base_product_service_id': product_service.product_service_id,
                'product_service_name': product_service.product_service_name,
                'product_service_description': product_service.product_service_description,
                'product_service_pic_path': product_service.product_service_pic_path,
                # Category information
                'category_id': category.category_id,
                'category_name': category.category_name,
                'category_description': category.category_description,
                # Seller-specific information
                'price': float(listing.price), # Ensure price is a float for sorting
                'stock': listing.stock,
                'store_id': store.store_id,
                'store_name': store.store_name,
                'store_description': store.store_description,
            }
            documents.append(doc)
        
        print(f"Prepared {len(documents)} documents for indexing")

        # 4. Configure and Add Documents to Meilisearch Index
        try:
            print(f"Updating index '{INDEX_NAME}'...")
            
            # Set index settings
            # These settings are crucial for the search logic in the API
            settings = {
                'searchableAttributes': [
                    'product_service_name',
                    'product_service_description',
                    'store_name',
                    'store_description',
                    'category_name',
                    'category_description',
                    'price',
                    'stock'
                ],
                'filterableAttributes': [
                    'base_product_service_id',
                    'store_id',
                    'category_id',
                    'document_type',
                    'price',
                    'stock'
                ],
                'sortableAttributes': [
                    'store_name',
                    'product_service_name',
                    'category_name',
                    'price',
                    'stock'
                ],
                'rankingRules': [
                    'words',
                    'typo',
                    'proximity',
                    'attribute',
                    'sort',
                    'exactness',
                    'price:asc' # Custom ranking rule to favor lower prices
                ]
            }
            task = client.index(INDEX_NAME).update_settings(settings)
            print(f"Update settings task queued (Task UID: {task.task_uid}). Waiting for completion...")
            # Wait up to 5 seconds for the settings update to complete, After 5 seconds the script continues,
            # but execution will raise an exception despite the task goes on, because this line's idea was
            # to ensure task completion before proceeding
            client.wait_for_task(task.task_uid, timeout_in_ms=5000)
            print("Index settings updated successfully")

            # Add documents to the index
            task = client.index(INDEX_NAME).add_documents(documents, primary_key='id')
            print(f"Add documents task queued (Task UID: {task.task_uid}). Waiting for completion...")
            client.wait_for_task(task.task_uid, timeout_in_ms=5000)
            print("Documents added successfully")

        except Exception as e:
            print(f"Error: An error occurred while indexing documents to Meilisearch. Details: {e}")
            return

    print("Product indexing process completed successfully")


if __name__ == '__main__':
    run_indexing()
