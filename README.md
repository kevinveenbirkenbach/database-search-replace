# pg_bulk_find_replace

Bulk **search** (and optional **replace**) of strings across all text/varchar columns in a PostgreSQL database.
- Runs either **natively** on the host (using `psql`) or **inside a container** via `docker exec` when `--container` is provided.
- The SQL logic is rendered from a single **Jinja2** template (`templates/query.sql.j2`) so you can easily modify the behavior.
- Safe-by-default: uses server-side loops; `REPLACE()` is only executed when `--replace` is given.

## Quick start

```bash
# 1) Install deps (Jinja2 only)
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 2) Search only (no changes), local psql:
python main.py -d mydb -p mysecret -s "old.example"

# 3) Replace (search + replace), local psql:
python main.py -d mydb -p mysecret -s "old.example" -r "new.example"

# 4) Search inside container "postgres_db":
python main.py -d mydb -p mysecret -s "old.example" -c postgres_db

# 5) Replace inside container:
python main.py -d mydb -p mysecret -s "old.example" -r "new.example" -c postgres_db
```

## Arguments

```
  -h, --help                Show help
  -d, --database TEXT       (required) Database name
  -U, --user TEXT           Database user (default: postgres)
  -p, --password TEXT       (required) Database password (exported as PGPASSWORD)
  -H, --host TEXT           Host (default: localhost)
  -P, --port INT            Port (default: 5432)
  -s, --search TEXT         (required) Search term
  -r, --replace TEXT        Replacement term; if provided → **replace mode**
  -c, --container TEXT      Docker container name to execute `psql` in
  --psql-path TEXT          Path to psql binary (default: psql)
```

## What it does

- **Search mode (no `--replace`)**: Lists occurrences of the search text, returning rows with schema, table, column, row identifier and the matched value.
- **Replace mode (`--replace` given)**: Performs in-place updates with `REPLACE(column, search, replace)` on all matching text/varchar columns, and prints a summary of modified rows per table/column.

> Tip: Always take a backup before running replace mode in production.
