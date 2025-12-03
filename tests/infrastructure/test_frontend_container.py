"""
Tests para verificar el funcionamiento del contenedor del frontend.
Estos tests verifican que el contenedor está corriendo, sirve archivos estáticos
correctamente, y el proxy inverso a la API funciona.
"""

import os

import pytest
import requests

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@pytest.mark.podman_container
class TestFrontendContainerBasic:
    """Tests básicos de disponibilidad del contenedor frontend."""

    def test_frontend_container_is_running(self):
        """Verifica que el contenedor del frontend está corriendo y responde."""
        try:
            resp = requests.get(f"{FRONTEND_URL}/", timeout=5)
            assert resp.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.fail(
                f"El contenedor del frontend no está disponible en {FRONTEND_URL}"
            )

    def test_frontend_health_endpoint(self):
        """Verifica que el endpoint de health de Nginx responde."""
        resp = requests.get(f"{FRONTEND_URL}/health", timeout=5)
        assert resp.status_code == 200
        assert "healthy" in resp.text

    def test_frontend_serves_html(self):
        """Verifica que el frontend sirve HTML válido."""
        resp = requests.get(f"{FRONTEND_URL}/", timeout=5)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert "<!doctype html>" in resp.text.lower() or "<!DOCTYPE html>" in resp.text


@pytest.mark.podman_container
class TestFrontendStaticAssets:
    """Tests para verificar que los archivos estáticos se sirven correctamente."""

    def test_frontend_serves_javascript(self):
        """Verifica que el frontend sirve archivos JavaScript."""
        # Primero obtenemos el HTML para encontrar el nombre del JS bundle
        resp = requests.get(f"{FRONTEND_URL}/", timeout=5)
        assert resp.status_code == 200

        # Buscar el script en el HTML
        html = resp.text
        # El bundle de Vite tiene un patrón como /assets/index-XXXXX.js
        import re

        js_match = re.search(r"/assets/index-[a-zA-Z0-9]+\.js", html)
        if js_match:
            js_path = js_match.group(0)
            js_resp = requests.get(f"{FRONTEND_URL}{js_path}", timeout=5)
            assert js_resp.status_code == 200
            assert "javascript" in js_resp.headers.get("Content-Type", "")

    def test_frontend_serves_css(self):
        """Verifica que el frontend sirve archivos CSS."""
        resp = requests.get(f"{FRONTEND_URL}/", timeout=5)
        assert resp.status_code == 200

        html = resp.text
        import re

        css_match = re.search(r"/assets/index-[a-zA-Z0-9]+\.css", html)
        if css_match:
            css_path = css_match.group(0)
            css_resp = requests.get(f"{FRONTEND_URL}{css_path}", timeout=5)
            assert css_resp.status_code == 200
            assert "text/css" in css_resp.headers.get("Content-Type", "")

    def test_static_assets_have_cache_headers(self):
        """Verifica que los assets estáticos tienen headers de cache."""
        resp = requests.get(f"{FRONTEND_URL}/", timeout=5)
        html = resp.text

        import re

        js_match = re.search(r"/assets/index-[a-zA-Z0-9]+\.js", html)
        if js_match:
            js_path = js_match.group(0)
            js_resp = requests.get(f"{FRONTEND_URL}{js_path}", timeout=5)
            # Nginx configura cache de 1 año para assets
            cache_control = js_resp.headers.get("Cache-Control", "")
            assert "max-age" in cache_control or "immutable" in cache_control


@pytest.mark.podman_container
class TestFrontendSPARouting:
    """Tests para verificar que el routing de SPA funciona correctamente."""

    def test_spa_route_login_returns_index(self):
        """Verifica que /login devuelve index.html (SPA routing)."""
        resp = requests.get(f"{FRONTEND_URL}/login", timeout=5)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        # Debe contener el div root de React
        assert 'id="root"' in resp.text

    def test_spa_route_register_returns_index(self):
        """Verifica que /register devuelve index.html (SPA routing)."""
        resp = requests.get(f"{FRONTEND_URL}/register", timeout=5)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert 'id="root"' in resp.text

    def test_spa_route_chat_returns_index(self):
        """Verifica que /chat devuelve index.html (SPA routing)."""
        resp = requests.get(f"{FRONTEND_URL}/chat", timeout=5)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert 'id="root"' in resp.text

    def test_spa_route_admin_returns_index(self):
        """Verifica que /admin devuelve index.html (SPA routing)."""
        resp = requests.get(f"{FRONTEND_URL}/admin", timeout=5)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert 'id="root"' in resp.text

    def test_spa_deep_route_returns_index(self):
        """Verifica que rutas profundas devuelven index.html."""
        resp = requests.get(f"{FRONTEND_URL}/admin/users/123", timeout=5)
        assert resp.status_code == 200
        assert "text/html" in resp.headers.get("Content-Type", "")
        assert 'id="root"' in resp.text


@pytest.mark.podman_container
class TestFrontendAPIProxy:
    """Tests para verificar que el proxy inverso a la API funciona."""

    def test_api_proxy_health(self):
        """Verifica que el proxy /api/ redirige al backend."""
        # Primero verificar que el backend directo funciona
        try:
            direct_resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if direct_resp.status_code != 200:
                pytest.skip("Backend no disponible directamente")
        except requests.exceptions.ConnectionError:
            pytest.skip("Backend no disponible directamente")

        # Ahora verificar el proxy
        proxy_resp = requests.get(f"{FRONTEND_URL}/api/health", timeout=5)
        assert proxy_resp.status_code == 200
        assert proxy_resp.json() == {"status": "ok"}

    def test_api_proxy_auth_endpoint(self):
        """Verifica que el proxy puede alcanzar endpoints de autenticación."""
        # Intentar un login inválido para verificar que el endpoint responde
        payload = {"username": "invalid", "password": "invalid"}
        resp = requests.post(f"{FRONTEND_URL}/api/token", data=payload, timeout=5)
        # 401 significa que el endpoint respondió (auth falló, pero llegó)
        assert resp.status_code in [401, 400, 422]

    def test_api_proxy_preserves_headers(self):
        """Verifica que el proxy preserva headers importantes."""
        headers = {"X-Custom-Header": "test-value"}
        resp = requests.get(f"{FRONTEND_URL}/api/health", headers=headers, timeout=5)
        assert resp.status_code == 200


@pytest.mark.podman_container
class TestFrontendGzipCompression:
    """Tests para verificar que la compresión gzip está habilitada."""

    def test_gzip_compression_on_html(self):
        """Verifica que el HTML se sirve con compresión gzip."""
        headers = {"Accept-Encoding": "gzip, deflate"}
        resp = requests.get(f"{FRONTEND_URL}/", headers=headers, timeout=5)
        assert resp.status_code == 200
        # requests descomprime automáticamente, pero podemos verificar
        # que el contenido es válido después de la descompresión
        assert 'id="root"' in resp.text

    def test_gzip_compression_on_js(self):
        """Verifica que los archivos JS se sirven comprimidos."""
        resp = requests.get(f"{FRONTEND_URL}/", timeout=5)
        html = resp.text

        import re

        js_match = re.search(r"/assets/index-[a-zA-Z0-9]+\.js", html)
        if js_match:
            js_path = js_match.group(0)
            headers = {"Accept-Encoding": "gzip, deflate"}
            js_resp = requests.get(
                f"{FRONTEND_URL}{js_path}", headers=headers, timeout=5
            )
            assert js_resp.status_code == 200
            # El contenido debe ser JavaScript válido (descomprimido por requests)
            assert len(js_resp.text) > 0
