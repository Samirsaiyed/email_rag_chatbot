"""
Parse Enron email dataset.
"""
import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from src.config import RAW_DATA_DIR, INGESTION_CONFIG
from src.utils.helpers import (
    generate_id, clean_text, normalize_subject,
    parse_email_date, extract_email_address, extract_name_from_email
)
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")

class EmailParser:
    """Parse emails from Enron dataset CSV."""
    
    def __init__(self, csv_path: Path = None):
        """
        Initialize email parser.
        
        Args:
            csv_path: Path to emails.csv file
        """
        self.csv_path = csv_path or RAW_DATA_DIR / "emails.csv"
        self.df = None
    
    def load_csv(self) -> pd.DataFrame:
        """
        Load emails from CSV file.
        
        Returns:
            DataFrame with emails
        """
        logger.log_info(f"Loading emails from {self.csv_path}")
        
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.log_info(f"Loaded {len(self.df)} emails")
            return self.df
        except Exception as e:
            logger.log_error("Failed to load CSV", e)
            raise
    
    def _extract_headers(self, message: str) -> Dict[str, str]:
        """Extract email headers from message text."""
        headers = {}
        
        # Common header patterns (case-insensitive, flexible whitespace)
        header_patterns = {
            'from': r'From:\s*(.+?)(?:\n(?!\s)|$)',
            'to': r'To:\s*(.+?)(?:\n(?!\s)|$)',
            'cc': r'Cc:\s*(.+?)(?:\n(?!\s)|$)',
            'subject': r'Subject:\s*(.+?)(?:\n(?!\s)|$)',
            'date': r'Date:\s*(.+?)(?:\n(?!\s)|$)',
        }
        
        for key, pattern in header_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE | re.MULTILINE)
            if match:
                headers[key] = match.group(1).strip()
        
        return headers

    def parse_email(self, row: pd.Series) -> Optional[Dict]:
        """
        Parse a single email row into structured format.
        
        Args:
            row: DataFrame row
            
        Returns:
            Parsed email dictionary or None if invalid
        """
        try:
            # Extract fields (adjust column names based on your CSV)
            message_text = row.get('message', '')
            
            if not message_text or len(message_text) < INGESTION_CONFIG.min_body_length:
                return None
            
            # Parse email headers from message text
            headers = self._extract_headers(message_text)
            body = self._extract_body(message_text)
            
            # Generate message ID
            message_id = generate_id('M', message_text)
            
            # Try multiple ways to get date
            date_obj = None
            
            # Method 1: From headers
            if headers.get('date'):
                date_obj = parse_email_date(headers['date'])
            
            # Method 2: Check if there's a separate 'date' column in CSV
            if not date_obj and 'date' in row:
                date_obj = parse_email_date(str(row['date']))
            
            # Method 3: Try to extract from file path if it contains date info
            if not date_obj and 'file' in row:
                # Some Enron files have dates in path like "maildir/allen-p/sent/2001-05-14.txt"
                file_path = str(row.get('file', ''))
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', file_path)
                if date_match:
                    try:
                        # REMOVE: from datetime import datetime
                        # datetime is already imported at top
                        date_obj = datetime(
                            int(date_match.group(1)),
                            int(date_match.group(2)),
                            int(date_match.group(3))
                        )
                    except:
                        pass

            # Apply date filter only if we have a valid date AND filter is configured
            if date_obj and INGESTION_CONFIG.date_range_start:
                # Remove timezone info to make comparison work
                if date_obj.tzinfo is not None:
                    date_obj = date_obj.replace(tzinfo=None)
                
                start_date = datetime.fromisoformat(INGESTION_CONFIG.date_range_start)
                end_date = datetime.fromisoformat(INGESTION_CONFIG.date_range_end)
                
                if not (start_date <= date_obj <= end_date):
                    return None

            
            # Extract sender and recipients
            from_email = extract_email_address(headers.get('from', ''))
            from_name = extract_name_from_email(headers.get('from', ''))
            
            to_emails = self._parse_recipients(headers.get('to', ''))
            cc_emails = self._parse_recipients(headers.get('cc', ''))
            
            # Clean body
            if INGESTION_CONFIG.remove_forwarding_headers:
                body = self._remove_forwarding_headers(body)
            
            if INGESTION_CONFIG.remove_signatures:
                body = self._remove_signature(body)
            
            body = clean_text(body)
            
            if len(body) < INGESTION_CONFIG.min_body_length:
                return None
            
            parsed_email = {
            'message_id': message_id,
            'date': date_obj.replace(tzinfo=None).isoformat() if date_obj else None,  # Strip timezone
            'from': from_email,
            'from_name': from_name,
            'to': to_emails,
            'cc': cc_emails,
            'subject': headers.get('subject', '').strip(),
            'subject_normalized': normalize_subject(headers.get('subject', '')),
            'body': body,
            'raw_message': message_text
        }
            
            return parsed_email
            
        except Exception as e:
            logger.log_error(f"Failed to parse email", e)
            return None
    
    def _extract_headers(self, message: str) -> Dict[str, str]:
        """Extract email headers from message text."""
        headers = {}
        
        # Common header patterns
        header_patterns = {
            'from': r'From:\s*(.+?)(?:\n|$)',
            'to': r'To:\s*(.+?)(?:\n|$)',
            'cc': r'Cc:\s*(.+?)(?:\n|$)',
            'subject': r'Subject:\s*(.+?)(?:\n|$)',
            'date': r'Date:\s*(.+?)(?:\n|$)',
        }
        
        for key, pattern in header_patterns.items():
            match = re.search(pattern, message, re.IGNORECASE | re.MULTILINE)
            if match:
                headers[key] = match.group(1).strip()
        
        return headers
    
    def _extract_body(self, message: str) -> str:
        """Extract email body from message text."""
        # Body typically starts after headers (after first blank line)
        parts = re.split(r'\n\s*\n', message, maxsplit=1)
        
        if len(parts) > 1:
            return parts[1].strip()
        
        return message.strip()
    
    def _parse_recipients(self, recipients_str: str) -> List[str]:
        """Parse comma-separated recipients."""
        if not recipients_str:
            return []
        
        # Split by comma and extract email addresses
        recipients = []
        for recipient in recipients_str.split(','):
            email = extract_email_address(recipient)
            if email:
                recipients.append(email)
        
        return recipients
    
    def _remove_forwarding_headers(self, body: str) -> str:
        """Remove forwarding headers from email body."""
        # Remove patterns like "-----Original Message-----"
        body = re.sub(r'-+\s*Original Message\s*-+.*?(?=\n\n|\Z)', '', body, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove forwarding info
        body = re.sub(r'Forwarded by.*?(?=\n\n|\Z)', '', body, flags=re.DOTALL | re.IGNORECASE)
        
        return body.strip()
    
    def _remove_signature(self, body: str) -> str:
        """Remove email signature from body."""
        # Common signature patterns
        signature_patterns = [
            r'\n--\s*\n.*',  # -- separator
            r'\nSent from my.*',  # Mobile signatures
            r'\nBest regards,.*',
            r'\nThanks,.*',
        ]
        
        for pattern in signature_patterns:
            body = re.sub(pattern, '', body, flags=re.DOTALL | re.IGNORECASE)
        
        return body.strip()
    
    def parse_all_emails(self) -> List[Dict]:
        """
        Parse all emails from CSV.
        
        Returns:
            List of parsed email dictionaries
        """
        if self.df is None:
            self.load_csv()
        
        logger.log_info("Parsing all emails...")
        
        parsed_emails = []
        for idx, row in self.df.iterrows():
            parsed = self.parse_email(row)
            if parsed:
                parsed_emails.append(parsed)
            
            if (idx + 1) % 1000 == 0:
                logger.log_info(f"Processed {idx + 1} emails, parsed {len(parsed_emails)}")
        
        logger.log_info(f"Successfully parsed {len(parsed_emails)} emails")
        return parsed_emails