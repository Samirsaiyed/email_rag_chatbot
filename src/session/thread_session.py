"""
Thread session orchestrator - combines all components.
"""
from typing import Dict, List
import uuid
from src.retrieval.retriever_factory import RetrieverFactory
from src.memory.memory_manager import MemoryManager
from src.graph.query_rewriter import QueryRewriter
from src.qa.qa_chain import QAChain
from src.utils.logger import TraceLogger


class ThreadSession:
    """Manages a conversation session for a specific thread."""
    
    def __init__(self, thread_id: str, session_id: str = None):
        """
        Initialize thread session.
        
        Args:
            thread_id: Thread to search within
            session_id: Optional session identifier
        """
        self.thread_id = thread_id
        self.session_id = session_id or str(uuid.uuid4())[:8]  # Simple ID generation
        
        # Initialize components
        self.logger = TraceLogger(session_id=self.session_id)
        
        # Load retriever
        factory = RetrieverFactory()
        self.retriever = factory.load_hybrid_retriever(thread_id)
        
        # Initialize memory
        self.memory = MemoryManager(max_turns=5)
        
        # Initialize query rewriter
        self.query_rewriter = QueryRewriter()
        
        # Initialize QA chain
        self.qa_chain = QAChain()
        
        self.logger.log_info(f"Session initialized for thread {thread_id}")
    
    def ask(self, question: str, top_k: int = 5) -> Dict:
        """Ask a question with trace logging."""
        trace_id = str(uuid.uuid4())[:8]
        
        # Log initial query
        self.logger.log_trace("query_received", {
            "trace_id": trace_id,
            "question": question,
            "thread_id": self.thread_id,
            "top_k": top_k
        })
        
        # Get memory and rewrite
        memory_context = self.memory.get_context_for_rewrite()
        rewrite_result = self.query_rewriter.rewrite(question, memory_context)
        
        # Log rewrite
        self.logger.log_trace("query_rewritten", {
            "trace_id": trace_id,
            "original_query": question,
            "rewritten_query": rewrite_result['rewritten_query'],
            "reasoning": rewrite_result['reasoning']
        })
        
        # Retrieve
        retrieved_docs = self.retriever.retrieve(rewrite_result['rewritten_query'], top_k=top_k)
        
        # Log retrieval
        self.logger.log_trace("retrieval_complete", {
            "trace_id": trace_id,
            "num_docs": len(retrieved_docs),
            "top_chunks": [
                {
                    "chunk_id": doc.metadata.get('chunk_id'),
                    "message_id": doc.metadata.get('message_id'),
                    "score": float(score),
                    "doc_type": doc.metadata.get('doc_type')
                }
                for doc, score in retrieved_docs[:3]
            ]
        })
        
        # Generate answer
        qa_result = self.qa_chain.answer(rewrite_result['rewritten_query'], retrieved_docs)
        
        # Log answer generation
        self.logger.log_trace("answer_generated", {
            "trace_id": trace_id,
            "answer": qa_result['answer'],
            "num_citations": len(qa_result['citations']),
            "citations": qa_result['citations']
        })
        
        # Update memory
        self.memory.add_turn(question, qa_result['answer'])
        
        # Build response
        response = {
            'answer': qa_result['answer'],
            'citations': qa_result['citations'],
            'rewritten_query': rewrite_result['rewritten_query'],
            'rewrite_reasoning': rewrite_result['reasoning'],
            'retrieved_chunks': [
                {
                    'chunk_id': ctx['chunk_id'],
                    'message_id': ctx['message_id'],
                    'score': ctx['score']
                }
                for ctx in qa_result['context_used']
            ],
            'trace_id': trace_id,
            'thread_id': self.thread_id,
            'session_id': self.session_id
        }
        
        return response
    
    def reset(self):
        """Reset session memory."""
        self.memory.clear()
        self.logger.log_info("Session memory cleared")