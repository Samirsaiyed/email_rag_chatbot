"""
Group emails into conversation threads.
"""
import json
from typing import Dict, List
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from src.config import THREADS_DIR, INGESTION_CONFIG
from src.utils.helpers import generate_id
from src.utils.logger import TraceLogger

logger = TraceLogger(session_id="ingestion")

class ThreadBuilder:
    """Build conversation threads from parsed emails."""
    
    def __init__(self):
        """Initialize thread builder."""
        self.threads = {}
        self.thread_metadata = []
    
    def build_threads(self, emails: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group emails into threads based on normalized subject.
        
        Args:
            emails: List of parsed email dictionaries
            
        Returns:
            Dictionary mapping thread_id to list of emails
        """
        logger.log_info("Building email threads...")
        
        # Group by normalized subject
        subject_groups = defaultdict(list)
        
        for email in emails:
            subject = email.get('subject_normalized', '')
            if subject:
                subject_groups[subject].append(email)
        
        # Filter and select threads
        selected_threads = self._select_threads(subject_groups)
        
        # Assign thread IDs and sort by date
        for subject, thread_emails in selected_threads.items():
            # Sort emails by date
            thread_emails.sort(key=lambda x: x.get('date', ''))
            
            # Generate thread ID
            thread_id = generate_id('T', subject)
            
            # Add thread_id to each email
            for email in thread_emails:
                email['thread_id'] = thread_id
            
            self.threads[thread_id] = thread_emails
            
            # Create metadata
            self.thread_metadata.append({
                'thread_id': thread_id,
                'subject': thread_emails[0].get('subject', ''),
                'subject_normalized': subject,
                'message_count': len(thread_emails),
                'start_date': thread_emails[0].get('date'),
                'end_date': thread_emails[-1].get('date'),
                'participants': self._get_participants(thread_emails)
            })
        
        logger.log_info(f"Created {len(self.threads)} threads")
        return self.threads
    
    def _select_threads(self, subject_groups: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """
        Select threads based on criteria.
        
        Args:
            subject_groups: Dictionary mapping subject to emails
            
        Returns:
            Selected threads
        """
        # Filter by message count
        filtered = {}
        
        for subject, emails in subject_groups.items():
            msg_count = len(emails)
            
            if (INGESTION_CONFIG.min_messages_per_thread <= msg_count <= 
                INGESTION_CONFIG.max_messages_per_thread):
                filtered[subject] = emails
        
        # Sort by message count (descending) and take top N
        sorted_threads = sorted(
            filtered.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )
        
        selected = dict(sorted_threads[:INGESTION_CONFIG.target_thread_count])
        
        logger.log_info(
            f"Selected {len(selected)} threads from {len(subject_groups)} total"
        )
        
        return selected
    
    def _get_participants(self, emails: List[Dict]) -> List[str]:
        """Get unique participants in a thread."""
        participants = set()
        
        for email in emails:
            # Add sender
            if email.get('from'):
                participants.add(email['from'])
            
            # Add recipients
            for recipient in email.get('to', []):
                participants.add(recipient)
            
            for recipient in email.get('cc', []):
                participants.add(recipient)
        
        return sorted(list(participants))
    
    def save_threads(self):
        """Save threads to JSON files."""
        logger.log_info(f"Saving threads to {THREADS_DIR}")
        
        # Save each thread
        for thread_id, emails in self.threads.items():
            thread_file = THREADS_DIR / f"{thread_id}.json"
            
            with open(thread_file, 'w', encoding='utf-8') as f:
                json.dump(emails, f, indent=2, ensure_ascii=False)
        
        # Save thread metadata
        metadata_file = THREADS_DIR / "thread_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.thread_metadata, f, indent=2, ensure_ascii=False)
        
        logger.log_info(f"Saved {len(self.threads)} threads")
    
    def load_thread(self, thread_id: str) -> List[Dict]:
        """
        Load a specific thread from disk.
        
        Args:
            thread_id: Thread identifier
            
        Returns:
            List of emails in thread
        """
        thread_file = THREADS_DIR / f"{thread_id}.json"
        
        if not thread_file.exists():
            raise FileNotFoundError(f"Thread {thread_id} not found")
        
        with open(thread_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_all_threads(self) -> Dict[str, List[Dict]]:
        """
        Load all threads from disk.
        
        Returns:
            Dictionary mapping thread_id to emails
        """
        metadata_file = THREADS_DIR / "thread_metadata.json"
        
        if not metadata_file.exists():
            return {}
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        threads = {}
        for meta in metadata:
            thread_id = meta['thread_id']
            threads[thread_id] = self.load_thread(thread_id)
        
        return threads