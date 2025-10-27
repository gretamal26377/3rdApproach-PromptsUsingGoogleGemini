"""
Generate Flask-SQLAlchemy models.py using SQLAlchemy reflection / automap as source of truth.
This script reflects the database schema and writes a static, reviewable Flask-SQLAlchemy
`db.Model` file suitable for use in this project.

Usage (from backend/):
  python scripts/generate_models_automap.py --out=app/shared/models_sql2orm_flask_sqlalchemy.py
  python scripts/generate_models_automap.py --url "mysql+pymysql://user:pass@db:3306/marketplace_db"

If --url is not provided the script will attempt to load backend/app/shared/config.py using
importlib and read Config.SQLALCHEMY_DATABASE_URI.

Important: review the generated file before committing. The script makes a best-effort mapping
from SQL types to Flask-SQLAlchemy types and renders foreign keys, primary keys, unique and
nullable flags. Adjust manually if you need custom relationships/back_populates/uselist flags.
"""

from __future__ import annotations
import os
import argparse
import importlib.util
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Enum

# Type mapping (best-effort)
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
    'JSON': 'db.JSON',
}


def coltype_to_string(col_type) -> str:
    """Return a string like 'db.String(100)' or 'db.Integer' for a Column type object"""
    try:
        # Get the class name of the column type in uppercase for comparison. eg: 'VARCHAR', 'INTEGER', etc.
        clsname = col_type.__class__.__name__.upper()
    except Exception:
        # str(): Get the string representation of an object
        clsname = str(col_type).upper()

    # length-aware types
    if hasattr(col_type, 'length') and getattr(col_type, 'length'):
        return f"db.String({col_type.length})"

    for key in TYPE_MAP:
        if key in clsname:
            return TYPE_MAP[key]
    # 'db.String' is fallback, and is valid for SQLAlchemy, representing a variable-length string
    return 'db.String'


def snake_to_camel(name: str) -> str:
    parts = name.split('_')
    return ''.join(p.capitalize() for p in parts)

def render_column(col) -> str:
    """Render a column line for a Flask-SQLAlchemy model class"""
    name = col.name
    typ = coltype_to_string(col.type)
    
    # Enhanced enum detection
    if isinstance(col.type, Enum) and hasattr(col.type, 'enums') and getattr(col.type, 'enums'):
        # Render as db.Enum with values. ',' is the separator and goes before join to avoid trailing comma
        # repr(): Get the string representation of an object
        enum_vals = ', '.join(repr(e) for e in col.type.enums)
        typ = f"db.Enum({enum_vals})"
    
    # Build positional args first (type, foreign keys)
    args = [typ]
    if col.foreign_keys:
        fk = list(col.foreign_keys)[0]
        args.append(f"db.ForeignKey('{fk.target_fullname}')")
    
    # Then keyword args
    kwargs = []
    if col.primary_key:
        kwargs.append('primary_key=True')
    if not col.nullable and not col.primary_key:
        kwargs.append('nullable=False')
    if getattr(col, 'unique', False):
        kwargs.append('unique=True')
    
    # Combine: positional first, then keywords
    all_args = args + kwargs
    return f"    {name} = db.Column({', '.join(all_args)})"

def generate_models_from_metadata(meta: MetaData, out_path: str) -> int:
    lines = []
    lines.append('from .database import db')
    lines.append('from sqlalchemy import Index, ForeignKeyConstraint, text')
    lines.append('')
    lines.append('# Auto-generated models file — review before committing')
    lines.append('')

    # Precompute FK maps so we can emit back_populates on both sides
    fk_map = {}  # child_table -> list of (local_col_name, referred_table)
    parent_map = {}  # parent_table -> list of (child_table, local_col_name)

    # meta.tables.items(): Corresponds to a dictionary where keys are table names and values are Table objects
    # containing the tables schema information, such as fields, constraints, indexes, etc
    for table_name, table in meta.tables.items():
        for col in table.columns:
            for fk in col.foreign_keys:
                parent = fk.column.table.name
                fk_map.setdefault(table_name, []).append((col.name, parent))
                parent_map.setdefault(parent, []).append((table_name, col.name))

    for table_name, table in meta.tables.items():
        cls_name = snake_to_camel(table_name)
        lines.append(f'class {cls_name}(db.Model):')
        lines.append(f"    __tablename__ = '{table_name}'")

        # render table indexes
        targs = []
        if table.indexes:
            for ix in table.indexes:
                cols = ', '.join([f"'{c.name}'" for c in ix.columns])
                unique = ', unique=True' if ix.unique else ''
                targs.append(f"Index('{ix.name}', {cols}{unique})")

        # [...]: This is a List Comprehension. It iterates over each constraint c in table.constraints
        # fkcs: A list of ForeignKeyConstraint objects in the table's constraints
        fkcs = [c for c in table.constraints if c.__class__.__name__ == 'ForeignKeyConstraint']
        for fk in fkcs:
            # use .elements rather than .columns to avoid typing issues
            cols = ', '.join([f"'{elem.parent.name}'" for elem in fk.elements]) # type: ignore
            refs = ', '.join([f"'{elem.column.table.name}.{elem.column.name}'" for elem in fk.elements]) # type: ignore
            targs.append(f"ForeignKeyConstraint([{cols}], [{refs}])")

        # Render __table_args__ if we have any
        if targs:
            lines.append('    __table_args__ = (')
            for t in targs:
                lines.append('        ' + t + ',')
            lines.append('    )')

        lines.append('')

        # table.columns: An iterable collection of Column objects representing the columns/fields in the table
        for col in table.columns:
            lines.append(render_column(col))

        lines.append('')

        # Relationships: child side (this table has FKs to parents)
        for local_col, parent in fk_map.get(table_name, []):
            parent_class = snake_to_camel(parent)
            # derive attribute name on child from column name (drop trailing _id)
            if local_col.endswith('_id'):
                child_attr = local_col[:-3]
            else:
                child_attr = local_col
            # parent side collection name (use child table name, plural-ish)
            parent_collection = table_name if table_name.endswith('s') else table_name + 's'
            lines.append(f"    {child_attr} = db.relationship('{parent_class}', back_populates='{parent_collection}')")

        # Relationships: parent side (collections of children)
        for child_table, child_col in parent_map.get(table_name, []):
            child_class = snake_to_camel(child_table)
            # collection attribute name: use child_table plural (keep as-is)
            collection_attr = child_table if child_table.endswith('s') else child_table + 's'
            # derive child's attribute name used via back_populates
            if child_col.endswith('_id'):
                child_attr = child_col[:-3]
            else:
                child_attr = child_col
            lines.append(f"    {collection_attr} = db.relationship('{child_class}', back_populates='{child_attr}')")

        """ Mostly used for debugging purposes; leaving commented out for now
        # safe __repr__ using primary keys
        pk_cols = [c.name for c in table.primary_key.columns] if table.primary_key.columns else [list(table.columns)[0].name]
        lines.append('    def __repr__(self):')
        if len(pk_cols) == 1:
            lines.append(f"        return f'<{cls_name} {{{{self.{pk_cols[0]}}}}}>'")
        else:
            inner = ', '.join([f"{c}={{{{self.{c}}}}}" for c in pk_cols])
            lines.append(f"        return f'<{cls_name} {inner}>'")
        """

        lines.append('')
        lines.append('')

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text('\n'.join(lines), encoding='utf-8')
    return len(meta.tables)


def load_config_db_url() -> str | None:
    # Attempt to load backend/app/shared/config.py like other scripts in this repo do
    try:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(base, 'app', 'shared', 'config.py')
        spec = importlib.util.spec_from_file_location('projconf', config_path)
        conf = importlib.util.module_from_spec(spec) # type: ignore  # try-except handles None case
        spec.loader.exec_module(conf) # type: ignore
        return getattr(conf.Config, 'SQLALCHEMY_DATABASE_URI', None)
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Flask-SQLAlchemy models from DB schema (reflection/automap approach)')
    parser.add_argument('--url', help='Database URL (overrides project config)')
    parser.add_argument('--out', default=os.path.join('app', 'shared', 'models_sql2orm_flask_sqlalchemy.py'), help='Output models_sql2orm_flask_sqlalchemy.py path relative to backend dir')
    parser.add_argument('--force', action='store_true', help='Overwrite without prompt')
    args = parser.parse_args()

    db_url = args.url or load_config_db_url()
    if not db_url:
        print('ERROR: No database URL provided and could not load backend/app/shared/config.py')
        return

    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', args.out))
    if os.path.exists(out_path) and not args.force:
        reply = input(f"Output file {out_path} exists. Overwrite? [y/N]: ")
        if reply.lower() != 'y':
            print('Aborted')
            return

    engine = create_engine(db_url)

    meta = MetaData()
    meta.reflect(bind=engine)

    n = generate_models_from_metadata(meta, out_path)
    print(f'Wrote {out_path} with {n} tables')


if __name__ == '__main__':
    main()
