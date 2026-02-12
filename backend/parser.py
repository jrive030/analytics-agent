"""
Parse Excel and CSV files into pandas DataFrames.
Power BI users can export to Excel or CSV and upload those files.
"""
import io
from pathlib import Path
from typing import Any

import pandas as pd


def parse_upload(content: bytes, filename: str) -> dict[str, Any]:
    """
    Parse an uploaded file (Excel or CSV) into a dict of sheet/table name -> DataFrame.
    Returns {"tables": {"Sheet1": <df>, ...}, "schema": <summary>}.
    """
    suffix = Path(filename).suffix.lower()
    tables: dict[str, pd.DataFrame] = {}

    if suffix in (".xlsx", ".xls"):
        # Excel: one DataFrame per sheet
        excel = pd.ExcelFile(io.BytesIO(content))
        for sheet in excel.sheet_names:
            tables[sheet] = pd.read_excel(excel, sheet_name=sheet)
    elif suffix == ".csv":
        tables["Sheet1"] = pd.read_csv(io.BytesIO(content))
    else:
        raise ValueError(f"Unsupported format: {suffix}. Use .xlsx, .xls, or .csv")

    schema = _build_schema(tables)
    return {"tables": {k: v.to_dict(orient="split") for k, v in tables.items()}, "schema": schema}


def _build_schema(tables: dict[str, pd.DataFrame]) -> str:
    parts = []
    for name, df in tables.items():
        parts.append(f"Table: {name}")
        parts.append(f"  Rows: {len(df)}, Columns: {list(df.columns)}")
        parts.append(f"  Dtypes: {df.dtypes.astype(str).to_dict()}")
        parts.append("")
    return "\n".join(parts).strip()
