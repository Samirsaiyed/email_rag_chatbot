"""
Test the QA chain with retrieval.
"""
from src.retrieval.retriever_factory import RetrieverFactory
from src.qa.qa_chain import QAChain
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="test_qa")

def main():
    """Test QA chain."""
    
    logger.log_info("Testing QA Chain with Retrieval")
    logger.log_info("=" * 60)
    
    # Load retriever
    thread_id = "T-58ae003b"
    factory = RetrieverFactory()
    retriever = factory.load_hybrid_retriever(thread_id)
    
    # Create QA chain
    qa_chain = QAChain()
    
    # Test questions
    test_questions = [
        "What is the budget amount?",
        "Who needs to finalize the vendor contract?",
        "What are the technical specifications?"
    ]
    
    for question in test_questions:
        logger.log_info(f"\n{'='*60}")
        logger.log_info(f"Question: {question}")
        logger.log_info("-" * 60)
        
        # Retrieve
        docs = retriever.retrieve(question, top_k=5)
        
        # Generate answer
        result = qa_chain.answer(question, docs)
        
        logger.log_info(f"\n📝 Answer:\n{result['answer']}")
        
        logger.log_info(f"\n📚 Citations:")
        for citation in result['citations']:
            logger.log_info(f"  - {citation['citation_text']}")
            if citation.get('filename'):
                logger.log_info(f"    File: {citation['filename']}")
        
        logger.log_info(f"\n🔍 Context Used: {len(result['context_used'])} chunks")
    
    logger.log_info("\n" + "=" * 60)
    logger.log_info("QA Chain Test Complete!")

if __name__ == "__main__":
    main()