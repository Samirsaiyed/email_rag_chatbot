"""
QA chain using OpenAI.
"""
from typing import List, Tuple, Dict
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from .prompts import QA_SYSTEM_PROMPT
from .citation_engine import CitationEngine
from src.config import LLM_CONFIG
from dotenv import load_dotenv

load_dotenv()


class QAChain:
    """Question answering chain with OpenAI."""
    
    def __init__(self):
        """Initialize QA chain."""
        self.llm = ChatOpenAI(
            model=LLM_CONFIG.model_name,
            temperature=LLM_CONFIG.temperature,
            max_tokens=LLM_CONFIG.max_tokens,
            api_key=LLM_CONFIG.api_key
        )
        
        self.prompt = ChatPromptTemplate.from_template(QA_SYSTEM_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()
        self.citation_engine = CitationEngine()
    
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
        
        # Build context from top 3 docs
        context_parts = []
        for i, (doc, score) in enumerate(retrieved_docs[:3], 1):
            metadata = doc.metadata
            source = f"[Document {i}]"
            if metadata.get('filename'):
                source += f" {metadata['filename']}"
            if metadata.get('page_no'):
                source += f" (page {metadata['page_no']})"
            
            content = doc.page_content[:500]
            context_parts.append(f"{source}\n{content}\n")
        
        context = "\n".join(context_parts)
        
        try:
            # Generate answer
            raw_answer = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            raw_answer = raw_answer.strip()
            
            # Add citations
            answer_with_citations, citations = self.citation_engine.add_citations(
                raw_answer,
                retrieved_docs[:3]
            )
            
            return {
                'answer': answer_with_citations,
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
            print(f"OpenAI Error: {e}")
            return {
                'answer': f"Error generating answer: {str(e)}",
                'citations': [],
                'context_used': []
            }