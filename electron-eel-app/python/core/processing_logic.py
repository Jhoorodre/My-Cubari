import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm # ADICIONADO: Importar tqdm
# from ..api_clients.github_client import GithubClient # Comentado ou a ser ajustado se necessário
from api_clients.catbox_client import CatboxClient # MODIFICADO: .. -> .
from api_clients.buzzheavier_client import upload_file_buzzheavier # MODIFICADO: .. -> .

from .file_system_utils import natural_sort_key as fs_natural_sort_key

# Configuração de logs para este módulo, se necessário, ou confiar no logging configurado no chamador.
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parallel_upload_files(image_file_names, chapter_path, catbox_client: CatboxClient, max_workers):
    """
    Processa uma lista de nomes de arquivos de imagem para upload paralelo para o Catbox.
    Retorna uma lista de URLs diretas das imagens e uma lista de IDs de arquivo.
    image_file_names: lista de nomes de arquivos (não caminhos completos) dentro de chapter_path.
    chapter_path: caminho completo para o diretório do capítulo.
    catbox_client: instância do CatboxClient.
    max_workers: número máximo de uploads simultâneos.
    """
    uploaded_ids = []
    direct_image_urls = []
    failures = []
    
    def process_file(filename):
        filepath = os.path.join(chapter_path, filename)
        # Chama o método do cliente
        uploaded_url, error = catbox_client.upload_file(filepath)
        return filename, uploaded_url, error
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_file, filename): filename for filename in image_file_names}
        
        with tqdm(total=len(image_file_names), desc=f"Enviando imagens de {os.path.basename(chapter_path)}") as pbar:
            for future in as_completed(futures):
                filename, uploaded_url, error = future.result()
                pbar.update(1)
                
                if uploaded_url:
                    file_id = uploaded_url.split("/")[-1]
                    uploaded_ids.append(file_id)
                    direct_image_urls.append(uploaded_url)
                    pbar.set_description(f"Enviado: {filename}")
                else:
                    failures.append((filename, error))
                    pbar.set_description(f"Falha: {filename}")
    
    if failures:
        logging.error(f"\n{len(failures)} uploads falharam para o capítulo {os.path.basename(chapter_path)}:")
        for filename, error in failures:
            logging.error(f"  - {filename}: {error}")
    
    return uploaded_ids, direct_image_urls, failures

def process_manga_chapter(manga_path, manga_name, chapter_dir_name, catbox_client: CatboxClient, album_title_template, album_description_template, max_workers):
    """
    Processa um único capítulo de mangá: lista imagens, faz upload e cria um álbum.
    manga_path: caminho para a pasta raiz do mangá (onde os diretórios dos capítulos estão).
    manga_name: nome do mangá (usado para templates).
    chapter_dir_name: nome do diretório do capítulo.
    catbox_client: instância do CatboxClient.
    album_title_template: template para o título do álbum.
    album_description_template: template para a descrição do álbum.
    max_workers: número máximo de uploads simultâneos.
    """
    chapter_full_path = os.path.join(manga_path, chapter_dir_name)
    logging.info(f"\nProcessando capítulo: {chapter_dir_name}")

    if not os.path.isdir(chapter_full_path):
        logging.error(f"{chapter_full_path} não é um diretório. Pulando.")
        return None, None, [] # album_url, direct_image_urls, failures

    image_file_names = sorted(
        [f for f in os.listdir(chapter_full_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))],
        key=fs_natural_sort_key
    )

    if not image_file_names:
        logging.warning(f"Nenhuma imagem válida encontrada em {chapter_dir_name}. Pulando.")
        return None, None, []

    logging.info(f"Encontradas {len(image_file_names)} imagens para upload em {chapter_dir_name}")
    
    uploaded_ids, direct_image_urls, failures = parallel_upload_files(
        image_file_names, chapter_full_path, catbox_client, max_workers
    )

    if not uploaded_ids:
        logging.error(f"Nenhuma imagem enviada com sucesso para {chapter_dir_name}. Não será possível criar o álbum.")
        return None, direct_image_urls, failures

    album_title = album_title_template.format(manga_name=manga_name, chapter_name=chapter_dir_name)
    album_description = album_description_template.format(manga_name=manga_name, chapter_name=chapter_dir_name)
    
    logging.info(f"Criando álbum para {chapter_dir_name} com {len(uploaded_ids)} imagens...")
    # Chama o método do cliente
    album_url = catbox_client.create_album(album_title, album_description, uploaded_ids)

    if album_url:
        logging.info(f"Álbum criado para {chapter_dir_name}: {album_url}")
    else:
        logging.error(f"Falha ao criar o álbum para {chapter_dir_name}.")

    return album_url, direct_image_urls, failures
