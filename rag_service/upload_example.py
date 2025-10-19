#!/usr/bin/env python3
"""
Script de ejemplo para subir documentos al servicio RAG.

Uso:
    python upload_example.py archivo.pdf "Lógica Difusa" apuntes "Conjuntos difusos"
    
O editar las variables al final del script y ejecutar:
    python upload_example.py
"""

import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuración
RAG_URL = "http://localhost:8081"


def upload_document(
    file_path: str,
    asignatura: str,
    tipo_documento: str,
    tema: str = None,
    autor: str = None,
    fuente: str = "PRADO UGR",
    idioma: str = "es",
    licencia: str = None
):
    """
    Sube un documento al servicio RAG.
    
    Args:
        file_path: Ruta al archivo (PDF, TXT)
        asignatura: Nombre de la asignatura
        tipo_documento: Tipo: apuntes, ejercicios, examenes, practicas
        tema: Tema específico (opcional)
        autor: Autor del documento (opcional)
        fuente: Fuente del documento (default: "PRADO UGR")
        idioma: Código de idioma (default: "es")
        licencia: Licencia del documento (opcional)
    
    Returns:
        dict: Resultado de la operación o None si hubo error
    """
    url = f"{RAG_URL}/upload"
    
    # Verificar que el archivo existe
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Error: Archivo no encontrado: {file_path}")
        return None
    
    # Verificar extensión
    valid_extensions = ['.pdf', '.txt', '.docx', '.md', '.markdown']
    if file_path.suffix.lower() not in valid_extensions:
        print(f"❌ Error: Extensión no soportada: {file_path.suffix}")
        print(f"   Extensiones válidas: {', '.join(valid_extensions)}")
        return None
    
    # Preparar metadata
    metadata = {
        "asignatura": asignatura,
        "tipo_documento": tipo_documento,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "fuente": fuente,
        "idioma": idioma,
        "auto_index": True  # Indexar automáticamente
    }
    
    if tema:
        metadata["tema"] = tema
    if autor:
        metadata["autor"] = autor
    if licencia:
        metadata["licencia"] = licencia
    
    # Preparar petición
    print(f"\n{'='*60}")
    print(f"📤 SUBIENDO DOCUMENTO")
    print(f"{'='*60}")
    print(f"Archivo:     {file_path.name}")
    print(f"Tamaño:      {file_path.stat().st_size / 1024:.2f} KB")
    print(f"Asignatura:  {asignatura}")
    print(f"Tipo:        {tipo_documento}")
    if tema:
        print(f"Tema:        {tema}")
    if autor:
        print(f"Autor:       {autor}")
    print(f"{'='*60}")
    
    try:
        files = {'file': open(file_path, 'rb')}
        print()
        data = {'metadata': json.dumps(metadata)}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ¡ÉXITO!")
            print(f"{'='*60}")
            print(f"📄 Archivo:       {result['filename']}")
            print(f"🆔 ID Documento:  {result['doc_id']}")
            print(f"🔢 Chunks:        {result['indexed_count']}")
            print(f"⏰ Timestamp:     {result['timestamp']}")
            print(f"{'='*60}\n")
            return result
        else:
            print(f"\n❌ ERROR {response.status_code}")
            print(f"{'='*60}")
            print(response.text)
            print(f"{'='*60}\n")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: No se puede conectar con el servicio RAG")
        print(f"   URL: {url}")
        print(f"   ¿Está el servicio corriendo?")
        print(f"   Ejecuta: docker-compose up rag-service\n")
        return None
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {e}\n")
        return None


def list_files(asignatura: str = None, tipo_documento: str = None):
    """
    Lista archivos en el servicio.
    
    Args:
        asignatura: Filtrar por asignatura (opcional)
        tipo_documento: Filtrar por tipo de documento (opcional)
    """
    url = f"{RAG_URL}/files"
    
    params = {}
    if asignatura:
        params['asignatura'] = asignatura
    if tipo_documento:
        params['tipo_documento'] = tipo_documento
    
    try:
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{'='*60}")
            print(f"📁 ARCHIVOS EN EL SISTEMA")
            print(f"{'='*60}")
            print(f"Total: {data['total_files']} archivos\n")
            
            if data['files']:
                for i, file in enumerate(data['files'], 1):
                    print(f"{i:3}. {file}")
            else:
                print("No hay archivos.")
            
            print(f"{'='*60}\n")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: No se puede conectar con el servicio RAG\n")


def list_subjects():
    """Lista todas las asignaturas disponibles."""
    url = f"{RAG_URL}/subjects"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{'='*60}")
            print(f"📚 ASIGNATURAS DISPONIBLES")
            print(f"{'='*60}")
            print(f"Total: {data['total_subjects']} asignaturas\n")
            
            for i, subject in enumerate(data['subjects'], 1):
                print(f"{i}. {subject}")
            
            print(f"{'='*60}\n")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: No se puede conectar con el servicio RAG\n")


def search_documents(query: str, asignatura: str = None, top_k: int = 3):
    """
    Busca en los documentos.
    
    Args:
        query: Consulta de búsqueda
        asignatura: Filtrar por asignatura (opcional)
        top_k: Número de resultados (default: 3)
    """
    url = f"{RAG_URL}/search"
    
    payload = {
        "query": query,
        "top_k": top_k
    }
    
    if asignatura:
        payload['asignatura'] = asignatura
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{'='*60}")
            print(f"🔍 RESULTADOS DE BÚSQUEDA")
            print(f"{'='*60}")
            print(f"Consulta: {query}")
            print(f"Total:    {data['total_results']} resultados\n")
            
            for i, result in enumerate(data['results'], 1):
                print(f"{'-'*60}")
                print(f"Resultado #{i}")
                print(f"{'-'*60}")
                print(f"Score:       {result['score']:.4f}")
                print(f"Asignatura:  {result['metadata']['asignatura']}")
                print(f"Tipo:        {result['metadata']['tipo_documento']}")
                print(f"Tema:        {result['metadata'].get('tema', 'N/A')}")
                print(f"\nContenido:")
                print(f"{result['content'][:300]}...")
                print()
            
            print(f"{'='*60}\n")
        else:
            print(f"❌ Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: No se puede conectar con el servicio RAG\n")


def check_health():
    """Verifica el estado del servicio."""
    url = f"{RAG_URL}/health"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n{'='*60}")
            print(f"💚 ESTADO DEL SERVICIO")
            print(f"{'='*60}")
            print(f"Estado:         {data['status']}")
            print(f"Qdrant:         {'✅ Conectado' if data['qdrant_connected'] else '❌ Desconectado'}")
            
            if 'collection' in data:
                col = data['collection']
                print(f"\nColección:      {col['name']}")
                print(f"Documentos:     {col['points_count']}")
                print(f"Vectores:       {col['vectors_count']}")
            
            print(f"{'='*60}\n")
            return True
        else:
            print(f"❌ Servicio no disponible (código {response.status_code})\n")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n{'='*60}")
        print(f"❌ SERVICIO NO DISPONIBLE")
        print(f"{'='*60}")
        print(f"No se puede conectar con: {url}")
        print(f"\nVerifica que el servicio esté corriendo:")
        print(f"  docker ps | grep rag-service")
        print(f"\nO inícialo con:")
        print(f"  docker-compose up rag-service")
        print(f"{'='*60}\n")
        return False


def main():
    """Función principal."""
    print("\n" + "="*60)
    print("  📤 SCRIPT DE UPLOAD - SERVICIO RAG")
    print("="*60)
    
    # Verificar estado del servicio
    if not check_health():
        return
    
    # Modo interactivo si no hay argumentos
    if len(sys.argv) == 1:
        print("\n🔧 MODO INTERACTIVO\n")
        
        # Preguntar qué hacer
        print("¿Qué deseas hacer?")
        print("1. Subir un documento")
        print("2. Listar archivos")
        print("3. Listar asignaturas")
        print("4. Buscar en documentos")
        print("5. Salir")
        
        opcion = input("\nOpción (1-5): ").strip()
        
        if opcion == "1":
            file_path = input("Ruta del archivo: ").strip()
            asignatura = input("Asignatura: ").strip()
            tipo_documento = input("Tipo (apuntes/ejercicios/examenes/practicas): ").strip()
            tema = input("Tema (opcional, Enter para omitir): ").strip() or None
            autor = input("Autor (opcional, Enter para omitir): ").strip() or None
            licencia = input("Licencia (opcional, Enter para omitir): ").strip() or None
            upload_document(file_path, asignatura, tipo_documento, tema, autor, licencia=licencia)
        elif opcion == "2":
            asignatura = input("Filtrar por asignatura (Enter para todas): ").strip() or None
            list_files(asignatura)
        elif opcion == "3":
            list_subjects()
        elif opcion == "4":
            query = input("Búsqueda: ").strip()
            asignatura = input("Filtrar por asignatura (Enter para todas): ").strip() or None
            search_documents(query, asignatura)
        else:
            print("Saliendo...\n")
    # Modo con argumentos
    elif len(sys.argv) >= 4:
        file_path = sys.argv[1]
        asignatura = sys.argv[2]
        tipo_documento = sys.argv[3]
        tema = sys.argv[4] if len(sys.argv) > 4 else None
        autor = sys.argv[5] if len(sys.argv) > 5 else None
        licencia = sys.argv[6] if len(sys.argv) > 6 else None
        upload_document(file_path, asignatura, tipo_documento, tema, autor, licencia=licencia)
    else:
        print("\n📖 USO:")
        print(f"  {sys.argv[0]} <archivo> <asignatura> <tipo> [tema] [autor] [licencia]")
        print("\nEJEMPLOS:")
        print(f'  {sys.argv[0]} apuntes.pdf "Lógica Difusa" apuntes "Conjuntos difusos" "CC-BY-4.0"')
        print(f'  {sys.argv[0]} ejercicios.pdf "Álgebra" ejercicios')
        print("\nO ejecuta sin argumentos para modo interactivo:")
        print(f"  {sys.argv[0]}")
        print()


if __name__ == "__main__":
    main()
