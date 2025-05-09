document.addEventListener('DOMContentLoaded', () => {
    // --- Seletores da Nova UI ---
    const navLinks = document.querySelectorAll('.main-nav .nav-link');
    const views = document.querySelectorAll('.view');
    const contentTitle = document.getElementById('content-title');
    // const backButton = document.getElementById('back-button'); // Lógica do botão voltar a ser implementada se necessário

    // --- Seletores para Funcionalidades (adaptados da lógica original) ---
    // Área de Logs
    const logsArea = document.getElementById('logs-area');
    // TODO: Adicionar um botão 'clear-logs-button' ao HTML da view de Log se desejado.
    // const clearLogsButton = document.getElementById('clear-logs-button');

    // Gerenciamento de Arquivos (View Upload)
    const addFilesButton = document.getElementById('add-files-button');
    const addPastaButton = document.getElementById('add-pasta-button');
    const filterInput = document.getElementById('filter-input');
    const aplicarFilterButton = document.getElementById('aplicar-button'); // Renomeado de 'aplicar-button' para clareza
    const fileTableBody = document.getElementById('file-list'); // ID da tbody na nova HTML
    const marcarTodosButton = document.getElementById('marcar-todos');
    const desmarcarTodosButton = document.getElementById('desmarcar-todos');
    const removerButton = document.getElementById('remover-button');
    const limparListaButton = document.getElementById('limpar-button'); // Renomeado de 'limpar-button' para clareza
    const selectionInfoSpan = document.getElementById('selection-info');

    // Metadados do Mangá (View Upload)
    const tituloMangaInput = document.getElementById('titulo-manga');
    const titulosAlternativosInput = document.getElementById('titulos-alternativos');
    const descricaoTextarea = document.getElementById('descricao');
    const autorInput = document.getElementById('autor');
    const artistaInput = document.getElementById('artista');
    const grupoScanInput = document.getElementById('grupo-scan');
    const urlCapaInput = document.getElementById('url-capa');
    const statusInput = document.getElementById('status'); // Ex: Finalizado, Em Lançamento
    const tituloCapituloInput = document.getElementById('titulo-capitulo');
    // TODO: Adicionar campos 'last-update' e botão 'update-timestamp-button' ao HTML de metadados se desejado.
    // const lastUpdateInput = document.getElementById('last-update');
    // const updateTimestampButton = document.getElementById('update-timestamp-button');
    const preencherAutomaticamenteButton = document.getElementById('preencher-automaticamente');
    const limparCamposMetadataButton = document.getElementById('limpar-campos'); // Renomeado para clareza
    const salvarMetadadosButton = document.getElementById('salvar-metadados');

    // Configurações GitHub (View Configuração)
    const githubUsernameInput = document.getElementById('github-username');
    const githubTokenInput = document.getElementById('github-token');
    const githubRepoInput = document.getElementById('github-repo');
    const githubBranchInput = document.getElementById('github-branch');
    const salvarConfigGithubButton = document.getElementById('salvar-config-github');

    // Upload (Footer da View Upload)
    const uploadPrincipalButton = document.getElementById('upload-button'); // Botão principal de Upload
    const urlsSalvasButton = document.getElementById('urls-button'); // Presumindo que terá funcionalidade
    const titulosSalvosButton = document.getElementById('titulos-button'); // Presumindo que terá funcionalidade

    // Buzzheavier Host Configuration
    const buzzHeavierApiKeyInput = document.getElementById('buzzheavier-api-key');
    const buzzHeavierFolderIdInput = document.getElementById('buzzheavier-folder-id');
    const buzzHeavierFileVisibilitySelect = document.getElementById('buzzheavier-file-visibility');
    const saveBuzzHeavierConfigButton = document.getElementById('save-buzzheavier-config');
    const testBuzzHeavierConnectionButton = document.getElementById('test-buzzheavier-connection');

    // --- Seletores para Catbox Host Configuration ---
    const catboxUserhashInput = document.getElementById('catbox-userhash');
    const saveCatboxConfigButton = document.getElementById('save-catbox-config');

    // --- Estado da Aplicação ---
    let currentFiles = []; // Array para armazenar os arquivos adicionados

    // --- Lógica de Navegação da Nova UI ---
    function showView(viewId, title) {
        views.forEach(view => {
            view.classList.remove('active');
            if (view.id === viewId) {
                view.classList.add('active');
            }
        });
        contentTitle.textContent = title;
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === viewId.replace('view-', '')) {
                link.classList.add('active');
            }
        });
    }

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const viewName = link.dataset.view;
            const viewId = `view-${viewName}`;
            let title = link.textContent.replace(link.querySelector('.nav-icon').textContent, '').trim();
            showView(viewId, title);
        });
    });

    const configOptionButtons = document.querySelectorAll('.config-option-button');
    const configContents = document.querySelectorAll('.config-content');
    configOptionButtons.forEach(button => {
        button.addEventListener('click', () => {
            configOptionButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const targetConfig = button.dataset.configTarget;
            configContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `config-${targetConfig}`) {
                    content.classList.add('active');
                }
            });
        });
    });

    const hostTabButtons = document.querySelectorAll('.host-tab-button');
    const hostTabContents = document.querySelectorAll('.host-tab-content');
    hostTabButtons.forEach(button => {
        button.addEventListener('click', () => {
            hostTabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const targetHostTab = button.dataset.hostTab;
            hostTabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `host-tab-${targetHostTab}`) {
                    content.classList.add('active');
                }
            });
        });
    });

    showView('view-upload', 'Upload'); // Inicializar com a view de Upload

    // --- Lógica de Logging ---
    function addLog(message, type = 'info') {
        if (!logsArea) return;
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`; 
        logEntry.textContent = `[${timestamp}] ${message}`;
        logsArea.appendChild(logEntry);
        logsArea.scrollTop = logsArea.scrollHeight;
    }

    // Função para registrar ações do frontend no backend e no log local
    async function logAction(message, level = 'info', toBackend = true) {
        addLog(message, level); // Log local sempre
        if (toBackend && eel && typeof eel.log_frontend_action === 'function') {
            try {
                await eel.log_frontend_action(message, level)();
            } catch (error) {
                console.error('Erro ao chamar eel.log_frontend_action:', error);
                addLog(`Falha ao enviar log para backend: ${error}`, 'error');
            }
        } else if (toBackend) {
            console.warn('eel.log_frontend_action não está disponível para:', message);
        }
    }

    if (eel && typeof eel.expose === 'function') {
        eel.expose(addLog, 'add_log_message_js'); // Python pode chamar esta função
    }

    // if (clearLogsButton) {
    //     clearLogsButton.addEventListener('click', () => {
    //         if (logsArea) logsArea.innerHTML = '';
    //         addLog('Logs limpos.');
    //     });
    // }

    // --- Lógica de Gerenciamento de Arquivos ---
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / 1048576).toFixed(1) + ' MB';
    }

    function getStatusText(status) {
        switch (status) {
            case 'pending': return 'Pendente';
            case 'uploading': return 'Enviando...';
            case 'success': return 'Enviado';
            case 'error': return 'Erro';
            default: return 'Desconhecido';
        }
    }
    
    function updateSelectionInfo() {
        if (!selectionInfoSpan) return;
        // Modifica para usar a lista que está sendo renderizada, não apenas currentFiles
        const displayedFiles = fileTableBody.rows.length > 0 ? getDisplayedFiles() : [];
        const selectedCount = displayedFiles.filter(file => file.selected).length;
        selectionInfoSpan.textContent = `Sel: ${selectedCount} / Exibidos: ${displayedFiles.length} (Total: ${currentFiles.length})`;
    }

    function renderFileList(filesToRender = currentFiles) { // Modificado para aceitar uma lista de arquivos
        if (!fileTableBody) return;
        fileTableBody.innerHTML = ''; // Limpar tabela
        
        // Se nenhum arquivo for passado (ex: filtro não encontrou nada), exibe a lista original ou uma mensagem
        const files = filesToRender.length > 0 || filterInput.value.trim() ? filesToRender : currentFiles;

        files.forEach((file) => {
            const originalIndex = currentFiles.findIndex(f => f.path === file.path); // Encontra o índice original
            const row = fileTableBody.insertRow();
            row.className = file.selected ? 'selected' : '';
            // Adiciona um data attribute para fácil identificação do arquivo original
            row.dataset.filePath = file.path; 
            row.innerHTML = `
                <td>${file.name} ${file.chapter ? '/ ' + file.chapter : ''} ${file.manga ? '/ ' + file.manga : ''}</td>
                <td>${formatFileSize(file.size)}</td>
                <td class="status-${file.status}">${getStatusText(file.status)}</td>
            `;
            row.addEventListener('click', () => {
                if (originalIndex !== -1) { // Garante que o arquivo original foi encontrado
                    currentFiles[originalIndex].selected = !currentFiles[originalIndex].selected;
                    // Re-renderiza com a mesma lista que foi passada (ou a lista original se o filtro estiver vazio)
                    const currentFilterText = filterInput.value.toLowerCase().trim();
                    if (currentFilterText) {
                        aplicarFilterButton.click(); // Re-aplica o filtro para manter a visualização consistente
                    } else {
                        renderFileList(currentFiles);
                    }
                }
            });
        });
        updateSelectionInfo();
    }

    // Função auxiliar para obter os arquivos atualmente exibidos na tabela
    function getDisplayedFiles() {
        const displayedFilePaths = Array.from(fileTableBody.rows).map(row => row.dataset.filePath);
        return currentFiles.filter(file => displayedFilePaths.includes(file.path));
    }

    function addFileToApp(fileData) { // fileData: {name, path, size, chapter?, manga?}
        if (currentFiles.some(f => f.path === fileData.path)) {
            addLog(`Arquivo já adicionado: ${fileData.name}`, 'warn');
            return;
        }
        currentFiles.push({
            ...fileData,
            selected: true, // Selecionar por padrão ao adicionar
            status: 'pending'
        });
    }

    if (addFilesButton) {
        addFilesButton.addEventListener('click', async () => {
            if (!eel) return;
            try {
                const files = await eel.selecionar_arquivos_eel()();
                if (files && files.length > 0) {
                    files.forEach(file => addFileToApp({ name: file.name, path: file.path, size: file.size }));
                    renderFileList();
                    addLog(`${files.length} arquivo(s) adicionado(s).`);
                }
            } catch (error) {
                addLog(`Erro ao selecionar arquivos: ${error}`, 'error');
            }
        });
    }

    if (addPastaButton) {
        addPastaButton.addEventListener('click', async () => {
            if (!eel) return;
            try {
                // A função selecionar_pasta() deve retornar o caminho da pasta
                // A função listar_arquivos_pasta(caminho) deve retornar a lista de arquivos {name, path, size}
                const folderPath = await eel.selecionar_pasta_eel()();
                if (folderPath) {
                    addLog(`Listando arquivos da pasta: ${folderPath}`);
                    const filesInFolder = await eel.listar_arquivos_pasta_eel(folderPath)(); // Supondo que esta função exista no Python
                    if (filesInFolder && filesInFolder.length > 0) {
                        filesInFolder.forEach(file => addFileToApp({ name: file.name, path: file.path, size: file.size }));
                        renderFileList();
                        addLog(`${filesInFolder.length} arquivo(s) da pasta adicionado(s).`);
                    } else {
                        addLog(`Nenhum arquivo encontrado na pasta selecionada.`);
                    }
                }
            } catch (error) {
                addLog(`Erro ao selecionar pasta ou listar arquivos: ${error}`, 'error');
            }
        });
    }
    
    // TODO: Implementar lógica de filtro com aplicarFilterButton e filterInput
    if(aplicarFilterButton){
        aplicarFilterButton.addEventListener('click', () => {
            const filterText = filterInput.value.toLowerCase().trim();
            if (!filterText) {
                // Se o filtro estiver vazio, renderizar todos os arquivos
                renderFileList(currentFiles); // Passa a lista original
                addLog('Filtro limpo. Exibindo todos os arquivos.', 'info');
                return;
            }

            const filteredFiles = currentFiles.filter(file => {
                const nameMatch = file.name && file.name.toLowerCase().includes(filterText);
                const chapterMatch = file.chapter && file.chapter.toLowerCase().includes(filterText);
                const mangaMatch = file.manga && file.manga.toLowerCase().includes(filterText);
                return nameMatch || chapterMatch || mangaMatch;
            });

            renderFileList(filteredFiles); // Passa a lista filtrada
            addLog(`Filtro aplicado: "${filterText}". ${filteredFiles.length} arquivo(s) encontrado(s).`, 'info');
        });
    }

    if (marcarTodosButton) {
        marcarTodosButton.addEventListener('click', () => {
            const filesToModify = getDisplayedFiles();
            filesToModify.forEach(file => {
                const originalFile = currentFiles.find(f => f.path === file.path);
                if (originalFile) originalFile.selected = true;
            });
            const currentFilterText = filterInput.value.toLowerCase().trim();
            if (currentFilterText) aplicarFilterButton.click(); else renderFileList();
        });
    }

    if (desmarcarTodosButton) {
        desmarcarTodosButton.addEventListener('click', () => {
            const filesToModify = getDisplayedFiles();
            filesToModify.forEach(file => {
                const originalFile = currentFiles.find(f => f.path === file.path);
                if (originalFile) originalFile.selected = false;
            });
            const currentFilterText = filterInput.value.toLowerCase().trim();
            if (currentFilterText) aplicarFilterButton.click(); else renderFileList();
        });
    }

    if (removerButton) {
        removerButton.addEventListener('click', () => {
            const selectedPaths = getDisplayedFiles().filter(file => file.selected).map(f => f.path);
            currentFiles = currentFiles.filter(file => !selectedPaths.includes(file.path));
            
            const currentFilterText = filterInput.value.toLowerCase().trim();
            if (currentFilterText) {
                aplicarFilterButton.click(); // Re-aplica o filtro
            } else {
                renderFileList(); // Renderiza a lista atualizada
            }
            addLog('Arquivos selecionados removidos da lista.');
        });
    }

    if (limparListaButton) {
        limparListaButton.addEventListener('click', () => {
            currentFiles = [];
            renderFileList();
            addLog('Lista de arquivos limpa.');
        });
    }
    
    // --- Lógica de Metadados ---
    if (salvarMetadadosButton) {
        salvarMetadadosButton.addEventListener('click', async () => {
            const metadata = {
                titulo: tituloMangaInput.value,
                titulosAlternativos: titulosAlternativosInput.value,
                descricao: descricaoTextarea.value,
                autor: autorInput.value,
                artista: artistaInput.value,
                grupoScan: grupoScanInput.value,
                urlCapa: urlCapaInput.value,
                status: statusInput.value,
                tituloCapitulo: tituloCapituloInput.value,
                // lastUpdate: lastUpdateInput.value // Se o campo for adicionado
            };
            if (!eel) return;
            try {
                // Supondo uma função Python para salvar/processar metadados
                await eel.salvar_metadados_manga_eel(metadata)(); 
                addLog('Metadados do mangá salvos (simulado).', 'success');
            } catch (error) {
                addLog(`Erro ao salvar metadados: ${error}`, 'error');
            }
        });
    }

    if (limparCamposMetadataButton) {
        limparCamposMetadataButton.addEventListener('click', () => {
            tituloMangaInput.value = '';
            titulosAlternativosInput.value = '';
            descricaoTextarea.value = '';
            autorInput.value = '';
            artistaInput.value = '';
            grupoScanInput.value = '';
            urlCapaInput.value = '';
            statusInput.value = '';
            tituloCapituloInput.value = '';
            logAction('Campos de metadados limpos pelo usuário.', 'info', false);
        });
    }
    // TODO: Implementar lógica para preencherAutomaticamenteButton
    if(preencherAutomaticamenteButton){
        preencherAutomaticamenteButton.addEventListener('click', () => {
            logAction('Tentativa de preenchimento automático de metadados (funcionalidade pendente).', 'info');
        });
    }
    // TODO: Implementar lógica para updateTimestampButton se o campo for adicionado


    // --- Lógica de Configurações do GitHub ---
    if (salvarConfigGithubButton) {
        salvarConfigGithubButton.addEventListener('click', async () => {
            const config = {
                username: githubUsernameInput.value,
                token: githubTokenInput.value,
                repo: githubRepoInput.value,
                branch: githubBranchInput.value,
            };
            if (!config.username || !config.token || !config.repo || !config.branch) {
                logAction('Falha ao salvar config GitHub: Todos os campos são obrigatórios.', 'error', false);
                return;
            }
            logAction(`Tentando salvar configurações do GitHub: ${JSON.stringify(config)}`, 'info');
            if (!eel) return;
            try {
                const result = await eel.save_github_config_eel(config.token, config.username, config.repo, config.branch)(); 
                if (result && result.status === 'success') {
                    logAction('Configurações do GitHub salvas com sucesso.', 'success');
                } else {
                    logAction(`Erro ao salvar configurações do GitHub: ${result.message || 'Erro desconhecido'}`, 'error');
                }
            } catch (error) {
                logAction(`Erro catastrófico ao salvar configurações do GitHub: ${error}`, 'error');
            }
        });
    }

    async function loadGitHubConfig() {
        logAction('Tentando carregar configurações do GitHub...', 'info', false);
        if (!eel || !githubUsernameInput) return;
        try {
            const config = await eel.load_github_config_eel()();
            if (config && config.token) { // Verificar um campo chave como token
                githubUsernameInput.value = config.repo_owner || ''; // Ajustado para repo_owner
                githubTokenInput.value = config.token || '';
                githubRepoInput.value = config.repo_name || ''; // Ajustado para repo_name
                githubBranchInput.value = config.branch || 'main';
                logAction(`Configurações do GitHub carregadas: ${JSON.stringify(config)}`, 'info', false);
            } else if (config && config.error) {
                logAction(`Erro retornado ao carregar config GitHub: ${config.error}`, 'error', false);
            } else {
                logAction('Nenhuma configuração do GitHub encontrada ou configuração incompleta.', 'info', false);
            }
        } catch (e) {
            logAction(`Erro ao carregar configurações do GitHub: ${e}`, 'error', false);
        }
    }

    // --- Lógica de Configurações do Buzzheavier ---
    if (saveBuzzHeavierConfigButton) {
        saveBuzzHeavierConfigButton.addEventListener('click', async () => {
            const apiKey = buzzHeavierApiKeyInput.value.trim();
            if (!apiKey) {
                addLog('É necessário fornecer uma API Key do Buzzheavier', 'error');
                return;
            }

            const config = {
                apiKey: apiKey,
                folderId: buzzHeavierFolderIdInput.value.trim() || null,
                fileVisibility: buzzHeavierFileVisibilitySelect.value
            };

            logAction(`Tentando salvar configurações do Buzzheavier: ${JSON.stringify(config)}`, 'info');
            if (!eel) return;
            try {
                const result = await eel.save_buzzheavier_config_eel(config.apiKey, config.folderId, config.fileVisibility)();
                if (result && result.status === 'success') {
                    addLog('Configurações do Buzzheavier salvas com sucesso.', 'success');
                } else {
                    addLog(`Erro ao salvar configurações: ${result.message || 'Erro desconhecido'}`, 'error');
                }
            } catch (error) {
                addLog(`Erro ao salvar configurações do Buzzheavier: ${error}`, 'error');
            }
        });
    }

    if (testBuzzHeavierConnectionButton) {
        testBuzzHeavierConnectionButton.addEventListener('click', async () => {
            const apiKey = buzzHeavierApiKeyInput.value.trim();
            if (!apiKey) {
                addLog('É necessário fornecer uma API Key para testar a conexão', 'error');
                return;
            }

            if (!eel) return;
            try {
                addLog('Testando conexão com Buzzheavier...', 'info');
                const result = await eel.test_buzzheavier_connection_eel(apiKey)();
                if (result && result.success) {
                    addLog(`Conexão com Buzzheavier bem sucedida! Usuário: ${result.username || 'Desconhecido'}`, 'success');
                } else {
                    addLog(`Falha na conexão: ${result.error || 'Erro desconhecido'}`, 'error');
                }
            } catch (error) {
                addLog(`Erro ao testar conexão: ${error}`, 'error');
            }
        });
    }

    // Função para carregar as configurações salvas do Buzzheavier
    async function loadBuzzHeavierConfig() {
        logAction('Tentando carregar configurações do Buzzheavier...', 'info', false);
        if (!eel || !buzzHeavierApiKeyInput) return;
        try {
            const config = await eel.load_buzzheavier_config_eel()();
            if (config && config.apiKey) {
                buzzHeavierApiKeyInput.value = config.apiKey;
                if (config.folderId) buzzHeavierFolderIdInput.value = config.folderId;
                if (config.fileVisibility && buzzHeavierFileVisibilitySelect) {
                    buzzHeavierFileVisibilitySelect.value = config.fileVisibility;
                }
                logAction(`Configurações do Buzzheavier carregadas: ${JSON.stringify(config)}`, 'info', false);
            } else if (config && config.error) {
                logAction(`Erro retornado ao carregar config Buzzheavier: ${config.error}`, 'error', false);
            } else {
                logAction('Nenhuma configuração do Buzzheavier encontrada ou API Key ausente.', 'info', false);
            }
        } catch (e) {
            logAction(`Erro ao carregar configurações do Buzzheavier: ${e}`, 'error', false);
        }
    }

    // --- Lógica de Configurações do Catbox ---
    if (saveCatboxConfigButton) {
        saveCatboxConfigButton.addEventListener('click', async () => {
            if (!eel || !catboxUserhashInput) return;
            const userhash = catboxUserhashInput.value.trim();
            logAction(`Tentando salvar configuração do Catbox com userhash: '${userhash}'`, 'info');
            try {
                // A função Python espera um objeto, mas só temos userhash aqui.
                // Ajuste na chamada Python ou aqui. Por ora, mantendo como estava.
                const result = await eel.save_catbox_config_eel(userhash)(); 
                if (result && result.status === 'success') {
                    logAction('Configuração do Catbox salva com sucesso.', 'success');
                } else {
                    logAction(`Erro ao salvar configuração do Catbox: ${result.message || 'Erro desconhecido'}`, 'error');
                }
            } catch (error) {
                logAction(`Erro catastrófico ao salvar configuração do Catbox: ${error}`, 'error');
            }
        });
    }

    async function loadCatboxConfig() {
        logAction('Tentando carregar configuração do Catbox...', 'info', false);
        if (!eel || !catboxUserhashInput) return;
        try {
            const config = await eel.load_catbox_config_eel()();
            if (config && typeof config.userhash !== 'undefined') {
                catboxUserhashInput.value = config.userhash;
                logAction(`Configuração do Catbox carregada. Userhash: '${config.userhash}'`, 'info', false);
            } else if (config && config.error) {
                logAction(`Erro retornado ao carregar config Catbox: ${config.error}`, 'error', false);
            } else {
                logAction('Nenhuma configuração do Catbox (userhash) encontrada.', 'info', false);
            }
        } catch (e) {
            logAction(`Erro ao carregar configuração do Catbox: ${e}`, 'error', false);
        }
    }

    async function loadSavedHostConfigs() {
        logAction('Iniciando carregamento de todas as configurações de host salvas...', 'info', false);
        await loadGitHubConfig();
        await loadBuzzHeavierConfig();
        await loadCatboxConfig();
        // Adicionar chamadas para carregar outras configs (G Drive, Dropbox, etc.) aqui quando implementadas
        // Ex: await loadGoogleDriveConfig();
        logAction('Carregamento de todas as configurações de host concluído.', 'info', false);
    }

    // Chamar ao inicializar para carregar configurações salvas
    loadSavedHostConfigs();

    // --- Integração com Seleção de Host no Upload ---
    // Isso permitirá que o usuário escolha o host na hora do upload
    function getActiveHostConfig() {
        // Verificar qual host está ativo atualmente
        const activeHostTab = document.querySelector('.host-tab-button.active');
        if (!activeHostTab) return { type: 'catbox' }; // Padrão
        
        const hostType = activeHostTab.dataset.hostTab;
        
        switch (hostType) {
            case 'buzzheavier':
                return {
                    type: 'buzzheavier',
                    apiKey: buzzHeavierApiKeyInput ? buzzHeavierApiKeyInput.value : '',
                    folderId: buzzHeavierFolderIdInput ? buzzHeavierFolderIdInput.value : '',
                    fileVisibility: buzzHeavierFileVisibilitySelect ? buzzHeavierFileVisibilitySelect.value : 'public'
                };
            case 'catbox':
                return { 
                    type: 'catbox', 
                    userhash: catboxUserhashInput ? catboxUserhashInput.value : '' 
                };
            // Outros casos para outros hosts podem ser adicionados aqui
            default:
                return { type: 'catbox' }; // Host padrão
        }
    }

    // --- Lógica de Upload Principal ---
    if (uploadPrincipalButton) {
        uploadPrincipalButton.addEventListener('click', async () => {
            const filesToUpload = currentFiles.filter(file => file.selected && file.status !== 'success');
            if (filesToUpload.length === 0) {
                logAction('Nenhum arquivo selecionado para upload ou todos já foram enviados.', 'warn', false);
                return;
            }
            
            const activeHostConfig = getActiveHostConfig();
            logAction(`Iniciando upload e geração de Cubari JSON para ${filesToUpload.length} arquivo(s) para ${activeHostConfig.type}.`, 'info');

            if (!eel) return;

            // Marcar arquivos como 'uploading' na UI antes de iniciar
            filesToUpload.forEach(file => {
                file.status = 'uploading';
            });
            renderFileList(); // Atualiza a UI para mostrar 'Enviando...'

            const filePathsToUpload = filesToUpload.map(file => file.path);

            // Coletar metadados da UI para cubari_options
            const cubariOptions = {
                title: tituloMangaInput.value || "Mangá Desconhecido",
                alternative_titles: titulosAlternativosInput.value ? titulosAlternativosInput.value.split(',').map(s => s.trim()) : [],
                description: descricaoTextarea.value || "",
                authors: autorInput.value ? [autorInput.value.trim()] : [],
                artists: artistaInput.value ? [artistaInput.value.trim()] : [],
                scanlator_group: grupoScanInput.value || "",
                cover_url: urlCapaInput.value || "",
                status_manga: statusInput.value || "", // Usando status_manga para não colidir com status de arquivo
                chapter_title: tituloCapituloInput.value || "Capítulo Desconhecido",
                // Adicionar quaisquer outros campos de cubari_options que possam ser configurados via UI ou padrão
            };

            try {
                const filePathsJson = JSON.stringify(filePathsToUpload);
                const hostConfigJson = JSON.stringify(activeHostConfig);
                const cubariOptionsJson = JSON.stringify(cubariOptions);

                logAction('Chamando eel.process_manga_chapter_eel com:', 'debug');
                logAction(`  File Paths: ${filePathsJson}`, 'debug');
                logAction(`  Host Config: ${hostConfigJson}`, 'debug');
                logAction(`  Cubari Options: ${cubariOptionsJson}`, 'debug');

                // Chama a função Python para processar o capítulo e gerar o JSON Cubari
                const resultJson = await eel.process_manga_chapter_eel(filePathsJson, hostConfigJson, cubariOptionsJson)();
                
                // Espera-se que resultJson seja o JSON Cubari como string, ou uma string de erro JSON
                let cubariData;
                let processingError = null;
                try {
                    cubariData = JSON.parse(resultJson);
                    if (cubariData.error) { // Backend pode retornar um JSON com uma chave de erro
                        processingError = cubariData.error;
                        cubariData = null; // Não há dados Cubari válidos
                    }
                } catch (parseError) {
                    processingError = `Falha ao parsear resposta do backend: ${resultJson}`;
                    cubariData = null;
                }

                if (processingError) {
                    logAction(`Erro ao processar capítulo e gerar Cubari JSON: ${processingError}`, 'error');
                    // Marcar todos os arquivos que estavam 'uploading' como 'error'
                    filesToUpload.forEach(f => {
                        if (f.status === 'uploading') f.status = 'error';
                    });
                } else if (cubariData) {
                    logAction('JSON Cubari gerado com sucesso:', 'success');
                    logAction(JSON.stringify(cubariData, null, 2), 'info'); // Loga o JSON formatado
                    // TODO: Oferecer download do JSON ou exibi-lo em algum lugar na UI

                    // Atualizar status dos arquivos com base no Cubari JSON gerado
                    const uploadedUrls = [];
                    if (cubariData.chapters && cubariData.chapters.length > 0) {
                        const firstChapter = cubariData.chapters[0];
                        if (firstChapter.groups) {
                            Object.values(firstChapter.groups).forEach(groupPages => {
                                groupPages.forEach(pageUrl => uploadedUrls.push(pageUrl));
                            });
                        }
                    }

                    filesToUpload.forEach(file => {
                        // Se a URL do arquivo (ou alguma representação dela) estiver no Cubari JSON, marcou como sucesso
                        // Esta é uma verificação simplista. O ideal seria que o backend retornasse o status de cada arquivo.
                        // Por agora, vamos assumir que se o Cubari JSON foi gerado, os arquivos nele contidos foram bem sucedidos.
                        // E os que não estão lá, mas foram tentados, falharam.
                        // A função `process_manga_chapter_eel` já usa `upload_files_to_host_parallel` que retorna detalhes.
                        // Seria melhor se `process_manga_chapter_eel` retornasse esses detalhes também.
                        // Por enquanto, vamos marcar como sucesso se o JSON foi gerado e erro caso contrário.
                        // Esta lógica precisa de refinamento se quisermos status individual preciso aqui sem mudar o backend.
                        
                        // Tentativa de encontrar o arquivo no resultado (pode não ser direto)
                        // A URL no Cubari JSON é a URL final. O `file.path` é o caminho local.
                        // Precisamos de uma forma de mapear `file.path` para `url` ou que o backend retorne o status por `file.path`.
                        
                        // Simplificação: Se chegamos aqui sem `processingError`, consideramos os que foram para upload como sucesso por ora.
                        // Esta parte precisará de ajuste se `process_manga_chapter_eel` não retornar detalhes de upload individuais
                        // que possam ser mapeados de volta para `file.path`.
                        // A função `upload_files_to_host_parallel` retorna `{'path': original_path, 'status': 'success', 'url': url}`.
                        // Se `process_manga_chapter_eel` pudesse passar essa lista de volta, seria ideal.

                        // Assumindo que `cubariData` implica que os arquivos pretendidos estão lá.
                        // Esta é uma GRANDE simplificação. O correto seria o backend retornar os status individuais.
                        const foundInCubari = uploadedUrls.some(url => file.original_url_after_upload === url); // Precisamos de original_url_after_upload
                        // Como não temos `original_url_after_upload` facilmente aqui, vamos apenas marcar como sucesso se não houve erro geral.
                        file.status = 'success'; 
                        // TODO: Tentar extrair a URL do cubariData se possível para popular file.url
                        // Exemplo: se o nome do arquivo local puder ser encontrado na URL do cubariData.
                        const fileNameOnly = file.name;
                        const matchedUrl = uploadedUrls.find(url => url && url.includes(fileNameOnly));
                        if (matchedUrl) {
                            file.url = matchedUrl;
                        }
                    });
                    logAction('JSON Cubari gerado e arquivos marcados como sucesso (simplificado).', 'success');
                }

            } catch (error) {
                logAction(`Erro crítico durante o processo de geração do Cubari JSON: ${error}`, 'error');
                filesToUpload.forEach(f => {
                    if (f.status === 'uploading') f.status = 'error';
                });
            }
            renderFileList(); // Re-renderiza a lista para mostrar os status finais
            addLog('Processo de upload e geração de Cubari JSON concluído.');
        });
    }

    // --- Lógica do Modal de Seleção de Diretório (HTML ausente) ---
    // A lógica abaixo depende de elementos HTML que não estão presentes no 
    // novo 'manga_uploader.html' (ex: #directory-modal, #directory-list).
    // Mantenho as funções caso o HTML seja adicionado posteriormente.
    /*
    const modal = document.getElementById('directory-modal');
    const closeButtonModal = document.querySelector('.close-button'); // Seletor genérico, ajuste se necessário
    const directoryList = document.getElementById('directory-list');
    const currentPathDisplay = document.getElementById('current-path');
    const modalCancelButton = document.getElementById('modal-cancel-button');
    const modalSelectButton = document.getElementById('modal-select-button');
    let currentModalPath = '';
    let directoryModalCallback = null;

    function openDirectoryModal(path, callback) {
        if (!modal) {
            addLog("Modal de diretório não encontrado no HTML.", "error");
            return;
        }
        currentModalPath = path || '.';
        directoryModalCallback = callback;
        loadDirectoriesForModal(currentModalPath);
        modal.classList.add('active');
    }

    function closeDirectoryModal() {
        if (modal) modal.classList.remove('active');
    }

    async function loadDirectoriesForModal(path) {
        if (!eel || !directoryList || !currentPathDisplay) return;
        try {
            const result = await eel.get_directories_eel(path)(); // Supondo eel.get_directories(path) -> {path, dirs, error}
            if (result.error) {
                addLog(`Erro ao listar diretórios: ${result.error}`, 'error');
                return;
            }
            currentModalPath = result.path;
            currentPathDisplay.textContent = `Caminho: ${currentModalPath}`;
            directoryList.innerHTML = '';
            if (currentModalPath !== '/') { // Ou lógica para Windows: if (currentModalPath !== 'C:\\') etc.
                const upItem = document.createElement('div');
                upItem.className = 'directory-item';
                upItem.innerHTML = '📁 <b>..</b> (Subir)';
                upItem.addEventListener('click', () => {
                    const parentPath = currentModalPath.substring(0, currentModalPath.lastIndexOf('/')) || '/';
                    loadDirectoriesForModal(parentPath);
                });
                directoryList.appendChild(upItem);
            }
            result.dirs.forEach(dir => {
                const dirItem = document.createElement('div');
                dirItem.className = 'directory-item';
                dirItem.innerHTML = `📁 ${dir}`;
                dirItem.addEventListener('click', () => {
                    const newPath = currentModalPath === '/' ? `/${dir}` : `${currentModalPath}/${dir}`;
                    loadDirectoriesForModal(newPath);
                });
                directoryList.appendChild(dirItem);
            });
        } catch (error) {
            addLog(`Erro ao carregar diretórios para modal: ${error}`, 'error');
        }
    }
    if (closeButtonModal) closeButtonModal.addEventListener('click', closeDirectoryModal);
    if (modalCancelButton) modalCancelButton.addEventListener('click', closeDirectoryModal);
    if (modalSelectButton) {
        modalSelectButton.addEventListener('click', () => {
            if (directoryModalCallback) directoryModalCallback(currentModalPath);
            closeDirectoryModal();
        });
    }
    */
    // Exemplo de uso do modal (se o botão 'choose-output-button' existisse):
    // const chooseOutputButton = document.getElementById('choose-output-button');
    // const outputFolderInput = document.getElementById('output-folder');
    // if (chooseOutputButton && outputFolderInput) {
    //     chooseOutputButton.addEventListener('click', () => {
    //         openDirectoryModal('.', (selectedPath) => {
    //             outputFolderInput.value = selectedPath;
    //             addLog(`Pasta de saída definida: ${selectedPath}`);
    //         });
    //     });
    // }


    // --- Configurações de Hosts Específicos (HTML ausente/placeholder) ---
    // Exemplo para Catbox - a lógica abaixo depende de campos que não estão no HTML atual da aba Catbox.
    /*
    const catboxUserhashInput = document.getElementById('catbox-userhash');
    const saveCatboxUserhashButton = document.getElementById('save-userhash-button');
    if (saveCatboxUserhashButton && catboxUserhashInput) {
        saveCatboxUserhashButton.addEventListener('click', async () => {
            const userhash = catboxUserhashInput.value.trim();
            if (!userhash) {
                addLog('Por favor, informe o seu userhash do Catbox.', 'error');
                return;
            }
            if (!eel) return;
            try {
                // Supondo eel.save_catbox_config(userhash)
                const result = await eel.save_catbox_config(userhash)(); 
                if (result.success) addLog('Userhash Catbox salvo.', 'success');
                else addLog(`Erro ao salvar userhash Catbox: ${result.error}`, 'error');
            } catch (error) {
                addLog(`Erro ao salvar userhash Catbox: ${error}`, 'error');
            }
        });
    }
    async function loadSavedHostConfigs() {
        // Carregar userhash do Catbox se existir
        // if (eel && catboxUserhashInput) {
        //     try {
        //         const config = await eel.get_catbox_config()();
        //         if (config && config.userhash) {
        //             catboxUserhashInput.value = config.userhash;
        //             addLog('Userhash Catbox carregado.');
        //         }
        //     } catch (e) { addLog('Erro ao carregar config Catbox.', 'error'); }
        // }
        // Carregar outras configs de host...
    }
    // loadSavedHostConfigs(); // Chamar para carregar configs ao iniciar
    */

    // --- Inicialização e Funções Globais Expostas ao Python ---
    if (eel && typeof eel.expose === 'function') {
        eel.expose(updateUploadProgress, 'update_upload_progress_js');
    }
    function updateUploadProgress(fileName, percentage) {
        // Encontrar o arquivo na lista e atualizar seu status/progresso visualmente
        // Esta é uma implementação mais complexa que exigiria uma coluna de progresso na tabela.
        addLog(`Progresso de ${fileName}: ${percentage}%`);
        const fileEntry = currentFiles.find(f => f.name === fileName || f.path.endsWith(fileName));
        if (fileEntry) {
            // Poderia adicionar uma propriedade 'progress' ao objeto file e re-renderizar.
            // fileEntry.progress = percentage;
            // renderFileList(); // Isso pode ser custoso se chamado frequentemente.
            // Alternativamente, atualizar diretamente o DOM da célula de status/progresso.
        }
    }
    
    addLog('Interface do Uploader de Mangás inicializada.');
    logAction('Interface do Uploader de Mangás inicializada e JS carregado.', 'info', true); // Log inicial

    // Adicionar listeners de log para botões importantes
    const buttonsToLog = [
        { id: 'add-files-button', logMessage: 'Botão "Add Arquivos" clicado' },
        { id: 'add-pasta-button', logMessage: 'Botão "Add Pasta" clicado' },
        { id: 'aplicar-button', logMessage: 'Botão "Aplicar Filtro" clicado' },
        { id: 'marcar-todos', logMessage: 'Botão "Marcar Todos" clicado' },
        { id: 'desmarcar-todos', logMessage: 'Botão "Desmarcar Todos" clicado' },
        { id: 'remover-button', logMessage: 'Botão "Remover" clicado' },
        { id: 'limpar-button', logMessage: 'Botão "Limpar" clicado' },
        { id: 'preencher-automaticamente', logMessage: 'Botão "Preencher Automaticamente" clicado' },
        { id: 'limpar-campos', logMessage: 'Botão "Limpar Campos" clicado' },
        { id: 'salvar-metadados', logMessage: 'Botão "Salvar Metadados" clicado' },
        { id: 'upload-button', logMessage: 'Botão "Upload e Atualizar GitHub" clicado' },
        { id: 'urls-button', logMessage: 'Botão "URLs Salvas" clicado' },
        { id: 'titulos-button', logMessage: 'Botão "Títulos Salvos" clicado' },
        { id: 'salvar-config-github', logMessage: 'Botão "Salvar Configurações GitHub" clicado' },
        { id: 'salvar-config-mongodb', logMessage: 'Botão "Salvar Configurações MongoDB" clicado' },
        { id: 'save-catbox-config', logMessage: 'Botão "Salvar Configuração Catbox" clicado' },
        { id: 'save-gdrive-config', logMessage: 'Botão "Salvar Configurações Google Drive" clicado' },
        { id: 'auth-gdrive', logMessage: 'Botão "Autenticar com Google" clicado' },
        { id: 'save-buzzheavier-config', logMessage: 'Botão "Salvar Configurações Buzzheavier" clicado' },
        { id: 'test-buzzheavier-connection', logMessage: 'Botão "Testar Conexão Buzzheavier" clicado' },
        { id: 'save-dropbox-config', logMessage: 'Botão "Salvar Configurações DropBox" clicado' },
        { id: 'auth-dropbox', logMessage: 'Botão "Autenticar com Dropbox" clicado' },
        { id: 'save-gofile-config', logMessage: 'Botão "Salvar Configurações GoFile" clicado' },
        { id: 'save-pixeldrain-config', logMessage: 'Botão "Salvar Configurações Pixeldrain" clicado' }
    ];

    buttonsToLog.forEach(btnInfo => {
        const button = document.getElementById(btnInfo.id);
        if (button) {
            button.addEventListener('click', () => {
                // Usar logAction para enviar ao backend e log local
                logAction(btnInfo.logMessage, 'info', true); 
            });
        }
    });

    // Adicionar listeners de log para navegação
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (event) => {
            const viewName = event.currentTarget.dataset.view;
            const viewTitle = event.currentTarget.textContent.trim();
            logAction(`Navegação para a view: ${viewTitle} (data-view: ${viewName})`, 'info', true);
        });
    });

    document.querySelectorAll('.config-option-button').forEach(button => {
        button.addEventListener('click', () => {
            const configTarget = button.dataset.configTarget;
            logAction(`Botão de opção de configuração clicado: ${configTarget}`, 'info', true);
        });
    });

    document.querySelectorAll('.host-tab-button').forEach(button => {
        button.addEventListener('click', () => {
            const hostTab = button.dataset.hostTab;
            logAction(`Botão de aba de host clicado: ${hostTab}`, 'info', true);
        });
    });

});

// Remover a função logFrontendAction global duplicada, pois logAction a substitui.
// async function logFrontendAction(message, level = 'info') { ... }