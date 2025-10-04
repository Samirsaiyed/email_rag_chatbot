"""
BM25 keyword-based retriever.
"""
from typing import List, Tuple
from langchain.schema import Document
from rank_bm25 import BM25Okapi


class BM25Retriever:
    """BM25-based keyword retriever."""
    
    def __init__(self, bm25_index: BM25Okapi, documents: List[Document]):
        """
        Initialize BM25 retriever.
        
        Args:
            bm25_index: Pre-built BM25 index
            documents: List of documents (for retrieving by index)
        """
        self.bm25_index = bm25_index
        self.documents = documents
    
    def retrieve(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """
        Retrieve documents using BM25.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            
        Returns:
            List of (document, score) tuples
        """
        # Tokenize query (simple whitespace tokenization)
        tokenized_query = query.lower().split()
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(tokenized_query)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]
        
        # Return documents with scores
        results = [
            (self.documents[idx], float(scores[idx]))
            for idx in top_indices
        ]
        
        return results