import os
import re
from tkinter import filedialog, Tk

# Inicializar o Tkinter para diálogos de seleção, mas ocultar a janela principal
# Isso é importante para que as funções de diálogo funcionem sem que uma janela Tk apareça desnecessariamente.
_root_tk = Tk()
_root_tk.withdraw()

def natural_sort_key(s):
    """Chave para ordenação natural de strings com números"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def get_image_files_from_dir(directory):
    """Retorna uma lista de arquivos de imagem em um diretório, ordenados naturalmente"""
    if not os.path.isdir(directory):
        return []
    
    return sorted(
        [os.path.join(directory, f) for f in os.listdir(directory) 
         if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))],
        key=lambda x: natural_sort_key(os.path.basename(x))
    )

def selecionar_arquivos():
    """Abre um diálogo para selecionar múltiplos arquivos."""
    # Usa a instância _root_tk para garantir que o Tkinter está inicializado
    arquivos = filedialog.askopenfilenames(title="Selecione os arquivos", parent=_root_tk)
    return list(arquivos)

def selecionar_pasta():
    """Abre um diálogo para selecionar uma pasta."""
    # Usa a instância _root_tk
    pasta = filedialog.askdirectory(title="Selecione uma pasta", parent=_root_tk)
    return pasta

def listar_arquivos_pasta(folder_path):
    """Lista os arquivos em uma pasta selecionada e suas subpastas."""
    if not os.path.isdir(folder_path):
        return []
    arquivos = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
            except OSError:
                size = 0 # Ou algum outro valor padrão se o arquivo não puder ser acessado
            arquivos.append({
                "name": file,
                "path": file_path,
                "size": size
            })
    return arquivos
