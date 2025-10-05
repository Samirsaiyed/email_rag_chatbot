"""
Pydantic models for API requests and responses.
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    """Request to start a new session."""
    thread_id: str = Field(..., description="Thread ID to search")


class StartSessionResponse(BaseModel):
    """Response for session start."""
    session_id: str
    thread_id: str
    message: str


class AskRequest(BaseModel):
    """Request to ask a question."""
    session_id: str = Field(..., description="Session ID")
    question: str = Field(..., min_length=1, description="Question to ask")
    top_k: Optional[int] = Field(5, ge=1, le=10, description="Number of results")


class Citation(BaseModel):
    """Citation information."""
    type: str
    message_id: Optional[str] = None
    page: Optional[int] = None
    filename: Optional[str] = None
    citation_text: str


class RetrievedChunk(BaseModel):
    """Retrieved chunk information."""
    chunk_id: str
    message_id: str
    score: float


class AskResponse(BaseModel):
    """Response for ask question."""
    answer: str
    citations: List[Citation]
    rewritten_query: str
    rewrite_reasoning: str
    retrieved_chunks: List[RetrievedChunk]
    trace_id: str
    thread_id: str
    session_id: str


class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    detail: Optional[str] = None