import importlib

subjects_module = importlib.import_module("rag_service.routes.subjects")


def test_list_subjects_route(api_client, monkeypatch):
    # Patch the symbol in the actual subjects module so the router function uses it
    monkeypatch.setattr(
        subjects_module, "ls_subjects", lambda: ["matematica", "fisica"]
    )

    resp = api_client.get("/subjects")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_subjects"] == 2
    assert "matematica" in data["subjects"]


def test_list_document_types_route(api_client, monkeypatch):
    monkeypatch.setattr(
        subjects_module, "ls_document_types", lambda asignatura: ["apuntes", "examen"]
    )

    resp = api_client.get("/subjects/Matematica/types")
    assert resp.status_code == 200
    data = resp.json()
    assert data["asignatura"] == "Matematica"
    assert data["total_types"] == 2


def test_list_subjects_handles_exception(api_client, monkeypatch):
    def raise_err():
        raise RuntimeError("boom")

    monkeypatch.setattr(subjects_module, "ls_subjects", raise_err)
    resp = api_client.get("/subjects")
    assert resp.status_code == 500
    data = resp.json()
    assert "Failed to list subjects" in data["detail"]
