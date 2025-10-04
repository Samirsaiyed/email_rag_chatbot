"""
Link sample PDF attachments to specific emails in threads.
Since Enron CSV doesn't have real attachments, we'll manually map our mock PDFs.
"""
import json
from pathlib import Path
from src.config import THREADS_DIR, ATTACHMENTS_DIR
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="link_attachments")

def main():
    """Link attachments to specific emails."""
    
    # Load thread metadata to find suitable emails
    metadata_file = THREADS_DIR / "thread_metadata.json"
    with open(metadata_file, 'r') as f:
        thread_metadata = json.load(f)
    
    # We'll pick a thread that could plausibly have these attachments
    # Let's use the first thread for this demo
    target_thread_id = thread_metadata[0]['thread_id']
    
    # Load the thread emails
    thread_file = THREADS_DIR / f"{target_thread_id}.json"
    with open(thread_file, 'r') as f:
        emails = json.load(f)
    
    # Create attachment mapping
    # We'll attach our PDFs to specific messages in the thread
    attachment_links = [
        {
            "attachment_id": "A-budget-proposal",
            "filename": "Q2_Budget_Proposal.pdf",
            "thread_id": target_thread_id,
            "message_id": emails[5]['message_id'],  # 6th email in thread
            "description": "Q2 budget proposal with financial details"
        },
        {
            "attachment_id": "A-contract-draft",
            "filename": "Storage_Contract_Draft_v2.pdf",
            "thread_id": target_thread_id,
            "message_id": emails[8]['message_id'],  # 9th email
            "description": "Storage vendor contract draft"
        },
        {
            "attachment_id": "A-meeting-minutes",
            "filename": "IT_Meeting_Minutes_Apr2001.pdf",
            "thread_id": target_thread_id,
            "message_id": emails[3]['message_id'],  # 4th email
            "description": "IT meeting minutes discussing budget"
        },
        {
            "attachment_id": "A-vendor-comparison",
            "filename": "Vendor_Comparison_Analysis.pdf",
            "thread_id": target_thread_id,
            "message_id": emails[7]['message_id'],  # 8th email
            "description": "Vendor comparison analysis"
        },
        {
            "attachment_id": "A-technical-specs",
            "filename": "Storage_Technical_Specs.pdf",
            "thread_id": target_thread_id,
            "message_id": emails[9]['message_id'],  # 10th email
            "description": "Technical specifications for storage"
        }
    ]
    
    # Save the mapping
    mapping_file = ATTACHMENTS_DIR / "attachment_links.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(attachment_links, f, indent=2, ensure_ascii=False)
    
    logger.log_info(f"✓ Created attachment links for thread {target_thread_id}")
    logger.log_info(f"✓ Linked {len(attachment_links)} attachments to emails")
    logger.log_info(f"✓ Saved mapping to {mapping_file}")
    
    # Display the links
    for link in attachment_links:
        logger.log_info(f"\n  {link['filename']}")
        logger.log_info(f"    → Message: {link['message_id']}")
        logger.log_info(f"    → {link['description']}")

if __name__ == "__main__":
    main()