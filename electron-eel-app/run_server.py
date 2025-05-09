#!/usr/bin/env python3
"""
Script para iniciar apenas o servidor Eel sem o Electron
Útil para ambientes sem interface gráfica ou para testes
"""
import os
import sys
import importlib.util
import webbrowser
from pathlib import Path
import logging
import argparse

# Configuração de logs
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Iniciar o servidor Eel.")
parser.add_argument('--port', type=int, default=3000, help="Porta para o servidor (padrão: 3000)")
parser.add_argument('--host', type=str, default='localhost', help="Host para o servidor (padrão: localhost)")
parser.add_argument(
    '--loglevel',
    type=str,
    default='INFO',
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help="Nível de log (padrão: INFO)"
)
args = parser.parse_args()

# Configuração de logs com base no argumento de linha de comando
log_level = getattr(logging, args.loglevel.upper(), logging.INFO)
logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s')

# Verifica se o Eel está instalado
try:
    import eel
    import psutil
except ImportError:
    print("Instalando dependências...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "eel", "psutil"])
    import eel
    import psutil

# Inicializa o Eel com o diretório web
web_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
eel.init(web_path)

# Configurar sys.path e importar funções Eel diretamente
# Obter o diretório do script atual (run_server.py), que é .../electron-eel-app
server_script_dir = os.path.dirname(os.path.abspath(__file__))
# Construir o caminho para o diretório 'python' que contém nossos módulos
python_modules_dir = os.path.join(server_script_dir, "python")

# Adicionar o diretório 'python' ao sys.path para permitir importações como 'from eel_interface...'
if python_modules_dir not in sys.path:
    sys.path.insert(0, python_modules_dir) # Inserir no início para prioridade

try:
    # Importar o módulo que contém as funções decoradas com @eel.expose.
    # O simples ato de importar este módulo é suficiente para que o Eel
    # registre as funções devido aos decoradores @eel.expose nelas.
    # Tenta importar o módulo usando importlib se o import direto falhar
    eel_exposed_path = os.path.join(python_modules_dir, "eel_interface", "eel_exposed_functions.py")
    spec = importlib.util.spec_from_file_location("eel_interface.eel_exposed_functions", eel_exposed_path)
    if spec and spec.loader:
        eel_exposed_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(eel_exposed_module)
        logging.info("Módulo 'eel_interface.eel_exposed_functions' importado via importlib e funções Eel registradas com sucesso.")
    else:
        raise ImportError(f"Não foi possível localizar o módulo em {eel_exposed_path}")
except ImportError as e:
    logging.error(f"Erro crítico ao importar 'eel_interface.eel_exposed_functions': {e}")
    logging.error(f"Verifique se o arquivo '{os.path.join(python_modules_dir, 'eel_interface', 'eel_exposed_functions.py')}' existe.")
    logging.error(f"Certifique-se também de que o diretório '{os.path.join(python_modules_dir, 'eel_interface')}' contém um arquivo __init__.py.")
    logging.error(f"Caminho para python_modules_dir (adicionado ao sys.path): {python_modules_dir}")
    logging.error(f"Conteúdo atual de sys.path: {sys.path}")
    sys.exit(1)
except Exception as e:
    logging.error(f"Erro inesperado durante a importação de módulos Python para Eel: {e}")
    sys.exit(1)

if __name__ == "__main__":
    logging.info("=" * 50)
    logging.info("Iniciando servidor Python Eel (sem Electron)")
    logging.info("=" * 50)
    
    try:
        logging.info(f"Iniciando servidor em http://{args.host}:{args.port}...")
        # Inicia o servidor Eel
        eel.start('index.html', mode='default', port=args.port, host=args.host)
    except OSError as e:
        if e.winerror == 10048 or e.errno == 98: # Address already in use (Windows/Linux)
            logging.error(f"Erro: A porta {args.port} no host '{args.host}' já está em uso.")
            logging.error("Verifique se outra instância do servidor ou outro aplicativo está usando esta porta.")
        else:
            logging.error(f"Erro de sistema operacional ao iniciar o servidor: {e}")
    except Exception as e:
        logging.error(f"Erro ao iniciar o servidor: {e}")