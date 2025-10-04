"""
Individual nodes for LangGraph workflows.
"""
import re
from typing import Dict
from .state import QueryRewriteState


class QueryRewriteNodes:
    """Nodes for query rewriting workflow."""
    
    @staticmethod
    def analyze_query(state: QueryRewriteState) -> Dict:
        """
        Analyze if query needs rewriting.
        
        Args:
            state: Current state
            
        Returns:
            Updated state
        """
        query = state['original_query'].lower()
        
        # Check for pronouns (handle punctuation)
        pronouns = ['it', 'that', 'this', 'he', 'she', 'they', 'him', 'her', 'them']
        has_pronouns = any(
            re.search(r'\b' + re.escape(p) + r'\b', query) 
            for p in pronouns
        )
        
        # Check for references
        references = ['the draft', 'the contract', 'the proposal', 'the document', 
                    'the file', 'the budget', 'the approval', 'earlier', 'previous']
        has_references = any(ref in query for ref in references)
        
        # Needs rewrite if has pronouns/references or is very short
        needs_rewrite = has_pronouns or has_references or len(query.split()) < 3
        
        return {
            **state,
            'has_pronouns': has_pronouns,
            'has_references': has_references,
            'needs_rewrite': needs_rewrite
        }
    
    @staticmethod
    def rewrite_query(state: QueryRewriteState) -> Dict:
        """
        Rewrite query using context.
        
        Args:
            state: Current state
            
        Returns:
            Updated state with rewritten query
        """
        if not state['needs_rewrite']:
            return {
                **state,
                'rewritten_query': state['original_query'],
                'rewrite_reasoning': 'Query is clear, no rewrite needed'
            }
        
        query = state['original_query']
        rewritten = query
        reasoning_parts = []
        
        last_mentioned = state.get('last_mentioned', {})
        
        # Handle "it", "that", "this" -> last mentioned entity
        if re.search(r'\b(it|that|this)\b', query, re.IGNORECASE):
            # Priority: amount > file
            if last_mentioned.get('amount'):
                amount = last_mentioned['amount']
                rewritten = re.sub(
                    r'\bit\b', 
                    f'the ${amount} budget', 
                    rewritten, 
                    count=1,
                    flags=re.IGNORECASE
                )
                reasoning_parts.append(f"Resolved 'it' to 'the ${amount} budget'")
            elif last_mentioned.get('file') and '.pdf' in last_mentioned['file'].lower():
                file_name = last_mentioned['file']
                rewritten = re.sub(
                    r'\b(it|that|this)\b', 
                    file_name, 
                    rewritten, 
                    count=1,
                    flags=re.IGNORECASE
                )
                reasoning_parts.append(f"Resolved pronoun to '{file_name}'")
        
        # Handle "he", "she", "they" -> last mentioned person
        if re.search(r'\b(he|she|they)\b', query, re.IGNORECASE):
            if last_mentioned.get('person'):
                person = last_mentioned['person']
                rewritten = re.sub(r'\bshe\b', person, rewritten, flags=re.IGNORECASE)
                rewritten = re.sub(r'\bhe\b', person, rewritten, flags=re.IGNORECASE)
                rewritten = re.sub(r'\bthey\b', person, rewritten, flags=re.IGNORECASE)
                reasoning_parts.append(f"Resolved pronoun to '{person}'")
        
        # If still no changes and needs rewrite, add context
        if rewritten == query:
            context_parts = []
            if last_mentioned.get('file'):
                context_parts.append(last_mentioned['file'])
            if last_mentioned.get('amount'):
                context_parts.append(f"${last_mentioned['amount']}")
            
            if context_parts:
                rewritten = f"{query} ({', '.join(context_parts)})"
                reasoning_parts.append("Added contextual entities")
        
        reasoning = '; '.join(reasoning_parts) if reasoning_parts else 'No rewrite needed'
        
        return {
            **state,
            'rewritten_query': rewritten,
            'rewrite_reasoning': reasoning
        }
    
    @staticmethod
    def should_rewrite(state: QueryRewriteState) -> str:
        """
        Decide if rewriting is needed.
        
        Args:
            state: Current state
            
        Returns:
            Next node to execute
        """
        return "rewrite" if state.get('needs_rewrite', False) else "skip"