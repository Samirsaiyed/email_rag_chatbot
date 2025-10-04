"""
JSON trace logging utility.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
from src.config import RUNS_DIR

class TraceLogger:
    """Logger for conversation traces."""
    
    def __init__(self, session_id: str = None):
        """
        Initialize trace logger.
        
        Args:
            session_id: Session identifier
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_dir = RUNS_DIR / self.session_id
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "trace.jsonl"
        
        # Setup standard logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log_turn(self, trace_data: Dict[str, Any]):
        """
        Log a conversation turn to JSONL file.
        
        Args:
            trace_data: Dictionary containing trace information
        """
        trace_record = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            **trace_data
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            json.dump(trace_record, f, ensure_ascii=False)
            f.write('\n')
        
        self.logger.info(f"Logged turn: {trace_data.get('trace_id', 'unknown')}")
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def log_error(self, message: str, error: Exception = None):
        """Log error message."""
        if error:
            self.logger.error(f"{message}: {str(error)}")
        else:
            self.logger.error(message)