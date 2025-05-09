import eel
import os
import sys
import logging # Adicionado
import codecs

# Configuração de logs para este módulo - explicitamente com codificação UTF-8
# Usar um formato similar ao run_server.py para consistência
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - [%(module)s.%(funcName)s:%(lineno)d] - %(message)s',
                   handlers=[logging.StreamHandler(codecs.getwriter('utf-8')(sys.stdout.buffer))])

# Adicionar o diretório raiz do projeto Python ao sys.path
# Isso permite que 'python' seja tratado como um pacote de nível superior.
python_dir = os.path.dirname(os.path.abspath(__file__)) # .../electron-eel-app/python
project_root = os.path.dirname(python_dir) # .../electron-eel-app

if project_root not in sys.path:
    sys.path.insert(0, project_root) # Adiciona 'electron-eel-app' ao início do sys.path

# Não é mais necessário adicionar python_dir separadamente se project_root está no path
# e os imports são feitos como python.module.xxx

logging.info(f"sys.path atualizado: {sys.path}")

# Agora podemos importar as funções expostas ao Eel usando o caminho absoluto do pacote
try:
    from python.eel_interface.eel_exposed_functions import (
        selecionar_arquivos_eel,
        selecionar_pasta_eel,
        listar_arquivos_pasta_eel,
        salvar_metadados_manga_eel,
        save_github_config_eel,
        load_github_config_eel,
        save_buzzheavier_config_eel,
        load_buzzheavier_config_eel,
        test_buzzheavier_connection_eel,
        upload_arquivo_eel,
        get_directories_eel,
        parallel_upload_files_eel,
        process_manga_chapter_eel,
        create_catbox_album_eel,
        save_catbox_config_eel,
        load_catbox_config_eel,
        list_json_files_eel, # Renomeado de list_json_files para consistência
        read_json_file_eel,  # Renomeado de read_json_file para consistência
        get_system_info_eel, # Renomeado de get_system_info para consistência
        process_chapter_eel, # Placeholder
        rodar_manga_processor_eel # Placeholder, renomeado de rodar_manga_processor
    )
    logging.info("Funções Eel de 'python.eel_interface.eel_exposed_functions' importadas com sucesso.")
except ImportError as e:
    logging.error(f"Erro ao importar funções de 'python.eel_interface.eel_exposed_functions': {e}")
    # Considerar sair se as funções Eel não puderem ser carregadas, pois a aplicação não funcionará.
    sys.exit(1)
except Exception as e:
    logging.error(f"Erro inesperado durante a importação de funções Eel: {e}")
    sys.exit(1)


if __name__ == '__main__':
    logging.info("=" * 50)
    logging.info("Iniciando script python/main.py (para Electron)")
    logging.info("=" * 50)

    # Inicializa o Eel com a pasta web
    web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
    eel.init(web_dir)
    logging.info(f"Eel inicializado com o diretório web: {web_dir}")
    
    # Expor funções (elas já estão decoradas com @eel.expose em eel_exposed_functions.py)
    # O Eel as encontrará automaticamente se o módulo for importado e as funções estiverem decoradas.
    # Não é necessário chamá-las aqui explicitamente com eel.expose() novamente.
    logging.info("Funções Eel já devem estar expostas devido à importação e decoradores @eel.expose.")
    logging.info("Tentando iniciar aplicação Eel para Electron...")
    # Inicia a aplicação Eel, abrindo a página manga_uploader.html
    # O Electron se encarregará de criar a janela.
    
    # Lista de portas para tentar, começando com a porta 3000 como padrão
    portas_para_tentar = [3000, 3001, 3002, 3003, 3004, 3005]
    porta_utilizada = None
    
    try:
        for porta in portas_para_tentar:
            try:
                logging.info(f"Tentando iniciar servidor Eel na porta {porta}...")
                # Enviamos uma mensagem especial para o Electron capturar a porta
                print(f"EEL_PORT:{porta}", flush=True)
                
                eel.start('manga_uploader.html', size=(1200, 800), block=True, port=porta) 
                porta_utilizada = porta
                logging.info(f"Aplicação Eel iniciada e bloqueando na porta {porta}.")
                break
            except OSError as e:
                if hasattr(e, 'winerror') and e.winerror == 10048 or hasattr(e, 'errno') and e.errno == 98:
                    logging.error(f"Porta {porta} já está em uso, tentando a próxima...")
                    # Continua para a próxima porta
                else:
                    logging.error(f"Erro de sistema operacional ao iniciar o Eel: {e}")
                    break
        
        if porta_utilizada is None:
            logging.error("Não foi possível iniciar o servidor Eel em nenhuma porta disponível.")
            logging.error("Verifique se há muitas instâncias da aplicação rodando.")
            
    except (SystemExit, MemoryError, KeyboardInterrupt) as e:
        logging.info(f"Aplicação Eel encerrada (SystemExit/MemoryError/KeyboardInterrupt): {e}")
    except Exception as e:
        logging.error(f"Ocorreu um erro inesperado ao iniciar o Eel: {e}")
        # Considere um fallback ou log mais detalhado aqui
        
    logging.info("Script python/main.py finalizado.")