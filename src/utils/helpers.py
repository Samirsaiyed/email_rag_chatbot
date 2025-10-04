"""
Common helper functions.
"""
import re
import hashlib
from datetime import datetime
from typing import Optional

def generate_id(prefix: str, content: str) -> str:
    """
    Generate a unique ID based on content hash.
    
    Args:
        prefix: Prefix for the ID (e.g., 'T' for thread, 'M' for message)
        content: Content to hash
        
    Returns:
        Unique ID string
    """
    hash_obj = hashlib.md5(content.encode())
    hash_hex = hash_obj.hexdigest()[:8]
    return f"{prefix}-{hash_hex}"

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Raw text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-\'\"@]', '', text)
    
    return text.strip()

def normalize_subject(subject: str) -> str:
    """
    Normalize email subject for thread grouping.
    Removes RE:, FW:, FWD:, etc.
    
    Args:
        subject: Email subject
        
    Returns:
        Normalized subject
    """
    if not subject:
        return ""
    
    # Remove common prefixes
    subject = re.sub(r'^(RE|FW|FWD|Fwd|Re):\s*', '', subject, flags=re.IGNORECASE)
    
    # Remove extra whitespace
    subject = re.sub(r'\s+', ' ', subject).strip()
    
    return subject.lower()

def parse_email_date(date_str: str) -> Optional[datetime]:
    """
    Parse email date string to datetime object.
    
    Args:
        date_str: Date string from email
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    
    # Common email date formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y %H:%M:%S %z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except (ValueError, TypeError):
            continue
    
    return None

def extract_email_address(email_str: str) -> str:
    """
    Extract email address from string like 'John Doe <john@example.com>'.
    
    Args:
        email_str: Email string
        
    Returns:
        Email address
    """
    if not email_str:
        return ""
    
    match = re.search(r'<([^>]+)>', email_str)
    if match:
        return match.group(1).strip()
    
    return email_str.strip()

def extract_name_from_email(email_str: str) -> str:
    """
    Extract name from email string like 'John Doe <john@example.com>'.
    
    Args:
        email_str: Email string
        
    Returns:
        Name or email if no name found
    """
    if not email_str:
        return ""
    
    # Try to extract name before <email>
    match = re.match(r'([^<]+)<', email_str)
    if match:
        name = match.group(1).strip()
        # Remove quotes if present
        name = name.strip('"\'')
        return name
    
    # If no name, return the email address
    return extract_email_address(email_str)