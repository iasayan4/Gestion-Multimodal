import os
import json
import base64
from openai import OpenAI

client = OpenAI()

def encode_image(image_path: str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_image(file_path: str):
    """Integración Pura Visión Artificial. Base64 a GPT-4o-mini para OCR Inteligente."""
    try:
        print(f"[IMAGE_OCR] Analizando espectro visual de: {file_path}")
        
        # 1. Codificación Cruda
        base64_image = encode_image(file_path)
        
        # 2. Visión Artificial Deep Perception
        print("[IMAGE_OCR] Invocando Visión en GPT-4o-mini...")
        prompt_system = (
            "Eres el Subsistema de Visión de Antigravity. Tu misión es extraer TODO el texto legible (OCR) de la imagen suministrada "
            "y deducir qué clase de documento/imagen es (Factura, ID, Gráfico, etc.). "
            "Devuelve la respuesta SOLO en JSON con las llaves 'document_type', 'ocr_text' y 'summary'."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analiza esta imagen gráfica:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "low" # Mitigación de tokens visuales
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        cognitive_data = json.loads(response.choices[0].message.content)

        return {
            "status": "success", 
            "type": "computer_vision", 
            "cognitive_inference": cognitive_data,
            "raw_snippet": str(cognitive_data.get('ocr_text', ''))[:150] + "..."
        }
    except Exception as e:
        print(f"[ERROR][IMAGE_OCR]: {str(e)}")
        return {"status": "error", "message": f"[ERROR][IMAGE_OCR]: {str(e)}"}
