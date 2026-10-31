"""Lab 7 - Majd Aboul Hosn. Real SQLite and Flask tests, with no mocked CRUD."""
import os
import sqlite3
import subprocess
import sys
from contextlib import closing
from pathlib import Path

import pytest

import app as lab


@pytest.fixture
def user_data():
    return dict(name="Majd Aboul Hosn", email="majd@example.com",
                phone="+96170000000", address="Beirut", country="Lebanon")


@pytest.fixture
def stored_user(user_data):
    return lab.insert_user(user_data)


def read_rows():
    """Read committed data independently of the application's get functions."""
    with closing(sqlite3.connect(lab.DATABASE)) as conn:
        conn.row_factory = sqlite3.Row
        return [dict(row) for row in conn.execute("SELECT * FROM users ORDER BY user_id")]


def test_database_initialization_on_first_run(tmp_path):
    # The supplied Lab 5 has no seed users. Do not invent instructor records.
    database = tmp_path / "first-run.db"
    assert not database.exists()
    env = dict(os.environ, LAB7_DATABASE=str(database), PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, "-c", "import app"],
                            cwd=Path(lab.__file__).parent, env=env,
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert database.is_file()
    with closing(sqlite3.connect(database)) as conn:
        columns = conn.execute("PRAGMA table_info(users)").fetchall()
        assert [(c[1], c[2], c[3], c[5]) for c in columns] == [
            ("user_id", "INTEGER", 1, 1), ("name", "TEXT", 1, 0),
            ("email", "TEXT", 1, 0), ("phone", "TEXT", 1, 0),
            ("address", "TEXT", 1, 0), ("country", "TEXT", 1, 0)]
        assert conn.execute("SELECT * FROM users").fetchall() == []


def test_insert_user(user_data):
    result = lab.insert_user(user_data)
    assert type(result["user_id"]) is int and result["user_id"] > 0
    assert result == dict(user_data, user_id=result["user_id"])
    assert read_rows() == [result]


def test_get_users(user_data):
    assert lab.get_users() == []
    first = lab.insert_user(user_data)
    second = lab.insert_user(dict(user_data, name="Second User", email="second@example.com"))
    assert first["user_id"] != second["user_id"]
    assert lab.get_users() == [first, second] == read_rows()


def test_get_user_by_id(stored_user, user_data):
    other = lab.insert_user(dict(user_data, name="Other User"))
    assert lab.get_user_by_id(stored_user["user_id"]) == stored_user
    assert lab.get_user_by_id(other["user_id"]) == other


def test_update_user(stored_user, user_data):
    other = lab.insert_user(dict(user_data, name="Unchanged User"))
    updated = dict(stored_user, name="Updated Name", email="updated@example.com",
                   phone="+33123456789", address="Paris", country="France")
    assert lab.update_user(updated) == updated
    assert read_rows() == [updated, other]


def test_delete_user(stored_user, user_data):
    other = lab.insert_user(dict(user_data, name="Keep Me"))
    assert lab.delete_user(stored_user["user_id"]) == {"status": "User deleted successfully"}
    assert lab.get_user_by_id(stored_user["user_id"]) == {}
    assert read_rows() == [other]


def test_api_get_user(client, stored_user):
    response = client.get(f"/api/users/{stored_user['user_id']}")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == stored_user


def test_api_add_user(client, user_data):
    response = client.post("/api/users/add", json=user_data)
    assert response.status_code == 200  # Original Lab 5 contract (not 201).
    assert response.is_json
    created = response.get_json()
    assert type(created["user_id"]) is int and created["user_id"] > 0
    assert created == dict(user_data, user_id=created["user_id"])
    assert read_rows() == [created]


def test_api_update_user(client, stored_user, user_data):
    other = lab.insert_user(dict(user_data, name="Keep Me"))
    payload = dict(stored_user, name="New Name", email="new@example.com",
                   phone="+44123456789", address="London", country="UK")
    response = client.put("/api/users/update", json=payload)
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == payload
    assert read_rows() == [payload, other]


def test_api_delete_user(client, stored_user, user_data):
    other = lab.insert_user(dict(user_data, name="Keep Me"))
    response = client.delete(f"/api/users/delete/{stored_user['user_id']}")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == {"status": "User deleted successfully"}
    assert read_rows() == [other]
    missing = client.get(f"/api/users/{stored_user['user_id']}")
    assert missing.status_code == 404
    assert missing.get_json() == {"error": "User not found"}


def test_initialization_preserves_existing_users(stored_user):
    lab.create_db_table()
    lab.create_db_table()
    assert read_rows() == [stored_user]


def test_missing_database_users(user_data, stored_user):
    assert lab.get_user_by_id(999) == {}
    assert lab.update_user(dict(user_data, user_id=999)) == {}
    assert lab.delete_user(999) == {}
    assert read_rows() == [stored_user]


def test_insert_missing_field_does_not_write_partial_record(user_data, stored_user):
    del user_data["email"]
    with pytest.raises(KeyError, match="email"):
        lab.insert_user(user_data)
    assert read_rows() == [stored_user]


def test_api_get_users(client, stored_user):
    response = client.get("/api/users")
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json() == [stored_user]


@pytest.mark.parametrize("method,path", [
    ("get", "/api/users/999"), ("put", "/api/users/update"),
    ("delete", "/api/users/delete/999")])
def test_api_missing_user(client, user_data, stored_user, method, path):
    kwargs = {"json": dict(user_data, user_id=999)} if method == "put" else {}
    response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 404
    assert response.get_json() == {"error": "User not found"}
    assert read_rows() == [stored_user]


@pytest.mark.parametrize("method,path", [
    ("post", "/api/users/add"), ("put", "/api/users/update")])
@pytest.mark.parametrize("field", ["name", "email", "phone", "address", "country"])
def test_api_rejects_missing_field(client, stored_user, method, path, field):
    payload = dict(stored_user)
    del payload[field]
    response = getattr(client, method)(path, json=payload)
    assert response.status_code == 400
    assert response.get_json() == {"error": f"{field} must be a nonempty string"}
    assert read_rows() == [stored_user]


@pytest.mark.parametrize("method,path", [
    ("get", "/api/users/0"), ("delete", "/api/users/delete/abc")])
def test_api_rejects_invalid_id(client, stored_user, method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid user_id"}
    assert read_rows() == [stored_user]
