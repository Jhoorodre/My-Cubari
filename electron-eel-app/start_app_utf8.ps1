# Script PowerShell para iniciar a aplicação com UTF-8 configurado corretamente

# Define a codificação do terminal como UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Define as variáveis de ambiente para UTF-8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONLEGACYWINDOWSSTDIO = "utf-8"
$env:PYTHONCOERCECLOCALE = "1"

# Lista de portas que o aplicativo pode usar
$portas = @(3000, 3001, 3002, 3003, 3004, 3005)

# Função para verificar e liberar portas
function Test-AndClearPort {
    param (
        [int]$porta
    )

    Write-Host "Verificando se há processos usando a porta $porta..."
    $processosNaPorta = Get-NetTCPConnection -LocalPort $porta -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

    if ($processosNaPorta) {
        foreach ($processoId in $processosNaPorta) {
            try {
                $processoInfo = Get-Process -Id $processoId -ErrorAction SilentlyContinue
                
                if ($processoInfo) {
                    Write-Host "Encontrado processo $($processoInfo.ProcessName) (ID: $processoId) usando a porta $porta"
                    $resposta = Read-Host "Deseja encerrar este processo? [S/N]"
                    
                    if ($resposta -eq "S" -or $resposta -eq "s") {
                        Write-Host "Encerrando processo $($processoInfo.ProcessName) (ID: $processoId)..."
                        Stop-Process -Id $processoId -Force
                        Write-Host "Processo encerrado com sucesso." -ForegroundColor Green
                    } else {
                        Write-Host "O processo não foi encerrado. A aplicação pode tentar usar outra porta." -ForegroundColor Yellow
                    }
                } else {
                    Write-Host "Processo ID $processoId não encontrado" -ForegroundColor Yellow
                }
            }
            catch {
                $errorMessage = $_.Exception.Message
                Write-Host "Erro ao processar o PID $processoId: $errorMessage" -ForegroundColor Red
            }
        }
    }
    else {
        Write-Host "Nenhum processo encontrado usando a porta $porta." -ForegroundColor Green
    }
}

# Verifica e libera cada porta
foreach ($porta in $portas) {
    Test-AndClearPort -porta $porta
}

# Tenta ativar o ambiente virtual Python a partir do diretório pai
$parentEnvPath = "..\\env_win\\Scripts\\Activate.ps1"
if (Test-Path $parentEnvPath) {
    Write-Host "Ativando ambiente virtual Python (env_win)..."
    try {
        & $parentEnvPath
    } catch {
        Write-Warning "Falha ao ativar o ambiente virtual Python em $parentEnvPath."
        Write-Warning $_.Exception.Message
    }
} else {
    Write-Warning "Aviso: Ambiente virtual $parentEnvPath nao encontrado."
    Write-Warning "         Considere executar o script setup.bat ou setup.ps1 na raiz do projeto."
}

# REMOVIDO - Bloco de inicialização do run_server.py
# Write-Host "Iniciando servidor Python (run_server.py)..."
# Start-Process python -ArgumentList "run_server.py" -WindowStyle Hidden -PassThru
#
# Write-Host "Aguardando o servidor Python iniciar (5 segundos)..."
# Start-Sleep -Seconds 5

Write-Host "Iniciando aplicacao Electron..."
electron .

# Opcional: Desativar o ambiente virtual ao sair
# if ($env:VIRTUAL_ENV) {
#     Write-Host "Desativando ambiente virtual..."
#     try {
#         deactivate
#     } catch {
#         Write-Warning "Comando \'deactivate\' nao encontrado ou falhou."
#     }
# }
