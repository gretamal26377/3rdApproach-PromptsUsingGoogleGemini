import unittest
from pathlib import Path
import tempfile
import textwrap
import importlib.util
import sys


def load_converter_module():
    """Dynamically load the converter script despite hyphens in filename."""
    repo_root = Path(__file__).resolve().parents[2]  # .../3rdApproach-PromptsUsingVSCodeCopilot-
    script_path = repo_root / "pwa-marketplace" / "backend" / "scripts" / "convert_models_sqlalchemy22flask-sqlalchemy.py"
    spec = importlib.util.spec_from_file_location("converter_module", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load converter at {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ConvertModelsTransformTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = load_converter_module()

    def _convert_text(self, src_text: str) -> str:
        src_text = textwrap.dedent(src_text).lstrip("\n")
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            src = td_path / "in_models.py"
            dst = td_path / "out_models.py"
            src.write_text(src_text, encoding="utf-8")
            self.converter.convert_file(src, dst)
            out = dst.read_text(encoding="utf-8")
            return out.replace("\r\n", "\n")

    def test_mapped_nested_multiline_and_relationship(self):
        src = """
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
        from sqlalchemy import Integer, Text, DateTime

        class Base(DeclarativeBase):
            pass

        class X(Base):
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
            payload: Mapped[list[dict[str, list[int]]]] = mapped_column(Text)
            created: Mapped[DateTime] = mapped_column(DateTime(
                timezone=True
            ))
            user: Mapped['User'] = relationship(back_populates="xs")
        """
        out = self._convert_text(src)
        # Header inserted
        self.assertTrue(out.startswith("from .database import db\n"))
        # Base -> db.Model
        self.assertIn("class X(db.Model):", out)
        # id column converted with db.Integer
        self.assertIn("id = db.Column(db.Integer, primary_key=True)", out)
        # payload uses db.Text
        self.assertIn("payload = db.Column(db.Text)", out)
        # created collapsed and preserved inner args
        self.assertIn("created = db.Column(db.DateTime(timezone=True))", out)
        # relationship converted and annotation removed
        self.assertIn("user = db.relationship(back_populates=\"xs\")", out)
        self.assertNotIn("user: Mapped", out)
        # original DeclarativeBase import removed
        self.assertNotIn("DeclarativeBase", out)

    def test_type_prefix_guard(self):
        src = """
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import String
        import sqlalchemy as sqlalchemy
        import sqlalchemy as sa

        class Base(DeclarativeBase):
            pass

        class Y(Base):
            name: Mapped[str] = mapped_column(String(50))
            count: Mapped[int] = mapped_column(sa.Integer)
            title: Mapped[str] = mapped_column(sqlalchemy.String(100))
        """
        out = self._convert_text(src)
        # Bare String gets db.String
        self.assertIn("name = db.Column(db.String(50))", out)
        # sa.Integer is left as-is (no db. prefix added)
        self.assertIn("count = db.Column(sa.Integer)", out)
        # sqlalchemy.String is left as-is (no db. prefix added)
        self.assertIn("title = db.Column(sqlalchemy.String(100))", out)

    def test_fallback_raw_mapped_column_line(self):
        src = """
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
        from sqlalchemy import Boolean

        class Base(DeclarativeBase):
            pass

        class Z(Base):
            raw = mapped_column(Boolean)
        """
        out = self._convert_text(src)
        self.assertIn("raw = db.Column(db.Boolean)", out)

    def test_header_already_present_only_once(self):
        src = """
        from .database import db
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

        class Base(DeclarativeBase):
            pass

        class H(Base):
            v: Mapped[int] = mapped_column(Integer)
        """
        out = self._convert_text(src)
        # Header should not be duplicated
        self.assertEqual(out.count("from .database import db"), 1)


if __name__ == "__main__":
    unittest.main()
