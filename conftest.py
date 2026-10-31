"""Isolate import-time initialization and every test from the real database."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# app.py initializes its database during import. Redirect it BEFORE importing,
# including when pytest collects the original Lab 5 unittest module.
with tempfile.TemporaryDirectory(prefix="lab7-import-") as directory:
    with patch.dict(os.environ, {"LAB7_DATABASE": str(Path(directory) / "import.db")}):
        import app as lab


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    monkeypatch.setattr(lab, "DATABASE", tmp_path / "users.db")
    monkeypatch.setitem(lab.app.config, "TESTING", True)
    lab.create_db_table()
    return lab.DATABASE


@pytest.fixture
def client():
    with lab.app.test_client() as client:
        yield client
