@echo off
REM Script de configuracao para Windows

echo === Configurando o ambiente para My-Cubari (Windows) ===
echo.

REM Verificar se Python esta instalado e obter o caminho
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python nao encontrado. Por favor, instale o Python 3.8 ou superior.
    goto :eof
) else (
    echo V Python encontrado
    for /f "tokens=*" %%i in ('python -c "import sys; print(sys.executable)"') do set PYTHON_EXE=%%i
    echo    Caminho: %PYTHON_EXE%
)

REM Verificar se Node.js esta instalado
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Node.js nao encontrado. Por favor, instale o Node.js v14 ou superior.
    goto :eof
) else (
    echo V Node.js encontrado
    node --version
)

REM Verificar se npm esta instalado
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X npm nao encontrado. Por favor, instale o npm (geralmente vem com o Node.js).
    goto :eof
) else (
    echo V npm encontrado
    npm --version
)

REM Criar ambiente virtual Python se nao existir
if not exist .\env_win\Scripts\activate.bat (
    echo.
    echo === Configurando ambiente virtual Python (env_win) ===
    "%PYTHON_EXE%" -m venv env_win
    if %errorlevel% neq 0 (
        echo X Falha ao criar ambiente virtual.
        goto :eof
    )
    echo Ambiente virtual env_win criado.
) else (
    echo Ambiente virtual env_win ja existe.
)

echo.
echo === Ativando ambiente virtual e instalando dependencias Python ===
CALL .\env_win\Scripts\activate.bat

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo X Falha ao instalar dependencias Python.
    CALL .\env_win\Scripts\deactivate.bat
    goto :eof
)

echo.
echo === Instalando dependencias Node.js ===
cd electron-eel-app
npm install
if %errorlevel% neq 0 (
    echo X Falha ao instalar dependencias Node.js.
    cd ..
    CALL .\env_win\Scripts\deactivate.bat
    goto :eof
)
cd ..

REM Desativar o ambiente virtual (opcional, mas boa pratica para scripts de setup)
REM CALL .\env_win\Scripts\deactivate.bat

echo.
echo === Configuracao concluida! ===
echo Para ativar o ambiente virtual Python manualmente no futuro, execute:
echo   .\env_win\Scripts\activate.bat
echo Para iniciar a aplicacao, use um dos scripts:
echo   iniciar_app.bat
echo   iniciar_app.ps1
echo (Eles tentarao ativar o ambiente virtual automaticamente)
echo.

:eof
pause
