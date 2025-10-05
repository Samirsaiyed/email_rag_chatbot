"""
Re-process all attachments (PDF, DOCX, TXT, HTML).
"""
import json
from src.config import ATTACHMENTS_DIR
from src.ingestion.attachment_extractor import AttachmentExtractor
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="reprocess_attachments")

def main():
    logger.log_info("Re-processing all attachments...")
    
    # Process all attachments
    extractor = AttachmentExtractor()
    attachments_data = extractor.process_attachments_directory(ATTACHMENTS_DIR)
    
    logger.log_info(f"✓ Processed {len(attachments_data)} attachments")
    
    # Save metadata
    metadata_path = ATTACHMENTS_DIR / "attachment_metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(attachments_data, f, indent=2, ensure_ascii=False)
    
    logger.log_info(f"✓ Saved metadata to {metadata_path}")
    
    # Display results by type
    type_counts = {}
    for att in attachments_data:
        file_type = att['file_type']
        type_counts[file_type] = type_counts.get(file_type, 0) + 1
    
    logger.log_info("\nAttachments by type:")
    for file_type, count in sorted(type_counts.items()):
        logger.log_info(f"  {file_type.upper()}: {count} files")
    
    # Display individual files
    logger.log_info("\nProcessed files:")
    for att in attachments_data:
        logger.log_info(f"\n  {att['filename']}:")
        logger.log_info(f"    Type: {att['file_type']}")
        logger.log_info(f"    Pages/Sections: {att['page_count']}")

if __name__ == "__main__":
    main()