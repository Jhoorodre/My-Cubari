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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Iniciar o servidor Eel.")
parser.add_argument('--port', type=int, default=8080, help="Porta para o servidor (padrão: 8080)")
args = parser.parse_args()

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

# Importa funções Python do main.py
try:
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "python"))
    import main as python_main
    logging.info("Módulo Python importado com sucesso.")
except ImportError as e:
    logging.error(f"Erro ao importar módulo Python: {e}")
    sys.exit(1)

if __name__ == "__main__":
    logging.info("=" * 50)
    logging.info("Iniciando servidor Python Eel (sem Electron)")
    logging.info("=" * 50)
    
    try:
        logging.info(f"Iniciando servidor na porta {args.port}...")
        # Inicia o servidor Eel
        eel.start('index.html', mode='default', port=args.port, host='localhost')
    except Exception as e:
        logging.error(f"Erro ao iniciar o servidor: {e}")