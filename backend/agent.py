"""
Data analyst agent: answers natural-language questions about uploaded data
using schema inspection and safe pandas operations.
"""
from __future__ import annotations

import os
from typing import Any

import pandas as pd

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

SYSTEM_PROMPT = """You are a helpful data analyst chatbot. The user has uploaded one or more datasets (Excel or CSV).
You will be given:
1. A schema description (table names, columns, dtypes).
2. Tools to describe the data and run pandas-style analyses.

Answer in clear, concise language. When you run a query, summarize the result in a sentence or two.
If the user's question cannot be answered from the data, say so and suggest what data would be needed."""


def get_schema_tool(schema: str) -> str:
    """Return schema for the LLM context."""
    return schema or "No data has been uploaded yet. Ask the user to upload an Excel or CSV file."


def run_analysis_tool(tables: dict[str, pd.DataFrame], query: str) -> str:
    """
    Run a pandas expression in a restricted scope. Only tables and pandas are available.
    The query should be valid Python that returns a result (e.g. df.head(), df.describe()).
    """
    if not tables:
        return "No data uploaded. Please upload an Excel or CSV file first."
    try:
        # Restrict globals to tables and pd
        local_vars: dict[str, Any] = {"pd": pd, **{k: v for k, v in tables.items()}}
        # Allow first table as 'df' for convenience
        first_name, first_df = next(iter(tables.items()))
        local_vars["df"] = first_df
        local_vars["tables"] = tables
        exec(f"__result__ = {query}", {"pd": pd, **tables}, local_vars)
        result = local_vars["__result__"]
        if isinstance(result, pd.DataFrame):
            return result.to_string(max_rows=20)
        return str(result)
    except Exception as e:
        return f"Error running analysis: {e}"


def answer_question(session_id: str, message: str, get_schema_fn: callable, get_tables_fn: callable) -> str:
    """
    Use the OpenAI API to answer a question about the session's data.
    Injects schema and optionally runs a suggested analysis.
    """
    if not OpenAI:
        return "OpenAI package not installed. Set OPENAI_API_KEY and install openai."
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY is not set. Add it to .env to enable the data analyst."

    schema = get_schema_fn(session_id)
    tables = get_tables_fn(session_id)

    user_content = (
        f"Schema of uploaded data:\n{get_schema_tool(schema)}\n\n"
        f"User question: {message}\n\n"
        "If you need to run an analysis, reply with a single line: RUN: <pandas expression using df or tables>. "
        "Example: RUN: df['Sales'].sum()"
    )

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        max_tokens=1024,
    )
    reply = (response.choices[0].message.content or "").strip()

    # If the model asked to run something, run it and append result
    if "RUN:" in reply:
        lines = reply.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().startswith("RUN:"):
                expr = line.strip()[4:].strip()
                outcome = run_analysis_tool(tables, expr)
                new_lines.append(f"Result:\n{outcome}")
            else:
                new_lines.append(line)
        reply = "\n".join(new_lines)

    return reply
