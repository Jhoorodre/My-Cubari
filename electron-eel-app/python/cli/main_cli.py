import os
import sys
import time
import json # Para salvar cubari_data e yaml_data se não usar as funções de cubari_utils
import yaml # Para salvar cubari_data e yaml_data se não usar as funções de cubari_utils

# Adicionar o diretório python ao sys.path para permitir importações relativas corretas
# Isso é crucial para que os módulos dentro de 'python' possam se encontrar.
python_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(python_dir)

from core.config_manager import load_generic_config, save_generic_config, load_batch_config
from core.processing_logic import process_manga_chapter as core_process_manga_chapter
from core.cubari_utils import save_json, save_yaml # Usar estas para salvar
from core.file_system_utils import fs_natural_sort_key, fs_selecionar_pasta
from api_clients.catbox_client import CatboxClient # Added import

# === Configurações Globais (podem ser importadas de um arquivo de settings no futuro) ===
# Estas são as mesmas que estavam em manga_uploader.py
# Idealmente, estas seriam carregadas de um arquivo de configuração ou passadas como argumentos
ROOT_FOLDER_CLI = "." # Renomeado para evitar conflito se este módulo importar manga_uploader
USERHASH_CLI = "" 
OUTPUT_JSON_FILE_CLI = "cubari_source.json"
OUTPUT_YAML_FILE_CLI = "index.yaml"
ALBUM_TITLE_TEMPLATE_CLI = "{manga_name} - Capítulo {chapter_name}"
ALBUM_DESCRIPTION_TEMPLATE_CLI = "Capítulo {chapter_name} de {manga_name}"
MAX_WORKERS_CLI = 5
BATCH_CONFIG_FILE_CLI = "upload_files-Config.txt" # Usado para carregar USERHASH inicial
SHUTDOWN_AFTER_UPLOAD_CLI = False
# FOLDER_ID_CLI = None # Se necessário para alguma lógica CLI específica

# Carregar USERHASH do batch_config se existir
initial_batch_config = load_batch_config(BATCH_CONFIG_FILE_CLI)
USERHASH_CLI = initial_batch_config.get("API-Key", USERHASH_CLI)
SHUTDOWN_AFTER_UPLOAD_CLI = initial_batch_config.get("Shutdown", "False") == "True"

def display_menu(config_file):
    config = load_generic_config(config_file)
    global USERHASH_CLI # Permitir que o menu modifique o USERHASH_CLI global

    while True:
        print("\nMenu:")
        print(f"1. Definir Userhash Catbox (Atual: {USERHASH_CLI or '(Não definido)'})")
        print("2. Processar Mangás e Gerar Arquivos (usando Userhash atual)")
        print("3. Sair")

        choice = input("Escolha uma opção: ")

        if choice == "1":
            USERHASH_CLI = input("Digite o novo Userhash do Catbox: ")
            config["API-Key"] = USERHASH_CLI # Salvar no arquivo de config genérico
            print(f"Userhash definido como: {USERHASH_CLI}")
        elif choice == "2":
            if not USERHASH_CLI:
                print("Userhash do Catbox não definido. Por favor, defina-o primeiro.")
                continue
            print(f"Iniciando processamento com Userhash: {USERHASH_CLI}")
            # Chamar a lógica principal de processamento que estava no main() do manga_uploader
            process_mangas_cli_interactive()
        elif choice == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")
        
        save_generic_config(config_file, config)

def process_mangas_cli_interactive():
    """Lógica de processamento de mangás interativa, similar ao antigo main() de manga_uploader."""
    global USERHASH_CLI # Acessa o USERHASH definido pelo menu ou carregado

    if not USERHASH_CLI:
        print("Userhash do Catbox não está definido. Não é possível processar.")
        USERHASH_CLI = input("Por favor, digite o Userhash do Catbox: ")
        if not USERHASH_CLI:
            print("Userhash não fornecido. Abortando.")
            return

    catbox_client = CatboxClient(USERHASH_CLI) # Create CatboxClient instance

    manga_root_folder = fs_selecionar_pasta() # Pede ao usuário para selecionar a pasta raiz dos mangás
    if not manga_root_folder:
        print("Nenhuma pasta selecionada. Abortando.")
        return

    manga_title = input(f"Digite o título do mangá (padrão: {os.path.basename(manga_root_folder)}): ") or os.path.basename(manga_root_folder)
    manga_description = input("Digite a descrição do mangá: ")
    manga_artist = input("Digite o nome do artista (ou Enter para deixar vazio): ") or ""
    manga_author = input("Digite o nome do autor (ou Enter para deixar vazio): ") or ""
    manga_cover = input("Digite a URL da capa (ou Enter para deixar vazio): ") or ""

    cubari_data = {
        "title": manga_title,
        "description": manga_description,
        "artist": manga_artist,
        "author": manga_author,
        "cover": manga_cover,
        "chapters": {},
    }
    yaml_data = {
        "title": manga_title,
        "description": manga_description,
        "artist": manga_artist,
        "author": manga_author,
        "cover": manga_cover,
        "chapters": {}
    }

    print(f"Processando mangá em: {manga_root_folder}")
    chapter_dirs = sorted(
        [d for d in os.listdir(manga_root_folder) if os.path.isdir(os.path.join(manga_root_folder, d))],
        key=fs_natural_sort_key
    )
    
    total_chapters = len(chapter_dirs)
    if total_chapters == 0:
        print(f"Nenhum diretório de capítulo encontrado em {manga_root_folder}.")
        return

    print(f"Encontrados {total_chapters} capítulos para processar.")

    for idx, chapter_dir_name in enumerate(chapter_dirs, start=1):
        print(f"\n[{idx}/{total_chapters}] Processando capítulo: {chapter_dir_name}")
        
        album_url, direct_image_urls, failures = core_process_manga_chapter(
            manga_root_folder, 
            manga_title, # Usar o título do mangá fornecido
            chapter_dir_name, 
            catbox_client, # Pass CatboxClient instance
            ALBUM_TITLE_TEMPLATE_CLI, 
            ALBUM_DESCRIPTION_TEMPLATE_CLI, 
            MAX_WORKERS_CLI
        )
        timestamp = str(int(time.time()))

        if failures:
            print(f"Houveram {len(failures)} falhas no upload para o capítulo {chapter_dir_name}:")
            for filename, error_msg in failures:
                print(f"  - {filename}: {error_msg}")

        if direct_image_urls:
            cubari_data["chapters"][str(chapter_dir_name)] = { # Usar nome do capítulo como chave
                "title": chapter_dir_name,
                "volume": "", # Adicionar lógica para volume se necessário
                "last_updated": timestamp,
                "groups": {
                    "": direct_image_urls
                }
            }
            yaml_data["chapters"][str(chapter_dir_name)] = {
                "title": chapter_dir_name,
                "volume": "",
                "groups": {
                    "": album_url if album_url else ""
                }
            }
            print(f"Capítulo {chapter_dir_name} processado.")
        else:
            print(f"Falha ao processar o capítulo {chapter_dir_name} ou nenhuma imagem enviada.")

    # Salvar os arquivos JSON e YAML
    output_json_path = os.path.join(manga_root_folder, f"{manga_title.replace(' ', '_')}_cubari.json")
    output_yaml_path = os.path.join(manga_root_folder, f"{manga_title.replace(' ', '_')}_index.yaml")
    
    save_json(cubari_data, output_json_path)
    print(f"\nArquivo JSON salvo como {output_json_path}")
    save_yaml(yaml_data, output_yaml_path)
    print(f"Arquivo YAML salvo como {output_yaml_path}")

    if SHUTDOWN_AFTER_UPLOAD_CLI:
        print("Desligamento solicitado após o upload. Desligando em 60 segundos...")
        # os.system("shutdown /s /t 60") # Comentado para segurança

def main_cli_runner():
    """Ponto de entrada principal para o CLI."""    
    # Usar o mesmo nome de arquivo de config que o batch script usava para consistência
    # ou definir um novo específico para este CLI interativo.
    config_file_for_menu = "cli_config.txt" 
    # Popular com userhash do batch se existir, para que o menu já comece com ele
    if USERHASH_CLI:
        initial_cli_config = load_generic_config(config_file_for_menu)
        initial_cli_config["API-Key"] = USERHASH_CLI
        save_generic_config(config_file_for_menu, initial_cli_config)

    display_menu(config_file_for_menu)

if __name__ == "__main__":
    main_cli_runner()
