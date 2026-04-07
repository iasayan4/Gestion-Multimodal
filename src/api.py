import os
import shutil
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Cargar entorno y dependencias base
from dotenv import load_dotenv
load_dotenv()

from src.modules import text_parser, audio_processor, image_ocr, document_parser

class TextPayload(BaseModel):
    content: str
    
app = FastAPI(title="Multimodal Orchestrator API", description="Antigravity Core Backend")

# Habilitar CORS para Sandbox local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "core": "Antigravity Multimodal Active"}

@app.post("/api/process_text")
async def process_text_endpoint(payload: TextPayload):
    content = payload.content
    print(f"[API] Recibido payload de texto/link: {content}")
    # Enrutador heurístico básico local
    if content.startswith("http"):
        result = text_parser.process_text(content)
    else:
        result = text_parser.process_text(content)
    return result

@app.post("/api/process_file")
async def process_file_endpoint(file: UploadFile = File(...)):
    print(f"[API] Recibido archivo: {file.filename}")
    filename = file.filename.lower()
    
    # 1. Zero-Leak Payload Buffer: Secure TMP creation
    os.makedirs("tmp", exist_ok=True)
    file_path = os.path.join("tmp", file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # 2. Análisis Sensorial Crudo
        if filename.endswith(('.pdf', '.xls', '.xlsx')):
            result = document_parser.process_document(file_path)
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            result = image_ocr.process_image(file_path)
        elif filename.endswith(('.mp3', '.wav', '.m4a', '.mp4', '.webm')):
            result = audio_processor.process_audio(file_path)
        else:
            result = {"status": "error", "message": "Formato no soportado en Sandbox"}
    finally:
        # 3. Limpieza inmediata (Amnesia del sistema)
        if os.path.exists(file_path):
            os.remove(file_path)
        
    return result
