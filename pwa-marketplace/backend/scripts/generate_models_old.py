"""
Generate static Flask-SQLAlchemy models.py from an existing database schema
using SQLAlchemy reflection.
It might be built using sqlacodegen package, but AI suggested this approach

This script lives inside backend/scripts so it has easy access to backend config
and paths. Default output is `app/shared/models.py` relative to the backend
package directory.

Usage (from repository root):
  python pwa-marketplace/backend/scripts/generate_models.py --out=app/shared/models.py

Or run from backend/:
  python scripts/generate_models.py --out=app/shared/models.py

If --url argument is not provided the script will try to load the project's Config
file at backend/app/shared/config.py through importlib import mechanism and use its 
SQLALCHEMY_DATABASE_URI

IMPORTANT: This script will overwrite the target file. Review the generated
output before committing.
"""

import os
import argparse
import importlib.util
from sqlalchemy import create_engine, MetaData

TYPE_MAP = {
    'INTEGER': 'db.Integer',
    'SMALLINT': 'db.SmallInteger',
    'BIGINT': 'db.BigInteger',
    'NUMERIC': 'db.Numeric',
    'DECIMAL': 'db.Numeric',
    'FLOAT': 'db.Float',
    'REAL': 'db.Float',
    'VARCHAR': 'db.String',
    'CHAR': 'db.String',
    'TEXT': 'db.Text',
    'BOOLEAN': 'db.Boolean',
    'DATE': 'db.Date',
    'DATETIME': 'db.DateTime',
    'TIMESTAMP': 'db.DateTime',
    'TIME': 'db.Time',
}

# Convert SQLAlchemy column type to string representation for db.Column
def coltype_to_string(col_type):
    try:
        clsname = col_type.__class__.__name__.upper()
    except Exception:
        clsname = str(col_type).upper()

    if hasattr(col_type, 'length') and getattr(col_type, 'length'):
        return f"db.String({col_type.length})"

    for key in TYPE_MAP:
        if key in clsname:
            return TYPE_MAP[key]

    return 'db.String'

# Convert snake_case to CamelCase
def snake_to_camel(name: str) -> str:
    parts = name.split('_')
    return ''.join(p.capitalize() for p in parts)

# Render a single column
def render_column(col):
    name = col.name
    typ = coltype_to_string(col.type)
    flags = []

    if col.primary_key:
        flags.append('primary_key=True')
    if not col.nullable:
        flags.append('nullable=False')
    if getattr(col, 'unique', False):
        flags.append('unique=True')
    if col.foreign_keys:
        fk = list(col.foreign_keys)[0]
        flags.append(f"db.ForeignKey('{fk.target_fullname}')")

    if flags:
        return f"    {name} = db.Column({typ}, {', '.join(flags)})"
    else:
        return f"    {name} = db.Column({typ})"


def generate_models(engine, out_path):
    # Reflect the database schema   
    meta = MetaData()
    meta.reflect(bind=engine)

    # Generate model classes for each table
    lines = []
    lines.append('from .database import db')
    lines.append('')
    lines.append('# Auto-generated models file — review before committing')
    lines.append('')

    # meta.tables.items(): Returns a dictionary of table names and Table objects
    for table_name, table in meta.tables.items():
        cls_name = snake_to_camel(table_name)
        lines.append(f"class {cls_name}(db.Model):")
        lines.append(f"    __tablename__ = '{table_name}'")
        lines.append('')

        for col in table.columns:
            col_line = render_column(col)
            lines.append(col_line)
        lines.append('')

        # Generate a safe __repr__ that includes all primary key columns (or first column if no PK)
        pk_cols = [c.name for c in table.primary_key.columns] if table.primary_key.columns else [list(table.columns)[0].name]
        lines.append('    def __repr__(self):')
        if len(pk_cols) == 1:
            # produce: return f'<Class {self.pk}>'
            lines.append(f"        return f'<{cls_name} {{{{self.{pk_cols[0]}}}}}>'")
        else:
            # produce: return f'<Class {self.a}, {self.b}>' where a/b are self.attr refs
            inner = ', '.join([f"{c}={{{{self.{c}}}}}" for c in pk_cols])
            lines.append(f"        return f'<{cls_name} {inner}>'")
        lines.append('')
        lines.append('')

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f'Wrote {out_path} with {len(meta.tables)} tables')


def main():
    parser = argparse.ArgumentParser(description='Generate Flask-SQLAlchemy models from DB')
    parser.add_argument('--url', help='Database URL (overrides project config)')
    parser.add_argument('--out', default=os.path.join('app', 'shared', 'models_sql2orm_flask-sqlalchemy.py'), help='Output models.py path relative to backend dir')
    parser.add_argument('--force', action='store_true', help='Overwrite without prompt')
    # parse_args: Parses the command-line arguments
    args = parser.parse_args()

    db_url = args.url
    if not db_url:
        # try to load backend/app/shared/config.py relative to this script
        try:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            config_path = os.path.join(base, 'app', 'shared', 'config.py')
            spec = importlib.util.spec_from_file_location('projconf', config_path)
            conf = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(conf)
            db_url = getattr(conf.Config, 'SQLALCHEMY_DATABASE_URI', None)
        except Exception as e:
            print('Could not load backend config:', e)
            db_url = None

    if not db_url:
        print('ERROR: No database URL provided and could not load backend/app/shared/config.py')
        return

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', args.out))
    if os.path.exists(out_path) and not args.force:
        reply = input(f"Output file {out_path} exists. Overwrite? [y/N]: ")
        if reply.lower() != 'y':
            print('Aborted')
            return
    # Create SQLAlchemy engine that will be used to reflect the database schema
    engine = create_engine(db_url)
    generate_models(engine, out_path)


if __name__ == '__main__':
    main()
