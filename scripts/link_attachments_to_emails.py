"""
Link PDF, DOCX, and TXT attachments to emails across multiple threads.
"""
import json
from pathlib import Path
from src.config import THREADS_DIR, ATTACHMENTS_DIR
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="link_attachments")

def main():
    """Link all attachments to emails across 4 threads."""
    
    # Load thread metadata
    metadata_file = THREADS_DIR / "thread_metadata.json"
    with open(metadata_file, 'r') as f:
        thread_metadata = json.load(f)
    
    # Create comprehensive mapping
    attachment_links = []
    
    # === Thread T-58ae003b: Storage/Budget (6 attachments) ===
    with open(THREADS_DIR / 'T-58ae003b.json', 'r') as f:
        emails_58ae = json.load(f)
    
    attachment_links.extend([
        {
            "attachment_id": "A-budget-proposal",
            "filename": "Q2_Budget_Proposal.pdf",
            "thread_id": "T-58ae003b",
            "message_id": emails_58ae[5]['message_id'],
            "description": "Q2 budget proposal with financial details"
        },
        {
            "attachment_id": "A-contract-draft",
            "filename": "Storage_Contract_Draft_v2.pdf",
            "thread_id": "T-58ae003b",
            "message_id": emails_58ae[8]['message_id'],
            "description": "Storage vendor contract draft"
        },
        {
            "attachment_id": "A-meeting-minutes",
            "filename": "IT_Meeting_Minutes_Apr2001.pdf",
            "thread_id": "T-58ae003b",
            "message_id": emails_58ae[3]['message_id'],
            "description": "IT meeting minutes"
        },
        {
            "attachment_id": "A-vendor-comparison",
            "filename": "Vendor_Comparison_Analysis.pdf",
            "thread_id": "T-58ae003b",
            "message_id": emails_58ae[7]['message_id'],
            "description": "Vendor comparison analysis"
        },
        {
            "attachment_id": "A-technical-specs",
            "filename": "Storage_Technical_Specs.pdf",
            "thread_id": "T-58ae003b",
            "message_id": emails_58ae[9]['message_id'],
            "description": "Technical specifications"
        },
        {
            "attachment_id": "A-storage-notes",
            "filename": "Storage_Upgrade_Notes.docx",
            "thread_id": "T-58ae003b",
            "message_id": emails_58ae[4]['message_id'],
            "description": "Internal notes on storage upgrade"
        }
    ])
    
    # === Thread T-3df8a268: Axia Energy (4 attachments) ===
    with open(THREADS_DIR / 'T-3df8a268.json', 'r') as f:
        emails_3df8 = json.load(f)
    
    attachment_links.extend([
        {
            "attachment_id": "A-axia-agreement",
            "filename": "Axia_Energy_Partnership_Agreement.pdf",
            "thread_id": "T-3df8a268",
            "message_id": emails_3df8[10]['message_id'],
            "description": "Axia Energy partnership agreement"
        },
        {
            "attachment_id": "A-axia-credit",
            "filename": "Axia_Credit_Analysis.pdf",
            "thread_id": "T-3df8a268",
            "message_id": emails_3df8[6]['message_id'],
            "description": "Credit analysis for Axia Energy"
        },
        {
            "attachment_id": "A-axia-negotiation",
            "filename": "Axia_Negotiation_Notes.docx",
            "thread_id": "T-3df8a268",
            "message_id": emails_3df8[8]['message_id'],
            "description": "Negotiation summary notes"
        },
        {
            "attachment_id": "A-axia-email",
            "filename": "Axia_Email_Forward.txt",
            "thread_id": "T-3df8a268",
            "message_id": emails_3df8[2]['message_id'],
            "description": "Forwarded email from Axia"
        }
    ])
    
    # === Thread T-8b62a250: El Paso Electric (3 attachments) ===
    with open(THREADS_DIR / 'T-8b62a250.json', 'r') as f:
        emails_8b62 = json.load(f)
    
    attachment_links.extend([
        {
            "attachment_id": "A-elpaso-ppa",
            "filename": "El_Paso_Power_Purchase_Agreement.pdf",
            "thread_id": "T-8b62a250",
            "message_id": emails_8b62[11]['message_id'],
            "description": "Power purchase agreement"
        },
        {
            "attachment_id": "A-elpaso-forecast",
            "filename": "El_Paso_Load_Forecast.pdf",
            "thread_id": "T-8b62a250",
            "message_id": emails_8b62[7]['message_id'],
            "description": "Load forecast analysis"
        },
        {
            "attachment_id": "A-elpaso-pricing",
            "filename": "El_Paso_Pricing_Discussion.txt",
            "thread_id": "T-8b62a250",
            "message_id": emails_8b62[9]['message_id'],
            "description": "Pricing strategy memo"
        }
    ])
    
    # === Thread T-a5f23567: PG&E (3 attachments) ===
    with open(THREADS_DIR / 'T-a5f23567.json', 'r') as f:
        emails_a5f2 = json.load(f)
    
    attachment_links.extend([
        {
            "attachment_id": "A-pge-crisis",
            "filename": "PGE_California_Crisis_Memo.pdf",
            "thread_id": "T-a5f23567",
            "message_id": emails_a5f2[12]['message_id'],
            "description": "PG&E crisis memo"
        },
        {
            "attachment_id": "A-pge-risk",
            "filename": "PGE_Risk_Mitigation_Strategy.pdf",
            "thread_id": "T-a5f23567",
            "message_id": emails_a5f2[15]['message_id'],
            "description": "Risk mitigation strategy"
        },
        {
            "attachment_id": "A-pge-timeline",
            "filename": "PGE_Crisis_Timeline.docx",
            "thread_id": "T-a5f23567",
            "message_id": emails_a5f2[10]['message_id'],
            "description": "Crisis timeline document"
        }
    ])
    
    # Save the mapping
    mapping_file = ATTACHMENTS_DIR / "attachment_links.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(attachment_links, f, indent=2, ensure_ascii=False)
    
    logger.log_info(f"✓ Created attachment links for 4 threads")
    logger.log_info(f"✓ Linked {len(attachment_links)} attachments total")
    logger.log_info(f"✓ Saved mapping to {mapping_file}")
    
    # Display summary by thread
    thread_counts = {}
    for link in attachment_links:
        tid = link['thread_id']
        thread_counts[tid] = thread_counts.get(tid, 0) + 1
    
    logger.log_info(f"\n📎 Attachment distribution:")
    for tid, count in sorted(thread_counts.items()):
        logger.log_info(f"  {tid}: {count} attachments")
    
    # Display by file type
    type_counts = {'pdf': 0, 'docx': 0, 'txt': 0}
    for link in attachment_links:
        fname = link['filename']
        if fname.endswith('.pdf'):
            type_counts['pdf'] += 1
        elif fname.endswith('.docx'):
            type_counts['docx'] += 1
        elif fname.endswith('.txt'):
            type_counts['txt'] += 1
    
    logger.log_info(f"\n📄 By file type:")
    logger.log_info(f"  PDF: {type_counts['pdf']}")
    logger.log_info(f"  DOCX: {type_counts['docx']}")
    logger.log_info(f"  TXT: {type_counts['txt']}")

if __name__ == "__main__":
    main()