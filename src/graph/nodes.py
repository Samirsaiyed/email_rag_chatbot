"""
LLM-powered nodes for query rewriting.
"""
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .state import QueryRewriteState
from src.config import LLM_CONFIG
import re
from dotenv import load_dotenv

load_dotenv()


class QueryRewriteNodes:
    """Nodes for query rewriting workflow using LLM."""
    
    def __init__(self):
        """Initialize with LLM."""
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Fast and cheap for rewriting
            temperature=0.1,  # Low temp for consistent rewrites
            max_tokens=100,
            api_key=LLM_CONFIG.api_key
        )
        
        self.rewrite_prompt = ChatPromptTemplate.from_template("""You are a query rewriting assistant. Your job is to rewrite vague or context-dependent queries into clear, standalone queries.

CONVERSATION HISTORY:
{conversation_history}

ENTITIES MENTIONED:
- People: {people}
- Files: {files}
- Amounts: {amounts}
- Dates: {dates}

ORIGINAL QUERY: {original_query}

INSTRUCTIONS:
1. If the query uses pronouns (it, that, he, she, they), replace them with the actual entities
2. If the query refers to previous context, make it explicit
3. If the query is already clear, return it unchanged
4. Keep the rewritten query concise and natural
5. Do NOT add extra information not implied by the context

REWRITTEN QUERY:""")
        
        self.chain = self.rewrite_prompt | self.llm | StrOutputParser()
    
    @staticmethod
    def analyze_query(state: QueryRewriteState) -> Dict:
        """Analyze if query needs rewriting."""
        query = state['original_query'].lower()
        
        # Check for pronouns
        pronouns = ['it', 'that', 'this', 'he', 'she', 'they', 'him', 'her', 'them']
        has_pronouns = any(
            re.search(r'\b' + re.escape(p) + r'\b', query) 
            for p in pronouns
        )
        
        # Check for references
        references = ['the draft', 'the contract', 'the proposal', 'the document', 
                     'the file', 'the budget', 'the approval', 'earlier', 'previous',
                     'that one', 'first', 'second', 'last']
        has_references = any(ref in query for ref in references)
        
        # Check for corrections
        corrections = ['no,', 'actually,', 'i meant', 'sorry,', 'instead']
        has_corrections = any(corr in query for corr in corrections)
        
        # Very short queries likely need context
        is_short = len(query.split()) < 4
        
        needs_rewrite = has_pronouns or has_references or has_corrections or is_short
        
        return {
            **state,
            'has_pronouns': has_pronouns,
            'has_references': has_references,
            'needs_rewrite': needs_rewrite
        }
    
    def rewrite_query(self, state: QueryRewriteState) -> Dict:
        """Rewrite query using LLM."""
        if not state['needs_rewrite']:
            return {
                **state,
                'rewritten_query': state['original_query'],
                'rewrite_reasoning': 'Query is clear, no rewrite needed'
            }
        
        try:
            # Prepare context
            entities = state.get('entities', {})
            last_mentioned = state.get('last_mentioned', {})
            
            # Get conversation snippet (last 2 turns)
            conv_history = state.get('conversation_history', '')
            if conv_history:
                lines = conv_history.split('\n')
                conv_history = '\n'.join(lines[-4:]) if len(lines) > 4 else conv_history
            
            # Format entities for prompt
            people = ', '.join(entities.get('people', [])[:3]) or 'None'
            files = ', '.join(entities.get('files', [])[:3]) or 'None'
            amounts = ', '.join(entities.get('amounts', [])[:3]) or 'None'
            dates = ', '.join(entities.get('dates', [])[:3]) or 'None'
            
            # Call LLM
            rewritten = self.chain.invoke({
                'conversation_history': conv_history or 'No previous conversation',
                'people': people,
                'files': files,
                'amounts': amounts,
                'dates': dates,
                'original_query': state['original_query']
            })
            
            rewritten = rewritten.strip()
            
            # If LLM didn't change it much, just use original
            if rewritten.lower() == state['original_query'].lower():
                reasoning = 'LLM determined no rewrite needed'
            else:
                reasoning = f'Resolved references using conversation context'
            
            return {
                **state,
                'rewritten_query': rewritten,
                'rewrite_reasoning': reasoning
            }
        
        except Exception as e:
            print(f"LLM rewrite error: {e}, falling back to original query")
            return {
                **state,
                'rewritten_query': state['original_query'],
                'rewrite_reasoning': f'LLM error, using original query'
            }
    
    @staticmethod
    def should_rewrite(state: QueryRewriteState) -> str:
        """Decide if rewriting is needed."""
        return "rewrite" if state.get('needs_rewrite', False) else "skip"