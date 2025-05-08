import requests
import base64
from datetime import datetime

# === Configurações do GitHub ===
GITHUB_API_URL = "https://api.github.com"

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
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/contents/{file_path}"
        response = requests.get(url, headers=headers)
        
        sha = None
        if response.status_code == 200:
            sha = response.json()["sha"]
        
        content_bytes = content.encode("utf-8")
        content_base64 = base64.b64encode(content_bytes).decode("utf-8")
        
        data = {
            "message": commit_message,
            "content": content_base64,
        }
        
        if sha:
            data["sha"] = sha
        
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        
        return f"https://raw.githubusercontent.com/{username}/{repo_name}/main/{file_path}", None
    except Exception as e:
        return None, f"Erro ao fazer upload para o GitHub: {str(e)}"

def get_saved_github_files(username, token, repo_name, file_extension=".json"):
    """
    Obtém uma lista de arquivos JSON salvos no repositório do GitHub
    """
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/contents"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        files = []
        for item in response.json():
            if item["type"] == "file" and item["name"].endswith(file_extension):
                file_url = item["download_url"]
                file_name = item["name"]
                
                commits_url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/commits?path={file_name}&page=1&per_page=1"
                commits_response = requests.get(commits_url, headers=headers)
                commits_response.raise_for_status()
                
                last_updated = ""
                if commits_response.json():
                    last_updated_str = commits_response.json()[0]["commit"]["committer"]["date"]
                    try:
                        dt = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
                        last_updated = dt.strftime("%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        last_updated = last_updated_str # Manter a string original se a conversão falhar
                
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
    """
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/git/ref/heads/{base_branch}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        base_sha = response.json()["object"]["sha"]

        url = f"{GITHUB_API_URL}/repos/{username}/{repo_name}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Branch '{branch_name}' criada com sucesso.")
        return True, None
    except Exception as e:
        print(f"Erro ao criar branch: {e}")
        return False, str(e)
