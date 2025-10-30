"""
Generate an Entity-Relationship Diagram (ERD) - Alternative Version

This script creates a visual representation of the database schema using
multiple rendering options, including methods that don't require Graphviz
system installation

Usage (from backend/):
    python                 "</body>",
                "<body>",
                "    <h1>Database Schema Documentation</h1>",
                f"    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            ]
            
            # Summary section
            tables = [t for t in db.metadata.tables.keys() if '_history' not in t]
            history_tables = [t for t in db.metadata.tables.keys() if '_history' in t]
            
            html_content.append("    <div class='summary'>")
            html_content.append("        <h2>Summary</h2>")
            html_content.append(f"        <p><strong>Total Tables:</strong> {len(db.metadata.tables)}</p>")nerate_er_diagram_alt
"""

import os
import sys
from datetime import datetime

# --- Path Setup ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --- End Path Setup ---

from app.shared.database import db
from app import create_app

# --- Configuration ---
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')
OUTPUT_BASE = f'er_diagram_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
# --- End Configuration ---


def check_graphviz_installed():
    """Check if Graphviz is installed on the system"""
    import subprocess
    try:
        subprocess.run(['dot', '-V'], capture_output=True, check=True)
        return True
    # If try fails due to CalledProcessError or FileNotFoundError then except triggers
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def generate_mermaid_diagram():
    """
    Generate an ER diagram in Mermaid format.
    Mermaid diagrams can be viewed in GitHub, VS Code, and many other tools
    """
    print("=" * 70)
    print("Entity-Relationship Diagram Generator - Mermaid Format")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        from app.shared import models_sql2orm_flask_sqlalchemy  # noqa: F401
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f'{OUTPUT_BASE}.mmd')
        
        print("\n📊 Generating ER Diagram in Mermaid format...")
        
        try:
            # Build Mermaid diagram
            mermaid_content = ["erDiagram"]
            
            # Iterate through all tables in metadata
            for table_name, table in db.metadata.tables.items():
                # Skip history tables for cleaner diagram
                if '_history' in table_name:
                    continue
                
                # Format table name for Mermaid
                entity_name = table_name.upper().replace('_', '-')
                
                # Add entity attributes
                mermaid_content.append(f"    {entity_name} {{")
                
                for column in table.columns:
                    col_type = str(column.type)
                    # Simplify type names for readability
                    if 'VARCHAR' in col_type or 'String' in col_type:
                        col_type = 'string'
                    elif 'INTEGER' in col_type or 'Integer' in col_type:
                        col_type = 'int'
                    elif 'TEXT' in col_type or 'Text' in col_type:
                        col_type = 'text'
                    elif 'DECIMAL' in col_type or 'Numeric' in col_type:
                        col_type = 'decimal'
                    elif 'DATETIME' in col_type or 'DateTime' in col_type:
                        col_type = 'datetime'
                    elif 'JSON' in col_type:
                        col_type = 'json'
                    
                    pk_marker = " PK" if column.primary_key else ""
                    fk_marker = " FK" if column.foreign_keys else ""
                    nullable = "" if column.nullable else " NOT_NULL"
                    
                    mermaid_content.append(
                        f"        {col_type} {column.name}{pk_marker}{fk_marker}{nullable}"
                    )
                
                mermaid_content.append("    }")
            
            # Add relationships
            mermaid_content.append("")
            for table_name, table in db.metadata.tables.items():
                if '_history' in table_name:
                    continue
                    
                entity_name = table_name.upper().replace('_', '-')
                
                for column in table.columns:
                    if column.foreign_keys:
                        for fk in column.foreign_keys:
                            ref_table = fk.column.table.name.upper().replace('_', '-')
                            # Determine relationship type based on primary key
                            if column.primary_key:
                                rel_type = "||--||"  # one-to-one
                            else:
                                rel_type = "||--o{"  # one-to-many
                            
                            mermaid_content.append(
                                f"    {ref_table} {rel_type} {entity_name} : has"
                            )
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(mermaid_content))
            
            print("\n✅ SUCCESS! ER Diagram generated in Mermaid format!")
            print(f"   📁 Location: {output_path}")
            print(f"   📏 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
            
            print("\n📋 How to view this diagram:")
            print("   • Open in VS Code with Mermaid preview extension")
            print("   • View on GitHub (automatic rendering)")
            print("   • Use https://mermaid.live/ to render and export")
            print("   • Convert to PDF using online tools or CLI")
            
            print("\n" + "=" * 70)
            return output_path
            
        except Exception as e:
            print("\n❌ ERROR: Failed to generate Mermaid diagram")
            print(f"   Details: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def generate_plantuml_diagram():
    """
    Generate an ER diagram in PlantUML format.
    PlantUML can be rendered in many editors and online tools
    """
    print("=" * 70)
    print("Entity-Relationship Diagram Generator - PlantUML Format")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        from app.shared import models_sql2orm_flask_sqlalchemy  # noqa: F401
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f'{OUTPUT_BASE}.puml')
        
        print("\n📊 Generating ER Diagram in PlantUML format...")
        
        try:
            # Build PlantUML diagram
            puml_content = ["@startuml", "!define Table(name,desc) class name as \"desc\" << (T,#FFAAAA) >>"]
            puml_content.append("!define primary_key(x) <b>x</b>")
            puml_content.append("!define foreign_key(x) <i>x</i>")
            puml_content.append("hide methods")
            puml_content.append("hide stereotypes")
            puml_content.append("")
            
            # Iterate through all tables
            for table_name, table in db.metadata.tables.items():
                # Skip history tables
                if '_history' in table_name:
                    continue
                
                puml_content.append(f"entity \"{table_name}\" as {table_name} {{")
                
                # Add columns
                for column in table.columns:
                    col_type = str(column.type)
                    pk_marker = " <<PK>>" if column.primary_key else ""
                    fk_marker = " <<FK>>" if column.foreign_keys else ""
                    
                    if column.primary_key:
                        puml_content.append(f"  + **{column.name}** : {col_type}{pk_marker}")
                    elif column.foreign_keys:
                        puml_content.append(f"  # *{column.name}* : {col_type}{fk_marker}")
                    else:
                        puml_content.append(f"  {column.name} : {col_type}")
                
                puml_content.append("}")
                puml_content.append("")
            
            # Add relationships
            for table_name, table in db.metadata.tables.items():
                if '_history' in table_name:
                    continue
                
                for column in table.columns:
                    if column.foreign_keys:
                        for fk in column.foreign_keys:
                            ref_table = fk.column.table.name
                            if '_history' not in ref_table:
                                puml_content.append(f"{ref_table} ||--o{{ {table_name}")
            
            puml_content.append("")
            puml_content.append("@enduml")
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(puml_content))
            
            print("\n✅ SUCCESS! ER Diagram generated in PlantUML format!")
            print(f"   📁 Location: {output_path}")
            print(f"   📏 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
            
            print("\n📋 How to view/render this diagram:")
            print("   • Use VS Code PlantUML extension")
            print("   • Visit http://www.plantuml.com/plantuml/uml/")
            print("   • Use PlantUML CLI: plantuml diagram.puml")
            print("   • IntelliJ IDEA has built-in PlantUML support")
            
            print("\n" + "=" * 70)
            return output_path
            
        except Exception as e:
            print("\n❌ ERROR: Failed to generate PlantUML diagram")
            print(f"   Details: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def generate_html_report():
    """
    Generate an HTML report with database schema information
    """
    print("=" * 70)
    print("Database Schema Report Generator - HTML Format")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        from app.shared import models_sql2orm_flask_sqlalchemy  # noqa: F401
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_path = os.path.join(OUTPUT_DIR, f'{OUTPUT_BASE}.html')
        
        print("\n📊 Generating Database Schema Report...")
        
        try:
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "    <meta charset='UTF-8'>",
                "    <title>Database Schema - ER Diagram</title>",
                "    /* <style>: Embed CSS styles directly in the HTML document */",
                "    <style>",
                "        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }",
                "        h1 { color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }",
                "        h2 { color: #555; margin-top: 30px; }",
                "        .table-container { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }",
                "        .table-name { font-size: 24px; color: #2196F3; margin-bottom: 10px; }",
                "        table { width: 100%; border-collapse: collapse; margin-top: 10px; }",
                "        th { background: #4CAF50; color: white; padding: 12px; text-align: left; }",
                "        td { padding: 10px; border-bottom: 1px solid #ddd; }",
                "        tr:hover { background: #f5f5f5; }",
                "        .pk { color: #e91e63; font-weight: bold; }",
                "        .fk { color: #2196F3; font-style: italic; }",
                "        .nullable { color: #999; }",
                "        .relationships { background: #fff9c4; padding: 10px; margin: 10px 0; border-left: 4px solid #fbc02d; }",
                "        .summary { background: #e3f2fd; padding: 20px; margin: 20px 0; border-radius: 8px; }",
                "        .badge { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 12px; margin-left: 5px; }",
                "        .badge-pk { background: #e91e63; color: white; }",
                "        .badge-fk { background: #2196F3; color: white; }",
                "        .badge-not-null { background: #4CAF50; color: white; }",
                "        .badge-unique { background: #9c27b0; color: white; }",
                "    </style>",
                "</head>",
                "<body>",
                f"    <h1>Database Schema Documentation</h1>",
                f"    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            ]
            
            # Summary section
            tables = [t for t in db.metadata.tables.keys() if '_history' not in t]
            history_tables = [t for t in db.metadata.tables.keys() if '_history' in t]
            
            html_content.append("    <div class='summary'>")
            html_content.append(f"        <h2>Summary</h2>")
            html_content.append(f"        <p><strong>Total Tables:</strong> {len(db.metadata.tables)}</p>")
            html_content.append(f"        <p><strong>Business Tables:</strong> {len(tables)}</p>")
            html_content.append(f"        <p><strong>History/Audit Tables:</strong> {len(history_tables)}</p>")
            html_content.append("    </div>")
            
            # Table details
            html_content.append("    <h2>Table Details</h2>")
            
            for table_name in sorted(tables):
                table = db.metadata.tables[table_name]
                html_content.append("    <div class='table-container'>")
                html_content.append(f"        <div class='table-name'>📋 {table_name}</div>")
                html_content.append("        <table>")
                html_content.append("            <thead>")
                html_content.append("                <tr><th>Column</th><th>Type</th><th>Constraints</th></tr>")
                html_content.append("            </thead>")
                html_content.append("            <tbody>")
                
                for column in table.columns:
                    badges = []
                    if column.primary_key:
                        badges.append("<span class='badge badge-pk'>PK</span>")
                    if column.foreign_keys:
                        badges.append("<span class='badge badge-fk'>FK</span>")
                    if not column.nullable:
                        badges.append("<span class='badge badge-not-null'>NOT NULL</span>")
                    if column.unique:
                        badges.append("<span class='badge badge-unique'>UNIQUE</span>")
                    
                    badges_html = ' '.join(badges)
                    html_content.append("                <tr>")
                    html_content.append(f"                    <td><strong>{column.name}</strong></td>")
                    html_content.append(f"                    <td>{column.type}</td>")
                    html_content.append(f"                    <td>{badges_html}</td>")
                    html_content.append("                </tr>")
                
                html_content.append("            </tbody>")
                html_content.append("        </table>")
                
                # Relationships
                relationships = []
                for column in table.columns:
                    if column.foreign_keys:
                        for fk in column.foreign_keys:
                            ref_table = fk.column.table.name
                            ref_column = fk.column.name
                            relationships.append(f"{column.name} → {ref_table}.{ref_column}")
                
                if relationships:
                    html_content.append("        <div class='relationships'>")
                    html_content.append("            <strong>Relationships:</strong><br>")
                    for rel in relationships:
                        html_content.append(f"            • {rel}<br>")
                    html_content.append("        </div>")
                
                html_content.append("    </div>")
            
            html_content.append("</body>")
            html_content.append("</html>")
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(html_content))
            
            print("\n✅ SUCCESS! Database Schema Report generated!")
            print(f"   📁 Location: {output_path}")
            print(f"   📏 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
            print("\n📋 Open in your web browser to view the schema")
            
            print("\n" + "=" * 70)
            return output_path
            
        except Exception as e:
            print("\n❌ ERROR: Failed to generate HTML report")
            print(f"   Details: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    """Main function to generate all diagram formats"""
    print("\n🎨 Database ER Diagram Generator")
    print("Generating multiple formats for flexibility...\n")
    
    # Empty list to track generated files
    results = []
    
    # Generate Mermaid diagram (best for GitHub/VS Code)
    mermaid_file = generate_mermaid_diagram()
    if mermaid_file:
        results.append(('Mermaid', mermaid_file))
    
    # Generate PlantUML diagram
    plantuml_file = generate_plantuml_diagram()
    if plantuml_file:
        results.append(('PlantUML', plantuml_file))
    
    # Generate HTML report
    html_file = generate_html_report()
    if html_file:
        results.append(('HTML', html_file))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n✅ Generated {len(results)} format(s):\n")
    
    for format_name, file_path in results:
        print(f"   • {format_name}: {file_path}")
    
    print("\n💡 Next steps:")
    print("   1. Open the HTML file in your browser for immediate viewing")
    print("   2. View the .mmd file in VS Code with Mermaid extension")
    print("   3. Convert Mermaid/PlantUML to PDF using online tools")
    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
