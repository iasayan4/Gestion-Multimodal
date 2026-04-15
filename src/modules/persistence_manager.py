import os
import json
import subprocess
from datetime import datetime

def persist_to_github(payload: dict, task_name: str = "analysis") -> dict:
    """
    Herramienta asilada (MCP Tool) para guardar un JSON localmente y subirlo al repositorio
    utilizando GITHUB_TOKEN y apuntando específicamente a MCP_SERVER_URL.
    Diseñado para ser invocado explícitamente bajo demanda por el Agente MCP.
    """
    token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("MCP_SERVER_URL")
    
    if not token or not repo_url:
        return {"status": "error", "message": "[ERROR] Faltan credenciales MCP_SERVER_URL o GITHUB_TOKEN."}

    # Transformar la URL para inyectar el token temporalmente
    # Ej: https://github.com/... -> https://ghp_...X@github.com/...
    if repo_url.startswith("https://") and "@" not in repo_url:
        auth_url = repo_url.replace("https://", f"https://{token}@")
    else:
        auth_url = repo_url
        
    try:
        print(f"[{task_name.upper()}] Petición de persistencia iniciada.")
        
        # 1. Asegurar directorio 'records' para almacenar la memoria
        records_dir = os.path.join(os.getcwd(), "records")
        os.makedirs(records_dir, exist_ok=True)
        
        # 2. Nombrar archivo de memoria externa
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task_name}_{timestamp}.json"
        filepath = os.path.join(records_dir, filename)
        
        # 3. Serializar Payload
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, ensure_ascii=False)
            
        print(f"[PERSISTENCE] Archivo {filename} creado físicamente.")
        
        # 4. Inyectar Credencial Temporal y hacer el commit individual
        subprocess.run(["git", "remote", "set-url", "origin", auth_url], check=True, capture_output=True)
        subprocess.run(["git", "add", filepath], check=True, capture_output=True)
        
        commit_msg = f"memoria(mcp): auto-persistencia delegada de {task_name}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)
        
        # 5. Push silencioso a la nube
        print(f"[PERSISTENCE] Subiendo {filename} a {repo_url}...")
        push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
        
        if push_result.returncode != 0 and "Everything up-to-date" not in push_result.stderr:
            raise Exception(f"Git Push falló: {push_result.stderr}")
                
        # 6. Zero-Leak Policy Lock: Borramos el token expuesto del .git/config
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=False, capture_output=True)

        return {
            "status": "success",
            "message": f"Payload persistido en la nube como {filename}",
            "file": filename,
            "repo": repo_url
        }
        
    except Exception as e:
        # Acción de rescate (Borrar token de origin en caso de CRASH)
        subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=False, capture_output=True)
        error_msg = f"[ERROR][PERSISTENCE]: {str(e)}"
        print(error_msg)
        return {"status": "error", "message": error_msg}
