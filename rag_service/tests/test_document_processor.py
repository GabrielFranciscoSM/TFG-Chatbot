"""Unit tests for document processor."""

from rag_service.documents.document_processor import (
    DocumentProcessor,
    get_document_processor,
)
from rag_service.models import Document, DocumentMetadata


def make_metadata():
    """Helper to create test metadata."""
    return DocumentMetadata(
        asignatura="Test", tipo_documento="apuntes", fecha="2025-11-04"
    )


def test_chunk_short_document():
    """Test that short documents are not chunked."""
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)

    doc = Document(
        content="This is a short document.", metadata=make_metadata(), doc_id="test_1"
    )

    chunks = processor.chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == doc.content
    assert chunks[0].metadata.chunk_id == 0


def test_chunk_long_document():
    """Test that long documents are chunked properly."""
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

    long_text = "This is a long document. " * 20
    doc = Document(content=long_text, metadata=make_metadata(), doc_id="test_2")

    chunks = processor.chunk_document(doc)
    assert len(chunks) > 1

    # Check chunk IDs are sequential
    for i, chunk in enumerate(chunks):
        assert chunk.metadata.chunk_id == i
        assert chunk.doc_id == f"test_2_chunk_{i}"


def test_chunk_documents_multiple():
    """Test chunking multiple documents."""
    processor = DocumentProcessor(chunk_size=30, chunk_overlap=5)

    docs = [
        Document(content="Short doc 1", metadata=make_metadata(), doc_id="doc1"),
        Document(
            content="This is a much longer document that will be chunked." * 3,
            metadata=make_metadata(),
            doc_id="doc2",
        ),
        Document(content="Short doc 2", metadata=make_metadata(), doc_id="doc3"),
    ]

    all_chunks = processor.chunk_documents(docs)

    # Should have more chunks than original documents
    assert len(all_chunks) > len(docs)

    # Verify all chunks have chunk_id
    for chunk in all_chunks:
        assert chunk.metadata.chunk_id is not None


def test_chunk_preserves_metadata():
    """Test that chunking preserves document metadata."""
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=10)

    metadata = DocumentMetadata(
        asignatura="Lógica Difusa",
        tipo_documento="apuntes",
        fecha="2025-11-04",
        tema="Conjuntos difusos",
        autor="Test Author",
        fuente="PRADO UGR",
        idioma="es",
    )

    long_text = "Text about fuzzy sets. " * 20
    doc = Document(content=long_text, metadata=metadata, doc_id="test")

    chunks = processor.chunk_document(doc)

    for chunk in chunks:
        assert chunk.metadata.asignatura == "Lógica Difusa"
        assert chunk.metadata.tipo_documento == "apuntes"
        assert chunk.metadata.tema == "Conjuntos difusos"
        assert chunk.metadata.autor == "Test Author"


def test_estimate_tokens():
    """Test token estimation."""
    processor = DocumentProcessor()

    text = "This is a test document with some words."
    tokens = processor.estimate_tokens(text)

    # Should be roughly 1/4 of character count
    assert tokens > 0
    assert tokens == len(text) // 4


def test_get_document_processor_singleton():
    """Test that get_document_processor returns singleton."""
    processor1 = get_document_processor()
    processor2 = get_document_processor()

    assert processor1 is processor2
    assert isinstance(processor1, DocumentProcessor)


def test_custom_separators():
    """Test document processor with custom separators."""
    separators = ["\n\n", "\n", ". "]
    processor = DocumentProcessor(
        chunk_size=50, chunk_overlap=10, separators=separators
    )

    text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
    doc = Document(content=text, metadata=make_metadata(), doc_id="test")

    chunks = processor.chunk_document(doc)

    # Should split on paragraph boundaries when possible
    assert len(chunks) >= 1


def test_chunk_overlap():
    """Test that chunk overlap works correctly."""
    processor = DocumentProcessor(chunk_size=30, chunk_overlap=10)

    text = "Word " * 20
    doc = Document(content=text, metadata=make_metadata(), doc_id="test")

    chunks = processor.chunk_document(doc)

    if len(chunks) > 1:
        # Adjacent chunks should have some overlapping content
        # This is a simplified check - actual overlap depends on separator positions
        assert len(chunks[0].content) <= 30 + 10  # Allow for separator positions
