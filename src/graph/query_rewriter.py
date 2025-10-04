"""
LangGraph workflow for query rewriting.
"""
from typing import Dict
from langgraph.graph import StateGraph, END
from .state import QueryRewriteState
from .nodes import QueryRewriteNodes


class QueryRewriter:
    """LangGraph-based query rewriter."""
    
    def __init__(self):
        """Initialize query rewriter."""
        self.nodes = QueryRewriteNodes()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the query rewriting workflow graph.
        
        Returns:
            Compiled StateGraph
        """
        # Create graph
        workflow = StateGraph(QueryRewriteState)
        
        # Add nodes
        workflow.add_node("analyze", self.nodes.analyze_query)
        workflow.add_node("rewrite", self.nodes.rewrite_query)
        workflow.add_node("skip", lambda state: {
            **state,
            'rewritten_query': state['original_query'],
            'rewrite_reasoning': 'Query is clear, no rewrite needed'
        })
        
        # Set entry point
        workflow.set_entry_point("analyze")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "analyze",
            self.nodes.should_rewrite,
            {
                "rewrite": "rewrite",
                "skip": "skip"
            }
        )
        
        # Add edges to END
        workflow.add_edge("rewrite", END)
        workflow.add_edge("skip", END)
        
        # Compile
        return workflow.compile()
    
    def rewrite(self, query: str, memory_context: Dict) -> Dict[str, str]:
        """
        Rewrite query using memory context.
        
        Args:
            query: Original query
            memory_context: Context from MemoryManager
            
        Returns:
            Dictionary with rewritten_query and reasoning
        """
        # Prepare initial state
        initial_state = {
            'original_query': query,
            'conversation_history': memory_context.get('conversation_history', ''),
            'entities': memory_context.get('entities', {}),
            'last_mentioned': memory_context.get('last_mentioned', {}),
            'has_pronouns': False,
            'has_references': False,
            'needs_rewrite': False,
            'rewritten_query': '',
            'rewrite_reasoning': ''
        }
        
        # Run graph
        result = self.graph.invoke(initial_state)
        
        return {
            'rewritten_query': result['rewritten_query'],
            'reasoning': result['rewrite_reasoning']
        }