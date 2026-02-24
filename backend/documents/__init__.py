"""
Documents Module

Provides document processing and text extraction:
- PDF parsing with pypdf
- DOCX parsing with python-docx
- Text preprocessing and splitting
- Metadata extraction
"""

from .processors import DocumentProcessor, PDFProcessor, DocxProcessor, TextProcessor
from .splitters import DocumentSplitter, create_splitter

__all__ = [
    'DocumentProcessor',
    'PDFProcessor',
    'DocxProcessor',
    'TextProcessor',
    'DocumentSplitter',
    'create_splitter',
]
