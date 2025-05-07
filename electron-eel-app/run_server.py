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
    print("Módulo Python importado com sucesso.")
except ImportError as e:
    print(f"Erro ao importar módulo Python: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("Iniciando servidor Python Eel (sem Electron)")
    print("=" * 50)
    
    try:
        print("Iniciando servidor na porta 8080...")
        # Inicia o servidor Eel
        eel.start('index.html', mode='default', port=8080, host='localhost')
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")