import eel
import sys
import os
import platform
import psutil
import json
import glob
from manga_uploader import (
    process_files, 
    get_image_files_from_dir, 
    create_album_catbox,
    generate_cubari_json,
    generate_yaml,
    save_json,
    save_yaml,
    upload_to_github,
    get_saved_github_files,
    save_config_to_file,
    load_config_from_file
)

# Configuração do caminho para os arquivos web
eel.init(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web'))

# Caminho para o arquivo de configuração
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')

# Configurações padrão
default_config = {
    "catbox": {
        "userhash": "",
        "create_albums": True,
        "upload_threads": 5
    },
    "github": {
        "username": "",
        "token": "",
        "repository": "My-Cubari",
        "default_scan_group": ""
    },
    "output": {
        "save_logs": True,
        "output_folder": ""
    },
    "manga_metadata": {}  # Armazenará os metadados dos mangás salvos
}

# Carregar configurações ou usar padrão se não existir
config = load_config_from_file(CONFIG_FILE) or default_config

# === Função auxiliar para obter diretórios e arquivos ===
@eel.expose
def get_directories(path="."):
    """Retorna lista de diretórios em um caminho"""
    try:
        if not path or path == ".":
            path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if not os.path.exists(path):
            return {"error": f"Caminho não existe: {path}"}
            
        directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        return {"dirs": directories, "path": os.path.abspath(path)}
    except Exception as e:
        return {"error": str(e)}

@eel.expose
def get_image_files(path):
    """Retorna lista de arquivos de imagem em um caminho"""
    try:
        if not os.path.exists(path):
            return {"error": f"Caminho não existe: {path}"}
            
        files = get_image_files_from_dir(path)
        
        # Determinar o capítulo e mangá com base no caminho
        chapter_name = os.path.basename(path)
        manga_name = os.path.basename(os.path.dirname(path))
        
        file_info = [
            {
                "name": os.path.basename(f),
                "path": f,
                "size": os.path.getsize(f),
                "chapter": chapter_name,
                "manga": manga_name
            } 
            for f in files
        ]
        return {"files": file_info}
    except Exception as e:
        return {"error": str(e)}

# === Configurações do Uploader ===
@eel.expose
def save_config(config_data):
    """Salva configurações do uploader"""
    try:
        global config
        
        # Atualiza as configurações recebidas
        if "catbox" in config_data:
            config["catbox"].update(config_data["catbox"])
        
        if "github" in config_data:
            config["github"].update(config_data["github"])
        
        if "output" in config_data:
            config["output"].update(config_data["output"])
        
        # Salva no arquivo
        success = save_config_to_file(config, CONFIG_FILE)
        
        return {"success": success}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@eel.expose
def get_saved_config():
    """Retorna a configuração atual"""
    return config

# === Funções de Upload ===
@eel.expose
def upload_files(file_list, userhash=None):
    """
    Faz upload de arquivos para o Catbox.moe
    file_list: lista de caminhos de arquivos para upload
    userhash: userhash do Catbox (opcional, usa o das configurações se não fornecido)
    """
    if not userhash:
        userhash = config["catbox"]["userhash"]
        
    if not userhash:
        return {"error": "Userhash não fornecido"}
        
    # Callback para atualizar o progresso no frontend
    def progress_callback(current, total, filename):
        eel.updateUploadProgress(current, total, filename)
    
    # Atualiza o número de threads com base nas configurações
    from manga_uploader import MAX_WORKERS
    global MAX_WORKERS
    MAX_WORKERS = config["catbox"]["upload_threads"]
    
    # Processa os arquivos
    uploaded_urls, failures = process_files(file_list, userhash, progress_callback)
    
    return {
        "success": True,
        "uploaded": len(uploaded_urls),
        "failed": len(failures),
        "urls": uploaded_urls,
        "failures": failures
    }

@eel.expose
def create_album(title, description, file_urls, userhash=None):
    """Cria um álbum no Catbox.moe"""
    if not userhash:
        userhash = config["catbox"]["userhash"]
        
    if not userhash:
        return {"error": "Userhash não fornecido"}
        
    album_url = create_album_catbox(title, description, file_urls, userhash)
    
    if album_url:
        return {"success": True, "album_url": album_url}
    else:
        return {"error": "Falha ao criar álbum"}

@eel.expose
def generate_cubari_files(metadata, chapters_data, output_path=None, github_upload=False):
    """
    Gera arquivos JSON e YAML compatíveis com Cubari.moe
    
    metadata: dicionário com os metadados do mangá
    chapters_data: dicionário com dados dos capítulos
    output_path: caminho onde salvar os arquivos (opcional)
    github_upload: se deve fazer upload para o GitHub
    """
    try:
        # Se não for especificado um caminho, usa o configurado ou o diretório atual
        if not output_path:
            output_path = config["output"]["output_folder"] or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Gera o nome base para os arquivos
        manga_title = metadata.get("title", "manga")
        base_filename = manga_title.lower().replace(" ", "_")
        
        # Gera e salva o JSON
        json_data = generate_cubari_json(metadata, chapters_data)
        json_file = os.path.join(output_path, f"{base_filename}_cubari.json")
        save_json(json_data, json_file)
        
        # Gera e salva o YAML
        yaml_data = generate_yaml(metadata, chapters_data)
        yaml_file = os.path.join(output_path, f"{base_filename}.yaml")
        save_yaml(yaml_data, yaml_file)
        
        result = {
            "success": True, 
            "json_file": json_file, 
            "yaml_file": yaml_file
        }
        
        # Salva os metadados para uso futuro
        config["manga_metadata"][manga_title] = {
            "title": manga_title,
            "description": metadata.get("description", ""),
            "author": metadata.get("author", ""),
            "artist": metadata.get("artist", ""),
            "cover": metadata.get("cover", ""),
            "status": metadata.get("status", ""),
            "json_file": json_file,
            "yaml_file": yaml_file,
            "last_updated": str(int(time.time()))
        }
        
        # Salva as configurações atualizadas
        save_config_to_file(config, CONFIG_FILE)
        
        # Upload para o GitHub se solicitado
        if github_upload:
            github_result = upload_cubari_to_github(json_file, base_filename)
            result.update(github_result)
        
        return result
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@eel.expose
def upload_cubari_to_github(json_file_path, file_base_name=None):
    """
    Faz upload de um arquivo JSON do Cubari para o GitHub
    
    json_file_path: caminho completo do arquivo JSON
    file_base_name: nome base do arquivo (opcional, extrai do json_file_path se não fornecido)
    """
    try:
        github_config = config["github"]
        
        # Verificar se as configurações do GitHub estão preenchidas
        if not github_config["username"] or not github_config["token"] or not github_config["repository"]:
            return {"error": "Configurações do GitHub incompletas. Preencha usuário, token e repositório."}
        
        # Ler o conteúdo do arquivo JSON
        with open(json_file_path, "r", encoding="utf-8") as f:
            json_content = f.read()
        
        # Determinar o nome do arquivo no GitHub
        if not file_base_name:
            file_base_name = os.path.basename(json_file_path).replace("_cubari.json", "")
        
        github_filename = f"{file_base_name}_cubari.json"
        
        # Criar mensagem de commit
        commit_message = f"Atualização automática: {file_base_name}"
        
        # Fazer upload para o GitHub
        github_url, error = upload_to_github(
            github_config["username"],
            github_config["token"],
            github_config["repository"],
            github_filename,
            json_content,
            commit_message
        )
        
        if github_url:
            return {
                "github_success": True,
                "github_url": github_url
            }
        else:
            return {
                "github_success": False,
                "github_error": error
            }
    except Exception as e:
        import traceback
        return {"github_success": False, "github_error": str(e), "traceback": traceback.format_exc()}

@eel.expose
def get_saved_github_manga_files():
    """Retorna a lista de arquivos de mangá salvos no GitHub"""
    try:
        github_config = config["github"]
        
        # Verificar se as configurações do GitHub estão preenchidas
        if not github_config["username"] or not github_config["token"] or not github_config["repository"]:
            return {"error": "Configurações do GitHub incompletas. Preencha usuário, token e repositório."}
        
        # Obter arquivos do GitHub
        files, error = get_saved_github_files(
            github_config["username"],
            github_config["token"],
            github_config["repository"],
            ".json"
        )
        
        if files is not None:
            return {"success": True, "files": files}
        else:
            return {"error": error}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}

@eel.expose
def get_saved_manga_metadata():
    """Retorna os metadados de mangás salvos localmente"""
    return {"success": True, "manga_metadata": config["manga_metadata"]}

# === Funções originais ===
@eel.expose
def say_hello_py(name):
    print(f"Hello from Python, {name}!")
    return f"Olá {name}, esta mensagem veio do Python!"

@eel.expose
def calculate(expression):
    try:
        # Avalia a expressão matemática (com segurança)
        result = eval(expression, {"__builtins__": {}}, {"abs": abs, "pow": pow, "round": round, "int": int, "float": float})
        return f"Resultado: {result}"
    except Exception as e:
        return f"Erro: {str(e)}"

@eel.expose
def get_system_info():
    info = {
        "sistema": platform.system(),
        "versao": platform.version(),
        "arquitetura": platform.architecture()[0],
        "processador": platform.processor(),
        "memoria_total": round(psutil.virtual_memory().total / (1024 ** 3), 2),  # Em GB
        "memoria_disponivel": round(psutil.virtual_memory().available / (1024 ** 3), 2),  # Em GB
        "cpu_uso": psutil.cpu_percent(interval=1)
    }
    return info

# Nova função para listar arquivos JSON no diretório
@eel.expose
def list_json_files():
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_files = glob.glob(os.path.join(workspace_dir, "*.json"))
    return [os.path.basename(f) for f in json_files if not f.endswith("config.json")]

# Nova função para ler conteúdo do arquivo JSON
@eel.expose
def read_json_file(filename):
    try:
        workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(workspace_dir, filename)
        
        # Verificar se o caminho está dentro do diretório de trabalho (segurança)
        if not os.path.normpath(file_path).startswith(os.path.normpath(workspace_dir)):
            return {"error": "Acesso negado: tentativa de acesso fora do diretório permitido"}
        
        # Verificar se o arquivo existe
        if not os.path.exists(file_path):
            return {"error": f"Arquivo não encontrado: {filename}"}
            
        # Ler e retornar o conteúdo JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            return content
    except json.JSONDecodeError:
        return {"error": f"Erro ao decodificar JSON: {filename} não é um arquivo JSON válido"}
    except Exception as e:
        return {"error": f"Erro ao ler arquivo: {str(e)}"}

# Função para iniciar a aplicação
def start_app():
    # Definindo opções para o modo de desenvolvimento
    options = {
        'mode': 'chrome',  # Alterado para 'chrome' para melhor compatibilidade
        'port': 8080,
        'host': 'localhost',
        'chromeFlags': ['--no-sandbox']
    }
    
    try:
        # Inicia o aplicativo web
        eel.start('index.html', options=options, size=(1200, 800))
    except (SystemExit, MemoryError, KeyboardInterrupt):
        # Lidar com fechamento do app
        print("Aplicação fechada!")

if __name__ == '__main__':
    start_app()