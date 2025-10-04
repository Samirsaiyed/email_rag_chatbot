"""
Test the hybrid retrieval system.
"""
from src.retrieval.retriever_factory import RetrieverFactory
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="test_retrieval")

def main():
    """Test retrieval on a sample thread."""
    
    # Load retriever for the thread with attachments
    thread_id = "T-58ae003b"
    
    logger.log_info(f"Loading retriever for thread {thread_id}...")
    factory = RetrieverFactory()
    retriever = factory.load_hybrid_retriever(thread_id)
    
    logger.log_info("✓ Retriever loaded successfully")
    
    # Test queries
    test_queries = [
        "What is the budget amount?",
        "Who approved the storage vendor?",
        "What are the technical specifications?",
        "Compare the draft with final version",
        "When is the delivery date?"
    ]
    
    logger.log_info("\n" + "="*60)
    logger.log_info("Testing Hybrid Retrieval")
    logger.log_info("="*60)
    
    for query in test_queries:
        logger.log_info(f"\nQuery: {query}")
        logger.log_info("-" * 60)
        
        # Retrieve
        results = retriever.retrieve(query, top_k=3)
        
        logger.log_info(f"Retrieved {len(results)} chunks:")
        
        for i, (doc, score) in enumerate(results, 1):
            metadata = doc.metadata
            logger.log_info(f"\n  [{i}] Score: {score:.4f}")
            logger.log_info(f"      Chunk ID: {metadata.get('chunk_id')}")
            logger.log_info(f"      Message ID: {metadata.get('message_id')}")
            logger.log_info(f"      Doc Type: {metadata.get('doc_type')}")
            
            if metadata.get('page_no'):
                logger.log_info(f"      Page: {metadata.get('page_no')}")
            if metadata.get('filename'):
                logger.log_info(f"      File: {metadata.get('filename')}")
            
            # Show preview of content
            preview = doc.page_content[:150].replace('\n', ' ')
            logger.log_info(f"      Preview: {preview}...")
    
    logger.log_info("\n" + "="*60)
    logger.log_info("Retrieval Test Complete!")
    logger.log_info("="*60)

if __name__ == "__main__":
    main()