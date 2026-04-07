import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

# Inicializar cliente OpenAI bajo Zero-Leak Policy (key se extrae automágicamente del .env)
client = OpenAI()

def fetch_url_content(url: str) -> str:
    """Realiza un GET seguro y limpia el HTML asimilando solo el texto (Anti token-leak)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Antigravity/1.0"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    # Parsear y limpiar etiquetas que generan overhead
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    # Obtener el texto purificado
    text = soup.get_text(separator=' ', strip=True)
    # Token mitigation: recortar los primeros 8000 caracteres (aprox. 2000 tokens)
    return text[:8000]

def analyze_with_llm(content: str) -> dict:
    """Envía el contenido compacto al GPT-4o Mini para inferencia estructurada."""
    prompt_system = (
        "Eres el Analista Multimodal Antigravity. Tu misión es devorar la carga de texto y extraer metadatos: "
        "Intención Principal, Idioma Detectado, y un Resumen Ejecutivo. "
        "Responde SOLO en formato JSON válido con las llaves 'intent', 'language' y 'summary'."
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": f"Analiza esta carga cruda:\n{content}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    import json
    return json.loads(response.choices[0].message.content)

def process_text(raw_text: str):
    """Limpieza de ruido/emojis, detección y fetch seguro."""
    try:
        content_to_analyze = raw_text.strip()
        is_url = content_to_analyze.startswith("http")
        
        # 1. Pipeline de Fetching (Si aplica)
        if is_url:
            print(f"[TEXT_PARSER] URL Detectada. Iniciando Scraping inteligente de: {content_to_analyze}")
            content_to_analyze = fetch_url_content(content_to_analyze)
        else:
            print("[TEXT_PARSER] Payload crudo de texto detectado.")
            # Restricción pasiva de mitigación de tokens (8000 char max)
            content_to_analyze = content_to_analyze[:8000]

        # 2. Análisis Cognitivo
        print("[TEXT_PARSER] Invocando LLM (gpt-4o-mini)...")
        cognitive_data = analyze_with_llm(content_to_analyze)

        # 3. Retorno Estructurado al Orquestador
        return {
            "status": "success",
            "type": "url_extraction" if is_url else "text_inference",
            "cognitive_inference": cognitive_data,
            "raw_snippet": content_to_analyze[:150] + "..." # Muestra corta en frontend
        }

    except Exception as e:
        print(f"[ERROR][TEXT_PARSER]: {str(e)}")
        return {"status": "error", "message": f"[ERROR][TEXT_PARSER]: {str(e)}"}
