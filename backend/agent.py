"""
Data analyst agent: answers natural-language questions about uploaded data
using schema and SQL (no pandas).
"""
from __future__ import annotations

import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

SYSTEM_PROMPT = """You are a helpful data analyst chatbot. The user has uploaded one or more datasets (Excel or CSV).
You will be given:
1. A schema description (table names, columns).
2. The ability to run SQL (SELECT only) on those tables. Table and column names may need double quotes if they contain spaces.

Answer in clear, concise language. When you run a query, summarize the result in a sentence or two.
If you need to run analysis, reply with exactly one line: RUN: SELECT ... (valid SQL). Use the table and column names from the schema.
If the user's question cannot be answered from the data, say so."""


def get_schema_tool(schema: str) -> str:
    return schema or "No data has been uploaded yet. Ask the user to upload an Excel or CSV file."


def answer_question(session_id: str, message: str, get_schema_fn: callable, run_sql_fn: callable) -> str:
    if not OpenAI:
        return "OpenAI package not installed. Set OPENAI_API_KEY and install openai."
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY is not set. Add it to .env to enable the data analyst."

    schema = get_schema_fn(session_id)

    user_content = (
        f"Schema of uploaded data:\n{get_schema_tool(schema)}\n\n"
        f"User question: {message}\n\n"
        'If you need to run a query, reply with exactly one line: RUN: SELECT ... (use table names from schema; put them in double quotes if they have spaces, e.g. "Sheet1").'
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

    if "RUN:" in reply:
        lines = reply.split("\n")
        new_lines = []
        for line in lines:
            if line.strip().upper().startswith("RUN:"):
                sql = line.strip()[4:].strip()
                outcome = run_sql_fn(session_id, sql)
                new_lines.append(f"Result:\n{outcome}")
            else:
                new_lines.append(line)
        reply = "\n".join(new_lines)

    return reply
