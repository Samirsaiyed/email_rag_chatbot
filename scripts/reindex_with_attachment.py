"""
Re-index the thread that has attachments linked to it.
"""
from src.config import THREADS_DIR, ATTACHMENTS_DIR
from src.ingestion.thread_builder import ThreadBuilder
from src.ingestion.indexer import Indexer
from src.utils.logger import TraceLogger
import json

logger = TraceLogger(session_id="reindex")

def main():
    # Load attachment links to find which thread has attachments
    links_file = ATTACHMENTS_DIR / "attachment_links.json"
    with open(links_file, 'r') as f:
        links = json.load(f)
    
    if not links:
        logger.log_info("No attachment links found")
        return
    
    # Get the thread ID
    thread_id = links[0]['thread_id']
    
    logger.log_info(f"Re-indexing thread {thread_id} with attachments...")
    
    # Load thread emails
    builder = ThreadBuilder()
    thread_emails = builder.load_thread(thread_id)
    
    # Re-index with attachments
    indexer = Indexer()
    indexer.index_thread(thread_id, thread_emails)  # Will auto-load attachments
    
    logger.log_info("✓ Re-indexing complete!")

if __name__ == "__main__":
    main()