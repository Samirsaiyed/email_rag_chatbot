"""
State definitions for LangGraph workflows.
"""
from typing import TypedDict, List, Dict, Optional


class QueryRewriteState(TypedDict):
    """State for query rewriting workflow."""
    
    # Input
    original_query: str
    conversation_history: str
    entities: Dict[str, List[str]]
    last_mentioned: Dict[str, str]
    
    # Intermediate
    has_pronouns: bool
    has_references: bool
    needs_rewrite: bool
    
    # Output
    rewritten_query: str
    rewrite_reasoning: str