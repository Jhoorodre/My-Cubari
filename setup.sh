#!/bin/bash
# Script de configuração para o projeto My-Cubari

echo "=== Configurando o ambiente para My-Cubari ==="
echo ""

# Adicionado suporte para Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Detectado Windows. Use setup.bat para configurar o ambiente."
    exit 1
fi

# Verificar se Python está instalado
if command -v python3 &>/dev/null; then
    echo "✅ Python encontrado"
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    echo "✅ Python encontrado"
    PYTHON_CMD="python"
else
    echo "❌ Python não encontrado. Por favor, instale o Python 3.6 ou superior."
    exit 1
fi

echo "Versão Python: $($PYTHON_CMD --version)"

# Verificar se Node.js está instalado
if command -v node &>/dev/null; then
    echo "✅ Node.js encontrado"
    echo "Versão Node.js: $(node --version)"
else
    echo "❌ Node.js não encontrado. Por favor, instale o Node.js v14 ou superior."
    exit 1
fi

# Verificar se npm está instalado
if command -v npm &>/dev/null; then
    echo "✅ npm encontrado"
    echo "Versão npm: $(npm --version)"
else
    echo "❌ npm não encontrado. Por favor, instale o npm."
    exit 1
fi

# Criar ambiente virtual Python
echo ""
echo "=== Configurando ambiente virtual Python ==="
if [ ! -d "env" ]; then
    echo "Criando ambiente virtual 'env'..."
    $PYTHON_CMD -m venv env
    if [ $? -ne 0 ]; then
        echo "X Falha ao criar ambiente virtual."
        exit 1
    fi
    echo "Ambiente virtual 'env' criado."
else
    echo "Ambiente virtual 'env' já existe."
fi

source env/bin/activate

# Instalar dependências Python
echo ""
echo "=== Instalando dependências Python ==="
pip install -r requirements.txt

# Instalar dependências Node.js
echo ""
echo "=== Instalando dependências Node.js ==="
cd electron-eel-app
npm install

echo ""
echo "=== Configuração concluída! ==="
echo "Para ativar o ambiente virtual Python: source env/bin/activate"
echo "Para iniciar a aplicação: cd electron-eel-app && npm start"
echo ""