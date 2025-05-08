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
        // Adicionar classes de tipo se necessário para estilização: log-info, log-error, log-success
        logEntry.className = `log-entry log-${type}`; 
        logEntry.textContent = `[${timestamp}] ${message}`;
        logsArea.appendChild(logEntry);
        logsArea.scrollTop = logsArea.scrollHeight;
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
        const selectedCount = currentFiles.filter(file => file.selected).length;
        selectionInfoSpan.textContent = `Sel: ${selectedCount} / Total: ${currentFiles.length}`;
    }

    function renderFileList() {
        if (!fileTableBody) return;
        fileTableBody.innerHTML = ''; // Limpar tabela
        currentFiles.forEach((file, index) => {
            const row = fileTableBody.insertRow();
            row.className = file.selected ? 'selected' : '';
            row.innerHTML = `
                <td>${file.name} ${file.chapter ? '/ ' + file.chapter : ''} ${file.manga ? '/ ' + file.manga : ''}</td>
                <td>${formatFileSize(file.size)}</td>
                <td class="status-${file.status}">${getStatusText(file.status)}</td>
            `;
            row.addEventListener('click', () => {
                currentFiles[index].selected = !currentFiles[index].selected;
                renderFileList(); // Re-renderizar para atualizar a classe e a contagem
            });
        });
        updateSelectionInfo();
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
                const files = await eel.selecionar_arquivos()();
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
                const folderPath = await eel.selecionar_pasta()();
                if (folderPath) {
                    addLog(`Listando arquivos da pasta: ${folderPath}`);
                    const filesInFolder = await eel.listar_arquivos_pasta(folderPath)(); // Supondo que esta função exista no Python
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
            const filterText = filterInput.value.toLowerCase();
            addLog(`Filtro aplicado: ${filterText}. Lógica de filtro a ser implementada.`, 'info');
            // Aqui você precisaria filtrar 'currentFiles' e chamar renderFileList()
        });
    }


    if (marcarTodosButton) {
        marcarTodosButton.addEventListener('click', () => {
            currentFiles.forEach(file => file.selected = true);
            renderFileList();
        });
    }

    if (desmarcarTodosButton) {
        desmarcarTodosButton.addEventListener('click', () => {
            currentFiles.forEach(file => file.selected = false);
            renderFileList();
        });
    }

    if (removerButton) {
        removerButton.addEventListener('click', () => {
            currentFiles = currentFiles.filter(file => !file.selected);
            renderFileList();
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
                await eel.salvar_metadados_manga(metadata)(); 
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
            // if(lastUpdateInput) lastUpdateInput.value = '';
            addLog('Campos de metadados limpos.');
        });
    }
    // TODO: Implementar lógica para preencherAutomaticamenteButton
    if(preencherAutomaticamenteButton){
        preencherAutomaticamenteButton.addEventListener('click', () => {
            addLog('Preenchimento automático de metadados a ser implementado.', 'info');
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
                addLog('Todos os campos de configuração do GitHub são obrigatórios.', 'error');
                return;
            }
            if (!eel) return;
            try {
                // Supondo uma função Python para salvar config do GitHub
                await eel.salvar_config_github(config)(); 
                addLog('Configurações do GitHub salvas (simulado).', 'success');
            } catch (error) {
                addLog(`Erro ao salvar configurações do GitHub: ${error}`, 'error');
            }
        });
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

            if (!eel) return;
            try {
                const result = await eel.save_buzzheavier_config(config)();
                if (result && result.success) {
                    addLog('Configurações do Buzzheavier salvas com sucesso.', 'success');
                } else {
                    addLog(`Erro ao salvar configurações: ${result.error || 'Erro desconhecido'}`, 'error');
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
                const result = await eel.test_buzzheavier_connection(apiKey)();
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
        if (!eel || !buzzHeavierApiKeyInput) return;
        try {
            const config = await eel.load_buzzheavier_config()();
            if (config && config.apiKey) {
                buzzHeavierApiKeyInput.value = config.apiKey;
                if (config.folderId) buzzHeavierFolderIdInput.value = config.folderId;
                if (config.fileVisibility && buzzHeavierFileVisibilitySelect) {
                    buzzHeavierFileVisibilitySelect.value = config.fileVisibility;
                }
                addLog('Configurações do Buzzheavier carregadas.', 'info');
            }
        } catch (e) {
            addLog('Erro ao carregar configurações do Buzzheavier.', 'error');
        }
    }

    // Modificar a função loadSavedHostConfigs para incluir Buzzheavier
    async function loadSavedHostConfigs() {
        // Carregar configurações do Github (já existente)
        // ...

        // Carregar configurações do Buzzheavier
        await loadBuzzHeavierConfig();
        
        // Outras configurações de hosts
        // ...
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
                // Retornar configurações do Catbox
                return { type: 'catbox', userhash: '' }; // O userhash será preenchido no backend
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
                addLog('Nenhum arquivo selecionado para upload ou todos já foram enviados.', 'warn');
                return;
            }
            
            const activeHostConfig = getActiveHostConfig();
            addLog(`Iniciando upload de ${filesToUpload.length} arquivo(s) para ${activeHostConfig.type}...`);

            if (!eel) return;
            try {
                for (const file of filesToUpload) {
                    file.status = 'uploading';
                    renderFileList(); // Atualiza status na UI
                    addLog(`Enviando: ${file.name} para ${activeHostConfig.type}`);
                    
                    // Usar o serviço real de upload
                    try {
                        const result = await eel.upload_arquivo(file.path, activeHostConfig)();
                        if (result && result.success) {
                            file.status = 'success';
                            addLog(`Sucesso: ${file.name} - URL: ${result.url}`, 'success');
                        } else {
                            file.status = 'error';
                            addLog(`Erro ao enviar ${file.name}: ${result.error || 'Erro desconhecido'}`, 'error');
                        }
                    } catch (uploadError) {
                        file.status = 'error';
                        addLog(`Erro ao enviar ${file.name}: ${uploadError}`, 'error');
                    }
                    
                    renderFileList();
                }
                addLog('Processo de upload concluído.');
            } catch (error) {
                addLog(`Erro crítico durante o upload: ${error}`, 'error');
                // Reverter status de arquivos que estavam 'uploading' para 'error'
                filesToUpload.forEach(f => { if(f.status === 'uploading') f.status = 'error'; });
                renderFileList();
            }
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
            const result = await eel.get_directories(path)(); // Supondo eel.get_directories(path) -> {path, dirs, error}
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
    console.log("Nova UI manga_uploader.js carregado e inicializado.");
});