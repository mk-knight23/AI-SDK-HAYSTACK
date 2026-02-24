"""
Document Splitters

Splits documents into chunks for efficient indexing and retrieval:
- Character-based splitting
- Token-aware splitting
- Metadata preservation
- Overlap management
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import re


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    document_id: Optional[str] = None
    chunk_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'content': self.content,
            'metadata': self.metadata,
            'document_id': self.documents_id,
            'chunk_index': self.chunk_index,
        }


class DocumentSplitter:
    """
    Splits documents into chunks for indexing and retrieval.

    Supports multiple splitting strategies:
    - Character-based: Splits by character count
    - Token-aware: Splits by token count (approximate)
    - Semantic: Splits by paragraphs/sentences
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separator: str = '\n\n',
        length_function: callable = len,
        keep_separator: bool = False,
    ):
        """
        Initialize the document splitter.

        Args:
            chunk_size: Target size for each chunk
            chunk_overlap: Number of characters/tokens to overlap between chunks
            separator: String to use for splitting (semantic split)
            length_function: Function to measure chunk size (len, token count, etc.)
            keep_separator: Whether to keep the separator in the output
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        self.length_function = length_function
        self.keep_separator = keep_separator

        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks."""
        # If text is shorter than chunk size, return as is
        if self.length_function(text) <= self.chunk_size:
            return [text] if text.strip() else []

        # Split by separator first (semantic splitting)
        splits = text.split(self.separator)
        if not splits:
            return []

        # Merge splits into chunks
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_length = self.length_function(split)

            # If single split is too large, split it further
            if split_length > self.chunk_size:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append(self.separator.join(current_chunk))
                    current_chunk = []
                    current_length = 0

                # Split the large chunk
                sub_chunks = self._split_large_chunk(split)
                chunks.extend(sub_chunks[:-1])  # All but last
                current_chunk = [sub_chunks[-1]]
                current_length = self.length_function(sub_chunks[-1])

            elif current_length + split_length + (len(self.separator) if current_chunk else 0) <= self.chunk_size:
                # Add to current chunk
                if current_chunk:
                    current_length += len(self.separator)
                current_chunk.append(split)
                current_length += split_length

            else:
                # Current chunk is full, save it
                if current_chunk:
                    chunks.append(self.separator.join(current_chunk))

                # Start new chunk with overlap
                overlap_chunks = self._get_overlap(current_chunk) if current_chunk else []
                current_chunk = overlap_chunks + [split]
                current_length = sum(self.length_function(s) for s in current_chunk)
                current_length += len(self.separator) * (len(current_chunk) - 1)

        # Add final chunk
        if current_chunk:
            chunks.append(self.separator.join(current_chunk))

        # Apply overlap to all chunks
        if self.chunk_overlap > 0:
            chunks = self._apply_overlap(chunks)

        return chunks

    def _split_large_chunk(self, text: str) -> List[str]:
        """Split a chunk that's too large into smaller pieces."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks

    def _get_overlap(self, chunks: List[str]) -> List[str]:
        """Get overlapping chunks from the end of the list."""
        if not chunks:
            return []

        overlap_chunks = []
        overlap_size = self.chunk_overlap

        # Work backwards through chunks
        for chunk in reversed(chunks):
            if overlap_size <= 0:
                break

            chunk_len = self.length_function(chunk)
            if chunk_len <= overlap_size:
                overlap_chunks.insert(0, chunk)
                overlap_size -= chunk_len
            else:
                # Take only part of the chunk
                overlap_chunks.insert(0, chunk[-overlap_size:])
                break

        return overlap_chunks

    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between adjacent chunks."""
        if len(chunks) <= 1:
            return chunks

        overlapped = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped.append(chunk)
            else:
                overlap_text = chunks[i - 1][-self.chunk_overlap:] if self.chunk_overlap > 0 else ''
                overlapped.append(overlap_text + chunk)

        return overlapped

    def split_document(
        self,
        document_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[DocumentChunk]:
        """Split a document into chunks with preserved metadata."""
        text_chunks = self.split_text(content)

        chunks = []
        for i, text_chunk in enumerate(text_chunks):
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                'chunk_size': self.length_function(text_chunk),
                'chunk_index': i,
                'total_chunks': len(text_chunks),
            })

            chunks.append(DocumentChunk(
                id=f"{document_id}_chunk_{i}",
                content=text_chunk,
                metadata=chunk_metadata,
                document_id=document_id,
                chunk_index=i,
            ))

        return chunks


class RecursiveCharacterSplitter(DocumentSplitter):
    """
    Splits text recursively using multiple separators.

    Tries different separators in order to maintain semantic coherence.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None,
    ):
        separators = separators or ['\n\n', '\n', '. ', ' ', '']
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separators[0],
        )
        self.separators = separators

    def split_text(self, text: str) -> List[str]:
        """Recursively split text using multiple separators."""
        return self._split_text_recursive(text, self.separators)

    def _split_text_recursive(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text trying different separators."""
        # Base case: no more separators or text fits in chunk
        if not separators or len(text) <= self.chunk_size:
            return [text] if text.strip() else []

        separator = separators[0]

        # Split by current separator
        splits = text.split(separator)
        if len(splits) == 1:
            # Separator not found, try next
            return self._split_text_recursive(text, separators[1:])

        # Try to merge splits into chunks
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_len = len(split)

            if current_length + split_len + (len(separator) if current_chunk else 0) <= self.chunk_size:
                if current_chunk:
                    current_chunk.append(separator)
                current_chunk.append(split)
                current_length += split_len + (len(separator) if current_chunk else 0)
            else:
                # Save current chunk
                if current_chunk:
                    chunks.append(''.join(current_chunk))

                # If split is too large, recursively split it
                if split_len > self.chunk_size:
                    sub_chunks = self._split_text_recursive(split, separators[1:])
                    chunks.extend(sub_chunks)
                    current_chunk = []
                    current_length = 0
                else:
                    # Start new chunk with overlap
                    current_chunk = [split]
                    current_length = split_len

        # Add final chunk
        if current_chunk:
            chunks.append(''.join(current_chunk))

        # Apply overlap
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._apply_overlap(chunks)

        return chunks


class SentenceSplitter(DocumentSplitter):
    """
    Splits text by sentences while respecting chunk size.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        super().__init__(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator='. ',
        )

    def split_text(self, text: str) -> List[str]:
        """Split text by sentences."""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_len = len(sentence)

            if current_length + sentence_len + 1 <= self.chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_len + 1
            else:
                if current_chunk:
                    chunks.append('. '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_len

        if current_chunk:
            chunks.append('. '.join(current_chunk))

        return chunks


def create_splitter(
    splitter_type: str = 'character',
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> DocumentSplitter:
    """
    Factory function to create a document splitter.

    Args:
        splitter_type: Type of splitter ('character', 'recursive', 'sentence')
        chunk_size: Target size for each chunk
        chunk_overlap: Number of characters to overlap

    Returns:
        A DocumentSplitter instance
    """
    if splitter_type == 'recursive':
        return RecursiveCharacterSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    elif splitter_type == 'sentence':
        return SentenceSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
    else:  # default to character
        return DocumentSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
