import json
from backend.logic.tools.guia_docente_scraper import UGRTeachingGuideScraper


def test_scraper_basic_fields():
    html = '''
    <html>
      <body>
        <h1 class="page-title">Trabajo Fin de Grado (TFG)</h1>
        <table class="datos-asignatura">
          <tr><th>Grado</th><td>Ingeniería Informática</td></tr>
          <tr><th>Curso</th><td>4</td></tr>
          <tr><th>Créditos</th><td>12</td></tr>
        </table>

        <h2 class="active-base">Prerrequisitos</h2>
        <div class="row">
          <div class="col100">
            <p>Conocimientos básicos de programación y algoritmia.</p>
          </div>
        </div>

        <h2 class="active-base">Breve descripción</h2>
        <div class="row">
          <div class="col100">
            <p>Proyecto de fin de grado orientado a la Ingeniería.</p>
          </div>
        </div>
      </body>
    </html>
    '''

    scraper = UGRTeachingGuideScraper(html, url="http://example.com/guia")
    data = scraper.parse()

    assert data["asignatura"] == "Trabajo Fin de Grado (TFG)"
    assert data["grado"] == "Ingeniería Informática"
    assert data["curso"] == "4"
    assert data["créditos"] == "12"

    # Sections
    assert "Conocimientos básicos de programación y algoritmia." in data["prerrequisitos_o_recomendaciones"]
    assert "Proyecto de fin de grado orientado a la Ingeniería." in data["breve_descripción_de_contenidos"]

    # JSON serialization
    js = scraper.to_json()
    parsed = json.loads(js)
    assert parsed["url"] == "http://example.com/guia"

