import os
import json
import yaml
import requests
import traceback
import time
import re
import concurrent.futures
from tqdm import tqdm
import logging
import argparse
from api_clients.catbox_client import upload_file_catbox, create_album_catbox
from core.cubari_utils import generate_cubari_json, generate_yaml, save_json, save_yaml
# Importar natural_sort_key de file_system_utils
from core.file_system_utils import natural_sort_key as fs_natural_sort_key
# Importar funções de processing_logic
from core.processing_logic import process_manga_chapter as core_process_manga_chapter

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Argumentos de linha de comando
parser = argparse.ArgumentParser(description="Processador de Mangás para Cubari (Modo Batch).")
parser.add_argument('--userhash', type=str, required=True, help="Userhash do Catbox (obrigatório)")
parser.add_argument('--manga-dir', type=str, required=True, help="Caminho para o diretório do mangá a ser processado (obrigatório)")
parser.add_argument('--title', type=str, help="Título do mangá. Se não fornecido, usa o nome do diretório do mangá.")
parser.add_argument('--description', type=str, default="", help="Descrição do mangá.")
parser.add_argument('--artist', type=str, default="", help="Nome do artista.")
parser.add_argument('--author', type=str, default="", help="Nome do autor.")
parser.add_argument('--cover', type=str, default="", help="URL da capa do mangá.")
parser.add_argument('--output-dir', type=str, default=".", help="Diretório onde os arquivos JSON e YAML de saída serão salvos.")
args = parser.parse_args()

# Substituir constantes por argumentos
USERHASH = args.userhash
MANGA_DIR_PATH = args.manga_dir
OUTPUT_DIR = args.output_dir

# O nome do mangá para templates e arquivos de saída
MANGA_NAME_FROM_DIR = os.path.basename(MANGA_DIR_PATH)
MANGA_TITLE = args.title if args.title else MANGA_NAME_FROM_DIR

# Nomes de arquivo de saída dinâmicos
safe_manga_title = re.sub(r'[^\w\-_.]', '_', MANGA_TITLE) # Sanitiza o título para nome de arquivo
OUTPUT_JSON_FILE = os.path.join(OUTPUT_DIR, f"{safe_manga_title}_cubari.json")
OUTPUT_YAML_FILE = os.path.join(OUTPUT_DIR, f"{safe_manga_title}_index.yaml")

# === Configurações ===
ALBUM_TITLE_TEMPLATE = "{manga_name} - Capítulo {chapter_name}"  # Template para o título do álbum
ALBUM_DESCRIPTION_TEMPLATE = "Capítulo {chapter_name} de {manga_name}"  # Template para a descrição
MAX_WORKERS = 5  # Número máximo de uploads simultâneos - ajuste conforme necessário


def main():
    if not os.path.isdir(MANGA_DIR_PATH):
        logging.error(f"O diretório do mangá especificado não existe: {MANGA_DIR_PATH}")
        return

    # Informações do mangá virão dos argumentos
    manga_title_arg = MANGA_TITLE
    manga_description_arg = args.description
    manga_artist_arg = args.artist
    manga_author_arg = args.author
    manga_cover_arg = args.cover

    cubari_data = {
        "title": manga_title_arg,
        "description": manga_description_arg,
        "artist": manga_artist_arg,
        "author": manga_author_arg,
        "cover": manga_cover_arg,
        "chapters": {},
    }

    yaml_data = {
        "title": manga_title_arg,
        "description": manga_description_arg,
        "artist": manga_artist_arg,
        "author": manga_author_arg,
        "cover": manga_cover_arg,
        "chapters": {}
    }

    logging.info(f"Iniciando processamento para: {manga_title_arg} em {MANGA_DIR_PATH}")

    chapter_dirs = sorted(
        [d for d in os.listdir(MANGA_DIR_PATH) if os.path.isdir(os.path.join(MANGA_DIR_PATH, d))],
        key=fs_natural_sort_key
    )
    
    total_chapters = len(chapter_dirs)
    if total_chapters == 0:
        logging.warning(f"Nenhum diretório de capítulo encontrado em {MANGA_DIR_PATH}. Nenhum arquivo será gerado.")
        return
        
    logging.info(f"Encontrados {total_chapters} capítulos para processar em {MANGA_DIR_PATH}")
    
    for idx, chapter_dir_name in enumerate(chapter_dirs, start=1):
        logging.info(f"\n[{idx}/{total_chapters}] Processando capítulo: {chapter_dir_name}")
        
        album_url, direct_image_urls, failures = core_process_manga_chapter(
            MANGA_DIR_PATH,      # Caminho para a pasta do mangá (que contém os capítulos)
            manga_title_arg,     # Nome/título do mangá para templates
            chapter_dir_name,    # Nome do diretório do capítulo atual
            USERHASH,            # Userhash do Catbox
            ALBUM_TITLE_TEMPLATE, 
            ALBUM_DESCRIPTION_TEMPLATE, 
            MAX_WORKERS
        )
        timestamp = str(int(time.time()))

        if failures:
            logging.warning(f"Houveram {len(failures)} falhas no upload para o capítulo {chapter_dir_name}:")
            for filename, error_msg in failures:
                logging.warning(f"  - {filename}: {error_msg}")

        if direct_image_urls:
            chapter_key = str(idx)
            cubari_data["chapters"][chapter_key] = {
                "title": chapter_dir_name,
                "volume": "",
                "last_updated": timestamp,
                "groups": {
                    "": direct_image_urls
                }
            }

            yaml_data["chapters"][chapter_key] = {
                "title": chapter_dir_name,
                "volume": "",
                "groups": {
                    "": album_url if album_url else ""
                }
            }

            logging.info(f"Capítulo {idx} processado com sucesso!")
        else:
            logging.error(f"Falha no capítulo {chapter_dir_name}.")

    save_json(cubari_data, OUTPUT_JSON_FILE)
    logging.info(f"\nArquivo JSON salvo como {OUTPUT_JSON_FILE}")

    save_yaml(yaml_data, OUTPUT_YAML_FILE)
    logging.info(f"Arquivo YAML salvo como {OUTPUT_YAML_FILE}")

    logging.info("\nProcesso concluído!")


if __name__ == "__main__":
    main()
