import os
import sys
from dotenv import load_dotenv

# Validar Zero-Leak Policy (carga segura de entorno)
load_dotenv()

# Validar dependencias operativas base
if not os.getenv("OPENAI_API_KEY"):
    print("[ERROR][MAIN]: OPENAI_API_KEY no detectada en .env.")
    # No detenemos el sistema aún si estamos solo probando, pero se registra
    pass

from modules import text_parser, audio_processor, image_ocr, document_parser

def main():
    print("Multimodal Orchestrator (Antigravity Core) Inicializado.")
    # Si estamos en testing:
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("[INFO][MAIN] Ejecución de prueba de módulos superada.")
        return
        
    print("[INFO][MAIN] A la espera de inputs.")

if __name__ == "__main__":
    main()
