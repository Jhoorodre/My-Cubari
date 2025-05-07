// Uploader de Mangás - JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // ===== Gerenciamento de temas =====
    const themeButton = document.getElementById('theme-button');
    const body = document.body;
    
    // Carrega tema preferido
    function loadThemePreference() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        body.classList.remove('light-theme', 'dark-theme');
        body.classList.add(`${currentTheme}-theme`);
    }
    
    // Alterna tema
    themeButton.addEventListener('click', function() {
        const isDark = body.classList.contains('dark-theme');
        body.classList.remove('light-theme', 'dark-theme');
        
        if (isDark) {
            body.classList.add('light-theme');
            localStorage.setItem('theme', 'light');
        } else {
            body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark');
        }
    });
    
    loadThemePreference();
    
    // ===== Seleção de abas =====
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove a classe ativa de todos os botões
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // Adiciona a classe ativa ao botão clicado
            button.classList.add('active');
            
            // Obtém a ID da aba
            const tabId = button.getAttribute('data-tab');
            
            // Esconde todos os conteúdos de abas
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Mostra o conteúdo da aba selecionada
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // ===== Gerenciamento de logs =====
    const logsArea = document.getElementById('logs-area');
    const clearLogsButton = document.getElementById('clear-logs-button');
    
    function addLog(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        logsArea.appendChild(logEntry);
        logsArea.scrollTop = logsArea.scrollHeight;
    }
    
    clearLogsButton.addEventListener('click', () => {
        logsArea.innerHTML = '';
        addLog('Logs limpos');
    });
    
    // ===== Gerenciamento de arquivos =====
    let fileList = [];
    const filesTbody = document.getElementById('files-tbody');
    const selectAllButton = document.getElementById('select-all-button');
    const unselectAllButton = document.getElementById('unselect-all-button');
    const removeButton = document.getElementById('remove-button');
    const selectionCountSpan = document.getElementById('selection-count');
    
    function updateSelectionCount() {
        const selectedCount = document.querySelectorAll('#files-tbody tr.selected').length;
        selectionCountSpan.textContent = `Sel: ${selectedCount} / Total: ${fileList.length}`;
    }
    
    function addFile(file) {
        // Evita duplicatas
        if (fileList.some(f => f.path === file.path)) {
            return;
        }
        
        fileList.push({
            name: file.name,
            path: file.path,
            size: file.size,
            chapter: file.chapter || '',
            manga: file.manga || '',
            selected: true,
            status: 'pending'
        });
        
        renderFileList();
    }
    
    function addFiles(files) {
        files.forEach(addFile);
        updateSelectionCount();
    }
    
    function renderFileList() {
        filesTbody.innerHTML = '';
        
        fileList.forEach((file, index) => {
            const row = document.createElement('tr');
            if (file.selected) {
                row.classList.add('selected');
            }
            
            row.innerHTML = `
                <td>${file.name}${file.chapter ? ' / ' + file.chapter : ''}${file.manga ? ' / ' + file.manga : ''}</td>
                <td>${formatFileSize(file.size)}</td>
                <td class="status-${file.status}">${getStatusText(file.status)}</td>
            `;
            
            row.addEventListener('click', () => {
                file.selected = !file.selected;
                row.classList.toggle('selected');
                updateSelectionCount();
            });
            
            filesTbody.appendChild(row);
        });
        
        updateSelectionCount();
    }
    
    function formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
        else return (bytes / 1048576).toFixed(1) + ' MB';
    }
    
    function getStatusText(status) {
        switch(status) {
            case 'pending': return 'Pendente';
            case 'uploading': return 'Enviando...';
            case 'success': return 'Enviado';
            case 'error': return 'Erro';
            default: return 'Desconhecido';
        }
    }
    
    selectAllButton.addEventListener('click', () => {
        fileList.forEach(file => file.selected = true);
        renderFileList();
    });
    
    unselectAllButton.addEventListener('click', () => {
        fileList.forEach(file => file.selected = false);
        renderFileList();
    });
    
    removeButton.addEventListener('click', () => {
        fileList = fileList.filter(file => !file.selected);
        renderFileList();
    });
    
    // ===== Modal de seleção de diretório =====
    const modal = document.getElementById('directory-modal');
    const closeButton = document.querySelector('.close-button');
    const directoryList = document.getElementById('directory-list');
    const currentPathDisplay = document.getElementById('current-path');
    const modalCancelButton = document.getElementById('modal-cancel-button');
    const modalSelectButton = document.getElementById('modal-select-button');
    
    let currentPath = '';
    let directoryCallback = null;
    
    function openDirectoryModal(path, callback) {
        currentPath = path || '.';
        directoryCallback = callback;
        
        loadDirectories(currentPath);
        modal.classList.add('active');
    }
    
    function closeDirectoryModal() {
        modal.classList.remove('active');
    }
    
    async function loadDirectories(path) {
        try {
            const result = await eel.get_directories(path)();
            
            if (result.error) {
                alert(`Erro ao listar diretórios: ${result.error}`);
                return;
            }
            
            currentPath = result.path;
            currentPathDisplay.textContent = `Caminho: ${currentPath}`;
            
            directoryList.innerHTML = '';
            
            // Adiciona item para subir um nível
            if (currentPath !== '/') {
                const upItem = document.createElement('div');
                upItem.className = 'directory-item';
                upItem.innerHTML = '📁 <b>..</b> (Subir)';
                upItem.addEventListener('click', () => {
                    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
                    loadDirectories(parentPath);
                });
                directoryList.appendChild(upItem);
            }
            
            // Adiciona os diretórios
            result.dirs.forEach(dir => {
                const dirItem = document.createElement('div');
                dirItem.className = 'directory-item';
                dirItem.innerHTML = `📁 ${dir}`;
                dirItem.addEventListener('click', () => {
                    const newPath = currentPath === '/' ? `/${dir}` : `${currentPath}/${dir}`;
                    loadDirectories(newPath);
                });
                directoryList.appendChild(dirItem);
            });
        } catch (error) {
            alert(`Erro ao carregar diretórios: ${error}`);
        }
    }
    
    closeButton.addEventListener('click', closeDirectoryModal);
    modalCancelButton.addEventListener('click', closeDirectoryModal);
    
    modalSelectButton.addEventListener('click', () => {
        if (directoryCallback) {
            directoryCallback(currentPath);
        }
        closeDirectoryModal();
    });
    
    // ===== Botões de adicionar arquivos e pastas =====
    const addFolderButton = document.getElementById('add-folder-button');
    const addFilesButton = document.getElementById('add-files-button');
    const chooseOutputButton = document.getElementById('choose-output-button');
    const outputFolderInput = document.getElementById('output-folder');
    
    addFolderButton.addEventListener('click', () => {
        openDirectoryModal('.', async (selectedPath) => {
            addLog(`Carregando imagens da pasta: ${selectedPath}`);
            
            try {
                const result = await eel.get_image_files(selectedPath)();
                
                if (result.error) {
                    addLog(`Erro ao carregar imagens: ${result.error}`, 'error');
                    return;
                }
                
                const files = result.files;
                addLog(`Encontradas ${files.length} imagens`, 'info');
                addFiles(files);
            } catch (error) {
                addLog(`Erro ao processar pasta: ${error}`, 'error');
            }
        });
    });
    
    chooseOutputButton.addEventListener('click', () => {
        openDirectoryModal('.', (selectedPath) => {
            outputFolderInput.value = selectedPath;
            addLog(`Pasta de saída definida: ${selectedPath}`);
        });
    });
    
    // ===== Configurações do Catbox =====
    const catboxUserhash = document.getElementById('catbox-userhash');
    const saveUserhashButton = document.getElementById('save-userhash-button');
    
    saveUserhashButton.addEventListener('click', async () => {
        const userhash = catboxUserhash.value.trim();
        
        if (!userhash) {
            addLog('Por favor, informe o seu userhash do Catbox', 'error');
            return;
        }
        
        try {
            const result = await eel.save_config(userhash)();
            
            if (result.success) {
                addLog('Userhash salvo com sucesso', 'info');
            } else {
                addLog(`Erro ao salvar userhash: ${result.error}`, 'error');
            }
        } catch (error) {
            addLog(`Erro ao salvar userhash: ${error}`, 'error');
        }
    });
    
    async function loadSavedConfig() {
        try {
            const config = await eel.get_saved_config()();
            
            if (config.userhash) {
                catboxUserhash.value = config.userhash;
                addLog('Userhash carregado das configurações');
            }
        } catch (error) {
            addLog(`Erro ao carregar configurações: ${error}`, 'error');
        }
    }
    
    // ===== Configurações do GitHub =====
    const githubUsername = document.getElementById('github-username');
    const githubToken = document.getElementById('github-token');
    const githubRepo = document.getElementById('github-repo');
    const githubBranch = document.getElementById('github-branch');
    const saveGithubConfigButton = document.getElementById('salvar-config-github');

    saveGithubConfigButton.addEventListener('click', async () => {
        const username = githubUsername.value.trim();
        const token = githubToken.value.trim();
        const repo = githubRepo.value.trim();
        const branch = githubBranch.value.trim();

        if (!username || !token || !repo || !branch) {
            addLog('Por favor, preencha todos os campos de configuração do GitHub.', 'error');
            return;
        }

        try {
            const result = await eel.save_github_config(username, token, repo, branch)();

            if (result) {
                addLog('Configurações do GitHub salvas com sucesso.', 'success');
            } else {
                addLog('Erro ao salvar configurações do GitHub.', 'error');
            }
        } catch (error) {
            addLog(`Erro ao salvar configurações do GitHub: ${error}`, 'error');
        }
    });

    // ===== Metadados do Mangá =====
    const mangaTitle = document.getElementById('manga-title');
    const mangaAltTitles = document.getElementById('manga-alt-titles');
    const mangaDescription = document.getElementById('manga-description');
    const mangaAuthor = document.getElementById('manga-author');
    const mangaArtist = document.getElementById('manga-artist');
    const mangaScanGroup = document.getElementById('manga-scan-group');
    const mangaCoverUrl = document.getElementById('manga-cover-url');
    const mangaStatus = document.getElementById('manga-status');
    const chapterTitle = document.getElementById('chapter-title');
    const lastUpdate = document.getElementById('last-update');
    
    const autoFillButton = document.getElementById('auto-fill-button');
    const clearFieldsButton = document.getElementById('clear-fields-button');
    const saveMetadataButton = document.getElementById('save-metadata-button');
    const updateTimestampButton = document.getElementById('update-timestamp-button');
    
    updateTimestampButton.addEventListener('click', () => {
        lastUpdate.value = Math.floor(Date.now() / 1000);
        addLog('Timestamp atualizado');
    });
    
    clearFieldsButton.addEventListener('click', () => {
        mangaTitle.value = '';
        mangaAltTitles.value = '';
        mangaDescription.value = '';
        mangaAuthor.value = '';
        mangaArtist.value = '';
        mangaScanGroup.value = '';
        mangaCoverUrl.value = '';
        mangaStatus.value = '';
        chapterTitle.value = '';
        addLog('Campos limpos');
    });
    
    // ===== Upload de Arquivos =====
    const startUploadButton = document.getElementById('start-upload-button');
    
    startUploadButton.addEventListener('click', async () => {
        const selectedFiles = fileList.filter(file => file.selected);
        
        if (selectedFiles.length === 0) {
            addLog('Selecione ao menos um arquivo para enviar', 'error');
            return;
        }
        
        const userhash = catboxUserhash.value.trim();
        
        if (!userhash) {
            addLog('Por favor, configure o seu userhash do Catbox na aba Host', 'error');
            return;
        }
        
        // Prepara metadados
        const metadata = {
            title: mangaTitle.value.trim(),
            description: mangaDescription.value.trim(),
            artist: mangaArtist.value.trim(),
            author: mangaAuthor.value.trim(),
            cover: mangaCoverUrl.value.trim()
        };
        
        // Dividir os arquivos por capítulo
        const filesByChapter = {};
        
        selectedFiles.forEach(file => {
            if (!filesByChapter[file.chapter]) {
                filesByChapter[file.chapter] = [];
            }
            
            filesByChapter[file.chapter].push(file.path);
        });
        
        const chapters = Object.keys(filesByChapter);
        addLog(`Iniciando upload de ${selectedFiles.length} arquivos em ${chapters.length} capítulos`);
        
        let chapterCounter = 0;
        const chaptersData = {};
        
        // Para cada capítulo, fazer o upload
        for (const chapter of chapters) {
            const filePaths = filesByChapter[chapter];
            chapterCounter++;
            
            addLog(`Processando capítulo ${chapter} (${chapterCounter}/${chapters.length})`);
            
            try {
                // Marcar arquivos como 'uploading'
                selectedFiles
                    .filter(file => file.chapter === chapter)
                    .forEach(file => {
                        file.status = 'uploading';
                    });
                renderFileList();
                
                addLog(`Enviando ${filePaths.length} arquivos do capítulo ${chapter}`);
                
                // Fazer o upload dos arquivos
                const uploadResult = await eel.upload_files(filePaths, userhash)();
                
                if (!uploadResult.success) {
                    addLog(`Erro ao enviar arquivos: ${uploadResult.error}`, 'error');
                    continue;
                }
                
                addLog(`${uploadResult.uploaded} arquivos enviados com sucesso`);
                
                // Marcar arquivos como success ou error
                selectedFiles
                    .filter(file => file.chapter === chapter)
                    .forEach(file => {
                        // Verifica se o arquivo falhou
                        const failed = uploadResult.failures.some(f => f[0] === file.name);
                        file.status = failed ? 'error' : 'success';
                    });
                renderFileList();
                
                // Se tivermos URLs de arquivos, salvamos para o capítulo
                if (uploadResult.urls && uploadResult.urls.length > 0) {
                    chaptersData[chapterCounter] = {
                        title: chapter || String(chapterCounter),
                        volume: "",
                        image_urls: uploadResult.urls,
                        album_url: "" // Será preenchido se criarmos um álbum
                    };
                    
                    // Criar álbum para o capítulo
                    const albumTitle = `${metadata.title} - Capítulo ${chapter}`;
                    const albumDesc = `Capítulo ${chapter} de ${metadata.title}`;
                    
                    addLog(`Criando álbum para capítulo ${chapter}`);
                    
                    const albumResult = await eel.create_album(
                        albumTitle,
                        albumDesc,
                        uploadResult.urls,
                        userhash
                    )();
                    
                    if (albumResult.success) {
                        addLog(`Álbum criado: ${albumResult.album_url}`);
                        chaptersData[chapterCounter].album_url = albumResult.album_url;
                    } else {
                        addLog(`Erro ao criar álbum: ${albumResult.error}`, 'error');
                    }
                }
                
            } catch (error) {
                addLog(`Erro no processamento do capítulo ${chapter}: ${error}`, 'error');
            }
        }
        
        // Gerar arquivos Cubari
        try {
            addLog('Gerando arquivos Cubari...');
            
            const outputPath = outputFolderInput.value || null;
            const result = await eel.generate_cubari_files(metadata, chaptersData, outputPath)();
            
            if (result.success) {
                addLog(`Arquivo JSON salvo em: ${result.json_file}`, 'success');
                addLog(`Arquivo YAML salvo em: ${result.yaml_file}`, 'success');
            } else {
                addLog(`Erro ao gerar arquivos Cubari: ${result.error}`, 'error');
            }
        } catch (error) {
            addLog(`Erro ao gerar arquivos Cubari: ${error}`, 'error');
        }
        
        addLog('Upload completo!', 'success');
    });
    
    // ===== Inicialização =====
    // Expomos esta função para ser chamada pelo Python
    eel.expose(updateUploadProgress);
    function updateUploadProgress(current, total, filename) {
        addLog(`Progresso: ${current}/${total} - ${filename}`);
    }
    
    // Carrega configurações salvas
    loadSavedConfig();
    
    // Define pasta de saída padrão
    outputFolderInput.value = '.';
    
    // Log inicial
    addLog('Uploader de Mangás inicializado');
});