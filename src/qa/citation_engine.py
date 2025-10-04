"""
Citation injection for answers.
"""
from typing import List, Tuple, Dict
from langchain.schema import Document
import re


class CitationEngine:
    """Handles citation injection into answers."""
    
    @staticmethod
    def add_citations(
        answer: str,
        retrieved_docs: List[Tuple[Document, float]]
    ) -> Tuple[str, List[Dict]]:
        """
        Add citations to answer based on retrieved documents.
        
        Args:
            answer: Generated answer text
            retrieved_docs: List of (document, score) tuples
            
        Returns:
            Tuple of (answer_with_citations, citation_list)
        """
        if not retrieved_docs:
            return answer, []
        
        citations = []
        answer_with_citations = answer
        
        # Extract key facts from answer (sentences)
        sentences = re.split(r'[.!?]+', answer)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # For each sentence, find the most relevant document
        for i, sentence in enumerate(sentences):
            if len(sentence.split()) < 3:  # Skip very short sentences
                continue
            
            # Find best matching document
            best_doc = None
            best_score = -1
            
            for doc, score in retrieved_docs:
                # Simple matching: check if key words appear in doc
                words = set(sentence.lower().split())
                doc_words = set(doc.page_content.lower().split())
                
                overlap = len(words & doc_words)
                if overlap > best_score:
                    best_score = overlap
                    best_doc = doc
            
            if best_doc and best_score > 2:  # At least 3 word overlap
                # Create citation
                metadata = best_doc.metadata
                citation = CitationEngine._create_citation(metadata)
                
                # Add citation to answer
                if citation and citation not in answer_with_citations:
                    # Add citation after the sentence
                    answer_with_citations = answer_with_citations.replace(
                        sentence,
                        f"{sentence} {citation}",
                        1
                    )
                    
                    # Track citation
                    citations.append({
                        'type': metadata.get('doc_type', 'unknown'),
                        'message_id': metadata.get('message_id'),
                        'page': metadata.get('page_no'),
                        'filename': metadata.get('filename'),
                        'citation_text': citation
                    })
        
        return answer_with_citations, citations
    
    @staticmethod
    def _create_citation(metadata: Dict) -> str:
        """
        Create citation string from metadata.
        
        Args:
            metadata: Document metadata
            
        Returns:
            Citation string like [msg: M-abc123] or [msg: M-abc123, page: 2]
        """
        message_id = metadata.get('message_id')
        if not message_id:
            return ""
        
        # Check if it's from a PDF (has page number)
        page_no = metadata.get('page_no')
        
        if page_no:
            return f"[msg: {message_id}, page: {page_no}]"
        else:
            return f"[msg: {message_id}]"