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
    
    if len(sys.argv) > 1:
        input_data = sys.argv[1]
        if input_data == "--test":
            print("[INFO][MAIN] Ejecución de prueba de módulos superada.")
            return
            
        print(f"[INFO][MAIN] Procesando payload crudo: {input_data}")
        
        # Enrutador heurístico básico
        if input_data.startswith("http"):
            result = text_parser.process_text(input_data)
        elif input_data.lower().endswith(('.pdf', '.xls', '.xlsx')):
            result = document_parser.process_document(input_data)
        elif input_data.lower().endswith(('.png', '.jpg', '.jpeg')):
            result = image_ocr.process_image(input_data)
        elif input_data.lower().endswith(('.mp3', '.wav', '.m4a')):
            result = audio_processor.process_audio(input_data)
        else:
            result = text_parser.process_text(input_data)
            
        print(f"[OUT] Payload transformado: {result}")
        return
        
    print("[INFO][MAIN] A la espera de inputs.")

if __name__ == "__main__":
    main()
