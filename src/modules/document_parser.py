import os
import json
from openai import OpenAI
import PyPDF2
# pandas se usaría aquí si agregamos bifurcación XLS posterior

client = OpenAI()

def process_document(file_path: str):
    """Extrae texto usando PyPDF2 y luego comprime y manda a GPT-4o-mini."""
    try:
        print(f"[DOCUMENT_PARSER] Analizando estructura documental de: {file_path}")
        
        # 1. Extracción Estática Anti-Token-Leak
        extracted_text = ""
        if file_path.lower().endswith(".pdf"):
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                # Extraemos máx las primeras 10 páginas para evadir fuga de saldo
                num_pages = min(len(reader.pages), 10)
                for page_num in range(num_pages):
                    page = reader.pages[page_num]
                    # Limpiamos null chars o saltos extraños
                    extracted_text += page.extract_text() + "\n"
        else:
            return {"status": "error", "message": "Solo PDF implementado en esta release."}

        # Restringimos a aprox 3000 tokens MAX
        extracted_text = extracted_text[:12000]
        
        # 2. Análisis Computacional
        print("[DOCUMENT_PARSER] Destilando información con GPT-4o-mini...")
        prompt_system = (
            "Eres el Analista Documental Antigravity. Tu trabajo es leer texto extraído de un PDF. "
            "Aisla la intención (contrato, factura, informe), enumera las Entidades Clave detectadas (nombres, fechas, precios) y da un Summary."
            "Responde estrictamente en JSON con llaves 'document_intent', 'key_entities' y 'summary'."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": f"Documento Extraído:\n{extracted_text}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        
        cognitive_data = json.loads(response.choices[0].message.content)

        return {
            "status": "success", 
            "type": "document_inference", 
            "cognitive_inference": cognitive_data,
            "raw_snippet": extracted_text[:150].replace('\n', ' ') + "..."
        }
    except Exception as e:
        print(f"[ERROR][DOCUMENT_PARSER]: {str(e)}")
        return {"status": "error", "message": f"[ERROR][DOCUMENT_PARSER]: {str(e)}"}
