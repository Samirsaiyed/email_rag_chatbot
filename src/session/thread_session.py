"""
Thread session orchestrator - combines all components.
"""
from typing import Dict, List
import uuid
import time
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
        self.session_id = session_id or str(uuid.uuid4())[:8]
        
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
        """
        Ask a question with trace logging.
        
        Args:
            question: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with answer and metadata
        """
        trace_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Log initial query
        self.logger.log_trace("query_received", {
            "trace_id": trace_id,
            "question": question,
            "thread_id": self.thread_id,
            "top_k": top_k
        })
        
        self.logger.log_info(f"[{trace_id}] Processing question: {question}")
        
        # Step 1: Get memory context
        memory_context = self.memory.get_context_for_rewrite()
        
        # Step 2: Rewrite query using memory
        rewrite_start = time.time()
        rewrite_result = self.query_rewriter.rewrite(question, memory_context)
        rewrite_time = time.time() - rewrite_start
        rewritten_query = rewrite_result['rewritten_query']
        
        # Log rewrite
        self.logger.log_trace("query_rewritten", {
            "trace_id": trace_id,
            "original_query": question,
            "rewritten_query": rewritten_query,
            "reasoning": rewrite_result['reasoning'],
            "latency_ms": int(rewrite_time * 1000)
        })
        
        self.logger.log_info(f"[{trace_id}] Rewritten query: {rewritten_query}")
        self.logger.log_info(f"[{trace_id}] Reasoning: {rewrite_result['reasoning']}")
        
        # Step 3: Retrieve documents
        retrieval_start = time.time()
        retrieved_docs = self.retriever.retrieve(rewritten_query, top_k=top_k)
        retrieval_time = time.time() - retrieval_start
        
        # Log retrieval
        self.logger.log_trace("retrieval_complete", {
            "trace_id": trace_id,
            "num_docs_retrieved": len(retrieved_docs),
            "latency_ms": int(retrieval_time * 1000),
            "retrieved_chunks": [
                {
                    "chunk_id": doc.metadata.get('chunk_id'),
                    "message_id": doc.metadata.get('message_id'),
                    "doc_type": doc.metadata.get('doc_type'),
                    "filename": doc.metadata.get('filename'),
                    "score": float(score)
                }
                for doc, score in retrieved_docs[:top_k]
            ]
        })
        
        self.logger.log_info(f"[{trace_id}] Retrieved {len(retrieved_docs)} documents")
        
        # Step 4: Generate answer
        qa_start = time.time()
        qa_result = self.qa_chain.answer(rewritten_query, retrieved_docs)
        qa_time = time.time() - qa_start
        
        # Log answer generation
        self.logger.log_trace("answer_generated", {
            "trace_id": trace_id,
            "answer": qa_result['answer'],
            "num_citations": len(qa_result['citations']),
            "citations": qa_result['citations'],
            "context_chunks_used": len(qa_result['context_used']),
            "latency_ms": int(qa_time * 1000)
        })
        
        self.logger.log_info(f"[{trace_id}] Generated answer with {len(qa_result['citations'])} citations")
        
        # Step 5: Update memory
        self.memory.add_turn(question, qa_result['answer'])
        
        # Calculate total time
        total_time = time.time() - start_time
        
        # Log completion
        self.logger.log_trace("turn_complete", {
            "trace_id": trace_id,
            "total_latency_ms": int(total_time * 1000),
            "breakdown": {
                "rewrite_ms": int(rewrite_time * 1000),
                "retrieval_ms": int(retrieval_time * 1000),
                "qa_ms": int(qa_time * 1000)
            }
        })
        
        # Build response
        response = {
            'answer': qa_result['answer'],
            'citations': qa_result['citations'],
            'rewritten_query': rewritten_query,
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
        self.logger.log_trace("memory_reset", {
            "session_id": self.session_id,
            "thread_id": self.thread_id
        })