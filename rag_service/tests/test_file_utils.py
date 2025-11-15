from rag_service.documents import file_utils


def test_list_subjects_and_types(tmp_path, monkeypatch, tmp_documents_dir):
    # create subjects and types (use unaccented name to match normalization)
    subj_dir = tmp_path / "logica-difusa"
    tipo_dir = subj_dir / "apuntes"
    tipo_dir.mkdir(parents=True)

    # create a file
    f = tipo_dir / "intro.txt"
    f.write_text("Contenido de ejemplo")

    # monkeypatch documents_path used by the module (best-effort)
    file_utils.documents_path = tmp_path

    subjects = file_utils.list_subjects()
    assert "logica-difusa" in subjects

    types = file_utils.list_document_types("logica difusa")
    assert "apuntes" in types


def test_list_files_root_and_filters(tmp_path):
    # create structure with two subjects
    s1 = tmp_path / "materia1" / "apuntes"
    s1.mkdir(parents=True)
    (s1 / "a.txt").write_text("a")

    s2 = tmp_path / "materia2" / "examen"
    s2.mkdir(parents=True)
    (s2 / "b.txt").write_text("b")

    file_utils.documents_path = tmp_path

    all_files = file_utils.list_files()
    assert any("materia1/apuntes/a.txt" in p for p in all_files)
    assert any("materia2/examen/b.txt" in p for p in all_files)

    filtered = file_utils.list_files(asignatura="materia1")
    assert len(filtered) == 1 and "materia1/apuntes/a.txt" in filtered[0]

    filtered2 = file_utils.list_files(asignatura="materia2", tipo_documento="examen")
    assert len(filtered2) == 1 and "materia2/examen/b.txt" in filtered2[0]


def test_get_file_info(tmp_path):
    file_utils.documents_path = tmp_path
    p = tmp_path / "doc.md"
    p.write_text("hello")

    info = file_utils.get_file_info("doc.md")
    assert info["filename"] == "doc.md"
    assert info["extension"] == ".md"
    assert info["size_bytes"] > 0

    # non-existent file raises
    try:
        file_utils.get_file_info("nope.txt")
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError:
        pass
