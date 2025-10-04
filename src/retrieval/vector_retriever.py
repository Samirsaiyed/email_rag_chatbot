"""
FAISS vector-based retriever.
"""
from typing import List, Tuple
from langchain.schema import Document
from langchain_community.vectorstores import FAISS


class VectorRetriever:
    """FAISS-based semantic retriever."""
    
    def __init__(self, faiss_index: FAISS):
        """
        Initialize vector retriever.
        
        Args:
            faiss_index: Pre-built FAISS vector store
        """
        self.faiss_index = faiss_index
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """
        Retrieve documents using vector similarity.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of (document, score) tuples
        """
        # Use FAISS similarity search with scores
        results = self.faiss_index.similarity_search_with_score(
            query,
            k=top_k
        )
        
        # FAISS returns (document, distance), we want (document, similarity score)
        # Convert distance to similarity: lower distance = higher similarity
        # Using negative distance as score (higher is better)
        results_with_similarity = [
            (doc, -float(distance))  # Negate distance to get similarity
            for doc, distance in results
        ]
        
        return results_with_similarity