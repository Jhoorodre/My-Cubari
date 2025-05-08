import os
import json

# Diretório para armazenar configurações específicas de hosts
HOST_CONFIG_DIR = "host_configs"

# Função para garantir que o diretório de configuração do host exista
def _ensure_host_config_dir():
    if not os.path.exists(HOST_CONFIG_DIR):
        os.makedirs(HOST_CONFIG_DIR)

# Função para obter o caminho do arquivo de configuração de um host
def _get_host_config_path(host_name):
    _ensure_host_config_dir()
    return os.path.join(HOST_CONFIG_DIR, f"{host_name}_config.json")

# Função para carregar configurações do arquivo gerado pelo script batch
def load_batch_config(config_file):
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line: # Adicionado para evitar erro se a linha não tiver "="
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip()
    return config

# Função para salvar configurações em um arquivo JSON (genérica)
def save_config_to_file(config_data, config_file):
    """Salva as configurações em um arquivo JSON"""
    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {e}")
        return False

# Função para carregar configurações de um arquivo JSON (genérica)
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

# Funções específicas para config do GitHub
def save_github_config(username, token, repo_name, branch_name, config_file="github_config.json"):
    config_data = {
        "username": username,
        "token": token,
        "repo_name": repo_name,
        "branch_name": branch_name
    }
    return save_config_to_file(config_data, config_file)

def load_github_config(config_file="github_config.json"):
    return load_config_from_file(config_file)

# Funções para configurações de hosts específicos (Catbox, Buzzheavier, etc.)
class ConfigManager:
    @staticmethod
    def save_host_config(host_name, config_data):
        """Salva a configuração de um host específico em um arquivo JSON."""
        config_file = _get_host_config_path(host_name)
        return save_config_to_file(config_data, config_file)

    @staticmethod
    def load_host_config(host_name):
        """Carrega a configuração de um host específico de um arquivo JSON."""
        config_file = _get_host_config_path(host_name)
        return load_config_from_file(config_file)

    # Manter as funções específicas do GitHub por enquanto, ou decidir migrá-las
    @staticmethod
    def save_github_config(username, token, repo_name, branch_name, config_file="github_config.json"):
        # Esta função pode ser mantida ou refatorada para usar save_host_config('github', data)
        # Por simplicidade, vamos mantê-la por agora, mas idealmente seria bom unificar.
        config_data = {
            "username": username,
            "token": token,
            "repo_name": repo_name,
            "branch_name": branch_name
        }
        return save_config_to_file(config_data, config_file) # Salva na raiz por enquanto

    @staticmethod
    def load_github_config(config_file="github_config.json"):
        # Similarmente, esta função pode ser mantida ou refatorada.
        return load_config_from_file(config_file) # Carrega da raiz por enquanto

# Funções para config genérica (formato key=value)
def load_generic_config(config_file):
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip()
    return config

def save_generic_config(config_file, config):
    with open(config_file, "w", encoding="utf-8") as f:
        for key, value in config.items():
            f.write(f"{key}={value}\n")
