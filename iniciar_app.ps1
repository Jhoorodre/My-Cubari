# Script para iniciar a aplicacao a partir do diretorio raiz

# Tenta ativar o ambiente virtual
$envPath = ".\env_win\Scripts\Activate.ps1"
if (Test-Path $envPath) {
    Write-Host "Ativando ambiente virtual Python..."
    try {
        & $envPath
    } catch {
        Write-Warning "Falha ao ativar o ambiente virtual. Verifique se o ambiente esta configurado corretamente."
        Write-Warning $_.Exception.Message
    }
} else {
    Write-Warning "Aviso: Ambiente virtual env_win nao encontrado em $envPath. Tentando prosseguir..."
    Write-Warning "         Considere executar o script setup.bat ou setup.ps1 primeiro."
}

$appDir = ".\electron-eel-app"
$startScript = ".\start_app_utf8.ps1"

if (Test-Path $appDir) {
    Set-Location -Path $appDir
    if (Test-Path $startScript) {
        try {
            & $startScript
        } catch {
            Write-Error "Erro ao executar $startScript : $($_.Exception.Message)"
            Read-Host "Pressione Enter para sair"
        }
    } else {
        Write-Error "Erro: $startScript nao encontrado no diretorio $appDir."
        Read-Host "Pressione Enter para sair"
    }
    Set-Location -Path ".."
} else {
    Write-Error "Erro: Diretorio da aplicacao $appDir nao encontrado."
    Read-Host "Pressione Enter para sair"
}

# Opcional: Desativar o ambiente virtual ao sair (se foi ativado)
# if ($env:VIRTUAL_ENV) {
#     Write-Host "Desativando ambiente virtual..."
#     try {
#         deactivate
#     } catch {
#         Write-Warning "Comando 'deactivate' nao encontrado ou falhou."
#     }
# }
