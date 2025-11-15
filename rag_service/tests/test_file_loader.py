import pytest

from rag_service.documents.file_loader import FileLoader, get_file_loader
from rag_service.models import DocumentMetadata


def make_metadata():
    return DocumentMetadata(
        asignatura="Prueba",
        tipo_documento="apuntes",
        fecha="2025-10-19",
    )


def test_load_text_and_markdown(tmp_path, monkeypatch):
    fl = FileLoader(documents_path=tmp_path)

    # text file
    p_txt = tmp_path / "materia" / "apuntes"
    p_txt.mkdir(parents=True)
    f = p_txt / "t1.txt"
    f.write_text("uno dos tres")

    meta = make_metadata()
    doc = fl.load_file("materia/apuntes/t1.txt", meta)
    assert "uno" in doc.content

    # markdown
    fmd = p_txt / "t2.md"
    fmd.write_text("# Title")
    doc2 = fl.load_file("materia/apuntes/t2.md", meta)
    assert "Title" in doc2.content


def test_unsupported_extension(tmp_path):
    fl = FileLoader(documents_path=tmp_path)
    p = tmp_path / "file.bin"
    p.write_bytes(b"\x00\x01")

    meta = make_metadata()
    with pytest.raises(ValueError):
        fl.load_file("file.bin", meta)


def test_save_uploaded_and_load(tmp_path):
    fl = FileLoader(documents_path=tmp_path)
    content = b"hola mundo"
    saved = fl.save_uploaded_file(content, "nuevo.txt", "Mi Asignatura", "Apuntes")

    assert saved.exists()
    # saved path should contain normalized subject and type
    assert "mi-asignatura" in str(saved)

    # Try loading via load_file when metadata provided
    meta = DocumentMetadata(
        asignatura="Mi Asignatura", tipo_documento="Apuntes", fecha="2025-10-19"
    )
    doc = fl.load_file("nuevo.txt", meta)
    assert "hola mundo" in doc.content


def test_get_file_loader_singleton(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENTS_PATH", str(tmp_path))
    # ensure singleton can be created without error
    g = get_file_loader()
    assert isinstance(g, FileLoader)
