import eel
import os
import sys

# Adicionar o diretório python ao sys.path para permitir importações relativas corretas
# Isso é crucial para que os módulos dentro de 'python' possam se encontrar.
# O diretório 'python' é o pai de 'eel_interface', 'core', 'api_clients'
python_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(python_dir)) # Adiciona o diretório pai de 'python' (electron-eel-app)
sys.path.append(python_dir) # Adiciona o próprio diretório 'python'

# Agora podemos importar as funções expostas ao Eel
from eel_interface.eel_exposed_functions import (
    selecionar_arquivos_eel,
    selecionar_pasta_eel,
    listar_arquivos_pasta_eel,
    salvar_metadados_manga_eel,
    salvar_config_github_eel,
    load_config_github_eel,
    save_buzzheavier_config_eel,
    load_buzzheavier_config_eel,
    test_buzzheavier_connection_eel,
    upload_arquivo_eel,
    get_directories_eel
    # Adicione aqui outras funções expostas que foram movidas para eel_exposed_functions.py
)

if __name__ == '__main__':
    # Inicializa o Eel com a pasta web
    web_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'web')
    eel.init(web_dir)
    
    # Expor funções (elas já estão decoradas com @eel.expose em eel_exposed_functions.py)
    # O Eel as encontrará automaticamente se o módulo for importado e as funções estiverem decoradas.
    # Não é necessário chamá-las aqui explicitamente com eel.expose() novamente.

    print("Iniciando aplicação Eel...")
    # Inicia a aplicação Eel, abrindo a página manga_uploader.html
    # O Electron se encarregará de criar a janela.
    try:
        eel.start('manga_uploader.html', size=(1200, 800), block=True) # block=True é importante para manter o Python rodando
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("Aplicação Eel encerrada.")
    except Exception as e:
        print(f"Ocorreu um erro ao iniciar o Eel: {e}")
        # Considere um fallback ou log mais detalhado aqui
        # Por exemplo, tentar uma porta diferente se a padrão estiver em uso.
        # eel.start('manga_uploader.html', size=(1200, 800), mode='chrome', port=8001)