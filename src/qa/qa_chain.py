"""
QA chain - supports both Ollama and OpenAI with inline citations.
"""
from typing import List, Tuple, Dict
from langchain.schema import Document
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .prompts import QA_SYSTEM_PROMPT
from src.config import LLM_CONFIG
import re


class QAChain:
    """Question answering chain with LLM support."""
    
    def __init__(self):
        """Initialize QA chain with LLM (Ollama or OpenAI)."""
        
        if LLM_CONFIG.use_ollama:
            # Use Ollama (open-source, local)
            self.llm = Ollama(
                model=LLM_CONFIG.ollama_model,
                base_url=LLM_CONFIG.ollama_base_url,
                temperature=LLM_CONFIG.temperature,
            )
            # Use PromptTemplate for Ollama
            self.prompt = PromptTemplate.from_template(QA_SYSTEM_PROMPT)
        else:
            # Use OpenAI
            self.llm = ChatOpenAI(
                model=LLM_CONFIG.model_name,
                temperature=LLM_CONFIG.temperature,
                max_tokens=LLM_CONFIG.max_tokens,
                api_key=LLM_CONFIG.api_key
            )
            # Use ChatPromptTemplate for OpenAI
            self.prompt = ChatPromptTemplate.from_template(QA_SYSTEM_PROMPT)
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def answer(
        self,
        question: str,
        retrieved_docs: List[Tuple[Document, float]]
    ) -> Dict:
        """Generate answer with citations."""
        
        if not retrieved_docs:
            return {
                'answer': "I don't have enough information to answer that question.",
                'citations': [],
                'context_used': []
            }
        
        # Build context with clear source attribution
        context_parts = []
        for i, (doc, score) in enumerate(retrieved_docs[:3], 1):
            metadata = doc.metadata
            
            # Format: [Document N] Message: M-xxx, File: name.pdf, Page: N
            source_line = f"[Document {i}] Message: {metadata.get('message_id', 'unknown')}"
            
            if metadata.get('filename'):
                source_line += f", File: {metadata['filename']}"
            if metadata.get('page_no'):
                source_line += f", Page: {metadata['page_no']}"
            
            content = doc.page_content[:500]
            context_parts.append(f"{source_line}\n{content}\n")
        
        context = "\n".join(context_parts)
        
        try:
            # Generate answer with citations
            raw_answer = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            raw_answer = raw_answer.strip()
            
            # Extract citations
            citations = self._extract_citations(raw_answer, retrieved_docs)
            
            return {
                'answer': raw_answer,
                'raw_answer': raw_answer,
                'citations': citations,
                'context_used': [
                    {
                        'chunk_id': doc.metadata.get('chunk_id'),
                        'message_id': doc.metadata.get('message_id'),
                        'score': float(score)
                    }
                    for doc, score in retrieved_docs[:3]
                ]
            }
        
        except Exception as e:
            print(f"LLM Error: {e}")
            return {
                'answer': f"Error generating answer: {str(e)}",
                'citations': [],
                'context_used': []
            }
    
    def _extract_citations(self, answer: str, retrieved_docs: List[Tuple[Document, float]]) -> List[Dict]:
        """Extract citations from answer text."""
        citations = []
        
        # Pattern: [msg: M-xxxxx] or [msg: M-xxxxx, page: N]
        pattern = r'\[msg:\s*([M\-a-f0-9]+)(?:,\s*page:\s*(\d+))?\]'
        matches = re.findall(pattern, answer)
        
        for message_id, page_num in matches:
            # Find the document this citation refers to
            for doc, _ in retrieved_docs:
                metadata = doc.metadata
                if metadata.get('message_id') == message_id:
                    citation = {
                        'type': metadata.get('doc_type', 'unknown'),
                        'message_id': message_id,
                        'page': int(page_num) if page_num else None,
                        'filename': metadata.get('filename'),
                        'citation_text': f"[msg: {message_id}" + (f", page: {page_num}]" if page_num else "]")
                    }
                    citations.append(citation)
                    break
        
        return citations