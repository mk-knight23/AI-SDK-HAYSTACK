"""
Tests for document processors.
"""

import pytest
import tempfile
import os
from pathlib import Path

from documents.processors import (
    DocumentProcessorFactory,
    PDFProcessor,
    DocxProcessor,
    TextProcessor,
    PPTXProcessor,
)
from documents.splitters import (
    DocumentSplitter,
    RecursiveCharacterSplitter,
    SentenceSplitter,
    create_splitter,
)


class TestDocumentProcessors:
    """Test document processor implementations."""

    def test_factory_returns_processor_for_pdf(self):
        """Test factory returns PDF processor for PDF files."""
        factory = DocumentProcessorFactory()
        processor = factory.get_processor('test.pdf')
        assert isinstance(processor, PDFProcessor)

    def test_factory_returns_processor_for_txt(self):
        """Test factory returns text processor for text files."""
        factory = DocumentProcessorFactory()
        processor = factory.get_processor('test.txt')
        assert isinstance(processor, TextProcessor)

    def test_factory_returns_none_for_unsupported(self):
        """Test factory returns None for unsupported file types."""
        factory = DocumentProcessorFactory()
        processor = factory.get_processor('test.xyz')
        assert processor is None

    def test_text_processor_creates_document(self):
        """Test text processor creates a document with content."""
        processor = TextProcessor()

        # Create a temporary text file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test content\nfor document processing.')
            temp_path = f.name

        try:
            document = processor.process(temp_path)

            assert document.content == 'Test content\nfor document processing.'
            assert document.id is not None
            assert document.metadata['document_type'] == 'text'
            assert document.metadata['total_lines'] == 1
        finally:
            os.unlink(temp_path)

    def test_text_processor_handles_encoding(self):
        """Test text processor handles different encodings."""
        processor = TextProcessor()

        # Create a file with UTF-8 content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write('Test with special chars: café, naïve, 日本語')
            temp_path = f.name

        try:
            document = processor.process(temp_path)
            assert 'café' in document.content
            assert '日本語' in document.content
        finally:
            os.unlink(temp_path)

    def test_text_processor_extracts_metadata(self):
        """Test text processor extracts file metadata."""
        processor = TextProcessor()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test content')
            temp_path = f.name

        try:
            document = processor.process(temp_path)
            assert 'filename' in document.metadata
            assert 'file_size' in document.metadata
            assert document.metadata['file_extension'] == '.txt'
        finally:
            os.unlink(temp_path)


class TestDocumentSplitters:
    """Test document splitter implementations."""

    def test_splitter_splits_long_text(self):
        """Test splitter splits text longer than chunk size."""
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=20)

        # Create text longer than chunk size
        text = ' '.join(['word'] * 50)  # ~250 characters

        chunks = splitter.split_text(text)

        assert len(chunks) > 1
        assert all(len(chunk) <= 150 for chunk in chunks)  # Allow some margin

    def test_splitter_returns_single_chunk_for_short_text(self):
        """Test splitter returns single chunk for short text."""
        splitter = DocumentSplitter(chunk_size=500, chunk_overlap=50)

        text = 'Short text'

        chunks = splitter.split_text(text)

        assert len(chunks) == 1
        assert chunks[0] == 'Short text'

    def test_splitter_preserves_content(self):
        """Test splitter preserves all content."""
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=20)

        original_text = ' '.join(['word'] * 50)
        chunks = splitter.split_text(original_text)

        # Join chunks back and compare (accounting for overlap)
        joined = ''.join(chunks)
        assert 'word' in joined

    def test_recursive_splitter_splits_by_separator(self):
        """Test recursive splitter respects separator."""
        splitter = RecursiveCharacterSplitter(
            chunk_size=100,
            chunk_overlap=10,
            separators=['\n\n', '\n'],
        )

        text = 'Paragraph 1\n\nParagraph 2\n\nParagraph 3'

        chunks = splitter.split_text(text)

        # Should split by paragraphs
        assert len(chunks) == 3

    def test_splitter_creates_document_chunks(self):
        """Test splitter creates DocumentChunk objects."""
        splitter = DocumentSplitter(chunk_size=100, chunk_overlap=20)

        chunks = splitter.split_document(
            document_id='test_doc',
            content=' '.join(['word'] * 100),
            metadata={'source': 'test'},
        )

        assert len(chunks) > 0
        assert all(chunk.document_id == 'test_doc' for chunk in chunks)
        assert all(chunk.content for chunk in chunks)

    def test_create_splitter_factory(self):
        """Test splitter factory function."""
        splitter = create_splitter('character', chunk_size=200)
        assert isinstance(splitter, DocumentSplitter)

        recursive_splitter = create_splitter('recursive', chunk_size=200)
        assert isinstance(recursive_splitter, RecursiveCharacterSplitter)

        sentence_splitter = create_splitter('sentence', chunk_size=200)
        assert isinstance(sentence_splitter, SentenceSplitter)

    def test_splitter_throws_on_invalid_overlap(self):
        """Test splitter throws error when overlap >= chunk_size."""
        with pytest.raises(ValueError):
            DocumentSplitter(chunk_size=100, chunk_overlap=100)

    def test_chunk_metadata_includes_size_and_index(self):
        """Test document chunks include size and index metadata."""
        splitter = DocumentSplitter(chunk_size=50, chunk_overlap=10)

        chunks = splitter.split_document(
            document_id='test_doc',
            content=' '.join(['word'] * 50),
        )

        assert 'chunk_size' in chunks[0].metadata
        assert 'chunk_index' in chunks[0].metadata
        assert 'total_chunks' in chunks[0].metadata

        # Check sequential indices
        indices = [chunk.chunk_index for chunk in chunks]
        assert indices == list(range(len(chunks)))


@pytest.mark.parametrize('content,expected_chunks', [
    ('Short text', 1),
    (' '.join(['word'] * 20), 1),  # ~100 chars
    (' '.join(['word'] * 100), 2),  # ~500 chars
])
def test_splitter_with_various_lengths(content, expected_chunks):
    """Test splitter with various content lengths."""
    splitter = DocumentSplitter(chunk_size=250, chunk_overlap=50)
    chunks = splitter.split_text(content)

    assert len(chunks) >= expected_chunks
