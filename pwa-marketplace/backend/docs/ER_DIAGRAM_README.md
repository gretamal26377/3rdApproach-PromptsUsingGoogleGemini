# Entity-Relationship Diagram Generator

This directory contains the automatically generated Entity-Relationship (ER) diagrams for the database schema defined in `app/shared/models_sql2orm_flask_sqlalchemy.py`

## 📋 Overview

The ER diagram provides a visual representation of:
- **Entities (Tables)**: All database tables in the system
- **Attributes (Columns)**: Fields within each table with their data types
- **Relationships**: Foreign key relationships between tables
- **Primary Keys**: Unique identifiers for each entity
- **Cardinality**: One-to-many, many-to-many relationships

## 🏗️ Database Schema Summary

The database consists of the following main entity groups:

### Core Business Entities
- **Categories**: Product/service categories
- **ProductsServices**: Base products/services catalog
- **Stores**: Seller/store information
- **StoreProductsServices**: Junction table linking stores to products with pricing
- **Customers**: Customer accounts
- **Orders**: Customer orders
- **OrderDetails**: Line items within orders

### Geographic Entities
- **Countries**: Country master data
- **StatesRegions**: States/regions within countries
- **Cities**: Cities within states/regions
- **CustomerAddresses**: Customer delivery addresses

### User Management
- **Users**: Store/admin user accounts
- **Roles**: User role definitions
- **StoreUserRole**: Junction table for user-store-role assignments

### Status Management
- **EntityStatuses**: General status codes for various entities
- **OrderStatuses**: Specific statuses for orders

### Audit/History Tables
All main entities have corresponding history tables (e.g., `categories_history`, `customers_history`) that track:
- INSERT, UPDATE, DELETE operations
- Timestamp of changes
- User who made the change
- Before/after data snapshots

## 🚀 Generating the ER Diagram

### Prerequisites

#### 1. Install Graphviz (System Dependency)

**Windows:**
```powershell
# Using Chocolatey
choco install graphviz

# Or download installer from:
# https://graphviz.org/download/
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install graphviz libgraphviz-dev
```

**macOS:**
```bash
brew install graphviz
```

Verify installation:
```powershell
dot -V
```

#### 2. Install Python Dependencies

```powershell
# From the backend directory
pip install eralchemy2 pygraphviz
```

Or install all requirements:
```powershell
pip install -r requirements.txt
```

### Running the Generator

From the `backend/` directory:

```powershell
python -m scripts.generate_er_diagram
```

The script will:
1. Load the database models from `app/shared/models_sql2orm_flask_sqlalchemy.py`
2. Generate an ER diagram in PDF format
3. Save it to `backend/docs/` with a timestamp in the filename

### Output

The generated PDF will be named:
```
er_diagram_YYYYMMDD_HHMMSS.pdf
```

Example: `er_diagram_20241029_143022.pdf`

## 📊 Understanding the Diagram

### Notation

- **Rectangles**: Represent entities (tables)
- **Ovals/Text inside rectangles**: Represent attributes (columns)
- **Lines with arrows**: Represent relationships (foreign keys)
- **PK**: Primary Key
- **FK**: Foreign Key
- **Bold text**: Primary key columns
- **Italic text**: Foreign key columns (in some notations)

### Relationship Cardinality

- **1 → N**: One-to-many relationship
- **N → M**: Many-to-many relationship (through junction tables)

### Key Relationships

1. **Store-Product Relationship**:
   - `Stores` ← `StoreProductsServices` → `ProductsServices`
   - A store can sell many products, and a product can be sold by many stores

2. **Order Management**:
   - `Customers` → `Orders` → `OrderDetails` → `StoreProductsServices`
   - Orders are linked to specific store product listings

3. **Geographic Hierarchy**:
   - `Countries` → `StatesRegions` → `Cities` → `CustomerAddresses`

4. **User-Store-Role Association**:
   - `Users` ← `StoreUserRole` → `Stores`
   - `StoreUserRole` → `Roles`

5. **Status Management**:
   - `EntityStatuses` is referenced by most entities
   - `OrderStatuses` is specific to order-related entities

## 🔧 Troubleshooting

### Error: "graphviz not found"
- Ensure Graphviz is installed and in your system PATH
- Restart your terminal/IDE after installation
- Verify with: `dot -V`

### Error: "No module named 'eralchemy2'"
```powershell
pip install eralchemy2
```

### Error: "pygraphviz installation failed"
On Windows, you might need to:
1. Install Visual C++ Build Tools
2. Set GRAPHVIZ_DIR environment variable
3. Or use pre-built wheels: `pip install --only-binary :all: pygraphviz`

### Database Connection Issues
If using the database URI method fails:
- The script automatically falls back to metadata mode
- Metadata mode generates the diagram without a live database connection
- It uses SQLAlchemy's metadata information from the model definitions

## 📝 Updating the Diagram

Regenerate the ER diagram whenever:
- New tables are added to the database
- Table schemas are modified
- Relationships change
- You need an updated visual reference

## 🎨 Customization

To customize the diagram appearance, you can modify the script:

```python
# In generate_er_diagram.py, you can add custom rendering options:
render_er(db_uri, output_path, mode='er')
```

Available modes:
- `'er'`: Entity-Relationship diagram (default, shows relationships clearly)
- `'graph'`: Graph representation (more compact)

## 📚 Related Documentation

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [ERAlchemy2 Documentation](https://github.com/maurerle/eralchemy2)
- [Graphviz Documentation](https://graphviz.org/documentation/)

## 🤝 Contributing

When making database schema changes:
1. Update the models in `app/shared/models_sql2orm_flask_sqlalchemy.py`
2. Run database migrations
3. Regenerate the ER diagram
4. Commit both the model changes and the new ER diagram

## 📄 License

This documentation and the generated diagrams are part of the project and follow the same license
