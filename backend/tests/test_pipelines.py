"""
Tests for RAG and indexing pipelines.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from haystack import Document

from pipelines.rag_pipeline import RAGPipeline, RAGConfig
from pipelines.indexing_pipeline import IndexingPipeline
from pipelines.hybrid_pipeline import HybridPipeline


class TestRAGConfig:
    """Test RAG configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RAGConfig()

        assert config.embedding_model == 'mistral-embed'
        assert config.llm_model == 'mistral-small'
        assert config.top_k == 5
        assert config.llm_temperature == 0.7
        assert config.llm_max_tokens == 512

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RAGConfig(
            top_k=10,
            llm_temperature=0.5,
            llm_max_tokens=1024,
        )

        assert config.top_k == 10
        assert config.llm_temperature == 0.5
        assert config.llm_max_tokens == 1024

    def test_prompt_template_includes_context(self):
        """Test prompt template includes context placeholder."""
        config = RAGConfig()
        template = config.get_prompt_template()

        assert '{% for doc in documents %}' in template
        assert '{{ doc.content }}' in template
        assert '{{ question }}' in template


class TestRAGPipeline:
    """Test RAG pipeline implementation."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        store = Mock()
        store.search.return_value = [
            Document(
                id='doc1',
                content='Sample content for testing.',
                meta={'source': 'test'},
            ),
        ]
        return store

    @pytest.fixture
    def mock_embedder(self):
        """Create mock embedder."""
        embedder = Mock()
        embedder.embed_text.return_value = [0.1] * 1024
        return embedder

    @pytest.fixture
    def mock_llm(self):
        """Create mock LLM."""
        llm = Mock()
        llm.generate.return_value = {
            'text': 'This is a test answer.',
            'meta': {},
        }
        return llm

    def test_pipeline_initialization(self, mock_vector_store, mock_embedder, mock_llm):
        """Test pipeline initializes correctly."""
        config = RAGConfig(top_k=3)
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            llm=mock_llm,
            config=config,
        )

        assert pipeline.vector_store == mock_vector_store
        assert pipeline.embedder == mock_embedder
        assert pipeline.llm == mock_llm
        assert pipeline.config.top_k == 3

    def test_pipeline_runs_query(self, mock_vector_store, mock_embedder, mock_llm):
        """Test pipeline runs a query end-to-end."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            llm=mock_llm,
        )

        result = pipeline.run('What is this about?')

        assert 'answer' in result
        assert 'sources' in result
        assert result['answer'] == 'This is a test answer.'
        assert len(result['sources']) == 1
        assert result['query'] == 'What is this about?'

    def test_pipeline_calls_embedder(self, mock_vector_store, mock_embedder, mock_llm):
        """Test pipeline calls embedder with query."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            llm=mock_llm,
        )

        pipeline.run('Test query')

        mock_embedder.embed_text.assert_called_once_with('Test query')

    def test_pipeline_calls_vector_store(self, mock_vector_store, mock_embedder, mock_llm):
        """Test pipeline calls vector store with embedding."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            llm=mock_llm,
        )

        pipeline.run('Test query')

        mock_vector_store.search.assert_called_once()
        call_args = mock_vector_store.search.call_args
        assert call_args[1]['top_k'] == 5  # default top_k

    def test_pipeline_handles_no_results(self, mock_vector_store, mock_embedder, mock_llm):
        """Test pipeline handles case with no search results."""
        mock_vector_store.search.return_value = []

        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            llm=mock_llm,
        )

        result = pipeline.run('Test query')

        assert "couldn't find any relevant information" in result['answer']
        assert result['sources'] == []

    def test_pipeline_with_custom_top_k(self, mock_vector_store, mock_embedder, mock_llm):
        """Test pipeline respects custom top_k parameter."""
        pipeline = RAGPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            llm=mock_llm,
        )

        pipeline.run('Test query', top_k=10)

        call_args = mock_vector_store.search.call_args
        assert call_args[1]['top_k'] == 10


class TestIndexingPipeline:
    """Test indexing pipeline implementation."""

    @pytest.fixture
    def mock_vector_store(self):
        """Create mock vector store."""
        store = Mock()
        store.add_documents.return_value = None
        return store

    @pytest.fixture
    def mock_embedder(self):
        """Create mock embedder."""
        embedder = Mock()
        embedder.embed_documents = lambda docs: docs  # Pass through
        return embedder

    @pytest.fixture
    def mock_splitter(self):
        """Create mock document splitter."""
        splitter = Mock()
        splitter.split_document.return_value = [
            Mock(
                id='chunk_1',
                content='Content 1',
                metadata={},
                document_id='doc1',
                chunk_index=0,
            ),
            Mock(
                id='chunk_2',
                content='Content 2',
                metadata={},
                document_id='doc1',
                chunk_index=1,
            ),
        ]
        return splitter

    def test_indexing_pipeline_initialization(self, mock_vector_store, mock_embedder, mock_splitter):
        """Test indexing pipeline initializes correctly."""
        pipeline = IndexingPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            splitter=mock_splitter,
        )

        assert pipeline.vector_store == mock_vector_store
        assert pipeline.embedder == mock_embedder
        assert pipeline.splitter == mock_splitter

    @patch('pipelines.indexing_pipeline.get_document_processor')
    def test_index_file_processes_and_stores(
        self,
        mock_get_processor,
        mock_vector_store,
        mock_embedder,
        mock_splitter,
    ):
        """Test indexing pipeline processes a file."""
        # Setup mocks
        mock_processor = Mock()
        mock_doc = Mock()
        mock_doc.id = 'doc1'
        mock_doc.content = 'Test content'
        mock_doc.metadata = {}
        mock_processor.process.return_value = mock_doc
        mock_get_processor.return_value = mock_processor

        pipeline = IndexingPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            splitter=mock_splitter,
        )

        result = pipeline.index_file('test.pdf')

        assert result['success'] is True
        assert result['document_id'] == 'doc1'
        assert result['chunks_added'] == 2

        mock_processor.process.assert_called_once_with('test.pdf', None)

    def test_index_text_stores_content(self, mock_vector_store, mock_embedder, mock_splitter):
        """Test indexing pipeline indexes raw text."""
        pipeline = IndexingPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            splitter=mock_splitter,
        )

        result = pipeline.index_text('Test content', 'custom_doc_id')

        assert result['success'] is True
        assert result['document_id'] == 'custom_doc_id'
        assert result['chunks_added'] == 2

    def test_delete_document_removes_chunks(self, mock_vector_store, mock_embedder, mock_splitter):
        """Test deleting a document removes all chunks."""
        mock_vector_store.get_documents.return_value = [
            Mock(id='chunk_1'),
            Mock(id='chunk_2'),
        ]
        mock_vector_store.delete_documents.return_value = 2

        pipeline = IndexingPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            splitter=mock_splitter,
        )

        result = pipeline.delete_document('doc1')

        assert result['success'] is True
        assert result['document_id'] == 'doc1'
        assert result['chunks_deleted'] == 2

    @patch('pipines.indexing_pipeline.get_document_processor')
    def test_index_file_handles_errors(
        self,
        mock_get_processor,
        mock_vector_store,
        mock_embedder,
        mock_splitter,
    ):
        """Test indexing pipeline handles processing errors."""
        mock_processor = Mock()
        mock_processor.process.side_effect = ValueError('File not supported')
        mock_get_processor.return_value = mock_processor

        pipeline = IndexingPipeline(
            vector_store=mock_vector_store,
            embedder=mock_embedder,
            splitter=mock_splitter,
        )

        result = pipeline.index_file('test.xyz')

        assert result['success'] is False
        assert 'error' in result
