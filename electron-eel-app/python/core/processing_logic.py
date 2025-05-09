import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm # ADICIONADO: Importar tqdm
# from ..api_clients.github_client import GithubClient # Comentado ou a ser ajustado se necessário
from ..api_clients.catbox_client import CatboxClient # MODIFICADO: . -> ..
from ..api_clients.buzzheavier_client import upload_file_buzzheavier as core_upload_file_buzzheavier # MODIFICADO: . -> .. e renomeado para evitar conflito

from .file_system_utils import natural_sort_key as fs_natural_sort_key

# Configuração de logs para este módulo, se necessário, ou confiar no logging configurado no chamador.
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _upload_single_file_for_batch(file_path, host_config, catbox_client_instance=None):
    """Função auxiliar para fazer upload de um único arquivo com base na configuração do host."""
    host_type = host_config.get("type", "catbox")
    
    if host_type == "catbox":
        userhash = host_config.get("userhash")
        if not userhash:
            return file_path, None, "Userhash do Catbox não fornecido no host_config"
        
        # Usa a instância do cliente se fornecida, caso contrário, cria uma nova (menos eficiente para batch)
        client_to_use = catbox_client_instance if catbox_client_instance else CatboxClient(userhash)
        # O método upload_file da classe CatboxClient retorna um dicionário {"url": ..., "error": ...}
        result = client_to_use.upload_file(file_path) 
        return file_path, result.get("url"), result.get("error")

    elif host_type == "buzzheavier":
        api_key = host_config.get("apiKey")
        folder_id = host_config.get("folderId")
        is_public = host_config.get("fileVisibility", "public") == "public"
        if not api_key:
            return file_path, None, "API Key do Buzzheavier não fornecida no host_config"
        
        # A função core_upload_file_buzzheavier retorna url, error
        url, error = core_upload_file_buzzheavier(file_path, api_key, folder_id, is_public)
        return file_path, url, error
    else:
        return file_path, None, f"Tipo de host desconhecido: {host_type}"

def upload_files_to_host_parallel(full_file_paths, host_config, max_workers=5):
    """
    Faz upload de uma lista de arquivos (caminhos completos) para o host especificado em paralelo.

    Args:
        full_file_paths (list): Lista de caminhos de arquivo completos.
        host_config (dict): Dicionário de configuração do host. 
                              Ex: {'type': 'catbox', 'userhash': 'xxxx'}
                              Ex: {'type': 'buzzheavier', 'apiKey': 'yyyy', 'folderId': 'zz', 'fileVisibility': 'public'}
        max_workers (int): Número máximo de threads de upload.

    Returns:
        list: Uma lista de dicionários, cada um representando o resultado do upload de um arquivo.
              Ex: [{'path': '/path/to/img1.jpg', 'status': 'success', 'url': 'http://...'},
                   {'path': '/path/to/img2.png', 'status': 'error', 'error': 'Falha no upload'}]
    """
    results = []
    
    # Para Catbox, é mais eficiente criar o cliente uma vez se todos os uploads forem para Catbox
    catbox_client_instance = None
    if host_config.get("type") == "catbox" and host_config.get("userhash"):
        catbox_client_instance = CatboxClient(host_config["userhash"])

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Mapeia cada future para o seu caminho de arquivo original para fácil referência
        future_to_path = {
            executor.submit(_upload_single_file_for_batch, path, host_config, catbox_client_instance): path 
            for path in full_file_paths
        }
        
        # Usar tqdm para barra de progresso no console (útil para depuração do backend)
        for future in tqdm(as_completed(future_to_path), total=len(full_file_paths), desc=f"Uploading to {host_config.get('type')}"):
            original_path = future_to_path[future]
            try:
                _original_path_returned, url, error_msg = future.result() # _original_path_returned deve ser igual a original_path
                if error_msg:
                    results.append({'path': original_path, 'status': 'error', 'error': str(error_msg)})
                    logger.error(f"Falha no upload de {original_path}: {error_msg}")
                else:
                    results.append({'path': original_path, 'status': 'success', 'url': url})
                    logger.info(f"Sucesso no upload de {original_path}: {url}")
            except Exception as exc:
                results.append({'path': original_path, 'status': 'error', 'error': str(exc)})
                logger.error(f"Exceção durante o upload de {original_path}: {exc}")
                
    return results

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
