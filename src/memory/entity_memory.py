"""
Entity memory for tracking important entities mentioned in conversation.
"""
import re
from typing import Dict, List, Set
from datetime import datetime


class EntityMemory:
    """Tracks entities (people, dates, files, amounts) from conversation."""
    
    def __init__(self):
        """Initialize entity memory."""
        self.entities: Dict[str, Set[str]] = {
            'people': set(),
            'dates': set(),
            'files': set(),
            'amounts': set(),
            'messages': set()
        }
        self.last_mentioned: Dict[str, str] = {}
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract entities from text.
        
        Args:
            text: Text to extract from
            
        Returns:
            Dictionary of extracted entities by type
        """
        extracted = {
            'people': self._extract_people(text),
            'dates': self._extract_dates(text),
            'files': self._extract_files(text),
            'amounts': self._extract_amounts(text),
            'messages': self._extract_message_ids(text)
        }
        
        return extracted
    
    def update(self, text: str):
        """
        Update entity memory from text.
        
        Args:
            text: Text to extract entities from
        """
        extracted = self.extract_entities(text)
        
        for entity_type, values in extracted.items():
            for value in values:
                self.entities[entity_type].add(value)
                self.last_mentioned[entity_type] = value
    
    def _extract_people(self, text: str) -> List[str]:
        """Extract people names from text."""
        # Simple pattern: Capitalized words (potential names)
        # Look for common name patterns
        people = []
        
        # Pattern for "Name from Department" or "Name @ email"
        patterns = [
            r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b',  # John Doe
            r'\b([A-Z][a-z]+)\s+from\s+\w+',    # Sarah from Finance
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            people.extend(matches)
        
        return people
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates from text."""
        dates = []
        
        # Common date patterns
        patterns = [
            r'\b(\d{4}-\d{2}-\d{2})\b',           # 2001-04-15
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',     # 4/15/2001
            r'\b([A-Z][a-z]+ \d{1,2},? \d{4})\b', # April 15, 2001
            r'\b(yesterday|today|tomorrow)\b',     # Relative dates
            r'\b(last|next) (week|month|year)\b'  # Relative periods
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if isinstance(matches[0] if matches else None, tuple):
                dates.extend([' '.join(m) for m in matches])
            else:
                dates.extend(matches)
        
        return dates
    
    def _extract_files(self, text: str) -> List[str]:
        """Extract file references from text."""
        files = []
        
        # File extensions
        pattern = r'\b([\w\-]+\.(pdf|docx?|xlsx?|txt|html?))\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        files.extend([m[0] for m in matches])
        
        # Common file-related phrases
        file_phrases = [
            r'the ([\w\s]+(?:document|file|report|proposal|contract|spec))',
            r'([\w\s]+(?:document|file|report|proposal|contract|spec))'
        ]
        
        for pattern in file_phrases:
            matches = re.findall(pattern, text, re.IGNORECASE)
            files.extend([m.strip() for m in matches if len(m.strip()) > 3])
        
        return files
    
    def _extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts and numbers from text."""
        amounts = []
        
        # Money patterns
        patterns = [
            r'\$\s?(\d+[,\d]*\.?\d*)\s?[KMB]?',  # $45,000 or $45K
            r'(\d+[,\d]*\.?\d*)\s?dollars?',      # 45000 dollars
            r'€\s?(\d+[,\d]*\.?\d*)',             # €45,000
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)
        
        return amounts
    
    def _extract_message_ids(self, text: str) -> List[str]:
        """Extract message IDs from text."""
        # Pattern: M-XXXXXXXX
        pattern = r'\b(M-[a-f0-9]{8})\b'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return matches
    
    def get_last_mentioned(self, entity_type: str) -> str:
        """
        Get the last mentioned entity of a type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            Last mentioned entity or empty string
        """
        return self.last_mentioned.get(entity_type, "")
    
    def get_all(self, entity_type: str) -> List[str]:
        """
        Get all entities of a type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            List of entities
        """
        return list(self.entities.get(entity_type, set()))
    
    def clear(self):
        """Clear all entities."""
        for entity_type in self.entities:
            self.entities[entity_type].clear()
        self.last_mentioned.clear()