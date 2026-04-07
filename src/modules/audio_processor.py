import os
import json
import uuid
import subprocess
import speech_recognition as sr
import imageio_ffmpeg
from openai import OpenAI

# Inicialización de OpenAI
client = OpenAI()

def process_audio(file_path: str):
    """Bypass Whisper: Transcripción híbrida FFmpeg + Google API + GPT-4o-mini"""
    temp_wav = None
    try:
        print(f"[AUDIO_PROCESSOR_HYBRID] Iniciando procesamiento de: {file_path}")
        
        # 1. Normalización con FFmpeg
        os.makedirs("tmp", exist_ok=True)
        temp_wav = os.path.abspath(f"tmp/{uuid.uuid4().hex}.wav")
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        
        # Verificamos si el archivo de entrada existe
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"El archivo {file_path} no fue encontrado.")

        print(f"[AUDIO_PROCESSOR_HYBRID] Extrayendo audio a WAV (16kHz Mono)...")
        # Forzamos formato wav y codec pcm_s16le
        command = [
            ffmpeg_exe,
            "-y",
            "-i", os.path.abspath(file_path),
            "-vn", 
            "-ac", "1", 
            "-ar", "16000", 
            "-f", "wav",
            temp_wav
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[FFMPEG ERROR] {result.stderr}")
            raise Exception("FFmpeg falló al procesar el archivo.")

        # Verificamos tamaño del wav resultante
        wav_size = os.path.getsize(temp_wav)
        print(f"[AUDIO_PROCESSOR_HYBRID] WAV generado: {wav_size} bytes")
        if wav_size < 1000:
             raise Exception("El audio extraído parece estar vacío o corrupto.")

        # 2. Transcripción Híbrida
        r = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            print("[AUDIO_PROCESSOR_HYBRID] Escuchando archivo con Recognizer...")
            # Ajustamos un poco para el ruido de fondo (WhatsApp videos suelen tener siseo)
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = r.record(source)
            
            print("[AUDIO_PROCESSOR_HYBRID] Enviando a Google Speech API (es-ES)...")
            try:
                transcription = r.recognize_google(audio_data, language="es-ES")
            except sr.UnknownValueError:
                print("[AUDIO_PROCESSOR_HYBRID] Google no entendió el audio (UnknownValue). Reintentando con en-US...")
                try:
                    transcription = r.recognize_google(audio_data, language="en-US")
                except sr.UnknownValueError:
                    return {
                        "status": "error", 
                        "message": "La IA no detectó voz legible en el archivo. ¿El audio es muy bajo o está en silencio?"
                    }
            
        print(f"[AUDIO_PROCESSOR_HYBRID] Transcripción: {transcription[:100]}...")

        # Limpieza
        if os.path.exists(temp_wav):
            os.remove(temp_wav)

        # 3. Análisis Cognitivo
        print("[AUDIO_PROCESSOR_HYBRID] Solicitando inferencia a GPT-4o-mini...")
        prompt_system = (
            "Eres el Auditor de Audio Multimodal Antigravity. Analiza esta transcripción. "
            "Responde SOLO en JSON: {'intent', 'tone', 'summary'}. "
            "Si el texto parece basura o no tiene sentido, indica 'insuficiente' en los campos."
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_system},
                {"role": "user", "content": f"Transcripción:\n{transcription[:8000]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        cognitive_data = json.loads(response.choices[0].message.content)

        return {
            "status": "success", 
            "type": "audio_inference_hybrid", 
            "cognitive_inference": cognitive_data,
            "raw_snippet": transcription[:150] + "..."
        }
    except Exception:
        import traceback
        error_msg = f"[ERROR][AUDIO_PROCESSOR_HYBRID]: {traceback.format_exc()}"
        print(error_msg)
        if temp_wav and os.path.exists(temp_wav):
             os.remove(temp_wav)
        return {"status": "error", "message": error_msg}
