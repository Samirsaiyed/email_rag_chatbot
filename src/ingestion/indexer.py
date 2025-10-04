"""
Build BM25 and FAISS indexes for each thread.
"""
import pickle
import json
from pathlib import Path
from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi
import numpy as np

from src.config import INDEXES_DIR, RETRIEVAL_CONFIG, MODEL_CONFIG
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")

class Indexer:
    """Build and save BM25 and FAISS indexes for threads."""
    
    def __init__(self):
        """Initialize indexer."""
        self.email_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Keep full emails mostly intact
            chunk_overlap=0,
            separators=["\n\n", "\n"]
        )
        
        self.attachment_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RETRIEVAL_CONFIG.chunk_size,
            chunk_overlap=RETRIEVAL_CONFIG.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Initialize embeddings model
        logger.log_info(f"Loading embeddings model: {MODEL_CONFIG.embedding_model}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=MODEL_CONFIG.embedding_model,
            model_kwargs={'device': MODEL_CONFIG.device}
        )
    
    def create_chunks(self, thread_emails: List[Dict], 
                     attachments: List[Dict] = None) -> List[Document]:
        """
        Create chunks from emails and attachments.
        
        Args:
            thread_emails: List of emails in thread
            attachments: List of attachment data (optional)
            
        Returns:
            List of LangChain Document objects
        """
        documents = []
        
        # Process emails
        for email in thread_emails:
            # Create document for email body
            email_text = f"Subject: {email.get('subject', '')}\n\n{email.get('body', '')}"
            
            # For emails, we typically keep them as single chunks
            # unless they're very long
            chunks = self.email_splitter.split_text(email_text)
            
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        'chunk_id': f"{email['message_id']}_chunk_{i}",
                        'thread_id': email.get('thread_id'),
                        'message_id': email['message_id'],
                        'doc_type': 'email',
                        'date': email.get('date'),
                        'from': email.get('from'),
                        'subject': email.get('subject')
                    }
                )
                documents.append(doc)
        
        # Process attachments if provided
        if attachments:
            for attachment in attachments:
                attachment_id = attachment['attachment_id']
                message_id = attachment.get('message_id', 'unknown')
                
                for page_data in attachment['pages']:
                    page_no = page_data['page_no']
                    page_text = page_data['text']
                    
                    # Split page into chunks
                    chunks = self.attachment_splitter.split_text(page_text)
                    
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                'chunk_id': f"{attachment_id}_p{page_no}_chunk_{i}",
                                'thread_id': thread_emails[0].get('thread_id'),
                                'message_id': message_id,
                                'attachment_id': attachment_id,
                                'doc_type': attachment['file_type'],
                                'filename': attachment['filename'],
                                'page_no': page_no
                            }
                        )
                        documents.append(doc)
        
        logger.log_info(f"Created {len(documents)} chunks")
        return documents
    
    def build_bm25_index(self, documents: List[Document]) -> BM25Okapi:
        """
        Build BM25 index from documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            BM25Okapi index
        """
        logger.log_info("Building BM25 index...")
        
        # Tokenize documents (simple whitespace tokenization)
        tokenized_docs = [doc.page_content.lower().split() for doc in documents]
        
        # Create BM25 index
        bm25_index = BM25Okapi(tokenized_docs)
        
        logger.log_info("BM25 index built successfully")
        return bm25_index
    
    def build_faiss_index(self, documents: List[Document]) -> FAISS:
        """
        Build FAISS vector index from documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            FAISS vector store
        """
        logger.log_info("Building FAISS index...")
        
        # Create FAISS index using LangChain
        vectorstore = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        logger.log_info("FAISS index built successfully")
        return vectorstore
    
    def save_thread_index(self, thread_id: str, documents: List[Document],
                         bm25_index: BM25Okapi, faiss_index: FAISS):
        """
        Save indexes and metadata for a thread.
        
        Args:
            thread_id: Thread identifier
            documents: List of documents
            bm25_index: BM25 index
            faiss_index: FAISS index
        """
        # Create thread index directory
        thread_index_dir = INDEXES_DIR / thread_id
        thread_index_dir.mkdir(parents=True, exist_ok=True)
        
        # Save BM25 index
        bm25_path = thread_index_dir / "bm25_index.pkl"
        with open(bm25_path, 'wb') as f:
            pickle.dump(bm25_index, f)
        
        # Save FAISS index
        faiss_dir = thread_index_dir / "faiss_index"
        faiss_index.save_local(str(faiss_dir))
        
        # Save document metadata (for retrieval reference)
        docs_metadata = []
        for doc in documents:
            docs_metadata.append({
                'chunk_id': doc.metadata.get('chunk_id'),
                'text_preview': doc.page_content[:200],  # Preview only
                'metadata': doc.metadata
            })
        
        metadata_path = thread_index_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                'thread_id': thread_id,
                'chunk_count': len(documents),
                'chunks': docs_metadata
            }, f, indent=2, ensure_ascii=False)
        
        # Save full documents for retrieval
        docs_path = thread_index_dir / "documents.pkl"
        with open(docs_path, 'wb') as f:
            pickle.dump(documents, f)
        
        logger.log_info(f"Saved indexes for thread {thread_id} to {thread_index_dir}")
    
    def index_thread(self, thread_id: str, thread_emails: List[Dict],
                    attachments: List[Dict] = None):
        """
        Build and save all indexes for a thread.
        
        Args:
            thread_id: Thread identifier
            thread_emails: List of emails in thread
            attachments: List of attachments (optional)
        """
        logger.log_info(f"Indexing thread {thread_id}...")
        
        # Create chunks
        documents = self.create_chunks(thread_emails, attachments)
        
        if not documents:
            logger.log_info(f"No documents to index for thread {thread_id}")
            return
        
        # Build indexes
        bm25_index = self.build_bm25_index(documents)
        faiss_index = self.build_faiss_index(documents)
        
        # Save everything
        self.save_thread_index(thread_id, documents, bm25_index, faiss_index)
        
        logger.log_info(f"Successfully indexed thread {thread_id}")
    
    def load_thread_index(self, thread_id: str) -> Dict:
        """
        Load indexes for a thread.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            Dictionary containing indexes and documents
        """
        thread_index_dir = INDEXES_DIR / thread_id
        
        if not thread_index_dir.exists():
            raise FileNotFoundError(f"Index for thread {thread_id} not found")
        
        # Load BM25 index
        bm25_path = thread_index_dir / "bm25_index.pkl"
        with open(bm25_path, 'rb') as f:
            bm25_index = pickle.load(f)
        
        # Load FAISS index
        faiss_dir = thread_index_dir / "faiss_index"
        faiss_index = FAISS.load_local(
            str(faiss_dir),
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Load documents
        docs_path = thread_index_dir / "documents.pkl"
        with open(docs_path, 'rb') as f:
            documents = pickle.load(f)
        
        # Load metadata
        metadata_path = thread_index_dir / "metadata.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return {
            'bm25_index': bm25_index,
            'faiss_index': faiss_index,
            'documents': documents,
            'metadata': metadata
        }