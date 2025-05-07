#!/usr/bin/env python3
"""
Script para iniciar a aplicação Electron + Python Eel
Este script simplifica o processo de inicialização, garantindo que todas as dependências
estejam instaladas antes de iniciar a aplicação.
"""
import os
import sys
import subprocess
import platform
import time

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    print("Verificando dependências...")
    
    # Verifica dependências do Python
    try:
        import eel
        import psutil
        print("✅ Dependências Python estão instaladas")
    except ImportError as e:
        print(f"❌ Dependência Python faltando: {e}")
        print("Instalando dependências Python...")
        subprocess.run([sys.executable, "-m", "pip", "install", "eel", "psutil"])
    
    # Verifica dependências do Node.js
    node_modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_modules")
    if not os.path.exists(node_modules):
        print("❌ Dependências do Node.js não encontradas")
        print("Instalando dependências do Node.js...")
        subprocess.run(["npm", "install"], cwd=os.path.dirname(os.path.abspath(__file__)))
    else:
        print("✅ Dependências Node.js estão instaladas")

def start_app():
    """Inicia a aplicação Electron"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os_type = platform.system()
    
    print(f"Iniciando aplicação Electron no diretório: {app_dir}")
    
    if os_type == "Windows":
        # No Windows, use o cmd para executar npm start
        subprocess.Popen(["cmd", "/c", "npm start"], cwd=app_dir)
    else:
        # No Linux/Mac, use bash
        subprocess.Popen(["npm", "start"], cwd=app_dir)
    
    print("Aplicação iniciada com sucesso!")

if __name__ == "__main__":
    print("=" * 50)
    print("Iniciador da Aplicação Electron + Python Eel")
    print("=" * 50)
    
    check_dependencies()
    start_app()
    
    print("\nPressione Ctrl+C para encerrar este script quando terminar de usar a aplicação")
    
    try:
        # Mantém o script rodando para mostrar possíveis erros
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando o script...")
        sys.exit(0)