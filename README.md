# Database Search & Replace (dbsr) 🔎✏️

Bulk **search** (and optional **replace**) of strings across all `text`/`varchar` columns in your databases.

- Supports **PostgreSQL** and **MariaDB**.
- Runs **natively** on the host or **inside a container** via `docker exec` when `--container` is provided.
- Logic is rendered from **Jinja2 templates** so you can tweak behavior easily:
  - PostgreSQL: `templates/query/postgres.sql.j2`
  - MariaDB: `templates/query/mariadb.sql.j2`
- Safe-by-default: in **search** mode it only lists matches; in **replace** mode it updates values using `REPLACE(...)`.
- PostgreSQL replace mode handles FKs **without superuser** by temporarily making non-deferrable FKs deferrable within the session, deferring checks, then restoring original definitions.  
  MariaDB replace mode uses session-scoped `foreign_key_checks=0` (restored afterwards).

---

## 🚀 Install via Kevin’s Package Manager

If you use **Kevin’s Package Manager**  
👉 <https://github.com/kevinveenbirkenbach/package-manager>

Install **dbsr** with:

```bash
pkgmgr install dbsr
````

After installation, see all commands and options:

```bash
dbsr --help
```

---

## 🧪 Quick start

### PostgreSQL

```bash
# Search only (no changes) – local
dbsr --type postgres -d mydb -p 'secret' -s "old.example"

# Replace (search + replace) – local
dbsr --type postgres -d mydb -p 'secret' -s "old.example" -r "new.example"

# Search inside container "postgres_db"
dbsr --type postgres -d mydb -p 'secret' -s "old.example" -c postgres_db

# Replace inside container
dbsr --type postgres -d mydb -p 'secret' -s ":old" -r ":new" -c postgres_db
```

### MariaDB

```bash
# Search only (no changes) – local (defaults to port 3306 for MariaDB)
dbsr --type mariadb -d mydb -U root -p 'secret' -s "old.example"

# Replace – local
dbsr --type mariadb -d mydb -U root -p 'secret' -s "old.example" -r "new.example"

# Inside container "mariadb"
dbsr --type mariadb -d mydb -U root -p 'secret' -s ":old" -r ":new" -c mariadb
```

---

## 🧰 Arguments

```
  -h, --help                Show help
  -t, --type TEXT           Database type: postgres | mariadb (default: postgres)
  -d, --database TEXT       (required) Database name
  -U, --user TEXT           Database user (default: postgres)
  -p, --password TEXT       (required) Database password
  -H, --host TEXT           Host (default: localhost)
  -P, --port INT            Port (default: 5432; for --type mariadb, auto-switches to 3306 if left at 5432)
  -s, --search TEXT         (required) Search term
  -r, --replace TEXT        Replacement term; if provided → replace mode
  -c, --container TEXT      Docker container name to execute client in
      --psql-path TEXT      Path to psql (PostgreSQL; default: psql)
      --mysql-path TEXT     Path to mysql (MariaDB/MySQL; default: mysql)
```

---

## 🧠 How it works (high level)

* **PostgreSQL**

  * Search: loops server-side over user tables/columns, collects matches into a temp table, then prints.
  * Replace: temporarily rebuilds **non-deferrable** foreign keys as **DEFERRABLE INITIALLY DEFERRED**, runs all updates with `SET CONSTRAINTS ALL DEFERRED`, then **restores** the original FK definitions. No superuser required (table ownership needed to alter FKs).

* **MariaDB**

  * Search: iterates over text-like columns via `INFORMATION_SCHEMA.COLUMNS`, collects matches.
  * Replace: sets `foreign_key_checks=0` **for the session**, performs updates, and restores the original setting.

> ⚠️ Always take a backup or run in a staging environment before using **replace** mode in production.

---

## 🧩 Templates

* PostgreSQL: `templates/query/postgres.sql.j2`
* MariaDB: `templates/query/mariadb.sql.j2`

Tweak these to adapt filtering (schemas, data types), logging, or update strategy.

---

## 📄 License

Released under the **MIT License**. See [LICENSE](./LICENSE).

**Author:** [Kevin Veen-Birkenbach](https://www.veen.world)
**Generated with:** ChatGPT — see *[this conversation](https://chatgpt.com/share/689dba44-2e18-800f-bcd2-158002faf8da)* ✨