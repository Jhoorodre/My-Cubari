@echo off
REM Arquivo batch para iniciar a aplicacao a partir do diretorio raiz

REM Tenta ativar o ambiente virtual
IF EXIST .\env_win\Scripts\activate.bat (
    echo Ativando ambiente virtual Python...
    CALL .\env_win\Scripts\activate.bat
) ELSE (
    echo Aviso: Ambiente virtual env_win nao encontrado. Tentando prosseguir...
    echo          Considere executar o script setup.bat primeiro.
)

cd .\electron-eel-app
REM Verifica se start_app_utf8.bat existe antes de tentar executa-lo
IF EXIST .\start_app_utf8.bat (
    CALL .\start_app_utf8.bat
) ELSE (
    echo Erro: start_app_utf8.bat nao encontrado no diretorio electron-eel-app.
    pause
)

REM Opcional: Desativar o ambiente virtual ao sair (se foi ativado)
REM IF DEFINED VIRTUAL_ENV (
REM     echo Desativando ambiente virtual...
REM     CALL .\env_win\Scripts\deactivate.bat
REM )
cd ..
