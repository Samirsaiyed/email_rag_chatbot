"""
API routes for the chatbot.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
import traceback
from .models import (
    StartSessionRequest, StartSessionResponse,
    AskRequest, AskResponse,
    ErrorResponse
)
from src.session.thread_session import ThreadSession

router = APIRouter()

# In-memory session storage
sessions: Dict[str, ThreadSession] = {}


@router.post("/start_session", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new conversation session for a thread."""
    try:
        print(f"Starting session for thread: {request.thread_id}")
        session = ThreadSession(thread_id=request.thread_id)
        sessions[session.session_id] = session
        print(f"Session created: {session.session_id}")
        
        return StartSessionResponse(
            session_id=session.session_id,
            thread_id=request.thread_id,
            message=f"Session started for thread {request.thread_id}"
        )
    except Exception as e:
        print(f"Error starting session: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """Ask a question in an existing session."""
    session = sessions.get(request.session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {request.session_id} not found"
        )
    
    try:
        result = session.ask(request.question, top_k=request.top_k)
        return AskResponse(**result)
    except Exception as e:
        print(f"Error processing question: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset_session")
async def reset_session(session_id: str):
    """Reset session memory."""
    session = sessions.get(session_id)
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    session.reset()
    return {"message": "Session reset successfully"}


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "sessions": len(sessions)}