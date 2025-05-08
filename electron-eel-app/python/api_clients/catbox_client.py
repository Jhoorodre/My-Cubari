import os
import requests
import time
import traceback
import logging
import mimetypes

# === Configurações ===
CATBOX_API_URL = "https://catbox.moe/user/api.php"  # Constante para a URL da API
RATE_LIMIT_DELAY = 0.5  # Pequeno delay para evitar bloqueio da API (em segundos)

class CatboxClient:
    def __init__(self, userhash=None):
        self.userhash = userhash

    def update_userhash(self, userhash):
        """Atualiza o userhash do cliente."""
        self.userhash = userhash

    def upload_file(self, file_path):
        """Faz upload de um arquivo para o Catbox.

        Args:
            file_path (str): O caminho para o arquivo a ser enviado.

        Returns:
            tuple: (url, error) onde url é o URL do arquivo enviado ou None,
                   e error é uma mensagem de erro ou None.
        """
        if not os.path.exists(file_path):
            return None, f"Arquivo não encontrado: {file_path}"
        
        try:
            time.sleep(RATE_LIMIT_DELAY)  # Pequeno delay para evitar rate limiting
            with open(file_path, "rb") as f:
                data = {
                    'reqtype': 'fileupload',
                    'fileToUpload': (os.path.basename(file_path), f, mimetypes.guess_type(file_path)[0] or 'application/octet-stream')
                }
                if self.userhash:
                    data['userhash'] = self.userhash

                response = requests.post(CATBOX_API_URL, files=data)
                response.raise_for_status()
                return response.text, None
        except Exception as e:
            return None, f"Erro ao enviar arquivo: {file_path}\\n{str(e)}"

    def create_album(self, title, description, file_urls):
        """Cria um álbum no Catbox.moe com os arquivos fornecidos."""
        if not self.userhash:
            # Idealmente, logar ou levantar uma exceção mais específica
            logging.error("Userhash não configurado para criar álbum no Catbox.")
            return None, "Userhash não configurado"

        data = {
            "reqtype": "createalbum",
            "userhash": self.userhash,
            "title": title,
            "desc": description,
            "files": " ".join(file_urls),
        }
        try:
            response = requests.post(CATBOX_API_URL, data=data)
            response.raise_for_status()
            return response.text, None  # Retorna a URL do álbum e nenhum erro
        except Exception as e:
            logging.error(f"Erro ao criar álbum no Catbox: {e}")
            traceback.print_exc()
            return None, str(e) # Retorna None para URL e a mensagem de erro
