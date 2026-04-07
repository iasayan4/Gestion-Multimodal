def process_image(file_path: str):
    """Extracción de frames y OCR. Clasificación de IDs/Facturas."""
    try:
        # Aquí se integraría Vision AI / Tesseract
        return {"status": "success", "type": "image", "file": file_path}
    except Exception as e:
        return f"[ERROR][IMAGE_OCR]: {str(e)}"
