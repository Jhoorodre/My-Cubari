import eel
import json
import logging
import os
import codecs # Importado para logging
import sys # Importado para logging

from ..core.config_manager import ConfigManager # Ajustado para import relativo
# CORRIGIDO: Sintaxe de importação para file_system_utils
from ..core.file_system_utils import ( # Ajustado para import relativo
    selecionar_arquivos as fs_selecionar_arquivos,
    selecionar_pasta as fs_selecionar_pasta,
    listar_arquivos_pasta as fs_listar_arquivos_pasta,
    get_image_files_from_dir
)
# CORRIGIDO: Importação de processing_logic e upload_files_to_host_parallel
from ..core.processing_logic import process_manga_chapter, upload_files_to_host_parallel # Ajustado para import relativo

# NOVAS IMPORTAÇÕES DE API_CLIENTS
from ..api_clients.catbox_client import CatboxClient
# Assumindo que test_buzzheavier_connection_internal existe em buzzheavier_client
from ..api_clients.buzzheavier_client import upload_file_buzzheavier, test_buzzheavier_connection 

logger = logging.getLogger(__name__) 

if not logger.handlers: 
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(levelname)s - [%(name)s.%(funcName)s:%(lineno)d] - %(message)s',
                       handlers=[logging.StreamHandler(codecs.getwriter('utf-8')(sys.stdout.buffer))])

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..")) 
config_dir = os.path.join(project_root, "config")

if not os.path.exists(config_dir):
    logger.warning(f"Diretório de configuração não encontrado em {config_dir}. Tentando criar.")
    try:
        os.makedirs(config_dir)
        logger.info(f"Diretório de configuração criado em {config_dir}.")
    except OSError as e:
        logger.error(f"Não foi possível criar o diretório de configuração {config_dir}: {e}. Usando o diretório atual para config.")
        config_dir = "." # Fallback para o diretório atual

config_path = os.path.join(config_dir, "config.json")
app_config_path = os.path.join(config_dir, "app_config.json")

config_manager = ConfigManager  # Não instancia, apenas referencia a classe
app_config_manager = ConfigManager  # Não instancia, apenas referencia a classe


@eel.expose
def get_app_config_eel():
    try:
        config = app_config_manager.load_config(app_config_path)
        logger.info("App config loaded.")
        return config if config else {}
    except Exception as e:
        logger.error(f"Error loading app config: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def save_app_config_eel(config_data):
    try:
        app_config_manager.save_config(app_config_path, config_data)
        logger.info("App config saved.")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error saving app config: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@eel.expose
def selecionar_arquivos_eel(): # Renomeado para evitar conflito com a função original, se importada diretamente
    """Abre um diálogo para selecionar arquivos (exposto ao Eel)."""
    return fs_selecionar_arquivos()

@eel.expose
def selecionar_pasta_eel():
    logger.info("Chamando selecionar_pasta_eel")
    try:
        folder_path = fs_selecionar_pasta()
        logger.debug(f"Pasta selecionada: {folder_path}")
        return folder_path
    except Exception as e:
        logger.error(f"Erro em selecionar_pasta_eel: {e}", exc_info=True)
        return None

@eel.expose
def listar_arquivos_pasta_eel(folder_path): # Renomeado
    """Lista os arquivos em uma pasta selecionada (exposto ao Eel)."""
    return fs_listar_arquivos_pasta(folder_path)

@eel.expose
def listar_arquivos_eel(folder_path):
    logger.info(f"Chamando listar_arquivos_eel para: {folder_path}")
    try:
        files = get_image_files_from_dir(folder_path)
        logger.debug(f"Arquivos encontrados: {len(files)}")
        return files 
    except Exception as e:
        logger.error(f"Erro em listar_arquivos_eel: {e}", exc_info=True)
        return []

@eel.expose
def salvar_metadados_manga_eel(metadata):
    """Salva os metadados do mangá em um arquivo JSON (exposto ao Eel)."""
    try:
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
            logger.info("Configuração do GitHub carregada.")
            return {
                "token": config.get('github_token'),
                "repo_owner": config.get('repo_owner'),
                "repo_name": config.get('repo_name'),
                "branch": config.get('branch', 'main') 
            }
        else:
            logger.info("Nenhuma configuração do GitHub encontrada.")
            return {"token": None, "repo_owner": None, "repo_name": None, "branch": 'main'}
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do GitHub: {e}")
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
        logger.info("Configuração do GitHub salva com sucesso.")
        return {"status": "success", "message": "Configuração do GitHub salva."}
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do GitHub: {e}")
        return {"status": "error", "message": str(e)}

@eel.expose
def test_buzzheavier_connection_eel(api_key):
    logger.info(f"Testando conexão com Buzzheavier com API Key: {'Sim' if api_key else 'Não'}")
    try:
        result = test_buzzheavier_connection(api_key)
        if result.get("success"):
            logger.info(f"Teste de conexão Buzzheavier: {result}")
            return result
        else:
            logger.error(f"Teste de conexão Buzzheavier falhou: {result}")
            return result
    except Exception as e:
        logger.error(f"Erro ao testar conexão Buzzheavier: {e}", exc_info=True)
        return {"success": False, "message": str(e)}

@eel.expose
def upload_arquivo_eel(file_path, host_config_json):
    logger.info(f"Upload de arquivo individual: {file_path} para host definido em JSON.")
    try:
        host_config = json.loads(host_config_json)
        host_type = host_config.get("type", "catbox")
        logger.info(f"Tipo de host: {host_type}, Arquivo: {file_path}")

        if host_type.lower() == "buzzheavier":
            api_key = host_config.get("apiKey")
            folder_id = host_config.get("folderId")
            is_public = host_config.get("fileVisibility", "public") == "public"
            if not api_key:
                logger.error("API Key do Buzzheavier não fornecida para upload_arquivo_eel.")
                return {"success": False, "error": "API Key do Buzzheavier não fornecida"}
            url, error = upload_file_buzzheavier(file_path, api_key, folder_id, is_public)
            if error:
                logger.error(f"Erro no upload para Buzzheavier (via upload_arquivo_eel): {error}")
                return {"success": False, "error": error}
            logger.info(f"Upload para Buzzheavier (via upload_arquivo_eel) bem-sucedido: {url}")
            return {"success": True, "url": url}
        elif host_type.lower() == "catbox":
            userhash = host_config.get("userhash")
            if not userhash:
                logger.error("Userhash do Catbox não fornecido para upload_arquivo_eel.")
                return {"success": False, "error": "Userhash do Catbox não fornecido"}
            catbox_client = CatboxClient(userhash)
            result = catbox_client.upload_file(file_path) 
            if result.get("error"):
                logger.error(f"Erro no upload para Catbox (via upload_arquivo_eel): {result.get('error')}")
                return {"success": False, "error": result.get("error")}
            logger.info(f"Upload para Catbox (via upload_arquivo_eel) bem-sucedido: {result.get('url')}")
            return {"success": True, "url": result.get("url")}
        else:
            logger.warning(f"Tipo de host desconhecido para upload_arquivo_eel: {host_type}")
            return {"success": False, "error": f"Tipo de host desconhecido: {host_type}"}
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in upload_arquivo_eel: {e}")
        return {"success": False, "error": f"JSON decode error: {e}"}
    except Exception as e:
        logger.error(f"Erro em upload_arquivo_eel: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

@eel.expose
def get_directories_eel(path):
    logger.info(f"Listando diretórios em: {path}")
    try:
        if not os.path.isdir(path):
            logger.warning(f"Caminho inválido ou não é diretório: {path}")
            return {"error": "Caminho inválido"}
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        logger.debug(f"Diretórios encontrados: {dirs}")
        return {"path": path, "dirs": dirs}
    except Exception as e:
        logger.error(f"Erro ao listar diretórios: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def upload_file_to_catbox_eel(file_path):
    logger.info(f"Upload para Catbox (específico): {file_path}")
    catbox_config = ConfigManager.load_host_config('catbox')
    userhash = catbox_config.get('userhash') if catbox_config else None
    if not userhash:
        logger.error("Userhash do Catbox não configurado para upload_file_to_catbox_eel.")
        return {"error": "Userhash do Catbox não configurado."}
    try:
        catbox_client = CatboxClient(userhash)
        result = catbox_client.upload_file(file_path)
        if result.get("error"):
            logger.error(f"Erro no upload para Catbox (específico): {result.get('error')}")
            return {"error": result.get("error")}
        logger.info(f"Upload para Catbox (específico) bem-sucedido: {result.get('url')}")
        return result
    except Exception as e:
        logger.error(f"Erro em upload_file_to_catbox_eel: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def create_catbox_album_eel(title, description, file_urls_json):
    logger.info(f"Criando álbum Catbox: {title}")
    catbox_config = ConfigManager.load_host_config('catbox')
    userhash = catbox_config.get('userhash') if catbox_config else None
    if not userhash:
        logger.error("Userhash do Catbox não configurado para create_catbox_album_eel.")
        return {"error": "Userhash do Catbox não configurado."}
    try:
        file_urls = json.loads(file_urls_json)
        file_ids = []
        for url_or_id in file_urls:
            if isinstance(url_or_id, str) and "://" not in url_or_id and "." in url_or_id:
                file_ids.append(url_or_id) # Assume que é um ID de arquivo (ex: abc.jpg)
            elif isinstance(url_or_id, str) and "/" in url_or_id:
                file_ids.append(url_or_id.split("/")[-1]) # Extrai ID da URL
            else:
                logger.warning(f"Entrada de arquivo inválida para criação de álbum Catbox: {url_or_id}")
        
        if not file_ids:
            logger.error("Nenhum ID de arquivo válido fornecido para criar álbum Catbox.")
            return {"error": "Nenhum ID de arquivo válido fornecido."}

        catbox_client = CatboxClient(userhash)
        album_result = catbox_client.create_album(title, description, file_ids)

        if isinstance(album_result, str) and album_result.startswith("http"):
             logger.info(f"Álbum Catbox criado: {album_result}")
             return {"album_url": album_result}
        elif isinstance(album_result, dict) and album_result.get("error"):
             logger.error(f"Erro ao criar álbum Catbox: {album_result.get('error')}")
             return {"error": album_result.get("error")}
        else: 
             logger.error(f"Resposta inesperada ao criar álbum Catbox: {album_result}")
             return {"error": "Resposta inesperada do servidor Catbox ao criar álbum."}
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON de URLs/IDs de arquivo: {e}")
        return {"error": f"Erro ao decodificar JSON de URLs/IDs de arquivo: {e}"}
    except Exception as e:
        logger.error(f"Erro em create_catbox_album_eel: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def process_manga_chapter_eel(file_paths_json, manga_title, chapter_title, chapter_description, host_selection, cubari_options_json):
    logger.info(f"Iniciando process_manga_chapter_eel com host: {host_selection}")
    try:
        file_paths = json.loads(file_paths_json)
        cubari_options = json.loads(cubari_options_json)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON em process_manga_chapter_eel: {e}")
        return {"error": f"Erro ao decodificar JSON: {e}"}

    host_config_for_core = {"type": host_selection.lower()}

    if host_selection.lower() == "catbox":
        catbox_cfg = ConfigManager.load_host_config('catbox')
        userhash = catbox_cfg.get('userhash') if catbox_cfg else None
        if not userhash:
            logger.error("Userhash do Catbox não configurado para process_manga_chapter_eel.")
            return {"error": "Userhash do Catbox não configurado."}
        host_config_for_core['userhash'] = userhash
        logger.info("Catbox config preparada para process_manga_chapter_eel.")
    elif host_selection.lower() == "buzzheavier":
        buzz_cfg = ConfigManager.load_host_config('buzzheavier')
        api_key = buzz_cfg.get('apiKey') if buzz_cfg else None
        if not api_key:
            logger.error("API Key do Buzzheavier não configurada para process_manga_chapter_eel.")
            return {"error": "API Key do Buzzheavier não configurada."}
        host_config_for_core['apiKey'] = api_key
        host_config_for_core['folderId'] = buzz_cfg.get('folderId')
        host_config_for_core['fileVisibility'] = buzz_cfg.get('fileVisibility', 'public')
        logger.info("Buzzheavier config preparada para process_manga_chapter_eel.")
    else:
        logger.error(f"Host de upload não suportado: {host_selection}")
        return {"error": f"Host de upload não suportado: {host_selection}"}

    try:
        logger.info(f"Chamando upload_files_to_host_parallel para {len(file_paths)} arquivos.")
        upload_results = upload_files_to_host_parallel(file_paths, host_config_for_core, max_workers=5)
        
        successful_uploads = [res for res in upload_results if res['status'] == 'success']
        failed_uploads_count = len(upload_results) - len(successful_uploads)
        logger.info(f"{len(successful_uploads)} arquivos enviados com sucesso, {failed_uploads_count} falharam.")

        if not successful_uploads:
            logger.error("Nenhum arquivo foi enviado com sucesso em process_manga_chapter_eel.")
            return {"error": "Nenhum arquivo foi enviado com sucesso.", "details": upload_results}

        cubari_json_output = {
            "title": manga_title,
            "description": chapter_description, # Adicionado description ao nível raiz do capítulo
            "artist": cubari_options.get("artist", ""),
            "author": cubari_options.get("author", ""),
            "chapters": {
                chapter_title: {
                    "title": chapter_title,
                    "description": chapter_description, # Pode ser redundante se já estiver no nível do capítulo
                    "groups": cubari_options.get("groups", {}),
                    "pages": [upload['url'] for upload in successful_uploads if upload.get('url')]
                }
            },
            "uploader": cubari_options.get("uploader", "")
        }
        # Adicionar outras opções de cubari_options se necessário
        for key, value in cubari_options.items():
            if key not in ["artist", "author", "groups", "uploader"]: # Evitar sobrescrever chaves já tratadas
                cubari_json_output.setdefault(key, value)

        logger.info("JSON do Cubari gerado.")
        return {"status": "success", "cubari_json": cubari_json_output, "upload_results": upload_results}

    except Exception as e:
        logger.error(f"Erro na lógica principal de process_manga_chapter_eel: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def parallel_upload_files_eel(file_paths_json, host_config_json):
    logger.info(f"parallel_upload_files_eel chamado com file_paths_json: {type(file_paths_json)}, host_config_json: {type(host_config_json)}")
    
    try:
        file_paths = json.loads(file_paths_json)
        host_config = json.loads(host_config_json)
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON em parallel_upload_files_eel: {e}")
        paths_for_error_return = []
        if isinstance(file_paths_json, str):
            try:
                loaded_paths = json.loads(file_paths_json)
                if isinstance(loaded_paths, list):
                    paths_for_error_return = loaded_paths
            except: 
                pass 
        return json.dumps([{'path': path, 'status': 'error', 'error': f"Erro de decodificação JSON: {e}"} for path in paths_for_error_return])
    except Exception as e: 
        logger.error(f"Erro inesperado ao carregar JSON em parallel_upload_files_eel: {e}", exc_info=True)
        return json.dumps([{'path': 'N/A', 'status': 'error', 'error': f"Erro inesperado ao carregar JSON: {e}"}])

    logger.info(f"Iniciando parallel_upload_files_eel com host: {host_config.get('type') if isinstance(host_config, dict) else 'N/A'}. Arquivos: {len(file_paths) if isinstance(file_paths, list) else 'N/A'}")

    if not isinstance(file_paths, list) or not all(isinstance(p, str) for p in file_paths):
        logger.error("parallel_upload_files_eel espera uma lista de strings de caminho de arquivo (file_paths).")
        return json.dumps([{'path': 'N/A', 'status': 'error', 'error': 'Formato de file_paths inválido. Esperava uma lista de strings.'}])

    if not isinstance(host_config, dict) or not host_config.get('type'):
        logger.error("Tipo de host não especificado ou formato de host_config inválido.")
        error_detail = 'Tipo de host não especificado ou host_config inválido.'
        if not isinstance(host_config, dict):
            error_detail = 'host_config não é um objeto JSON válido.'
        elif not host_config.get('type'):
            error_detail = 'Chave "type" ausente em host_config.'
        return json.dumps([{'path': path, 'status': 'error', 'error': error_detail} for path in file_paths])

    try:
        upload_results = upload_files_to_host_parallel(file_paths, host_config, max_workers=5) 
        logger.debug(f"Resultados do upload paralelo: {upload_results}")
        return json.dumps(upload_results) 
    except Exception as e:
        logger.error(f"Erro durante upload_files_to_host_parallel: {e}", exc_info=True)
        return json.dumps([{'path': path, 'status': 'error', 'error': str(e)} for path in file_paths])

@eel.expose
def save_catbox_config_eel(userhash):
    logger.info("Salvando configuração do Catbox.")
    try:
        ConfigManager.save_host_config('catbox', {'userhash': userhash}, base_dir=config_dir)
        logger.info("Configuração do Catbox salva com sucesso.")
        return {"status": "success", "message": "Configuração do Catbox salva."}
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do Catbox: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@eel.expose
def load_catbox_config_eel():
    logger.info("Carregando configuração do Catbox.")
    try:
        host_config = ConfigManager.load_host_config('catbox')
        userhash = host_config.get('userhash') if host_config else None
        logger.info(f"Configuração do Catbox carregada. Userhash: {'Presente' if userhash else 'Ausente'}")
        return {"userhash": userhash}
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do Catbox: {e}", exc_info=True)
        return {"userhash": None, "error": str(e)}

@eel.expose
def save_buzzheavier_config_eel(api_key, folder_id=None, file_visibility='public'):
    logger.info("Salvando configuração do Buzzheavier.")
    try:
        config_data = {
            'apiKey': api_key,
            'folderId': folder_id,
            'fileVisibility': file_visibility
        }
        ConfigManager.save_host_config('buzzheavier', config_data, base_dir=config_dir)
        logger.info("Configuração do Buzzheavier salva com sucesso.")
        return {"status": "success", "message": "Configuração do Buzzheavier salva."}
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do Buzzheavier: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@eel.expose
def load_buzzheavier_config_eel():
    logger.info("Carregando configuração do Buzzheavier.")
    try:
        config = ConfigManager.load_host_config('buzzheavier')
        if config:
            logger.info("Configuração do Buzzheavier carregada.")
            return {
                "apiKey": config.get('apiKey'),
                "folderId": config.get('folderId'),
                "fileVisibility": config.get('fileVisibility', 'public')
            }
        else:
            logger.info("Nenhuma configuração do Buzzheavier encontrada.")
            return {"apiKey": None, "folderId": None, "fileVisibility": 'public'}
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do Buzzheavier: {e}", exc_info=True)
        return {"apiKey": None, "folderId": None, "fileVisibility": 'public', "error": str(e)}

@eel.expose
def log_frontend_action(message, level='info'):
    log_level_map = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }
    numeric_level = log_level_map.get(level.lower(), logging.INFO)
    logger.log(numeric_level, f"[FRONTEND ACTION] {message}")

@eel.expose
def save_gdrive_config_eel(config_data_json):
    logger.info("Salvando configuração do Google Drive.")
    try:
        config_data = json.loads(config_data_json)
        ConfigManager.save_host_config('gdrive', config_data, base_dir=config_dir)
        return {"status": "success", "message": "Configuração do Google Drive salva."}
    except Exception as e:
        logger.error(f"Erro ao salvar config GDrive: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@eel.expose
def load_gdrive_config_eel():
    logger.info("Carregando configuração do Google Drive.")
    try:
        config = ConfigManager.load_host_config('gdrive', base_dir=config_dir)
        return config if config else {}
    except Exception as e:
        logger.error(f"Erro ao carregar config GDrive: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def save_dropbox_config_eel(config_data_json):
    logger.info("Salvando config Dropbox.")
    try:
        config_data = json.loads(config_data_json)
        ConfigManager.save_host_config('dropbox', config_data, base_dir=config_dir)
        return {"status": "success", "message": "Configuração do Dropbox salva."}
    except Exception as e:
        logger.error(f"Erro ao salvar config Dropbox: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

@eel.expose
def load_dropbox_config_eel():
    logger.info("Carregando config Dropbox.")
    try:
        config = ConfigManager.load_host_config('dropbox', base_dir=config_dir)
        return config if config else {}
    except Exception as e:
        logger.error(f"Erro ao carregar config Dropbox: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def save_gofile_config_eel(config_data_json):
    """Salva a configuração do GoFile."""
    try:
        config_data = json.loads(config_data_json)
        ConfigManager.save_host_config('gofile', config_data, base_dir=config_dir)
        logger.info("Configuração do GoFile salva com sucesso.", "success")
        return {"status": "success", "message": "Configuração do GoFile salva."}
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON para configuração do GoFile: {e}", "error")
        return {"status": "error", "message": f"JSON inválido: {e}"}
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do GoFile: {e}", "error")
        return {"status": "error", "message": str(e)}

@eel.expose
def load_gofile_config_eel():
    """Carrega a configuração do GoFile."""
    try:
        config = ConfigManager.load_host_config('gofile', base_dir=config_dir)
        if config:
            logger.info("Configuração do GoFile carregada.", "info")
            return config
        else:
            logger.info("Nenhuma configuração do GoFile encontrada.", "info")
            return {}
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do GoFile: {e}", "error")
        return {"error": str(e)}

@eel.expose
def save_pixeldrain_config_eel(config_data_json):
    """Salva a configuração do Pixeldrain."""
    try:
        config_data = json.loads(config_data_json)
        ConfigManager.save_host_config('pixeldrain', config_data, base_dir=config_dir)
        logger.info("Configuração do Pixeldrain salva com sucesso.", "success")
        return {"status": "success", "message": "Configuração do Pixeldrain salva."}
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON para configuração do Pixeldrain: {e}", "error")
        return {"status": "error", "message": f"JSON inválido: {e}"}
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do Pixeldrain: {e}", "error")
        return {"status": "error", "message": str(e)}

@eel.expose
def load_pixeldrain_config_eel():
    """Carrega a configuração do Pixeldrain."""
    try:
        config = ConfigManager.load_host_config('pixeldrain', base_dir=config_dir)
        if config:
            logger.info("Configuração do Pixeldrain carregada.", "info")
            return config
        else:
            logger.info("Nenhuma configuração do Pixeldrain encontrada.", "info")
            return {}
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do Pixeldrain: {e}", "error")
        return {"error": str(e)}

@eel.expose
def save_mongodb_config_eel(config_data_json):
    """Salva a configuração do MongoDB."""
    try:
        config_data = json.loads(config_data_json)
        ConfigManager.save_config('mongodb_config', config_data)
        logger.info("Configuração do MongoDB salva com sucesso.", "success")
        return {"status": "success", "message": "Configuração do MongoDB salva."}
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON para configuração do MongoDB: {e}", "error")
        return {"status": "error", "message": f"JSON inválido: {e}"}
    except Exception as e:
        logger.error(f"Erro ao salvar configuração do MongoDB: {e}", "error")
        return {"status": "error", "message": str(e)}

@eel.expose
def load_mongodb_config_eel():
    """Carrega a configuração do MongoDB."""
    try:
        config = ConfigManager.load_config('mongodb_config')
        if config:
            logger.info("Configuração do MongoDB carregada.", "info")
            return config
        else:
            logger.info("Nenhuma configuração do MongoDB encontrada.", "info")
            return {}
    except Exception as e:
        logger.error(f"Erro ao carregar configuração do MongoDB: {e}", "error")
        return {"error": str(e)}

@eel.expose
def get_system_info():
    logger.info("Coletando informações do sistema.")
    import platform, psutil
    try:
        mem = psutil.virtual_memory()
        info = {
            "sistema": platform.system(),
            "versao": platform.version(),
            "arquitetura": platform.machine(),
            "processador": platform.processor(),
            "memoria_total_gb": f"{mem.total / (1024**3):.2f}",
            "memoria_disponivel_gb": f"{mem.available / (1024**3):.2f}",
            "cpu_uso_percent": psutil.cpu_percent(interval=0.1)
        }
        return info
    except Exception as e:
        logger.error(f"Erro ao obter informações do sistema: {e}", exc_info=True)
        return {"error": str(e)}

@eel.expose
def rodar_manga_processor():
    logger.info("Rodando manga_processor (placeholder/não implementado).")
    # Esta função precisa de uma implementação clara do que "rodar_manga_processor" significa.
    # Se for para invocar o script manga_processor.py como um processo separado, use subprocess.
    # Se for para chamar uma função main() de lá, importe-a.
    return {"success": False, "error": "Função rodar_manga_processor não implementada."}
