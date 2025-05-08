import eel
import os
import json
# Importar funções dos módulos refatorados
from ..api_clients.catbox_client import upload_file_catbox
from ..api_clients.buzzheavier_client import (
    upload_file_buzzheavier,
    test_buzzheavier_connection as test_buzz_conn_internal,
    create_buzzheavier_folder
)
from ..core.config_manager import (
    save_github_config as save_gh_config_internal,
    load_github_config as load_gh_config_internal, # Adicionado para uma possível função de carregar config do GH via Eel
    save_buzzheavier_config_generic as save_buzz_config_internal,
    load_buzzheavier_config_generic as load_buzz_config_internal
)
from ..core.file_system_utils import (
    selecionar_arquivos as fs_selecionar_arquivos,
    selecionar_pasta as fs_selecionar_pasta,
    listar_arquivos_pasta as fs_listar_arquivos_pasta,
    get_image_files_from_dir # Adicionado se necessário para alguma lógica de Eel
)
# Adicionar quaisquer outras importações necessárias, como de processing_logic, se as funções Eel o exigirem.

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
def salvar_config_github_eel(config):
    """Salva as configurações do GitHub (exposto ao Eel)."""
    try:
        success = save_gh_config_internal(
            config.get("username"), 
            config.get("token"), 
            config.get("repo_name"), 
            config.get("branch_name")
        )
        if success:
            return {"success": True}
        else:
            return {"success": False, "error": "Falha ao salvar as configurações do GitHub via Eel"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def load_config_github_eel(): # Exemplo de como carregar, se necessário
    """Carrega as configurações do GitHub (exposto ao Eel)."""
    try:
        config = load_gh_config_internal()
        return config # Retorna o dicionário de configuração ou {} se não encontrado
    except Exception as e:
        return {"error": str(e)}

@eel.expose
def save_buzzheavier_config_eel(config):
    """Salva as configurações do Buzzheavier (exposto ao Eel)."""
    try:
        success = save_buzz_config_internal(config, "buzzheavier_config.json")
        if success:
            return {"success": True}
        else:
            return {"success": False, "error": "Falha ao salvar as configurações do Buzzheavier via Eel"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@eel.expose
def load_buzzheavier_config_eel():
    """Carrega as configurações do Buzzheavier (exposto ao Eel)."""
    try:
        config = load_buzz_config_internal("buzzheavier_config.json")
        return config # Retorna o dicionário de configuração ou {} se não encontrado
    except Exception as e:
        return {"error": str(e)}

@eel.expose
def test_buzzheavier_connection_eel(api_key):
    """Testa a conexão com o Buzzheavier (exposto ao Eel)."""
    # A função original em manga_uploader já chamava a interna.
    # Aqui chamamos diretamente a função do buzzheavier_client.
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
                 # Tentar carregar de uma config global ou pedir ao usuário se for interativo
                 # Por enquanto, vamos assumir que o userhash deve ser fornecido em host_config
                return {"success": False, "error": "Userhash do Catbox não fornecido para upload_arquivo_eel"}
            url, error = upload_file_catbox(file_path, userhash)
            if error:
                return {"success": False, "error": error}
            return {"success": True, "url": url}
            
        # Adicionar aqui a lógica para upload para GitHub via Eel se necessário
        # elif host_type == "github":
        #     # ... obter config do github, chamar upload_to_github ...

        else:
            # Simulação de upload genérico (como estava em manga_uploader.py antes da refatoração completa de upload_arquivo)
            # Esta parte pode ser removida se todos os uploads forem para hosts específicos.
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

# Adicione aqui outras funções que precisam ser expostas ao Eel.
# Por exemplo, uma função para iniciar o processamento de um mangá inteiro:
# @eel.expose
# def process_manga_eel(manga_folder_path, metadata, catbox_userhash, github_config, etc...):
#     try:
#         # Chamar core.processing_logic.process_manga_chapter ou uma função de orquestração de alto nível
#         # ... lógica para iterar capítulos, chamar process_manga_chapter ...
#         # ... gerar JSON/YAML final ...
#         # ... fazer upload para GitHub se configurado ...
#         return {"success": True, "message": "Processamento do mangá concluído"}
#     except Exception as e:
#         return {"success": False, "error": str(e)}
