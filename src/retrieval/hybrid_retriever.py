"""
Hybrid retriever combining BM25 and vector search with Reciprocal Rank Fusion.
"""
from typing import List, Tuple, Dict
from langchain.schema import Document
from .bm25_retriever import BM25Retriever
from .vector_retriever import VectorRetriever


class HybridRetriever:
    """Hybrid retriever using BM25 + Vector search with RRF fusion."""
    
    def __init__(
        self,
        bm25_retriever: BM25Retriever,
        vector_retriever: VectorRetriever,
        bm25_weight: float = 0.5,
        vector_weight: float = 0.5,
        k: int = 60  # RRF constant
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            bm25_retriever: BM25 retriever instance
            vector_retriever: Vector retriever instance
            bm25_weight: Weight for BM25 scores (0-1)
            vector_weight: Weight for vector scores (0-1)
            k: RRF constant (typical value: 60)
        """
        self.bm25_retriever = bm25_retriever
        self.vector_retriever = vector_retriever
        self.bm25_weight = bm25_weight
        self.vector_weight = vector_weight
        self.k = k
    
    def _reciprocal_rank_fusion(
        self,
        bm25_results: List[Tuple[Document, float]],
        vector_results: List[Tuple[Document, float]]
    ) -> List[Tuple[Document, float]]:
        """
        Combine results using Reciprocal Rank Fusion.
        
        RRF formula: score(d) = sum(1 / (k + rank(d)))
        
        Args:
            bm25_results: BM25 retrieval results
            vector_results: Vector retrieval results
            
        Returns:
            Fused and re-ranked results
        """
        # Create document ID to score mapping
        doc_scores: Dict[str, float] = {}
        doc_objects: Dict[str, Document] = {}
        
        # Process BM25 results
        for rank, (doc, _) in enumerate(bm25_results, start=1):
            doc_id = doc.metadata.get('chunk_id', id(doc))
            rrf_score = self.bm25_weight / (self.k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            doc_objects[doc_id] = doc
        
        # Process vector results
        for rank, (doc, _) in enumerate(vector_results, start=1):
            doc_id = doc.metadata.get('chunk_id', id(doc))
            rrf_score = self.vector_weight / (self.k + rank)
            doc_scores[doc_id] = doc_scores.get(doc_id, 0) + rrf_score
            doc_objects[doc_id] = doc
        
        # Sort by combined score
        sorted_docs = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return documents with scores
        return [
            (doc_objects[doc_id], score)
            for doc_id, score in sorted_docs
        ]
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """
        Retrieve documents using hybrid search.
        
        Args:
            query: Search query
            top_k: Number of final documents to return
            
        Returns:
            List of (document, score) tuples, sorted by fused score
        """
        # Retrieve from both sources (get more initially for better fusion)
        retrieval_k = top_k * 2  # Retrieve 2x documents from each source
        
        bm25_results = self.bm25_retriever.retrieve(query, top_k=retrieval_k)
        vector_results = self.vector_retriever.retrieve(query, top_k=retrieval_k)
        
        # Fuse results
        fused_results = self._reciprocal_rank_fusion(bm25_results, vector_results)
        
        # Return top-k
        return fused_results[:top_k]