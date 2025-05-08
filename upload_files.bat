@echo off
setlocal

:: Adicionado suporte para argumentos de linha de comando
if "%~1"=="" (
    echo ERRO: Caminho da pasta de origem não especificado.
    exit /b 1
)
if "%~2"=="" (
    echo ERRO: Caminho da pasta de destino não especificado.
    exit /b 1
)
set "source_folder=%~1"
set "destination_folder=%~2"

:: Configurações
set "log_file=C:\caminho\para\arquivo\de\log\upload_log.txt"

:: Função para registrar logs
:log
echo %date% %time%: %* >> "%log_file%"
exit /b

:: Verifica se a pasta de origem existe
if not exist "%source_folder%" (
    call :log "ERRO: A pasta de origem não existe: %source_folder%"
    exit /b 1
)

:: Verifica se a pasta de destino existe, se não, cria
if not exist "%destination_folder%" (
    mkdir "%destination_folder%"
    if errorlevel 1 (
        call :log "ERRO: Não foi possível criar a pasta de destino: %destination_folder%"
        exit /b 1
    )
)

:: Faz o upload dos arquivos
for %%f in ("%source_folder%\*") do (
    copy "%%f" "%destination_folder%"
    if errorlevel 1 (
        call :log "ERRO: Falha ao copiar o arquivo: %%f"
    ) else (
        call :log "SUCESSO: Arquivo copiado: %%f"
    )
)

call :log "Upload concluído."
endlocal
exit /b 0