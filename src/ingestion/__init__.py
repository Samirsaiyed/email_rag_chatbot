"""Data ingestion module."""
from .email_parser import EmailParser
from .thread_builder import ThreadBuilder
from .attachment_extractor import AttachmentExtractor
from .indexer import Indexer

__all__ = [
    'EmailParser',
    'ThreadBuilder',
    'AttachmentExtractor',
    'Indexer'
]