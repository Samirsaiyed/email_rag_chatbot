"""
Re-process attachments only (after fixing PDF extraction).
"""
import json
from src.config import ATTACHMENTS_DIR
from src.ingestion.attachment_extractor import AttachmentExtractor
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="reprocess_attachments")

def main():
    logger.log_info("Re-processing attachments...")
    
    # Process attachments
    extractor = AttachmentExtractor()
    attachments_path = ATTACHMENTS_DIR / "pdfs"
    
    if attachments_path.exists():
        attachments_data = extractor.process_attachments_directory(attachments_path)
        logger.log_info(f"✓ Processed {len(attachments_data)} attachments")
        
        # Save metadata
        metadata_path = ATTACHMENTS_DIR / "attachment_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(attachments_data, f, indent=2, ensure_ascii=False)
        
        logger.log_info(f"✓ Saved metadata to {metadata_path}")
        
        # Display results
        for att in attachments_data:
            logger.log_info(f"\n  {att['filename']}:")
            logger.log_info(f"    Pages: {att['page_count']}")
            logger.log_info(f"    Type: {att['file_type']}")
    else:
        logger.log_info(f"No attachments directory found at {attachments_path}")

if __name__ == "__main__":
    main()