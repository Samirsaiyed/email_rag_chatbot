"""
Extract text from attachments (PDF, DOCX, TXT, HTML).
"""
import fitz  # PyMuPDF
import docx
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from src.config import ATTACHMENTS_DIR
from src.utils.helpers import generate_id, clean_text
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")

class AttachmentExtractor:
    """Extract text from various document formats."""
    
    def __init__(self):
        """Initialize attachment extractor."""
        self.supported_formats = ['.pdf', '.docx', '.txt', '.html', '.htm']
    
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
            doc = fitz.open(pdf_path)
            
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
            List with single entry (DOCX treated as one page)
        """
        try:
            doc = docx.Document(docx_path)
            
            # Extract all paragraphs
            text = '\n'.join([para.text for para in doc.paragraphs])
            
            if text.strip():
                logger.log_info(f"Extracted text from {docx_path.name}")
                return [{
                    'page_no': 1,
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
            List with single entry
        """
        try:
            with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
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
            List with single entry
        """
        try:
            with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            
            if text.strip():
                logger.log_info(f"Extracted text from {html_path.name}")
                return [{
                    'page_no': 1,
                    'text': clean_text(text)
                }]
            
        except Exception as e:
            logger.log_error(f"Failed to extract HTML {html_path.name}", e)
        
        return []
    
    def extract_text(self, file_path: Path) -> Optional[Dict]:
        """
        Extract text from attachment file.
        
        Args:
            file_path: Path to attachment file
            
        Returns:
            Dictionary with attachment data or None
        """
        suffix = file_path.suffix.lower()
        
        if suffix not in self.supported_formats:
            logger.log_info(f"Unsupported format: {suffix}")
            return None
        
        # Extract based on file type
        pages_data = []
        
        if suffix == '.pdf':
            pages_data = self.extract_from_pdf(file_path)
        elif suffix == '.docx':
            pages_data = self.extract_from_docx(file_path)
        elif suffix == '.txt':
            pages_data = self.extract_from_txt(file_path)
        elif suffix in ['.html', '.htm']:
            pages_data = self.extract_from_html(file_path)
        
        if not pages_data:
            return None
        
        # Generate attachment ID
        attachment_id = generate_id('A', file_path.name)
        
        return {
            'attachment_id': attachment_id,
            'filename': file_path.name,
            'file_type': suffix[1:],  # Remove dot
            'pages': pages_data,
            'page_count': len(pages_data)
        }
    
    def process_attachments_directory(self, attachments_path: Path = None) -> List[Dict]:
        """
        Process all attachments in a directory.
        
        Args:
            attachments_path: Path to directory with attachments
            
        Returns:
            List of extracted attachment data
        """
        if attachments_path is None:
            attachments_path = ATTACHMENTS_DIR / "pdfs"
        
        if not attachments_path.exists():
            logger.log_info(f"Attachments directory not found: {attachments_path}")
            return []
        
        logger.log_info(f"Processing attachments from {attachments_path}")
        
        attachments_data = []
        
        for file_path in attachments_path.iterdir():
            if file_path.is_file():
                attachment_data = self.extract_text(file_path)
                if attachment_data:
                    attachments_data.append(attachment_data)
        
        logger.log_info(f"Processed {len(attachments_data)} attachments")
        return attachments_data