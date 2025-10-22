# ...existing code...
def convert_file(src: Path, dst: Path) -> None:
    text = src.read_text(encoding='utf-8')

    # remove the DeclarativeBase import line
    # \s+: represents one or more whitespace characters (spaces, tabs, newlines)
    # re.sub(pattern, replacement, string) replaces occurrences of pattern in string with replacement
    text = re.sub(r"from\s+sqlalchemy\.orm\s+import\s+DeclarativeBase,?\s*Mapped,?\s*mapped_column,?\s*relationship\s*\n", '', text)
    # remove explicit DeclarativeBase class if present
    text = re.sub(r"class\s+Base\s*\(DeclarativeBase\):\s*\n\s*pass\s*\n\n", '', text)
    # remove "from typing import List, Optional" if present
    text = re.sub(r"from\s+typing\s+import\s+List,?\s*Optional\s*\n", '', text)


    # add Flask-SQLAlchemy db import
    header = "from .database import db\n"
    text = header + text

    # This is best-effort: prefix common SQLAlchemy type names with db. when they appear as standalone identifiers
    # Text and text are different: Text is a type, text() is a function used to inyect literal SQL text
    # DECIMAL and Numeric are practically the same, they have different origins (DECIMAL from SQL standard, Numeric from Python)
    types = ['Integer','BigInteger','String','Text','JSON','DECIMAL','Date','DateTime','TIMESTAMP','Float','Numeric','Boolean']
    
    # Refactored to avoid altering import statements.
    # It works by splitting the text into lines and processing each line individually,
    # skipping any lines that start with 'from' or 'import'.
    processed_lines = []
    for line in text.splitlines():
        if line.strip().startswith(('from', 'import')):
            processed_lines.append(line)
            continue

        for t in types:
            # Only match the bare identifier when it's NOT already prefixed with db., sa., or sqlalchemy.
            # A simple negative lookbehind for a dot is enough here since we are already inside a non-import line.
            type_pattern = rf"(?<!\.)\b{t}\b"
            line = re.sub(type_pattern, f"db.{t}", line)
        processed_lines.append(line)
    text = "\n".join(processed_lines)

    # Replace mapped_column markers if any left
    text = text.replace('mapped_column', 'db.Column')

    dst.write_text(text, encoding='utf-8')
