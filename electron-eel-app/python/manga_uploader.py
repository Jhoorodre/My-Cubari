import os
import json
import yaml
import requests
import traceback
import time
import re
import concurrent.futures
from tqdm import tqdm
import base64
from datetime import datetime

# === Configurações ===
USERHASH = ""  # Será definido pela interface
CATBOX_API_URL = "https://catbox.moe/user/api.php"  # Constante para a URL da API
MAX_WORKERS = 5  # Número máximo de uploads simultâneos - ajuste conforme necessário
RATE_LIMIT_DELAY = 0.5  # Pequeno delay para evitar bloqueio da API (em segundos)

# === Configurações do GitHub ===
GITHUB_API_URL = "https://api.github.com"

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
        return None, f"Erro ao enviar arquivo: {filepath}\n{str(e)}"

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
        print(f"Erro ao criar álbum:\n{e}")
        traceback.print_exc()
        return None

def natural_sort_key(s):
    """Chave para ordenação natural de strings com números"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def process_files(file_paths, userhash, progress_callback=None):
    """
    Processa uma lista de arquivos para upload
    Retorna uma lista de URLs e uma lista de erros
    """
    uploaded_urls = []
    failures = []
    
    total_files = len(file_paths)
    processed = 0
    
    # Função para processar cada arquivo
    def process_file(file_path):
        filename = os.path.basename(file_path)
        uploaded_url, error = upload_file_catbox(file_path, userhash)
        return filename, uploaded_url, error
    
    # Usar ThreadPoolExecutor para uploads paralelos
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, file_path): file_path for file_path in file_paths}
        
        for future in concurrent.futures.as_completed(futures):
            filename, uploaded_url, error = future.result()
            processed += 1
            
            if progress_callback:
                progress_callback(processed, total_files, filename)
            
            if uploaded_url:
                uploaded_urls.append(uploaded_url)
            else:
                failures.append((filename, error))
    
    return uploaded_urls, failures

def get_image_files_from_dir(directory):
    """Retorna uma lista de arquivos de imagem em um diretório"""
    if not os.path.isdir(directory):
        return []
    
    return sorted(
        [os.path.join(directory, f) for f in os.listdir(directory) 
         if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))],
        key=lambda x: natural_sort_key(os.path.basename(x))
    )

def generate_cubari_json(metadata, chapters_data):
    """
    Gera um JSON compatível com Cubari.moe
    
    metadata: dicionário com os metadados do mangá
    chapters_data: dicionário com dados dos capítulos
    """
    cubari_data = {
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "artist": metadata.get("artist", ""),
        "author": metadata.get("author", ""),
        "cover": metadata.get("cover", ""),
        "chapters": {}
    }
    
    for chapter_num, chapter_info in chapters_data.items():
        cubari_data["chapters"][str(chapter_num)] = {
            "title": chapter_info.get("title", str(chapter_num)),
            "volume": chapter_info.get("volume", ""),
            "last_updated": str(int(time.time())),
            "groups": {
                "": chapter_info.get("image_urls", [])
            }
        }
    
    return cubari_data

def generate_yaml(metadata, chapters_data):
    """
    Gera um YAML compatível com Cubari.moe
    
    metadata: dicionário com os metadados do mangá
    chapters_data: dicionário com dados dos capítulos
    """
    yaml_data = {
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "artist": metadata.get("artist", ""),
        "author": metadata.get("author", ""),
        "cover": metadata.get("cover", ""),
        "chapters": {}
    }
    
    for chapter_num, chapter_info in chapters_data.items():
        yaml_data["chapters"][str(chapter_num)] = {
            "title": chapter_info.get("title", str(chapter_num)),
            "volume": chapter_info.get("volume", ""),
            "groups": {
                "": chapter_info.get("album_url", "")
            }
        }
    
    return yaml_data

def save_json(data, output_file):
    """Salva dados em um arquivo JSON"""
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return output_file

def save_yaml(data, output_file):
    """Salva dados em um arquivo YAML"""
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(data, f, sort_keys=False, allow_unicode=True)
    return output_file

# === GitHub API Functions ===
def upload_to_github(username, token, repo_name, file_path, content, commit_message):
    """
    Faz upload de um arquivo para o GitHub
    
    username: nome de usuário do GitHub
    token: token de acesso pessoal do GitHub
    repo_name: nome do repositório
    file_path: caminho do arquivo no repositório
    content: conteúdo do arquivo
    commit_message: mensagem de commit
    """
    try:
        # Primeiro, verificamos se o arquivo já existe no GitHub
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Verificar se o arquivo existe e obter o SHA se existir
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/contents/{file_path}"
        response = requests.get(url, headers=headers)
        
        # Se o arquivo existir, precisamos do SHA para atualizá-lo
        if response.status_code == 200:
            sha = response.json()["sha"]
        else:
            sha = None
        
        # Codificar o conteúdo em base64
        content_bytes = content.encode("utf-8")
        content_base64 = base64.b64encode(content_bytes).decode("utf-8")
        
        # Preparar dados para a API
        data = {
            "message": commit_message,
            "content": content_base64,
        }
        
        # Se estamos atualizando um arquivo existente, incluir o SHA
        if sha:
            data["sha"] = sha
        
        # Fazer a solicitação PUT para criar/atualizar o arquivo
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        
        # Retornar a URL do arquivo no GitHub
        return f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{file_path}", None
    except Exception as e:
        return None, f"Erro ao fazer upload para o GitHub: {str(e)}"

def get_saved_github_files(username, token, repo_name, file_extension=".json"):
    """
    Obtém uma lista de arquivos JSON salvos no repositório do GitHub
    
    username: nome de usuário do GitHub
    token: token de acesso pessoal do GitHub
    repo_name: nome do repositório
    file_extension: extensão do arquivo para filtrar
    
    Retorna: lista de dicionários com informações sobre os arquivos
    """
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Obter lista de arquivos no repositório
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/contents"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        files = []
        for item in response.json():
            if item["type"] == "file" and item["name"].endswith(file_extension):
                # Obter metadados do arquivo
                file_url = item["download_url"]
                file_name = item["name"]
                
                # Obter a data da última atualização através dos commits
                commits_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/commits?path={file_name}&page=1&per_page=1"
                commits_response = requests.get(commits_url, headers=headers)
                commits_response.raise_for_status()
                
                last_updated = ""
                if commits_response.json():
                    last_updated = commits_response.json()[0]["commit"]["committer"]["date"]
                    # Converter para formato mais legível
                    try:
                        dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                        last_updated = dt.strftime("%d/%m/%Y %H:%M:%S")
                    except:
                        pass
                
                # Extrair título do mangá do nome do arquivo
                manga_title = file_name.replace("_cubari.json", "").replace("_", " ").title()
                
                files.append({
                    "title": manga_title,
                    "file_name": file_name,
                    "raw_url": file_url,
                    "last_updated": last_updated
                })
        
        return files, None
    except Exception as e:
        return None, f"Erro ao obter arquivos do GitHub: {str(e)}"

def authenticate_github(token):
    """
    Verifica se o token do GitHub é válido.
    token: token de acesso pessoal do GitHub
    Retorna True se o token for válido, caso contrário, False.
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(f"{GITHUB_API_URL}/user", headers=headers)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Erro de autenticação no GitHub: {e}")
        return False


def create_branch(username, token, repo_name, branch_name, base_branch="main"):
    """
    Cria uma nova branch em um repositório do GitHub.
    username: nome de usuário do GitHub
    token: token de acesso pessoal do GitHub
    repo_name: nome do repositório
    branch_name: nome da nova branch
    base_branch: branch base para criar a nova branch (padrão: main)
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        # Obter o SHA da branch base
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/git/ref/heads/{base_branch}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        base_sha = response.json()["object"]["sha"]

        # Criar a nova branch
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Branch '{branch_name}' criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar branch: {e}")

# Função para salvar configurações em um arquivo
def save_config_to_file(config_data, config_file):
    """Salva as configurações em um arquivo JSON"""
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

# Função para carregar configurações de um arquivo
def load_config_from_file(config_file):
    """Carrega as configurações de um arquivo JSON"""
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            return config_data
        return {}
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return {}

def save_github_config(username, token, repo_name, branch_name, config_file="github_config.json"):
    """
    Salva as configurações do GitHub em um arquivo JSON.
    username: nome de usuário do GitHub
    token: token de acesso pessoal do GitHub
    repo_name: nome do repositório
    branch_name: nome da branch
    config_file: nome do arquivo de configuração (padrão: github_config.json)
    """
    config_data = {
        "username": username,
        "token": token,
        "repo_name": repo_name,
        "branch_name": branch_name
    }
    return save_config_to_file(config_data, config_file)


def load_github_config(config_file="github_config.json"):
    """
    Carrega as configurações do GitHub de um arquivo JSON.
    config_file: nome do arquivo de configuração (padrão: github_config.json)
    Retorna um dicionário com as configurações ou um dicionário vazio se o arquivo não existir.
    """
    return load_config_from_file(config_file)