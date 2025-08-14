#!/usr/bin/env python3
# main.py
# Render a SQL script from Jinja2 and execute via psql (PostgreSQL)
# or mysql (MariaDB), locally or via `docker exec` when --container is set.

import argparse
import os
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def build_args():
    p = argparse.ArgumentParser(
        description="Bulk search (and optional replace) across all text/varchar columns in a database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("-t", "--type", choices=["postgres", "mariadb"], default="postgres",
                   help="Database type")
    p.add_argument("-d", "--database", required=True, help="Database name")
    p.add_argument("-U", "--user", default="postgres", help="Database user")
    p.add_argument("-p", "--password", required=True, help="Database password")
    p.add_argument("-H", "--host", default="localhost", help="Database host")
    p.add_argument("-P", "--port", type=int, default=5432,
                   help="Database port (auto 3306 for MariaDB if left at 5432)")
    p.add_argument("-s", "--search", required=True, help="Search text")
    p.add_argument("-r", "--replace", help="Replacement text; if provided → replace mode")
    p.add_argument("-c", "--container", help="Docker container name to run the client in")
    p.add_argument("--psql-path", default="psql", help="Path to the psql binary (PostgreSQL)")
    p.add_argument("--mysql-path", default="mysql", help="Path to the mysql binary (MariaDB/MySQL)")
    return p.parse_args()


def script_root() -> Path:
    """Directory of this script, resolving symlinks (works when installed via symlink)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def render_sql(db_type: str, mode: str, search_text: str, replace_text: str | None,
               template_root: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_root)),
        undefined=StrictUndefined,
        autoescape=False,
    )
    template_name = f"{db_type}.sql.j2"  # e.g. postgres.sql.j2 or mariadb.sql.j2
    tpl = env.get_template(template_name)
    return tpl.render(mode=mode, search_text=search_text, replace_text=replace_text)


def run_client(sql_text: str, args):
    # Auto-adjust default port for MariaDB if left at the PostgreSQL default
    if args.type == "mariadb" and args.port == 5432:
        args.port = 3306

    if args.type == "postgres":
        env = os.environ.copy()
        env["PGPASSWORD"] = args.password

        base_psql = [
            args.psql_path,
            "-v", "ON_ERROR_STOP=1",
            "-h", args.host,
            "-p", str(args.port),
            "-U", args.user,
            "-d", args.database,
        ]

        if args.container:
            cmd = [
                "docker", "exec", "-i", args.container,
                "env", f"PGPASSWORD={args.password}",
                *base_psql, "-f", "-"  # read SQL from stdin
            ]
            print("Executing:", " ".join(cmd))
            subprocess.run(cmd, check=True, input=sql_text.encode("utf-8"))
        else:
            tmp_sql_path = Path.cwd() / ".pg_bulk_find_replace.sql"
            tmp_sql_path.write_text(sql_text, encoding="utf-8")
            cmd = [*base_psql, "-f", str(tmp_sql_path)]
            try:
                print("Executing:", " ".join(cmd))
                subprocess.run(cmd, check=True, env=env)
            finally:
                try:
                    tmp_sql_path.unlink(missing_ok=True)
                except Exception:
                    pass

    else:  # MariaDB
        env = os.environ.copy()
        env["MYSQL_PWD"] = args.password  # avoid password in argv

        base_mysql = [
            args.mysql_path,
            "-h", args.host,
            "-P", str(args.port),
            "-u", args.user,
            args.database,
            "--protocol=TCP",
        ]

        if args.container:
            cmd = [
                "docker", "exec", "-i", args.container,
                "env", f"MYSQL_PWD={args.password}",
                *base_mysql
            ]
            print("Executing:", " ".join(cmd))
            subprocess.run(cmd, check=True, input=sql_text.encode("utf-8"))
        else:
            print("Executing:", " ".join(base_mysql))
            subprocess.run(base_mysql, check=True, input=sql_text.encode("utf-8"), env=env)


def main():
    args = build_args()
    mode = "replace" if args.replace is not None else "search"

    # Templates live in templates/query/{postgres|mariadb}.sql.j2
    template_root = script_root() / "templates" / "query"
    template_path = template_root / f"{args.type}.sql.j2"
    if not template_path.exists():
        print(
            "ERROR: Template not found.\n"
            f"Expected at: {template_path}\n"
            "Make sure the template is installed next to this script.",
            file=sys.stderr
        )
        sys.exit(2)

    sql_text = render_sql(
        args.type, mode=mode, search_text=args.search, replace_text=args.replace,
        template_root=template_root
    )
    run_client(sql_text, args)


if __name__ == "__main__":
    main()
