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
import logging

# Configuração de logs com codificação UTF-8 explícita
import codecs
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(codecs.getwriter('utf-8')(sys.stdout.buffer))])

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    logging.info("Verificando dependências...")

    # Verifica dependências do Python
    try:
        import eel
        import psutil
        logging.info("✅ Dependências Python estão instaladas")
    except ImportError as e:
        logging.warning(f"❌ Dependência Python faltando: {e}")
        logging.info("Instalando dependências Python...")
        subprocess.run([sys.executable, "-m", "pip", "install", "eel", "psutil"])

    # Verifica dependências do Node.js
    node_modules = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_modules")
    if not os.path.exists(node_modules):
        logging.warning("❌ Dependências do Node.js não encontradas")
        logging.info("Instalando dependências do Node.js...")
        subprocess.run(["npm", "install"], cwd=os.path.dirname(os.path.abspath(__file__)))
    else:
        logging.info("✅ Dependências Node.js estão instaladas")

def start_app():
    """Inicia a aplicação Electron"""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os_type = platform.system()

    logging.info(f"Iniciando aplicação Electron no diretório: {app_dir}")

    try:
        if os_type == "Windows":
            # No Windows, use o cmd para executar npm start
            subprocess.Popen(["cmd", "/c", "npm start"], cwd=app_dir)
        else:
            # No Linux/Mac, use bash
            subprocess.Popen(["npm", "start"], cwd=app_dir)

        logging.info("Aplicação iniciada com sucesso!")
    except Exception as e:
        logging.error(f"Erro ao iniciar a aplicação: {e}")

if __name__ == "__main__":
    logging.info("=" * 50)
    logging.info("Iniciador da Aplicação Electron + Python Eel")
    logging.info("=" * 50)

    check_dependencies()
    start_app()

    logging.info("\nPressione Ctrl+C para encerrar este script quando terminar de usar a aplicação")

    try:
        # Mantém o script rodando para mostrar possíveis erros
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nEncerrando o script...")
        sys.exit(0)