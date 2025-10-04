"""
Create sample PDF attachments for testing.
"""
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from src.config import ATTACHMENTS_DIR
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")

def create_sample_pdf(filename: str, content: list, output_dir: Path):
    """
    Create a simple PDF with given content.
    
    Args:
        filename: Name of PDF file
        content: List of tuples (page_number, text_content)
        output_dir: Output directory
    """
    pdf_path = output_dir / filename
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    
    for page_num, text in content:
        # Add title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"Page {page_num}")
        
        # Add content
        c.setFont("Helvetica", 12)
        
        # Split text into lines
        lines = text.split('\n')
        y_position = 700
        
        for line in lines:
            if y_position < 50:  # Start new page if needed
                c.showPage()
                c.setFont("Helvetica", 12)
                y_position = 750
            
            c.drawString(50, y_position, line[:80])  # Max 80 chars per line
            y_position -= 20
        
        c.showPage()
    
    c.save()
    logger.log_info(f"Created PDF: {filename}")

def main():
    """Create sample attachments."""
    
    # Create output directory
    output_dir = ATTACHMENTS_DIR / "pdfs"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.log_info(f"Creating sample attachments in {output_dir}")
    
    # Sample 1: Budget Proposal
    create_sample_pdf(
        "Q2_Budget_Proposal.pdf",
        [
            (1, """Q2 2001 Budget Proposal
            
Department: IT Infrastructure
Submitted by: John Doe
Date: April 15, 2001

Summary:
This document outlines the proposed budget for Q2 2001.
Total requested amount: $45,000

Breakdown:
- Storage vendor upgrade: $25,000
- Network equipment: $15,000
- Software licenses: $5,000
            """),
            (2, """Detailed Justification:

Storage Vendor Upgrade ($25,000):
The current storage system is reaching capacity.
We need to upgrade to ensure business continuity.
Vendor: StorageTech Solutions
Expected delivery: May 2001

Network Equipment ($15,000):
Replacement of aging switches in Building A.
Will improve network reliability and speed.

Software Licenses ($5,000):
Annual renewals for enterprise software.
            """)
        ],
        output_dir
    )
    
    # Sample 2: Contract Draft
    create_sample_pdf(
        "Storage_Contract_Draft_v2.pdf",
        [
            (1, """Storage Vendor Contract - DRAFT v2
            
Between: Enron Corporation
And: StorageTech Solutions

Date: April 1, 2001

This agreement outlines the terms for storage system upgrade.

Proposed Amount: $38,000
Payment Terms: Net 30
Delivery Date: May 15, 2001

Equipment Specifications:
- 10TB storage capacity
- RAID 5 configuration
- 24/7 support included
            """)
        ],
        output_dir
    )
    
    # Sample 3: Meeting Minutes
    create_sample_pdf(
        "IT_Meeting_Minutes_Apr2001.pdf",
        [
            (1, """IT Department Meeting Minutes

Date: April 10, 2001
Attendees: John Doe, Sarah Johnson, Mike Chen

Agenda:
1. Q2 Budget Review
2. Storage Upgrade Discussion
3. Network Maintenance Schedule

Budget Discussion:
Sarah from Finance reviewed the Q2 budget proposal.
Initial proposal of $38,000 for storage was discussed.
Finance suggested increasing to $45,000 to include backup system.
Motion approved unanimously.

Action Items:
- John to finalize vendor contract
- Sarah to process purchase order
- Mike to schedule installation
            """)
        ],
        output_dir
    )
    
    # Sample 4: Vendor Comparison
    create_sample_pdf(
        "Vendor_Comparison_Analysis.pdf",
        [
            (1, """Storage Vendor Comparison Analysis

Date: March 28, 2001
Prepared by: IT Department

Vendors Evaluated:
1. StorageTech Solutions
2. DataSafe Inc.
3. EnterpriseStorage Corp.

Evaluation Criteria:
- Price
- Performance
- Support
- Delivery timeline
            """),
            (2, """Detailed Comparison:

StorageTech Solutions:
Price: $38,000
Performance: Excellent
Support: 24/7
Delivery: 6 weeks
Rating: 9/10

DataSafe Inc:
Price: $42,000
Performance: Good
Support: Business hours only
Delivery: 8 weeks
Rating: 7/10

EnterpriseStorage Corp:
Price: $35,000
Performance: Fair
Support: Limited
Delivery: 10 weeks
Rating: 6/10

Recommendation: StorageTech Solutions offers the best
value for our requirements.
            """)
        ],
        output_dir
    )
    
    # Sample 5: Technical Specifications
    create_sample_pdf(
        "Storage_Technical_Specs.pdf",
        [
            (1, """Technical Specifications Document

Product: Enterprise Storage Array Model X5000
Vendor: StorageTech Solutions

Hardware Specifications:
- Capacity: 10TB raw, 8TB usable (RAID 5)
- Interface: Fibre Channel 2Gbps
- Cache: 4GB battery-backed
- Expansion: Up to 40TB

Performance:
- IOPS: 15,000 sustained
- Throughput: 800 MB/s
- Latency: < 5ms average
            """),
            (2, """Software Features:

Management:
- Web-based administration console
- SNMP monitoring support
- Email alerts for critical events

Data Protection:
- Snapshot capability
- Replication support
- Hot spare drives

Support Package:
- 24/7 phone support
- 4-hour response time
- Annual firmware updates
- Quarterly health checks

Installation includes:
- On-site setup and configuration
- Data migration assistance
- Staff training (2 days)
            """)
        ],
        output_dir
    )
    
    logger.log_info(f"\n✓ Created 5 sample PDF attachments")
    logger.log_info(f"Location: {output_dir}")
    logger.log_info("\nNote: Link these attachments to specific messages")
    logger.log_info("by adding attachment references in your email data.")

if __name__ == "__main__":
    main()