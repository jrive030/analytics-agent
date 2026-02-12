"""
API: session, file upload (Excel/CSV), and chat with data analyst agent.
"""
import os
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import answer_question
from parser import parse_upload
from store import (
    create_session,
    get_schema,
    get_tables,
    get_tables_json,
    has_data,
    put_data,
)

load_dotenv()

app = FastAPI(title="Analytics Agent API", description="Upload Excel/CSV and chat with a data analyst.")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").strip().split(",")
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# --- Request/response models ---
class SessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


# --- Routes ---
@app.post("/session", response_model=SessionResponse)
def new_session():
    """Create a new session. Use the returned session_id for upload and chat."""
    return SessionResponse(session_id=create_session())


@app.post("/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    """Upload an Excel (.xlsx, .xls) or CSV file. Power BI: export to Excel or CSV first."""
    if not file.filename:
        raise HTTPException(400, "No filename")
    content = await file.read()
    try:
        result = parse_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    # Convert orient="split" back to DataFrames for the agent
    tables = {}
    for name, raw in result["tables"].items():
        tables[name] = pd.DataFrame(raw["data"], columns=raw["columns"])
    put_data(session_id, tables, result["schema"])
    return {
        "ok": True,
        "session_id": session_id,
        "tables": list(tables.keys()),
        "schema_preview": result["schema"][:500] + ("..." if len(result["schema"]) > 500 else ""),
    }


@app.get("/schema/{session_id}")
def schema(session_id: str):
    """Return schema and table list for the session."""
    if not has_data(session_id):
        return {"tables": [], "schema": ""}
    return {"tables": list(get_tables_json(session_id).keys()), "schema": get_schema(session_id)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a message to the data analyst agent."""
    reply = answer_question(req.session_id, req.message, get_schema, get_tables)
    return ChatResponse(reply=reply)


@app.get("/health")
def health():
    return {"status": "ok"}
