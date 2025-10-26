import json
import requests

url = "http://localhost:8080/scrape_guia"
with open("tmp/guia_docente_tfg.html", "r", encoding="utf-8") as f:
    html = f.read()

payload = {"html_content": html, "url": "https://example.com/guia"}
resp = requests.post(url, json=payload, timeout=30)
print(resp.status_code)
print(json.dumps(resp.json(), ensure_ascii=False, indent=2))