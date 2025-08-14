# pgsr — PostgreSQL Search & Replace 🔎✏️

Bulk **search** (and optional **replace**) of strings across all `text` / `varchar` columns in a PostgreSQL database.

- Runs either **natively** on the host (using `psql`) or **inside a container** via `docker exec` when `--container` is provided.
- The SQL logic is rendered from a single **Jinja2** template (`templates/query.sql.j2`) so you can easily tweak behavior.
- Safe-by-default: in **search** mode it only lists matches; in **replace** mode it updates values using `REPLACE(...)`.

---

## 🚀 Install via Kevin’s Package Manager

If you use **Kevin’s Package Manager**  
👉 <https://github.com/kevinveenbirkenbach/package-manager>

Install **pgsr** with:

```bash
pkgmgr install pgsr
````

After installation, see all commands and options:

```bash
pgsr --help
```

---

## 🧪 Quick start

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

---

## 🧰 Arguments

```
  -h, --help                Show help
  -d, --database TEXT       (required) Database name
  -U, --user TEXT           Database user (default: postgres)
  -p, --password TEXT       (required) Database password (exported as PGPASSWORD)
  -H, --host TEXT           Host (default: localhost)
  -P, --port INT            Port (default: 5432)
  -s, --search TEXT         (required) Search term
  -r, --replace TEXT        Replacement term; if provided → replace mode
  -c, --container TEXT      Docker container name to execute `psql` in
  --psql-path TEXT          Path to psql binary (default: psql)
```

---

## 📄 License

Released under the **MIT License**. See [LICENSE](./LICENSE).

**Author:** [Kevin Veen-Birkenbach](https://www.veen.world)
**Generated with:** ChatGPT — see *[this conversation](https://chatgpt.com/share/689dba44-2e18-800f-bcd2-158002faf8da)*
