@echo off
REM Configure codificação UTF-8 para o terminal
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
set PYTHONCOERCECLOCALE=1
set PYTHONIOENCODING=utf-8

REM Verifica múltiplas portas que o aplicativo pode usar
echo Verificando portas em uso...

REM Cria uma função para verificar e liberar uma porta
setlocal enabledelayedexpansion

REM Lista de portas para verificar
set "portas=3000 3001 3002 3003 3004 3005"

for %%p in (%portas%) do (
    echo Verificando porta %%p...
    netstat -ano | findstr :%%p | findstr LISTENING > nul
    if !errorlevel! equ 0 (
        echo Porta %%p está em uso.
        set /p resposta="Deseja tentar encerrar os processos usando esta porta? (S/N): "
        if /i "!resposta!"=="S" (
            for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p ^| findstr LISTENING') do (
                echo Tentando encerrar processo com PID %%a...
                taskkill /F /PID %%a 2>nul
                if !errorlevel! equ 0 (
                    echo Processo %%a encerrado com sucesso.
                ) else (
                    echo Não foi possível encerrar o processo %%a.
                )
            )
        ) else (
            echo Processo na porta %%p não será encerrado.
        )
    ) else (
        echo Porta %%p está livre.
    )
)

REM Tenta ativar o ambiente virtual Python a partir do diretório pai
IF EXIST "..\\env_win\\Scripts\\activate.bat" (
    echo Ativando ambiente virtual Python (env_win)...
    CALL "..\\env_win\\Scripts\\activate.bat"
) ELSE (
    echo Aviso: Ambiente virtual ..\\env_win nao encontrado. Tentando prosseguir...
    echo          Considere executar o script setup.bat na raiz do projeto.
)

echo.
echo Iniciando aplicação...
echo Pressione Ctrl+C para encerrar quando terminar
echo.

REM Iniciar a aplicação com codificação UTF-8 explícita
python -X utf8 start_app.py
