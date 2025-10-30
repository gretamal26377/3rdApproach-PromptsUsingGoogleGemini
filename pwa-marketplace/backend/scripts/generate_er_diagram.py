"""
Generate an Entity-Relationship Diagram (ERD) from the database models

This script creates a visual representation of the database schema defined in
models_sql2orm_flask_sqlalchemy.py or a DB live connection, and exports it as a PDF file

Requirements:
    - graphviz (system package)
    - eralchemy2 (Python package)
    
Usage (from backend/):
    python -m scripts.generate_er_diagram
"""

import os
import sys
from datetime import datetime

# --- Path Setup ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- End Path Setup ---

try:
    from eralchemy2 import render_er
    print("✓ eralchemy2 is installed")
except ImportError:
    print("ERROR: eralchemy2 is not installed.")
    print("Please install it with: pip install eralchemy2")
    print("Note: You also need graphviz installed on your system")
    print("  Windows: choco install graphviz or download from https://graphviz.org/download/")
    print("  Linux: sudo apt-get install graphviz")
    print("  Mac: brew install graphviz")
    sys.exit(1)

from app.shared.database import db
from app import create_app

# --- Configuration ---
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
OUTPUT_FILENAME = f'er_diagram_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
# --- End Configuration ---


def generate_er_diagram():
    """
    Generate an ER diagram live from the DB live connection and save it as a PDF
    """
    print("=" * 70)
    print("Entity-Relationship Diagram Generator from DB live connection")
    print("=" * 70)
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        
        print("\n📊 Generating ER Diagram from live database models...")
        # Print the 50 first DB URI chars coming from SQLALCHEMY_DATABASE_URI for verification and 'Not configured' if it isn't set
        print(f"   Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')[:50]}...")
        
        try:
            # Get the database URI from the app config
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            
            if not db_uri:
                print("\nERROR: SQLALCHEMY_DATABASE_URI not configured in app config")
                return
            
            # Generate the ER diagram
            # Mode options: 'er' (Entity-Relationship) or 'graph'
            # We'll use 'er' mode to show relationships clearly
            print("\n🎨 Creating diagram...")
            render_er(db_uri, output_path)
            
            print("\n✅ SUCCESS! ER Diagram generated successfully!")
            print(f"   📁 Location: {output_path}")
            print(f"   📏 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
            
            # Additional information
            print("\n📋 Diagram includes:")
            print("   • All database tables and their columns")
            print("   • Primary keys (PK)")
            print("   • Foreign keys (FK)")
            print("   • Relationships between tables")
            print("   • Data types for each column")
            
            print("\n" + "=" * 70)
            
        except Exception as e:
            print("\n❌ ERROR: Failed to generate ER diagram")
            print(f"   Details: {str(e)}")
            print("\nTroubleshooting tips:")
            print("   1. Ensure graphviz is installed on your system")
            print("   2. Check that the database is accessible")
            print("   3. Verify that models are properly defined")
            return


def generate_er_diagram_from_metadata():
    """
    Alternative method: Generate ER diagram directly from SQLAlchemy metadata models.
    This method doesn't require a live database connection
    """
    print("=" * 70)
    print("Entity-Relationship Diagram Generator (from Metadata models)")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        # Import all models to ensure they're registered with SQLAlchemy
        from app.shared import models_sql2orm_flask_sqlalchemy  # noqa: F401
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        
        print("\n📊 Generating ER Diagram from SQLAlchemy metadata...")
        
        try:
            # Create a temporary in-memory SQLite database with the schema
            from sqlalchemy import create_engine
            
            # Use an in-memory SQLite database
            temp_engine = create_engine('sqlite:///:memory:')
            
            # Create all tables in the temporary database
            db.metadata.create_all(bind=temp_engine)
            
            print("\n🎨 Creating diagram...")
            
            # Generate the diagram from the temporary database
            render_er('sqlite:///:memory:', output_path)
            
            # Alternative: if the above doesn't work, try rendering from metadata directly
            # This requires creating a DOT file first
            from eralchemy2 import intermediary_to_dot
            from eralchemy2.sqla import metadata_to_intermediary
            
            # Convert metadata to intermediary format
            tables = metadata_to_intermediary(db.metadata)
            
            # Generate DOT format
            dot_output = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME.replace('.pdf', '.dot'))
            intermediary_to_dot(tables, dot_output)
            
            # Convert DOT to PDF using graphviz
            import subprocess
            pdf_output = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
            subprocess.run(['dot', '-Tpdf', dot_output, '-o', pdf_output], check=True)
            
            print("\n✅ SUCCESS! ER Diagram generated successfully!")
            print(f"   📁 Location: {pdf_output}")
            print(f"   📏 File size: {os.path.getsize(pdf_output) / 1024:.2f} KB")
            
            print("\n📋 Diagram includes:")
            print("   • All database tables and their columns")
            print("   • Primary keys (PK)")
            print("   • Foreign keys (FK)")
            print("   • Relationships between tables")
            print("   • Data types for each column")
            
            # Clean up DOT file
            if os.path.exists(dot_output):
                os.remove(dot_output)
                print("   🧹 Cleaned up temporary DOT file")
            
            print("\n" + "=" * 70)
            
        except Exception as e:
            print("\n❌ ERROR: Failed to generate ER diagram")
            print(f"   Details: {str(e)}")
            print("\nTroubleshooting tips:")
            print("   1. Ensure graphviz is installed and in PATH")
            print("   2. Try running 'dot -V' to verify graphviz installation")
            print("   3. Check that eralchemy2 is properly installed")
            return


if __name__ == '__main__':
    print("\nChoose generation method:")
    print("1. From database URI (requires database connection)")
    print("2. From SQLAlchemy metadata (no database required)")
    
    # Default to metadata mode as it's more reliable
    try:
        generate_er_diagram_from_metadata()
    except Exception as e:
        print(f"\nMetadata mode failed: {e}")
        print("\nTrying database URI mode...")
        generate_er_diagram()
