"""
API: session, file upload (Excel/CSV), and chat with data analyst agent.
"""
import os

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import answer_question
from parser import parse_upload
from store import (
    create_session,
    get_schema,
    get_tables_json,
    has_data,
    put_data,
    run_sql,
)

load_dotenv()

app = FastAPI(title="Analytics Agent API", description="Upload Excel/CSV and chat with a data analyst.")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").strip().split(",")
app.add_middleware(CORSMiddleware, allow_origins=cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


class SessionResponse(BaseModel):
    session_id: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/session", response_model=SessionResponse)
def new_session():
    return SessionResponse(session_id=create_session())


@app.post("/upload")
async def upload_file(session_id: str, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename")
    content = await file.read()
    try:
        result = parse_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(400, str(e))
    put_data(session_id, result["tables"], result["schema"])
    return {
        "ok": True,
        "session_id": session_id,
        "tables": list(result["tables"].keys()),
        "schema_preview": result["schema"][:500] + ("..." if len(result["schema"]) > 500 else ""),
    }


@app.get("/schema/{session_id}")
def schema(session_id: str):
    if not has_data(session_id):
        return {"tables": [], "schema": ""}
    return {"tables": list(get_tables_json(session_id).keys()), "schema": get_schema(session_id)}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = answer_question(req.session_id, req.message, get_schema, run_sql)
    return ChatResponse(reply=reply)


@app.get("/health")
def health():
    return {"status": "ok"}
