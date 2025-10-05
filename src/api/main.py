"""
FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(
    title="Email RAG Chatbot API",
    description="Thread-based email search with conversational memory",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1", tags=["chat"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Email RAG Chatbot API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }