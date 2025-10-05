"""
Re-index all threads that have attachments.
"""
from src.config import ATTACHMENTS_DIR
from src.ingestion.thread_builder import ThreadBuilder
from src.ingestion.indexer import Indexer
from src.utils.logger import TraceLogger
import json

logger = TraceLogger(session_id="reindex_all")

def main():
    """Re-index all threads with attachments."""
    
    # Load attachment links to find which threads have attachments
    links_file = ATTACHMENTS_DIR / "attachment_links.json"
    with open(links_file, 'r') as f:
        links = json.load(f)
    
    # Get unique thread IDs that have attachments
    thread_ids = sorted(list(set(link['thread_id'] for link in links)))
    
    logger.log_info(f"Re-indexing {len(thread_ids)} threads with attachments...")
    logger.log_info(f"Threads: {', '.join(thread_ids)}\n")
    
    builder = ThreadBuilder()
    indexer = Indexer()
    
    results = []
    
    for thread_id in thread_ids:
        logger.log_info(f"{'='*60}")
        logger.log_info(f"Processing {thread_id}...")
        
        # Count attachments for this thread
        thread_attachments = [l for l in links if l['thread_id'] == thread_id]
        logger.log_info(f"  Attachments: {len(thread_attachments)}")
        
        # Load thread emails
        thread_emails = builder.load_thread(thread_id)
        logger.log_info(f"  Emails: {len(thread_emails)}")
        
        # Re-index with attachments (will auto-load from attachment_links.json)
        indexer.index_thread(thread_id, thread_emails)
        
        # Store result
        results.append({
            'thread_id': thread_id,
            'emails': len(thread_emails),
            'attachments': len(thread_attachments)
        })
        
        logger.log_info(f"  Status: Indexed successfully\n")
    
    # Summary
    logger.log_info(f"{'='*60}")
    logger.log_info(f"SUMMARY")
    logger.log_info(f"{'='*60}")
    
    total_attachments = sum(r['attachments'] for r in results)
    total_emails = sum(r['emails'] for r in results)
    
    logger.log_info(f"\nThreads indexed: {len(results)}")
    logger.log_info(f"Total emails: {total_emails}")
    logger.log_info(f"Total attachments: {total_attachments}")
    
    logger.log_info(f"\nPer-thread breakdown:")
    for result in results:
        logger.log_info(f"  {result['thread_id']}: {result['emails']} emails, {result['attachments']} attachments")
    
    logger.log_info(f"\nAll threads re-indexed successfully!")

if __name__ == "__main__":
    main()