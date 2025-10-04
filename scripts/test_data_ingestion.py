"""
Test the ingestion pipeline step by step.
"""
from pathlib import Path
from src.config import RAW_DATA_DIR, THREADS_DIR, INDEXES_DIR
from src.ingestion.email_parser import EmailParser
from src.ingestion.thread_builder import ThreadBuilder
from src.ingestion.indexer import Indexer
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="test_ingestion")

def test_email_parsing():
    """Test email parsing."""
    logger.log_info("\n=== Testing Email Parsing ===")
    
    parser = EmailParser()
    emails = parser.parse_all_emails()
    
    if emails:
        logger.log_info(f"✓ Parsed {len(emails)} emails")
        logger.log_info(f"\nSample email:")
        sample = emails[0]
        logger.log_info(f"  ID: {sample['message_id']}")
        logger.log_info(f"  From: {sample['from']}")
        logger.log_info(f"  Subject: {sample['subject']}")
        logger.log_info(f"  Date: {sample['date']}")
        logger.log_info(f"  Body preview: {sample['body'][:100]}...")
        return emails
    else:
        logger.log_error("✗ No emails parsed")
        return None

def test_thread_building(emails):
    """Test thread building."""
    logger.log_info("\n=== Testing Thread Building ===")
    
    builder = ThreadBuilder()
    threads = builder.build_threads(emails)
    
    if threads:
        logger.log_info(f"✓ Built {len(threads)} threads")
        
        # Show first thread
        first_thread_id = list(threads.keys())[0]
        first_thread = threads[first_thread_id]
        
        logger.log_info(f"\nSample thread: {first_thread_id}")
        logger.log_info(f"  Messages: {len(first_thread)}")
        logger.log_info(f"  Subject: {first_thread[0]['subject']}")
        logger.log_info(f"  Date range: {first_thread[0]['date']} to {first_thread[-1]['date']}")
        
        return threads
    else:
        logger.log_error("✗ No threads built")
        return None

def test_indexing(threads):
    """Test indexing."""
    logger.log_info("\n=== Testing Indexing ===")
    
    indexer = Indexer()
    
    # Index first thread as test
    first_thread_id = list(threads.keys())[0]
    first_thread = threads[first_thread_id]
    
    logger.log_info(f"Indexing thread: {first_thread_id}")
    indexer.index_thread(first_thread_id, first_thread)
    
    # Try to load it back
    logger.log_info("Loading index back...")
    loaded = indexer.load_thread_index(first_thread_id)
    
    logger.log_info(f"✓ Index loaded successfully")
    logger.log_info(f"  Documents: {len(loaded['documents'])}")
    logger.log_info(f"  BM25 index: {'Present' if loaded['bm25_index'] else 'Missing'}")
    logger.log_info(f"  FAISS index: {'Present' if loaded['faiss_index'] else 'Missing'}")

def main():
    """Run all tests."""
    logger.log_info("Starting Ingestion Pipeline Tests")
    logger.log_info("=" * 60)
    
    # Test 1: Email Parsing
    emails = test_email_parsing()
    if not emails:
        logger.log_error("Cannot proceed without emails")
        return
    
    # Test 2: Thread Building
    threads = test_thread_building(emails)
    if not threads:
        logger.log_error("Cannot proceed without threads")
        return
    
    # Test 3: Indexing
    test_indexing(threads)
    
    logger.log_info("\n" + "=" * 60)
    logger.log_info("All Tests Completed!")

if __name__ == "__main__":
    main()