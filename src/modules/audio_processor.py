import os
import json
from openai import OpenAI

# Zero-Leak Policy env load
client = OpenAI()

def process_audio(file_path: str):
    """Integra Whisper para Transcripción + LLM para Diarización Cognitiva."""
    try:
        print(f"[AUDIO_PROCESSOR] Procesando archivo de audio: {file_path}")
        
        # 1. Pipeline Auditivo Crudo (OpenAI Whisper)
        with open(file_path, "rb") as audio_file:
            print("[AUDIO_PROCESSOR] Invocando Whisper API...")
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file,
                response_format="text"
            )
        
        # 2. Análisis Cognitivo
        print("[AUDIO_PROCESSOR] Invocando GPT-4o-mini para Análisis Diarizado / Intent...")
        
        prompt_system = (
            "Eres el Analista Multimodal Antigravity (Auditor). Tienes la transcripción de un audio. "
            "Extrae metadatos: Intención Principal, Tono Deducido (Urgente, Amistoso, Formal, etc.) y Resumen. "
            "Responde SOLO en JSON válido con las llaves: 'intent', 'tone', 'summary'."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": transcription[:8000]}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        cognitive_data = json.loads(response.choices[0].message.content)

        return {
            "status": "success", 
            "type": "audio_inference", 
            "cognitive_inference": cognitive_data,
            "raw_snippet": transcription[:150] + "..."
        }
    except Exception as e:
        print(f"[ERROR][AUDIO_PROCESSOR]: {str(e)}")
        return {"status": "error", "message": f"[ERROR][AUDIO_PROCESSOR]: {str(e)}"}
