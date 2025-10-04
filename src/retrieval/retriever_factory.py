"""
Factory for loading retriever for a specific thread.
"""
from typing import Optional
from pathlib import Path
from .bm25_retriever import BM25Retriever
from .vector_retriever import VectorRetriever
from .hybrid_retriever import HybridRetriever
from src.ingestion.indexer import Indexer
from src.config import RETRIEVAL_CONFIG


class RetrieverFactory:
    """Factory for creating retrievers."""
    
    def __init__(self):
        """Initialize retriever factory."""
        self.indexer = Indexer()
    
    def load_hybrid_retriever(
        self,
        thread_id: str,
        bm25_weight: Optional[float] = None,
        vector_weight: Optional[float] = None
    ) -> HybridRetriever:
        """
        Load hybrid retriever for a thread.
        
        Args:
            thread_id: Thread identifier
            bm25_weight: BM25 weight (defaults to config)
            vector_weight: Vector weight (defaults to config)
            
        Returns:
            HybridRetriever instance
        """
        # Load indexes and documents
        index_data = self.indexer.load_thread_index(thread_id)
        
        # Create individual retrievers
        bm25_retriever = BM25Retriever(
            bm25_index=index_data['bm25_index'],
            documents=index_data['documents']
        )
        
        vector_retriever = VectorRetriever(
            faiss_index=index_data['faiss_index']
        )
        
        # Create hybrid retriever
        hybrid_retriever = HybridRetriever(
            bm25_retriever=bm25_retriever,
            vector_retriever=vector_retriever,
            bm25_weight=bm25_weight or RETRIEVAL_CONFIG.bm25_weight,
            vector_weight=vector_weight or RETRIEVAL_CONFIG.vector_weight
        )
        
        return hybrid_retriever