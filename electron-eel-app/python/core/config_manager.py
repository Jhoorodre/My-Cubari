import os
import json

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

# Funções específicas para config do Buzzheavier
def save_buzzheavier_config_generic(config_data, config_file="buzzheavier_config.json"):
    """Salva as configurações do Buzzheavier em um arquivo JSON."""
    return save_config_to_file(config_data, config_file)

def load_buzzheavier_config_generic(config_file="buzzheavier_config.json"):
    """Carrega as configurações do Buzzheavier de um arquivo JSON."""
    return load_config_from_file(config_file)

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
