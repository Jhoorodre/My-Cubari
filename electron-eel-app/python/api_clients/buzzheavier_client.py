import os
import requests

# URLs da API
BUZZHEAVIER_API_URL = "https://buzzheavier.com/api/v1"

def upload_file_buzzheavier(filepath, api_key, folder_id=None, is_public=True):
    """
    Faz upload de um arquivo para o Buzzheavier
    
    filepath: caminho do arquivo a ser enviado
    api_key: chave de API do Buzzheavier
    folder_id: ID da pasta para upload (opcional)
    is_public: se True, arquivo fica público
    """
    if not os.path.exists(filepath):
        return None, f"Arquivo não encontrado: {filepath}"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        data = {}
        if folder_id:
            data["folderId"] = folder_id
        
        data["visibility"] = "public" if is_public else "private"
        
        with open(filepath, "rb") as f:
            files = {"file": f}
            response = requests.post(
                f"{BUZZHEAVIER_API_URL}/upload", 
                headers=headers, 
                data=data, 
                files=files
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                return result.get("data", {}).get("url"), None
            else:
                return None, f"Erro ao enviar arquivo: {result.get('message', 'Erro desconhecido')}"
                
    except Exception as e:
        return None, f"Erro ao enviar arquivo: {filepath}\\n{str(e)}"

def test_buzzheavier_connection(api_key):
    """
    Testa a conexão com o Buzzheavier usando a API key fornecida
    
    api_key: chave de API do Buzzheavier
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.get(f"{BUZZHEAVIER_API_URL}/user", headers=headers)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            user_data = result.get("data", {})
            return {
                "success": True, 
                "username": user_data.get("username"), 
                "email": user_data.get("email")
            }
        else:
            return {"success": False, "error": result.get("message", "Erro desconhecido")}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def create_buzzheavier_folder(api_key, folder_name, parent_folder_id=None):
    """
    Cria uma pasta no Buzzheavier
    
    api_key: chave de API do Buzzheavier
    folder_name: nome da pasta
    parent_folder_id: ID da pasta pai (opcional)
    """
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {"name": folder_name}
        if parent_folder_id:
            data["parentId"] = parent_folder_id
            
        response = requests.post(
            f"{BUZZHEAVIER_API_URL}/folders", 
            headers=headers, 
            json=data
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            return result.get("data", {}).get("id"), None
        else:
            return None, f"Erro ao criar pasta: {result.get('message', 'Erro desconhecido')}"
            
    except Exception as e:
        return None, f"Erro ao criar pasta: {str(e)}"
