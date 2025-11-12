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

from app.shared.database import db   # type: ignore
from app import create_app   # type: ignore

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
        from app.shared import models_sql2orm_flask_sqlalchemy    # type: ignore  # noqa: F401
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)
        
        print("\n📊 Generating ER Diagram from SQLAlchemy metadata...")
        
        try:
            # --- Primary Method: In-memory SQLite with render_er ---
            print("\nAttempting primary method (in-memory SQLite)...")
            from sqlalchemy import create_engine
            
            # Use an in-memory SQLite database
            temp_engine = create_engine('sqlite:///:memory:')
            
            # Create all tables in the temporary database
            db.metadata.create_all(bind=temp_engine)
            
            print("\n🎨 Creating diagram...")
            
            # Generate the diagram from the temporary database
            render_er('sqlite:///:memory:', output_path)
            print("   ✅ Primary method successful.")

        except Exception as e1:
            print(f"\n⚠️ Primary method failed: {e1}")
            print("   Falling back to alternative method (metadata-to-dot)...")
            
            try:
                # --- Alternative Method: Metadata to DOT file ---
                import subprocess
                from eralchemy2.main import intermediary_to_dot
                from eralchemy2.main import metadata_to_intermediary  # type: ignore

                tables, relationships = metadata_to_intermediary(db.metadata)
                dot_output = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME.replace('.pdf', '.dot'))
                intermediary_to_dot(tables, relationships, output=dot_output)
                
                subprocess.run(['dot', '-Tpdf', dot_output, '-o', output_path], check=True)
                print("   ✅ Alternative method successful")

                # Clean up DOT file
                # if os.path.exists(dot_output):
                #    os.remove(dot_output)
                #    print("      🧹 Cleaned up temporary DOT file")

            except Exception as e2:
                print("\n❌ ERROR: Both generation methods failed")
                print(f"   Primary method error: {e1}")
                print(f"   Alternative method error: {e2}")
                print("\nTroubleshooting tips:")
                print("   1. Ensure graphviz is installed and in your system's PATH")
                print("   2. Run 'dot -V' in your terminal to verify graphviz installation")
                print("   3. Check for errors in your SQLAlchemy model definitions")
                return

        # --- Success Message ---
        print("\n✅ SUCCESS! ER Diagram generated successfully!")
        print(f"   📁 Location: {output_path}")
        if os.path.exists(output_path):
            print(f"   📏 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
        
        print("\n📋 Diagram includes:")
        print("   • All database tables and their columns")
        print("   • Primary keys (PK)")
        print("   • Foreign keys (FK)")
        print("   • Relationships between tables")
        print("   • Data types for each column")
        print("\n" + "=" * 70)


if __name__ == '__main__':
    print("\nIt'll try method (1), if fail, try method (2):")
    print("1. From SQLAlchemy metadata (no database required)")
    print("2. From database URI (requires database connection)")
    
    # Default to metadata mode as it's more reliable
    try:
        generate_er_diagram_from_metadata()
    except Exception as e:
        print(f"\nMetadata mode failed: {e}")
        print("\nTrying database URI mode...")
        generate_er_diagram()
