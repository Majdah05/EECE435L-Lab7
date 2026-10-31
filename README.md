# Lab 7 - Python testing

Majd Aboul Hosn | AUB Software Tools Lab | Fall 2026-2027

This project retains the supplied Lab 5 Flask/SQLite application and its eight
regression tests. The required `test_user_Majd_Aboul_Hosn.py` adds 29 pytest cases
(including parameterized cases), for **37 tests total**.

## Install and test (Windows PowerShell, Python 3.11+)

Extract the ZIP, open `Lab7-Majd-Aboul_Hosn` in VS Code, and open its terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
```

To use the exact lab command without activating a PowerShell script:

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
python -m pytest -v
```

SQLite is included with Python; no separate SQLite package is needed.

## Run the application

```powershell
.\.venv\Scripts\python.exe app.py
```

Open `http://localhost:5000/api/users`. Stop the server with Ctrl+C.
Normal startup creates `database.db` beside `app.py`. Existing records are kept.
The supplied Lab 5 has no seed users, the Lab 7 PDF names no initial records,
and the student confirmed none were specified. Thus the correct first-run user
list is `[]`; the initialization test verifies this and every schema column.
Sample users in tests are test data, not invented startup defaults.

## Graded requirements

| # | Functionality | Test in test_user_Majd_Aboul_Hosn.py |
| --- | --- | --- |
| 1 | First startup creates database, exact schema, empty initial user list | `test_database_initialization_on_first_run` |
| 2 | Insert persists all five fields and a generated ID | `test_insert_user` |
| 3 | Retrieve all users, including empty and multiple records | `test_get_users` |
| 4 | Retrieve correct user by ID | `test_get_user_by_id` |
| 5 | Update every field, preserve another user | `test_update_user` |
| 6 | Delete selected user, preserve another user | `test_delete_user` |
| 7 | GET `/api/users/<id>`: HTTP 200 and exact JSON | `test_api_get_user` |
| 8 | POST `/api/users/add`: JSON body, HTTP 200, exact returned and stored data | `test_api_add_user` |
| 9 | PUT `/api/users/update`: JSON body, HTTP 200, exact returned and stored data | `test_api_update_user` |
| 10 | DELETE `/api/users/delete/<id>`: HTTP 200, exact JSON message, removal and subsequent 404 | `test_api_delete_user` |

The actual Lab 5 function is named `get_user_by_id`, corresponding to the
handout's `Get_users_by_id`. Successful POST returns 200 in the original app.
Tests preserve that contract. Extra tests check repeat initialization, missing
users/fields, invalid IDs, malformed JSON, content types, SQL parameterization,
CORS, and the list endpoint. Failed writes must leave existing records intact.

## Isolation and changes to Lab 5

The only functional application change is an optional `LAB7_DATABASE`
environment variable for the SQLite path; the default location is unchanged.
Line endings were normalized. CRUD, routes, response bodies, validation and
HTTP status codes were retained.

`conftest.py` redirects the import-time database to a temporary directory before
loading the app. An automatic pytest fixture then uses a new temporary database
for each test and enables Flask testing mode. No CRUD function is mocked.
Successful writes are checked independently using SQLite queries. The startup
test runs a fresh Python process against a nonexistent temporary database.
The original regression tests retain their own temporary-database setup.

The original `Lab5-Postman.zip` remains unchanged outside this submission.
Postman exports and the original live HTTP capture helper are retained as
supporting source. They are not needed for pytest. The helper can be run using
`python tests/capture_examples.py` with port 5000 free; it regenerates the
Postman examples and creates `tests/http_results.json`.

## Screenshot and Moodle upload

Run `python -m pytest -v` as above. Once the terminal reports **37 passed**:

**SCREENSHOT NOW - Capture your terminal showing the successful Pytest results.**

Show the project folder/name, command, test results marked PASSED and the final
37-passed summary. Enlarge the terminal or reduce its font size if necessary.
The screenshot must be from your actual execution, not an edited result image.
Save it beside the ZIP as `Lab7-Majd-Aboul_Hosn-pytest.png`.

Updated submission instruction: upload `github-link.txt` to Moodle containing:

```text
https://github.com/Majdah05/EECE435L-Lab7
```

The repository contains the source files and the genuine pytest screenshot.
The original PDF also requests a ZIP and screenshot; those remain available
locally if Moodle asks for them separately.

Do not include virtual environments, caches, Git history or runtime databases
when rebuilding the submission ZIP.
