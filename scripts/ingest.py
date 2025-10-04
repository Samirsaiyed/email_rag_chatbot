"""
Main data ingestion pipeline.
Parses emails, builds threads, extracts attachments, and creates indexes.
"""
import json
from pathlib import Path
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, ATTACHMENTS_DIR
from src.ingestion.email_parser import EmailParser
from src.ingestion.thread_builder import ThreadBuilder
from src.ingestion.attachment_extractor import AttachmentExtractor
from src.ingestion.indexer import Indexer
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")

def main():
    """Run the complete ingestion pipeline."""
    
    logger.log_info("=" * 60)
    logger.log_info("Starting Email RAG Ingestion Pipeline")
    logger.log_info("=" * 60)
    
    # Step 1: Parse emails from CSV
    logger.log_info("\n[Step 1] Parsing emails from CSV...")
    email_parser = EmailParser()
    parsed_emails = email_parser.parse_all_emails()
    
    if not parsed_emails:
        logger.log_error("No emails parsed. Check your CSV file and date range.")
        return
    
    logger.log_info(f"✓ Parsed {len(parsed_emails)} emails")
    
    # Step 2: Build threads
    logger.log_info("\n[Step 2] Building email threads...")
    thread_builder = ThreadBuilder()
    threads = thread_builder.build_threads(parsed_emails)
    
    if not threads:
        logger.log_error("No threads created. Adjust filtering criteria.")
        return
    
    logger.log_info(f"✓ Created {len(threads)} threads")
    
    # Save threads to disk
    thread_builder.save_threads()
    logger.log_info("✓ Saved threads to disk")
    
    # Step 3: Process attachments (if any)
    logger.log_info("\n[Step 3] Processing attachments...")
    attachment_extractor = AttachmentExtractor()
    
    # Check if attachments directory exists
    attachments_path = ATTACHMENTS_DIR / "pdfs"
    attachments_data = []
    
    if attachments_path.exists():
        attachments_data = attachment_extractor.process_attachments_directory(attachments_path)
        logger.log_info(f"✓ Processed {len(attachments_data)} attachments")
        
        # Save attachment metadata
        attachment_metadata_path = ATTACHMENTS_DIR / "attachment_metadata.json"
        with open(attachment_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(attachments_data, f, indent=2, ensure_ascii=False)
    else:
        logger.log_info("⚠ No attachments directory found. Skipping attachments.")
        logger.log_info(f"  Create directory: {attachments_path}")
        logger.log_info("  And add PDF/DOCX files there if needed.")
    
    # Step 4: Build indexes for each thread
    logger.log_info("\n[Step 4] Building indexes for threads...")
    indexer = Indexer()
    
    for thread_id, thread_emails in threads.items():
        logger.log_info(f"\nIndexing thread: {thread_id}")
        logger.log_info(f"  Messages: {len(thread_emails)}")
        
        # Filter attachments for this thread (if any)
        thread_attachments = []
        # Note: You'll need to link attachments to messages
        # For now, we'll skip this if no linking info available
        
        # Build indexes
        indexer.index_thread(thread_id, thread_emails, thread_attachments)
    
    logger.log_info("\n" + "=" * 60)
    logger.log_info("Ingestion Pipeline Completed Successfully!")
    logger.log_info("=" * 60)
    
    # Print summary
    logger.log_info("\n📊 SUMMARY:")
    logger.log_info(f"  • Total emails parsed: {len(parsed_emails)}")
    logger.log_info(f"  • Total threads created: {len(threads)}")
    logger.log_info(f"  • Total attachments processed: {len(attachments_data)}")
    logger.log_info(f"\n📁 Output locations:")
    logger.log_info(f"  • Threads: {PROCESSED_DATA_DIR / 'threads'}")
    logger.log_info(f"  • Indexes: {PROCESSED_DATA_DIR.parent / 'indexes'}")
    
    # Print thread details
    logger.log_info("\n📋 Thread Details:")
    for meta in thread_builder.thread_metadata:
        logger.log_info(f"\n  Thread: {meta['thread_id']}")
        logger.log_info(f"    Subject: {meta['subject']}")
        logger.log_info(f"    Messages: {meta['message_count']}")
        logger.log_info(f"    Date range: {meta['start_date']} to {meta['end_date']}")
        logger.log_info(f"    Participants: {len(meta['participants'])}")

if __name__ == "__main__":
    main()