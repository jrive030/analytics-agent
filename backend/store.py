"""
In-memory store for uploaded datasets per session.
Uses SQLite for querying (no pandas).
"""
from __future__ import annotations

import sqlite3
import uuid
from typing import Any


def _quote(s: str) -> str:
    return '"' + s.replace('"', '""') + '"'


_store: dict[str, dict[str, Any]] = {}


def create_session() -> str:
    sid = str(uuid.uuid4())
    _store[sid] = {"tables": {}, "schema": "", "conn": None}
    return sid


def put_data(session_id: str, tables: dict[str, list[dict[str, Any]]], schema: str) -> None:
    if session_id not in _store:
        _store[session_id] = {"tables": {}, "schema": "", "conn": None}
    _store[session_id]["tables"] = tables
    _store[session_id]["schema"] = schema
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    for name, rows in tables.items():
        if not rows:
            continue
        cols = list(rows[0].keys())
        col_defs = ", ".join(f'{_quote(c)} TEXT' for c in cols)
        conn.execute(f'CREATE TABLE {_quote(name)} ({col_defs})')
        for row in rows:
            placeholders = ", ".join("?" for _ in cols)
            conn.execute(
                f'INSERT INTO {_quote(name)} ({", ".join(_quote(c) for c in cols)}) VALUES ({placeholders})',
                [str(row.get(c, "")) for c in cols],
            )
    conn.commit()
    if _store[session_id].get("conn"):
        _store[session_id]["conn"].close()
    _store[session_id]["conn"] = conn


def get_schema(session_id: str) -> str:
    return _store.get(session_id, {}).get("schema", "")


def run_sql(session_id: str, query: str) -> str:
    """Run a read-only SQL query; return result as string. Table names are as in schema (e.g. Sheet1)."""
    conn = _store.get(session_id, {}).get("conn")
    if not conn:
        return "No data uploaded. Please upload an Excel or CSV file first."
    query = query.strip().rstrip(";")
    if query.upper().strip().startswith(("INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER")):
        return "Only SELECT queries are allowed."
    try:
        cur = conn.execute(query)
        rows = cur.fetchall()
        if not rows:
            return "No rows returned."
        names = list(rows[0].keys()) if hasattr(rows[0], "keys") else list(range(len(rows[0])))
        lines = [" | ".join(str(names))] if names else []
        for row in rows:
            if hasattr(row, "keys"):
                lines.append(" | ".join(str(row[k]) for k in names))
            else:
                lines.append(" | ".join(str(v) for v in row))
        return "\n".join(lines[:21]) + ("\n..." if len(lines) > 21 else "")
    except Exception as e:
        return f"Error: {e}"


def get_tables_json(session_id: str) -> dict[str, Any]:
    return _store.get(session_id, {}).get("tables", {})


def has_data(session_id: str) -> bool:
    return bool(_store.get(session_id, {}).get("tables"))
