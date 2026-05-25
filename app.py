from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from rag_core import RAGCore

app = FastAPI(title="RAG Basico")
_rag: RAGCore | None = None
STATIC = Path(__file__).parent / "static"


def get_rag() -> RAGCore:
    global _rag
    if _rag is None:
        _rag = RAGCore()
    return _rag


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health() -> dict:
    return {"ok": True, "tipo": "rag_sin_ia"}


@app.post("/ingest")
async def ingest_file(file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    text = raw.decode("utf-8", errors="ignore")
    if not text.strip():
        raise HTTPException(status_code=400, detail="El archivo esta vacio")
    try:
        chunks = get_rag().ingest_text(text, source_name=file.filename or "archivo")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"ok": True, "chunks": chunks}


@app.post("/search")
def search(payload: dict) -> dict:
    question = payload.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Falta 'question'")
    try:
        raw_chunks = get_rag().search(question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"question": question, "raw_chunks": raw_chunks}
