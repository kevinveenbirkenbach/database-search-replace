#!/usr/bin/env python3
# main.py
# Render a SQL script from Jinja2 and execute via psql locally or with `docker exec` when --container is set.

import argparse
import os
import subprocess
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def build_args():
    p = argparse.ArgumentParser(
        description="Bulk search (and optional replace) across all text/varchar columns in a PostgreSQL database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("-d", "--database", required=True, help="Database name")
    p.add_argument("-U", "--user", default="postgres", help="Database user")
    p.add_argument("-p", "--password", required=True, help="Database password (sets PGPASSWORD)")
    p.add_argument("-H", "--host", default="localhost", help="Database host")
    p.add_argument("-P", "--port", type=int, default=5432, help="Database port")
    p.add_argument("-s", "--search", required=True, help="Search text")
    p.add_argument("-r", "--replace", help="Replacement text; if provided → replace mode")
    p.add_argument("-c", "--container", help="Docker container name to run psql in")
    p.add_argument("--psql-path", default="psql", help="Path to the psql binary")
    return p.parse_args()


def script_root() -> Path:
    """
    Determine the directory of this script, resolving symlinks.
    If bundled (PyInstaller), use the executable path.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def render_sql(mode: str, search_text: str, replace_text: str | None, template_dir: Path) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        undefined=StrictUndefined,
        autoescape=False,
    )
    tpl = env.get_template("query.sql.j2")
    return tpl.render(mode=mode, search_text=search_text, replace_text=replace_text)


def run_psql(sql_text: str, args):
    # Write SQL to a temp file for clarity
    tmp_sql_path = Path.cwd() / ".pg_bulk_find_replace.sql"
    tmp_sql_path.write_text(sql_text, encoding="utf-8")

    env = os.environ.copy()
    env["PGPASSWORD"] = args.password

    psql_cmd = [
        args.psql_path,
        "-v", "ON_ERROR_STOP=1",
        "-h", args.host,
        "-p", str(args.port),
        "-U", args.user,
        "-d", args.database,
        "-f", str(tmp_sql_path),
    ]

    cmd = ["docker", "exec", "-i", args.container] + psql_cmd if args.container else psql_cmd

    try:
        print("Executing:", " ".join(cmd))
        subprocess.run(cmd, check=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: psql exited with code {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)
    finally:
        try:
            tmp_sql_path.unlink(missing_ok=True)
        except Exception:
            pass


def main():
    args = build_args()
    mode = "replace" if args.replace is not None else "search"

    template_dir = script_root() / "templates"
    template_path = template_dir / "query.sql.j2"
    if not template_path.exists():
        print(
            "ERROR: Template not found.\n"
            f"Expected at: {template_path}\n"
            "Make sure the 'templates/query.sql.j2' file is installed next to this script.",
            file=sys.stderr
        )
        sys.exit(2)

    sql_text = render_sql(mode=mode, search_text=args.search, replace_text=args.replace, template_dir=template_dir)
    run_psql(sql_text, args)


if __name__ == "__main__":
    main()
