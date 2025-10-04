"""
Unified memory manager combining conversation and entity memory.
"""
from typing import Dict, Optional
from .conversation_memory import ConversationMemory
from .entity_memory import EntityMemory


class MemoryManager:
    """Manages both conversation and entity memory."""
    
    def __init__(self, max_turns: int = 5):
        """
        Initialize memory manager.
        
        Args:
            max_turns: Maximum conversation turns to keep
        """
        self.conversation = ConversationMemory(max_turns=max_turns)
        self.entities = EntityMemory()
    
    def add_turn(self, user_message: str, assistant_message: str):
        """
        Add a conversation turn and extract entities.
        
        Args:
            user_message: User's message
            assistant_message: Assistant's response
        """
        # Add to conversation memory
        self.conversation.add_turn(user_message, assistant_message)
        
        # Extract and store entities from both messages
        self.entities.update(user_message)
        self.entities.update(assistant_message)
    
    def get_context_for_rewrite(self) -> Dict[str, any]:
        """
        Get context needed for query rewriting.
        
        Returns:
            Dictionary with conversation history and entities
        """
        return {
            'conversation_history': self.conversation.get_recent_context(n=3),
            'last_user_message': self.conversation.get_last_user_message(),
            'last_assistant_message': self.conversation.get_last_assistant_message(),
            'entities': {
                'people': self.entities.get_all('people'),
                'files': self.entities.get_all('files'),
                'dates': self.entities.get_all('dates'),
                'amounts': self.entities.get_all('amounts'),
                'messages': self.entities.get_all('messages')
            },
            'last_mentioned': {
                'person': self.entities.get_last_mentioned('people'),
                'file': self.entities.get_last_mentioned('files'),
                'date': self.entities.get_last_mentioned('dates'),
                'amount': self.entities.get_last_mentioned('amounts'),
                'message': self.entities.get_last_mentioned('messages')
            }
        }
    
    def clear(self):
        """Clear all memory."""
        self.conversation.clear()
        self.entities.clear()