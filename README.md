# My-Cubari

Uma aplicação para gerenciar e visualizar mangas usando Electron e Python Eel.

## Estrutura do Projeto

- `electron-eel-app/`: Aplicação principal que combina Electron e Python Eel
  - `main.js`: Arquivo principal do Electron
  - `python/`: Código Python com backend da aplicação
  - `web/`: Frontend da aplicação (HTML, CSS, JS)
- Arquivos JSON: Configurações para cada manga/série (formato Cubari)

## Requisitos

### Node.js
- Node.js (v14 ou superior)
- npm (v6 ou superior)

### Python
- Python 3.6 ou superior
- pip (para instalação de pacotes)

### Dependências principais
- Electron
- Eel (Python)

## Instalação

### 1. Clone o repositório

```bash
git clone <URL_DO_SEU_REPOSITÓRIO>
cd My-Cubari
```

### 2. Instale as dependências JavaScript

```bash
cd electron-eel-app
npm install
```

### 3. Configure o ambiente Python

```bash
# Criar ambiente virtual (opcional, mas recomendado)
python -m venv env

# Ativar ambiente virtual 
# No Windows:
env\Scripts\activate
# No Linux/Mac:
source env/bin/activate

# Instalar dependências Python
pip install -r requirements.txt
```

## Executando a aplicação

```bash
# No diretório electron-eel-app
npm start
```

## Desenvolvimento

- Use `npm run dev` para iniciar no modo de desenvolvimento com DevTools
- Para construir uma versão distribuível: `npm run build`

## Versionamento

Este projeto está em desenvolvimento e sendo versionado gradualmente.