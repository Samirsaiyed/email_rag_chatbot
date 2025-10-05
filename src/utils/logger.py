"""
JSON trace logging for transparency.
"""
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

class TraceLogger:
    """Logger with JSONL trace output."""
    
    def __init__(self, session_id: str = "default"):
        """Initialize logger with session ID."""
        self.session_id = session_id
        self.logger = logging.getLogger(f"src.utils.logger.{session_id}")
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Setup JSONL trace file
        self.trace_file = None
        self._setup_trace_file()
    
    def _setup_trace_file(self):
        """Setup JSONL trace file in runs directory."""
        from src.config import RUNS_DIR
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = RUNS_DIR / f"{timestamp}_{self.session_id}"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        self.trace_file = session_dir / "trace.jsonl"
        self.log_info(f"Trace logging to: {self.trace_file}")
    
    def log_trace(self, event_type: str, data: Dict[str, Any]):
        """
        Log a trace event to JSONL file.
        
        Args:
            event_type: Type of event (e.g., 'query', 'retrieval', 'answer')
            data: Event data dictionary
        """
        if self.trace_file:
            trace_record = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "event_type": event_type,
                **data
            }
            
            with open(self.trace_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(trace_record, ensure_ascii=False) + '\n')
    
    def log_info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def log_error(self, message: str, error: Exception = None):
        """Log error message."""
        if error:
            self.logger.error(f"{message}: {str(error)}")
        else:
            self.logger.error(message)
    
    def log_warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)