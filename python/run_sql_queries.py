"""
Retail Sales & Customer Analytics - Run SQL Analysis
====================================================
Executes sql/analysis_queries.sql and sql/advanced_queries.sql against
data/retail.db and saves each result to reports/sql_results/<name>.csv
plus a combined summary markdown.
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

DB = Path("data/retail.db")
RES = Path("reports/sql_results")


def split_queries(sql: str) -> list[tuple[str, str]]:
    """Split a .sql file into (name, statement) pairs using comment headers."""
    statements = []
    for block in re.split(r"--\s*[A-Z]+[0-9]*\.", sql):
        block = block.strip()
        if not block:
            continue
        header = re.search(r"--\s*([A-Z]+[0-9]*)\.[^\n]*", sql[0:0] or block)
        name = header.group(1) if header else "query"
        statements.append((name, block))
    return statements


def split_statements(sql: str) -> list[tuple[str, str, str]]:
    """Split a .sql file into (name, title, executable_body) blocks using
    header comments of the form '-- Q1. <title>' / '-- A1. <title>'."""
    parts = re.split(r"(?m)^--\s*(Q\d+|A\d+)\.\s*", sql)
    blocks = []
    for i in range(1, len(parts), 2):
        name = parts[i]
        title = parts[i + 1].splitlines()[0].strip()
        body_lines = parts[i + 1].splitlines()[1:]
        body = "\n".join(l for l in body_lines if not l.strip().startswith("--"))
        body = body.strip().rstrip(";").strip()
        if body:
            blocks.append((name, title, body))
    return blocks


def run_file(con: sqlite3.Connection, sql: str, prefix: str) -> list[dict]:
    results = []
    for name, title, body in split_statements(sql):
        try:
            df = pd.read_sql_query(body, con)
        except Exception as e:  # pragma: no cover
            print(f"  ! {prefix}{name} ({title}) FAILED: {e}")
            continue
        if df.empty:
            continue
        df.to_csv(RES / f"{prefix}{name}.csv", index=False)
        results.append({"name": f"{prefix}{name}", "title": title, "rows": int(len(df)),
                        "columns": list(df.columns), "preview": df.head(10)})
        print(f"  {prefix}{name:>8} ({title}) -> {len(df):,} rows")
    return results


def main() -> None:
    RES.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    all_res = []

    for prefix, path in [("", "sql/analysis_queries.sql"),
                         ("", "sql/advanced_queries.sql")]:
        print(f"\n--- {path} ---")
        all_res += run_file(con, Path(path).read_text(encoding="utf-8"), prefix)

    # summary markdown
    lines = ["# SQL Analysis Results\n"]
    for r in all_res:
        lines.append(f"\n## {r['name']}. {r['title']}  ({r['rows']:,} rows)")
        lines.append(r["preview"].to_markdown(index=False))
    (Path("reports/sql_analysis_results.md")).write_text("\n".join(lines), encoding="utf-8")
    con.close()
    print(f"\nSaved {len(all_res)} query results -> {RES} + reports/sql_analysis_results.md")


if __name__ == "__main__":
    main()