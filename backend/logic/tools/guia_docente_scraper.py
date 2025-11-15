import json
import re
from typing import Any

from bs4 import BeautifulSoup


class UGRTeachingGuideScraper:
    """
    Scraper para convertir guías docentes HTML de la UGR al formato JSON especificado.
    """

    def __init__(self, html_content: str, url: str = ""):
        """
        Inicializa el scraper con el contenido HTML.

        Args:
            html_content: Contenido HTML de la guía docente
            url: URL de la página (opcional)
        """
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.url = url
        self.data = self._initialize_data_structure()

    def _initialize_data_structure(self) -> dict[str, Any]:
        """Inicializa la estructura de datos JSON."""
        return {
            "url": self.url,
            "asignatura": "",
            "grado": "",
            "rama": "",
            "módulo": "",
            "materia": "",
            "curso": "",
            "semestre": "",
            "créditos": "",
            "tipo": "",
            "profesorado_y_tutorias": [],
            "prerrequisitos_o_recomendaciones": [],
            "breve_descripción_de_contenidos": [],
            "competencias": {"general_competences": []},
            "resultados_de_aprendizaje": [],
            "programa_de_contenidos_teóricos_y_prácticos": {
                "teórico": [],
                "práctico": [],
            },
            "bibliografía": {
                "bibliografía_fundamental": [],
                "bibliografía_complementaria": [],
            },
            "enlaces_recomendados": [],
            "metodología_docente": [],
            "evaluación": {
                "evaluación_ordinaria": [],
                "evaluación_extraordinaria": [],
                "evaluación_única_final": [],
            },
            "software_libre": [],
        }

    def _clean_text(self, text: str) -> str:
        """Limpia el texto eliminando espacios extra y caracteres especiales."""
        if not text:
            return ""
        # Reemplazar múltiples espacios por uno solo
        text = re.sub(r"\s+", " ", text)
        # Eliminar espacios al inicio y final
        text = text.strip()
        return text

    def _extract_basic_info(self):
        """Extrae información básica de la asignatura."""
        # Título de la página (asignatura)
        title = self.soup.find("h1", class_="page-title")
        if title:
            self.data["asignatura"] = self._clean_text(title.get_text())

        # Tabla de datos básicos
        table = self.soup.find("table", class_="datos-asignatura")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    header = self._clean_text(th.get_text())
                    value = self._clean_text(td.get_text())

                    if "Titulación" in header or "Grado" in header:
                        self.data["grado"] = value
                    elif "Curso" in header:
                        self.data["curso"] = value
                    elif "Semestre" in header:
                        self.data["semestre"] = value
                    elif "Créditos" in header:
                        self.data["créditos"] = value
                    elif "Tipo" in header:
                        self.data["tipo"] = value

        # Información de módulo y materia
        modulo_sections = self.soup.find_all("div", class_="datos-modulo-full")
        for section in modulo_sections:
            h2 = section.find("h2")
            value_div = section.find("div", class_="value")
            if h2 and value_div:
                header = self._clean_text(h2.get_text())
                value = self._clean_text(value_div.get_text())

                if "Rama" in header:
                    self.data["rama"] = value
                elif "Módulo" in header:
                    self.data["módulo"] = value
                elif "Materia" in header:
                    self.data["materia"] = value

    def _extract_profesorado(self):
        """Extrae información del profesorado y tutorías."""
        profesores: list[dict[str, str]] = []

        # Buscar sección de profesorado
        prof_section = self.soup.find("div", class_="profesores")
        if prof_section:
            # Buscar todos los profesores en las secciones teóricas y prácticas
            profesor_divs = self.soup.find_all("div", class_="profesor")
            for prof_div in profesor_divs:
                link = prof_div.find("a")
                if link:
                    nombre = self._clean_text(link.get_text())
                else:
                    # Si no hay link, buscar el texto directamente
                    nombre = self._clean_text(prof_div.get_text())

                # Buscar tutorías asociadas
                tutorias_text = ""

                # Buscar la sección de tutorías por nombre del profesor
                nombre_headers = self.soup.find_all("h3", class_="nombre")
                for header in nombre_headers:
                    if self._clean_text(header.get_text()) in nombre:
                        tutorias_section = header.find_next("div", class_="tutorias")
                        if tutorias_section:
                            tutorias_text = self._clean_text(
                                tutorias_section.get_text()
                            )
                            break

                if nombre and nombre not in [p["nombre"] for p in profesores]:
                    profesores.append({"nombre": nombre, "tutorias": tutorias_text})

        self.data["profesorado_y_tutorias"] = profesores

    def _extract_section_content(self, section_title: str) -> list[str]:
        """
        Extrae el contenido de una sección específica.

        Args:
            section_title: Título de la sección a buscar

        Returns:
            Lista de párrafos de contenido
        """
        content = []

        # Buscar el h2 con el título
        headers = self.soup.find_all("h2", class_="active-base")
        for header in headers:
            if section_title.lower() in header.get_text().lower():
                # Buscar el siguiente div col100
                parent = header.find_parent("div", class_="row")
                if parent:
                    content_div = parent.find("div", class_="col100")
                    if content_div:
                        # Extraer párrafos
                        paragraphs = content_div.find_all(["p", "li"])
                        for p in paragraphs:
                            text = self._clean_text(p.get_text())
                            if text and text not in content:
                                content.append(text)
                break

        return content

    def _extract_competencias(self):
        """Extrae las competencias."""
        competencias: dict[str, list[str]] = {"general_competences": []}

        headers = self.soup.find_all("h2", class_="active-base")
        for header in headers:
            if "Competencias" in header.get_text():
                parent = header.find_parent("div", class_="row")
                if parent:
                    # Buscar subsecciones
                    subsections = parent.find_all("h3", class_="subtituloform")
                    for subsection in subsections:
                        subsection_title = self._clean_text(subsection.get_text())

                        # Buscar la lista asociada
                        ul = subsection.find_next("ul")
                        if ul:
                            competencias_list = []
                            for li in ul.find_all("li", recursive=False):
                                text = self._clean_text(li.get_text())
                                if text:
                                    competencias_list.append(text)

                            # Mapear a la estructura correcta
                            if "general" in subsection_title.lower():
                                competencias["general_competences"] = competencias_list
                            else:
                                # Crear nueva clave para otras competencias
                                key = subsection_title.lower().replace(" ", "_")
                                competencias[key] = competencias_list

                break

        self.data["competencias"] = competencias

    def _extract_programa_contenidos(self):
        """Extrae el programa de contenidos teóricos y prácticos."""
        headers = self.soup.find_all("h2", class_="active-base")
        for header in headers:
            if "Programa de contenidos" in header.get_text():
                parent = header.find_parent("div", class_="row")
                if parent:
                    # Buscar secciones teórico y práctico
                    h3_headers = parent.find_all("h3")
                    for h3 in h3_headers:
                        h3_text = self._clean_text(h3.get_text())
                        content_div = h3.find_next("div", class_="col100")

                        if content_div:
                            content = []
                            # Extraer todo el contenido
                            paragraphs = content_div.find_all(["p", "li", "ol"])
                            for p in paragraphs:
                                text = self._clean_text(p.get_text())
                                if text:
                                    content.append(text)

                            if "teórico" in h3_text.lower():
                                self.data[
                                    "programa_de_contenidos_teóricos_y_prácticos"
                                ]["teórico"] = content
                            elif "práctico" in h3_text.lower():
                                self.data[
                                    "programa_de_contenidos_teóricos_y_prácticos"
                                ]["práctico"] = content

                break

    def _extract_bibliografia(self):
        """Extrae la bibliografía."""
        headers = self.soup.find_all("h2", class_="active-base")
        for header in headers:
            if "Bibliografía" in header.get_text():
                parent = header.find_parent("div", class_="row")
                if parent:
                    h3_headers = parent.find_all("h3")
                    for h3 in h3_headers:
                        h3_text = self._clean_text(h3.get_text())
                        content_div = h3.find_next("div", class_="col100")

                        if content_div:
                            biblio_items = []
                            # Extraer items de bibliografía
                            items = content_div.find_all("li")
                            if items:
                                for item in items:
                                    text = self._clean_text(item.get_text())
                                    if text:
                                        biblio_items.append(text)
                            else:
                                # Si no hay lista, extraer párrafos
                                paragraphs = content_div.find_all("p")
                                for p in paragraphs:
                                    text = self._clean_text(p.get_text())
                                    if text:
                                        biblio_items.append(text)

                            if "fundamental" in h3_text.lower():
                                self.data["bibliografía"][
                                    "bibliografía_fundamental"
                                ] = biblio_items
                            elif "complementaria" in h3_text.lower():
                                self.data["bibliografía"][
                                    "bibliografía_complementaria"
                                ] = biblio_items

                break

    def _extract_evaluacion(self):
        """Extrae la información de evaluación."""
        headers = self.soup.find_all("h2", class_="active-base")
        for header in headers:
            if "Evaluación" in header.get_text():
                parent = header.find_parent("div", class_="row")
                if parent:
                    h3_headers = parent.find_all("h3")
                    for h3 in h3_headers:
                        h3_text = self._clean_text(h3.get_text())
                        content_div = h3.find_next("div", class_="col100")

                        if content_div:
                            content = []
                            paragraphs = content_div.find_all(["p", "li"])
                            for p in paragraphs:
                                text = self._clean_text(p.get_text())
                                if text:
                                    content.append(text)

                            if "ordinaria" in h3_text.lower():
                                self.data["evaluación"][
                                    "evaluación_ordinaria"
                                ] = content
                            elif "extraordinaria" in h3_text.lower():
                                self.data["evaluación"][
                                    "evaluación_extraordinaria"
                                ] = content
                            elif "única final" in h3_text.lower():
                                self.data["evaluación"][
                                    "evaluación_única_final"
                                ] = content

                break

    def parse(self) -> dict[str, Any]:
        """
        Ejecuta el proceso completo de parsing.

        Returns:
            Diccionario con toda la información extraída
        """
        self._extract_basic_info()
        self._extract_profesorado()

        # Extraer secciones de texto
        self.data["prerrequisitos_o_recomendaciones"] = self._extract_section_content(
            "Prerrequisitos"
        )
        self.data["breve_descripción_de_contenidos"] = self._extract_section_content(
            "Breve descripción"
        )
        self.data["resultados_de_aprendizaje"] = self._extract_section_content(
            "Resultados de aprendizaje"
        )
        self.data["enlaces_recomendados"] = self._extract_section_content(
            "Enlaces recomendados"
        )
        self.data["metodología_docente"] = self._extract_section_content(
            "Metodología docente"
        )
        self.data["software_libre"] = self._extract_section_content("Software Libre")

        # Extraer secciones estructuradas
        self._extract_competencias()
        self._extract_programa_contenidos()
        self._extract_bibliografia()
        self._extract_evaluacion()

        return self.data

    def to_json(self, indent: int = 2) -> str:
        """
        Convierte los datos extraídos a formato JSON.

        Args:
            indent: Número de espacios para indentación

        Returns:
            String con el JSON formateado
        """
        return json.dumps(self.data, ensure_ascii=False, indent=indent)

    def save_to_file(self, filename: str, indent: int = 2):
        """
        Guarda los datos extraídos en un archivo JSON.

        Args:
            filename: Nombre del archivo de salida
            indent: Número de espacios para indentación
        """
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=indent)


# Ejemplo de uso
def main():
    """Función principal de ejemplo."""

    # Leer archivo HTML
    with open("guia_docente_tfg.html", encoding="utf-8") as f:
        html_content = f.read()

    # Crear scraper y parsear
    scraper = UGRTeachingGuideScraper(
        html_content, url="https://www.ugr.es/estudiantes/grados/..."
    )

    # Parsear y obtener datos
    data = scraper.parse()

    # Guardar en archivo JSON
    scraper.save_to_file("guia_docente_output.json")

    # O imprimir en consola
    print(scraper.to_json())

    print(f"\n✓ Asignatura extraída: {data['asignatura']}")
    print(f"✓ Grado: {data['grado']}")
    print(f"✓ Profesores encontrados: {len(data['profesorado_y_tutorias'])}")


if __name__ == "__main__":
    main()
