"""
Chat routes for Digital Library Assistant.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid

from app.nlp.rag_engine import rag_engine
from app.nlp.memory import memory_manager

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    intent: str
    confidence: float
    entities: Dict[str, Any]
    books: List[Dict[str, Any]]
    suggested_questions: List[str]
    session_id: str

@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Processes student query using NLP intent recognition,
    entity extraction, and RAG knowledge retrieval.
    """
    query_text = payload.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    session_id = payload.session_id or str(uuid.uuid4())
    result = rag_engine.process_query(query_text, session_id=session_id)
    return result

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Retrieves conversation history for a given session."""
    history = memory_manager.get_chat_history(session_id)
    return {"session_id": session_id, "messages": history}

@router.post("/clear/{session_id}")
async def clear_history(session_id: str):
    """Clears conversation context and history for a given session."""
    memory_manager.clear_session(session_id)
    return {"status": "success", "message": "Session history cleared."}
