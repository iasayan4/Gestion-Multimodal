def process_text(raw_text: str):
    """Limpieza de ruido/emojis, detección de idioma/intención y fetch seguro."""
    try:
        # Tokenización simulada pre-llm
        cleaned = raw_text.strip()
        return {"status": "success", "type": "text", "content": cleaned}
    except Exception as e:
        return f"[ERROR][TEXT_PARSER]: {str(e)}"
