\
import os
import requests
import time
import traceback
import logging # Adicionado para o logging em create_album_catbox

# === Configurações ===
CATBOX_API_URL = "https://catbox.moe/user/api.php"  # Constante para a URL da API
RATE_LIMIT_DELAY = 0.5  # Pequeno delay para evitar bloqueio da API (em segundos)

def upload_file_catbox(filepath, userhash):
    """Faz upload de um único arquivo para o Catbox.moe"""
    if not os.path.exists(filepath):
        return None, f"Arquivo não encontrado: {filepath}"
    
    try:
        time.sleep(RATE_LIMIT_DELAY)  # Pequeno delay para evitar rate limiting
        with open(filepath, "rb") as f:
            files = {"fileToUpload": f}
            data = {"reqtype": "fileupload", "userhash": userhash}
            response = requests.post(CATBOX_API_URL, data=data, files=files)
            response.raise_for_status()
            return response.text, None
    except Exception as e:
        return None, f"Erro ao enviar arquivo: {filepath}\\n{str(e)}"

def create_album_catbox(title, description, file_urls, userhash):
    """Cria um álbum no Catbox.moe com os arquivos fornecidos"""
    data = {
        "reqtype": "createalbum",
        "userhash": userhash,
        "title": title,
        "desc": description,
        "files": " ".join(file_urls),
    }
    try:
        response = requests.post(CATBOX_API_URL, data=data)
        response.raise_for_status()
        return response.text
    except Exception as e:
        # Mantido o logging de erro como estava em manga_processor.py, 
        # mas usando o módulo logging importado.
        logging.error(f"Erro ao criar álbum:\\n{e}") 
        traceback.print_exc()
        return None
