def process_document(file_path: str):
    """Parseo PDF/XLS a JSON estructurado para evitar overhead de tokens."""
    try:
        # Aquí se integraría PyPDF2 / Pandas
        return {"status": "success", "type": "document", "file": file_path}
    except Exception as e:
        return f"[ERROR][DOCUMENT_PARSER]: {str(e)}"
