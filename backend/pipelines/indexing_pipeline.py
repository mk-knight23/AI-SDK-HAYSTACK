"""
Indexing Pipeline

Handles document ingestion, processing, and indexing.
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

from haystack import Document

from documents import get_document_processor, DocumentSplitter, create_splitter
from embeddings import MistralEmbeddingProvider
from vectorstores import QdrantVectorStore


class IndexingPipeline:
    """
    Pipeline for indexing documents into the vector store.

    Handles:
    - Document parsing
    - Text splitting
    - Embedding generation
    - Vector storage
    """

    def __init__(
        self,
        vector_store: QdrantVectorStore,
        embedder: MistralEmbeddingProvider,
        splitter: Optional[DocumentSplitter] = None,
    ):
        """
        Initialize the indexing pipeline.

        Args:
            vector_store: Vector store for document storage
            embedder: Embedding provider
            splitter: Document splitter (default: recursive with 500 chars)
        """
        self.vector_store = vector_store
        self.embedder = embedder
        self.splitter = splitter or create_splitter('recursive', chunk_size=500, chunk_overlap=50)
        self.document_processor = get_document_processor()

    def index_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Index a single file.

        Args:
            file_path: Path to the file
            metadata: Optional metadata to attach

        Returns:
            Dictionary with indexing results
        """
        try:
            # 1. Parse the document
            doc = self.document_processor.process(file_path, metadata)

            # 2. Split into chunks
            chunks = self.splitter.split_document(
                document_id=doc.id,
                content=doc.content,
                metadata=doc.metadata,
            )

            # 3. Convert to Haystack Documents
            haystack_docs = [
                Document(
                    id=chunk.id,
                    content=chunk.content,
                    meta={
                        **chunk.metadata,
                        'document_id': chunk.document_id,
                        'chunk_index': chunk.chunk_index,
                    },
                )
                for chunk in chunks
            ]

            # 4. Generate embeddings
            haystack_docs = self.embedder.embed_documents(haystack_docs)

            # 5. Store in vector database
            self.vector_store.add_documents(haystack_docs)

            return {
                'success': True,
                'document_id': doc.id,
                'chunks_added': len(chunks),
                'metadata': doc.metadata,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path,
            }

    def index_text(
        self,
        text: str,
        document_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Index raw text.

        Args:
            text: Text content to index
            document_id: Unique document identifier
            metadata: Optional metadata to attach

        Returns:
            Dictionary with indexing results
        """
        try:
            # 1. Split into chunks
            chunks = self.splitter.split_document(
                document_id=document_id,
                content=text,
                metadata=metadata or {},
            )

            # 2. Convert to Haystack Documents
            haystack_docs = [
                Document(
                    id=chunk.id,
                    content=chunk.content,
                    meta={
                        **chunk.metadata,
                        'document_id': chunk.document_id,
                        'chunk_index': chunk.chunk_index,
                    },
                )
                for chunk in chunks
            ]

            # 3. Generate embeddings
            haystack_docs = self.embedder.embed_documents(haystack_docs)

            # 4. Store in vector database
            self.vector_store.add_documents(haystack_docs)

            return {
                'success': True,
                'document_id': document_id,
                'chunks_added': len(chunks),
                'metadata': metadata or {},
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'document_id': document_id,
            }

    def index_directory(
        self,
        directory_path: str,
        pattern: str = '*',
        metadata: Optional[Dict[str, Any]] = None,
        max_files: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Index all files in a directory.

        Args:
            directory_path: Path to the directory
            pattern: Glob pattern for file matching
            metadata: Optional metadata to attach to all files
            max_files: Maximum number of files to process

        Returns:
            Dictionary with indexing results
        """
        directory = Path(directory_path)

        if not directory.is_dir():
            return {
                'success': False,
                'error': f"Not a directory: {directory_path}",
            }

        # Find matching files
        files = list(directory.glob(pattern))
        files = [f for f in files if f.is_file()]

        if max_files:
            files = files[:max_files]

        results = {
            'success': True,
            'total_files': len(files),
            'indexed': 0,
            'failed': 0,
            'errors': [],
        }

        for file_path in files:
            result = self.index_file(str(file_path), metadata)

            if result['success']:
                results['indexed'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'file': str(file_path),
                    'error': result.get('error'),
                })

        return results

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete a document and all its chunks from the index.

        Args:
            document_id: Document ID to delete

        Returns:
            Dictionary with deletion results
        """
        try:
            # Find all chunks for this document
            filters = {'document_id': document_id}
            chunks = self.vector_store.get_documents(filters=filters, limit=1000)

            # Delete all chunks
            chunk_ids = [chunk.id for chunk in chunks]
            deleted = self.vector_store.delete_documents(chunk_ids)

            return {
                'success': True,
                'document_id': document_id,
                'chunks_deleted': deleted,
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'document_id': document_id,
            }


def create_indexing_pipeline(
    vector_store: QdrantVectorStore,
    embedder: Optional[MistralEmbeddingProvider] = None,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> IndexingPipeline:
    """
    Factory function to create an indexing pipeline.

    Args:
        vector_store: Vector store for document storage
        embedder: Embedding provider (created if None)
        chunk_size: Size of document chunks
        chunk_overlap: Overlap between chunks

    Returns:
        Configured IndexingPipeline instance
    """
    if embedder is None:
        embedder = MistralEmbeddingProvider()

    splitter = create_splitter(
        splitter_type='recursive',
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    return IndexingPipeline(
        vector_store=vector_store,
        embedder=embedder,
        splitter=splitter,
    )
