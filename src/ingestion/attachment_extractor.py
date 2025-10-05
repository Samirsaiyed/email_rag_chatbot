"""
Extract text from attachments (PDF, DOCX, TXT, HTML).
"""
import pymupdf  # PyMuPDF
import docx
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from src.config import ATTACHMENTS_DIR
from src.utils.helpers import generate_id, clean_text
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")


class AttachmentExtractor:
    """Extract text from various attachment types."""
    
    def __init__(self):
        """Initialize attachment extractor."""
        pass
    
    def extract_from_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Extract text from PDF with page tracking.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of dictionaries with page text
        """
        pages_data = []
        
        try:
            doc = pymupdf.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                
                if text.strip():
                    pages_data.append({
                        'page_no': page_num + 1,  # 1-indexed
                        'text': clean_text(text)
                    })
            
            doc.close()
            logger.log_info(f"Extracted {len(pages_data)} pages from {pdf_path.name}")
            
        except Exception as e:
            logger.log_error(f"Failed to extract PDF {pdf_path.name}", e)
        
        return pages_data
    
    def extract_from_docx(self, docx_path: Path) -> List[Dict]:
        """
        Extract text from DOCX file.
        
        Args:
            docx_path: Path to DOCX file
            
        Returns:
            List with single dictionary containing all text
        """
        try:
            doc = docx.Document(docx_path)
            
            # Extract all paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = '\n'.join(paragraphs)
            
            if text.strip():
                logger.log_info(f"Extracted text from {docx_path.name}")
                return [{
                    'page_no': 1,  # DOCX doesn't have pages in the same way
                    'text': clean_text(text)
                }]
            
        except Exception as e:
            logger.log_error(f"Failed to extract DOCX {docx_path.name}", e)
        
        return []
    
    def extract_from_txt(self, txt_path: Path) -> List[Dict]:
        """
        Extract text from TXT file.
        
        Args:
            txt_path: Path to TXT file
            
        Returns:
            List with single dictionary containing all text
        """
        try:
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            if text.strip():
                logger.log_info(f"Extracted text from {txt_path.name}")
                return [{
                    'page_no': 1,
                    'text': clean_text(text)
                }]
            
        except Exception as e:
            logger.log_error(f"Failed to extract TXT {txt_path.name}", e)
        
        return []
    
    def extract_from_html(self, html_path: Path) -> List[Dict]:
        """
        Extract text from HTML file.
        
        Args:
            html_path: Path to HTML file
            
        Returns:
            List with single dictionary containing all text
        """
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator='\n')
            
            if text.strip():
                logger.log_info(f"Extracted text from {html_path.name}")
                return [{
                    'page_no': 1,
                    'text': clean_text(text)
                }]
            
        except Exception as e:
            logger.log_error(f"Failed to extract HTML {html_path.name}", e)
        
        return []
    
    def process_attachment(self, file_path: Path) -> Optional[Dict]:
        """
        Process a single attachment file.
        
        Args:
            file_path: Path to attachment file
            
        Returns:
            Dictionary with attachment data or None
        """
        file_ext = file_path.suffix.lower()
        
        # Extract based on file type
        if file_ext == '.pdf':
            pages_data = self.extract_from_pdf(file_path)
            file_type = 'pdf'
        elif file_ext in ['.docx', '.doc']:
            pages_data = self.extract_from_docx(file_path)
            file_type = 'docx'
        elif file_ext == '.txt':
            pages_data = self.extract_from_txt(file_path)
            file_type = 'txt'
        elif file_ext in ['.html', '.htm']:
            pages_data = self.extract_from_html(file_path)
            file_type = 'html'
        else:
            logger.log_info(f"Unsupported file type: {file_path.name}")
            return None
        
        if not pages_data:
            return None
        
        # Create attachment metadata
        attachment_data = {
            'attachment_id': generate_id('A', file_path.stem),
            'filename': file_path.name,
            'file_type': file_type,
            'page_count': len(pages_data),
            'pages': pages_data
        }
        
        return attachment_data
    
    def process_attachments_directory(self, base_dir: Path) -> List[Dict]:
        """
        Process all attachments in directory structure.
        
        Args:
            base_dir: Base attachments directory
            
        Returns:
            List of attachment data dictionaries
        """
        attachments_data = []
        
        # Process PDFs
        pdf_dir = base_dir / "pdfs"
        if pdf_dir.exists():
            for pdf_file in pdf_dir.glob("*.pdf"):
                attachment_data = self.process_attachment(pdf_file)
                if attachment_data:
                    attachments_data.append(attachment_data)
        
        # Process DOCX files
        docx_dir = base_dir / "docx"
        if docx_dir.exists():
            for docx_file in docx_dir.glob("*.docx"):
                attachment_data = self.process_attachment(docx_file)
                if attachment_data:
                    attachments_data.append(attachment_data)
        
        # Process TXT files
        txt_dir = base_dir / "txt"
        if txt_dir.exists():
            for txt_file in txt_dir.glob("*.txt"):
                attachment_data = self.process_attachment(txt_file)
                if attachment_data:
                    attachments_data.append(attachment_data)
        
        # Process HTML files
        html_dir = base_dir / "html"
        if html_dir.exists():
            for html_file in html_dir.glob("*.html"):
                attachment_data = self.process_attachment(html_file)
                if attachment_data:
                    attachments_data.append(attachment_data)
            for htm_file in html_dir.glob("*.htm"):
                attachment_data = self.process_attachment(htm_file)
                if attachment_data:
                    attachments_data.append(attachment_data)
        
        logger.log_info(f"Processed {len(attachments_data)} attachments")
        
        return attachments_data