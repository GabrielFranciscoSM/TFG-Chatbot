import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure project root is importable
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, ROOT_DIR)

from rag_service.api import app
from rag_service import config


@pytest.fixture
def tmp_documents_dir(tmp_path, monkeypatch):
    """Fixture that points the service to a temporary documents directory and
    updates modules that cached the path at import time.
    """
    # Point settings to tmp path
    monkeypatch.setenv("DOCUMENTS_PATH", str(tmp_path))
    config.settings.documents_path = str(tmp_path)

    # Update file_utils.documents_path which is evaluated at import time
    try:
        from rag_service.documents import file_utils

        file_utils.documents_path = tmp_path
    except Exception:
        # best-effort; tests will still use tmp_path directly when needed
        pass

    # Reset singleton _file_loader in file_loader module if present
    try:
        from rag_service.documents import file_loader

        file_loader._file_loader = None
    except Exception:
        pass

    return tmp_path


@pytest.fixture
def api_client(tmp_documents_dir):
    """Test client that ensures the service uses the temporary documents dir."""
    return TestClient(app)
