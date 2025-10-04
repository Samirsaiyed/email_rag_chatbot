"""
Conversation memory for tracking chat history.
"""
from typing import List, Dict, Optional
from langchain.memory import ConversationBufferMemory


class ConversationMemory:
    """Manages conversation history."""
    
    def __init__(self, max_turns: int = 5):
        """
        Initialize conversation memory.
        
        Args:
            max_turns: Maximum number of turns to keep
        """
        self.max_turns = max_turns
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.turns: List[Dict[str, str]] = []
    
    def add_turn(self, user_message: str, assistant_message: str):
        """
        Add a conversation turn.
        
        Args:
            user_message: User's message
            assistant_message: Assistant's response
        """
        # Add to LangChain memory
        self.memory.save_context(
            {"input": user_message},
            {"output": assistant_message}
        )
        
        # Add to our list
        self.turns.append({
            "user": user_message,
            "assistant": assistant_message
        })
        
        # Keep only last N turns
        if len(self.turns) > self.max_turns:
            self.turns = self.turns[-self.max_turns:]
    
    def get_recent_context(self, n: Optional[int] = None) -> str:
        """
        Get recent conversation context as formatted string.
        
        Args:
            n: Number of recent turns (default: all)
            
        Returns:
            Formatted conversation history
        """
        turns_to_show = self.turns[-n:] if n else self.turns
        
        if not turns_to_show:
            return ""
        
        context_parts = []
        for turn in turns_to_show:
            context_parts.append(f"User: {turn['user']}")
            context_parts.append(f"Assistant: {turn['assistant']}")
        
        return "\n".join(context_parts)
    
    def get_last_user_message(self) -> Optional[str]:
        """Get the last user message."""
        if self.turns:
            return self.turns[-1]["user"]
        return None
    
    def get_last_assistant_message(self) -> Optional[str]:
        """Get the last assistant message."""
        if self.turns:
            return self.turns[-1]["assistant"]
        return None
    
    def clear(self):
        """Clear all conversation history."""
        self.memory.clear()
        self.turns = []