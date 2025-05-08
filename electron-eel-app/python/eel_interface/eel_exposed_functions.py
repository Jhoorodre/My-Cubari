import eel
import os
import json
import logging
from api_clients.catbox_client import CatboxClient
from api_clients.buzzheavier_client import (
    upload_file_buzzheavier,
    test_buzzheavier_connection as test_buzz_conn_internal,
    create_buzzheavier_folder
)
from core.config_manager import ConfigManager
from core.file_system_utils import (
    selecionar_arquivos as fs_selecionar_arquivos,
    selecionar_pasta as fs_selecionar_pasta,
    listar_arquivos_pasta as fs_listar_arquivos_pasta,
    get_image_files_from_dir
)
# MODIFICADO: Nomes das funções importadas
from core.processing_logic import process_manga_chapter, parallel_upload_files

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função de utilidade para log no frontend e console
def log_message(message, level='info'):
    """Envia uma mensagem de log para o console Python e para o frontend via Eel."""
    print(f"[{level.upper()}] {message}") # Log no console Python
    try:
        if eel is not None and hasattr(eel, 'log_to_frontend'): # Verifica se eel está disponível e a função existe no JS
            eel.log_to_frontend(message, level) # Chama a função JS para logar no frontend
    except Exception as e:
        print(f"[ERROR] Falha ao enviar log para o frontend: {e}")

@eel.expose
def selecionar_arquivos_eel(): # Renomeado para evitar conflito com a função original, se importada diretamente
    """Abre um diálogo para selecionar arquivos (exposto ao Eel)."""
    return fs_selecionar_arquivos()

@eel.expose
def selecionar_pasta_eel(): # Renomeado
    """Abre um diálogo para selecionar uma pasta (exposto ao Eel)."""
    return fs_selecionar_pasta()

@eel.expose
def listar_arquivos_pasta_eel(folder_path): # Renomeado
    """Lista os arquivos em uma pasta selecionada (exposto ao Eel)."""
    return fs_listar_arquivos_pasta(folder_path)

@eel.expose
def salvar_metadados_manga_eel(metadata):
    """Salva os metadados do mangá em um arquivo JSON (exposto ao Eel)."""
    try:
        # Esta função é simples e pode permanecer aqui ou ser movida para um utilitário de metadados se crescer.
        with open("manga_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def load_github_config_eel():
    """Carrega a configuração do GitHub."""
    try:
        config = ConfigManager.load_github_config()
        if config:
            log_message("Configuração do GitHub carregada.", "info")
            return {
                "token": config.get('github_token'),
                "repo_owner": config.get('repo_owner'),
                "repo_name": config.get('repo_name'),
                "branch": config.get('branch', 'main') # Default to 'main' if not found
            }
        else:
            log_message("Nenhuma configuração do GitHub encontrada.", "info")
            return {"token": None, "repo_owner": None, "repo_name": None, "branch": 'main'}
    except Exception as e:
        log_message(f"Erro ao carregar configuração do GitHub: {e}", "error")
        return {"token": None, "repo_owner": None, "repo_name": None, "branch": 'main', "error": str(e)}

@eel.expose
def save_github_config_eel(token, repo_owner, repo_name, branch='main'):
    """Salva a configuração do GitHub."""
    try:
        ConfigManager.save_github_config(
            github_token=token,
            repo_owner=repo_owner,
            repo_name=repo_name,
            branch=branch
        )
        log_message("Configuração do GitHub salva com sucesso.", "success")
        return {"status": "success", "message": "Configuração do GitHub salva."}
    except Exception as e:
        log_message(f"Erro ao salvar configuração do GitHub: {e}", "error")
        return {"status": "error", "message": str(e)}

@eel.expose
def test_buzzheavier_connection_eel(api_key):
    """Testa a conexão com o Buzzheavier (exposto ao Eel)."""
    return test_buzz_conn_internal(api_key)

@eel.expose
def upload_arquivo_eel(file_path, host_config):
    """Faz o upload de um arquivo para o host especificado (exposto ao Eel)."""
    try:
        host_type = host_config.get("type", "catbox")
        
        if host_type == "buzzheavier":
            api_key = host_config.get("apiKey", "")
            folder_id = host_config.get("folderId", None)
            is_public = host_config.get("fileVisibility", "public") == "public"
            
            if not api_key:
                return {"success": False, "error": "API Key do Buzzheavier não fornecida"}
            
            url, error = upload_file_buzzheavier(file_path, api_key, folder_id, is_public)
            if error:
                return {"success": False, "error": error}
            return {"success": True, "url": url}
            
        elif host_type == "catbox":
            userhash = host_config.get("userhash", "") # Deve vir do frontend ou config
            if not userhash:
                log_message("Userhash do Catbox não fornecido para upload_arquivo_eel.", "error")
                return {"success": False, "error": "Userhash do Catbox não fornecido para upload_arquivo_eel"}
            
            # CORREÇÃO: Usar CatboxClient para o upload
            catbox_client = CatboxClient(userhash)
            result = catbox_client.upload_file(file_path) # upload_file retorna um dict

            if result.get("error"):
                log_message(f"Erro no upload para Catbox (via upload_arquivo_eel): {result.get('error')}", "error")
                return {"success": False, "error": result.get("error")}
            
            log_message(f"Upload para Catbox (via upload_arquivo_eel) bem-sucedido: {result.get('url')}", "info")
            return {"success": True, "url": result.get("url")}
            
        else:
            import time
            time.sleep(1) # Simula o tempo de upload
            return {"success": True, "url": f"https://example.com/simulated/{os.path.basename(file_path)}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def get_directories_eel(path):
    """Lista os diretórios em um caminho especificado (exposto ao Eel)."""
    try:
        if not os.path.isdir(path):
            return {"error": "Caminho inválido"}
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return {"path": path, "dirs": dirs}
    except Exception as e:
        return {"error": str(e)}

@eel.expose
def upload_file_to_catbox_eel(file_path):
    """Expõe a função de upload para o Catbox."""
    catbox_config = ConfigManager.load_host_config('catbox')
    userhash = catbox_config.get('userhash') if catbox_config else None
    if not userhash:
        log_message("Userhash do Catbox não configurado.", "error")
        return {"error": "Userhash do Catbox não configurado."}
    catbox_client = CatboxClient(userhash)
    return catbox_client.upload_file(file_path)

@eel.expose
def create_catbox_album_eel(title, description, file_urls_json):
    """Expõe a função de criar álbum no Catbox."""
    catbox_config = ConfigManager.load_host_config('catbox')
    userhash = catbox_config.get('userhash') if catbox_config else None
    if not userhash:
        log_message("Userhash do Catbox não configurado.", "error")
        return {"error": "Userhash do Catbox não configurado."}
    catbox_client = CatboxClient(userhash)
    try:
        file_urls = json.loads(file_urls_json)
    except json.JSONDecodeError as e:
        log_message(f"Erro ao decodificar JSON de URLs de arquivo: {e}", "error")
        return {"error": f"Erro ao decodificar JSON de URLs de arquivo: {e}"}
    return catbox_client.create_album(title, description, file_urls)

@eel.expose
def process_manga_chapter_eel(file_paths_json, manga_title, chapter_title, chapter_description, host_selection, cubari_options_json):
    """
    Processa um capítulo de mangá: faz upload das imagens e cria o JSON do Cubari.
    Espera file_paths_json e cubari_options_json como strings JSON.
    """
    log_message(f"Iniciando process_manga_chapter_eel com host: {host_selection}")
    try:
        file_paths = json.loads(file_paths_json)
        cubari_options = json.loads(cubari_options_json)
    except json.JSONDecodeError as e:
        log_message(f"Erro ao decodificar JSON em process_manga_chapter_eel: {e}", "error")
        return {"error": f"Erro ao decodificar JSON: {e}"}

    catbox_client = None
    buzz_api_key = None

    if host_selection == "Catbox":
        catbox_config = ConfigManager.load_host_config('catbox')
        userhash = catbox_config.get('userhash') if catbox_config else None
        if not userhash:
            log_message("Userhash do Catbox não configurado para process_manga_chapter_eel.", "error")
            return {"error": "Userhash do Catbox não configurado."}
        catbox_client = CatboxClient(userhash)
        log_message("Catbox client inicializado para process_manga_chapter_eel.")
    elif host_selection == "Buzzheavier":
        buzz_config = ConfigManager.load_host_config('buzzheavier')
        buzz_api_key = buzz_config.get('apiKey') if buzz_config else None
        if not buzz_api_key:
            log_message("API Key do Buzzheavier não configurada.", "error")
            return {"error": "API Key do Buzzheavier não configurada."}
        log_message("Buzzheavier API Key carregada para process_manga_chapter_eel.")

    # MODIFICADO: Chamada da função sem o prefixo 'core_'
    return process_manga_chapter(
        file_paths=file_paths,
        manga_title=manga_title,
        chapter_title=chapter_title,
        chapter_description=chapter_description,
        host_selection=host_selection,
        catbox_client=catbox_client,
        buzz_api_key=buzz_api_key,
        cubari_options=cubari_options
    )

@eel.expose
def parallel_upload_files_eel(file_paths_json, host_selection):
    """
    Faz upload de múltiplos arquivos em paralelo.
    Espera file_paths_json como uma string JSON.
    """
    log_message(f"Iniciando parallel_upload_files_eel com host: {host_selection}")
    try:
        file_paths = json.loads(file_paths_json)
    except json.JSONDecodeError as e:
        log_message(f"Erro ao decodificar JSON em parallel_upload_files_eel: {e}", "error")
        return {"error": f"Erro ao decodificar JSON: {e}"}

    catbox_client = None
    buzz_api_key = None

    if host_selection == "Catbox":
        catbox_config = ConfigManager.load_host_config('catbox')
        userhash = catbox_config.get('userhash') if catbox_config else None
        if not userhash:
            log_message("Userhash do Catbox não configurado para parallel_upload_files_eel.", "error")
            return {"error": "Userhash do Catbox não configurado."}
        catbox_client = CatboxClient(userhash)
        log_message("Catbox client inicializado para parallel_upload_files_eel.")
    elif host_selection == "Buzzheavier":
        buzz_config = ConfigManager.load_host_config('buzzheavier')
        buzz_api_key = buzz_config.get('apiKey') if buzz_config else None
        if not buzz_api_key:
            log_message("API Key do Buzzheavier não configurada para parallel_upload_files_eel.", "error")
            return {"error": "API Key do Buzzheavier não configurada."}
        log_message("Buzzheavier API Key carregada para parallel_upload_files_eel.")
    
    # MODIFICADO: Chamada da função sem o prefixo 'core_'
    return parallel_upload_files(
        file_paths=file_paths,
        host_selection=host_selection,
        catbox_client=catbox_client,
        buzz_api_key=buzz_api_key
    )

@eel.expose
def save_catbox_config_eel(userhash):
    """Salva a configuração do Catbox (userhash)."""
    try:
        ConfigManager.save_host_config('catbox', {'userhash': userhash})
        log_message("Configuração do Catbox salva com sucesso.", "success")
        return {"status": "success", "message": "Configuração do Catbox salva."}
    except Exception as e:
        log_message(f"Erro ao salvar configuração do Catbox: {e}", "error")
        return {"status": "error", "message": str(e)}

@eel.expose
def load_catbox_config_eel():
    """Carrega a configuração do Catbox (userhash)."""
    try:
        config = ConfigManager.load_host_config('catbox')
        userhash = config.get('userhash') if config else None
        log_message(f"Configuração do Catbox carregada. Userhash: {'Presente' if userhash else 'Ausente'}", "info")
        return {"userhash": userhash}
    except Exception as e:
        log_message(f"Erro ao carregar configuração do Catbox: {e}", "error")
        return {"userhash": None, "error": str(e)}

@eel.expose
def save_buzzheavier_config_eel(api_key, username=None, password=None, upload_url=None):
    """Salva a configuração do Buzzheavier."""
    try:
        config_data = {
            'apiKey': api_key,
            'username': username,
            'password': password,
            'upload_url': upload_url
        }
        ConfigManager.save_host_config('buzzheavier', config_data)
        log_message("Configuração do Buzzheavier salva com sucesso.", "success")
        return {"status": "success", "message": "Configuração do Buzzheavier salva."}
    except Exception as e:
        log_message(f"Erro ao salvar configuração do Buzzheavier: {e}", "error")
        return {"status": "error", "message": str(e)}

@eel.expose
def load_buzzheavier_config_eel():
    """Carrega a configuração do Buzzheavier."""
    try:
        config = ConfigManager.load_host_config('buzzheavier')
        if config:
            log_message("Configuração do Buzzheavier carregada.", "info")
            return {
                "apiKey": config.get('apiKey'),
                "username": config.get('username'),
                "password": config.get('password'),
                "upload_url": config.get('upload_url')
            }
        else:
            log_message("Nenhuma configuração do Buzzheavier encontrada.", "info")
            return {"apiKey": None, "username": None, "password": None, "upload_url": None}
    except Exception as e:
        log_message(f"Erro ao carregar configuração do Buzzheavier: {e}", "error")
        return {"apiKey": None, "username": None, "password": None, "upload_url": None, "error": str(e)}
