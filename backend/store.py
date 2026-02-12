"""
In-memory store for uploaded datasets per session.
In production you might use Redis or a DB keyed by user/session.
"""
from __future__ import annotations

import uuid
from typing import Any

import pandas as pd


_store: dict[str, dict[str, Any]] = {}


def create_session() -> str:
    sid = str(uuid.uuid4())
    _store[sid] = {"tables": {}, "schema": "", "raw_tables": {}}
    return sid


def put_data(session_id: str, tables: dict[str, pd.DataFrame], schema: str) -> None:
    if session_id not in _store:
        _store[session_id] = {"tables": {}, "schema": "", "raw_tables": {}}
    # Keep DataFrames for agent queries
    _store[session_id]["raw_tables"] = tables
    _store[session_id]["schema"] = schema
    _store[session_id]["tables"] = {k: v.to_dict(orient="split") for k, v in tables.items()}


def get_schema(session_id: str) -> str:
    return _store.get(session_id, {}).get("schema", "")


def get_tables(session_id: str) -> dict[str, pd.DataFrame]:
    return _store.get(session_id, {}).get("raw_tables", {})


def get_tables_json(session_id: str) -> dict[str, Any]:
    return _store.get(session_id, {}).get("tables", {})


def has_data(session_id: str) -> bool:
    return bool(_store.get(session_id, {}).get("raw_tables"))
