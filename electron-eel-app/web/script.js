// Aguarda o carregamento do DOM antes de executar o código
document.addEventListener('DOMContentLoaded', function() {
    // Elementos da interface - Seção de boas-vindas
    const nameInput = document.getElementById('name-input');
    const sendButton = document.getElementById('send-button');
    const responseArea = document.getElementById('response');
    
    // Elementos da interface - Seção da calculadora
    const calcInput = document.getElementById('calc-input');
    const calcButton = document.getElementById('calc-button');
    const calcResponse = document.getElementById('calc-response');
    const calcKeys = document.querySelectorAll('.calc-key');
    
    // Elementos da interface - Seção de informações do sistema
    const systemInfoButton = document.getElementById('system-info-button');
    const systemInfoContainer = document.getElementById('system-info');
    
    // Elementos da interface - Visualizador de JSON
    const jsonFileSelector = document.getElementById('json-file-selector');
    const loadJsonButton = document.getElementById('load-json-button');
    const jsonContent = document.getElementById('json-content');
    
    // Elementos da interface - Alternador de tema
    const themeButton = document.getElementById('theme-button');
    const body = document.body;
    
    // Inicialização
    loadJsonFiles();
    loadThemePreference();
    
    // ======= Funções expostas para o Python =======
    
    // Função JavaScript que será chamada pelo Python
    eel.expose(showMessage);
    function showMessage(message) {
        responseArea.textContent = message;
    }
    
    // ======= Funções de tema =======
    
    // Carrega a preferência de tema do armazenamento local
    function loadThemePreference() {
        const currentTheme = localStorage.getItem('theme') || 'light';
        body.classList.remove('light-theme', 'dark-theme');
        body.classList.add(`${currentTheme}-theme`);
    }
    
    // Alterna entre tema claro e escuro
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
    
    // ======= Funções do Visualizador JSON =======
    
    // Carrega a lista de arquivos JSON disponíveis
    async function loadJsonFiles() {
        try {
            const files = await eel.list_json_files()();
            
            // Limpa opções existentes (exceto a primeira)
            while (jsonFileSelector.options.length > 1) {
                jsonFileSelector.remove(1);
            }
            
            // Adiciona as novas opções
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                jsonFileSelector.appendChild(option);
            });
        } catch (error) {
            console.error("Erro ao carregar lista de arquivos JSON:", error);
        }
    }
    
    // Carrega e exibe o conteúdo de um arquivo JSON
    loadJsonButton.addEventListener('click', async function() {
        const selectedFile = jsonFileSelector.value;
        
        if (selectedFile) {
            try {
                // Exibe mensagem de carregamento
                jsonContent.textContent = "Carregando...";
                
                // Carrega o conteúdo do arquivo JSON
                const content = await eel.read_json_file(selectedFile)();
                
                if (content.error) {
                    jsonContent.textContent = `Erro: ${content.error}`;
                } else {
                    // Formata e destaca o JSON
                    const formattedJson = JSON.stringify(content, null, 2);
                    jsonContent.innerHTML = syntaxHighlightJson(formattedJson);
                }
            } catch (error) {
                jsonContent.textContent = `Erro ao carregar arquivo: ${error}`;
                console.error("Erro ao carregar arquivo JSON:", error);
            }
        } else {
            jsonContent.textContent = "Por favor, selecione um arquivo JSON para visualizar.";
        }
    });
    
    // Função para destacar a sintaxe do JSON
    function syntaxHighlightJson(json) {
        json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
        return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
            let cls = 'json-number';
            if (/^"/.test(match)) {
                if (/:$/.test(match)) {
                    cls = 'json-key';
                    // Remove as aspas do final
                    match = match.substr(0, match.length - 1);
                } else {
                    cls = 'json-string';
                }
            } else if (/true|false/.test(match)) {
                cls = 'json-boolean';
            } else if (/null/.test(match)) {
                cls = 'json-null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
        });
    }
    
    // ======= Seção de boas-vindas =======
    
    // Adiciona evento de clique ao botão
    sendButton.addEventListener('click', async function() {
        const name = nameInput.value.trim();
        if (name) {
            try {
                // Chama a função Python e recebe a resposta
                const response = await eel.say_hello_py(name)();
                responseArea.textContent = response;
            } catch (error) {
                responseArea.textContent = `Erro: ${error}`;
                console.error("Erro ao chamar função Python:", error);
            }
        } else {
            responseArea.textContent = "Por favor, digite seu nome primeiro!";
        }
    });
    
    // ======= Seção da Calculadora =======
    
    // Adiciona evento de clique ao botão de calcular
    calcButton.addEventListener('click', async function() {
        const expression = calcInput.value.trim();
        if (expression) {
            try {
                // Chama a função Python para calcular
                const result = await eel.calculate(expression)();
                calcResponse.textContent = result;
            } catch (error) {
                calcResponse.textContent = `Erro: ${error}`;
                console.error("Erro ao calcular:", error);
            }
        } else {
            calcResponse.textContent = "Por favor, digite uma expressão matemática!";
        }
    });
    
    // Adiciona eventos para os botões da calculadora
    calcKeys.forEach(key => {
        key.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            calcInput.value += value;
            calcInput.focus();
        });
    });
    
    // ======= Seção de Informações do Sistema =======
    
    // Adiciona evento de clique ao botão de informações do sistema
    systemInfoButton.addEventListener('click', async function() {
        try {
            // Exibe mensagem de carregamento
            systemInfoContainer.innerHTML = '<div class="loading">Coletando informações do sistema...</div>';
            
            // Chama a função Python para obter informações do sistema
            const systemInfo = await eel.get_system_info()();
            
            // Limpa o container de informações
            systemInfoContainer.innerHTML = '';
            
            // Cria elementos para exibir as informações
            for (const [key, value] of Object.entries(systemInfo)) {
                const infoItem = document.createElement('div');
                infoItem.className = 'info-item';
                
                const infoLabel = document.createElement('div');
                infoLabel.className = 'info-label';
                infoLabel.textContent = formatLabel(key);
                
                const infoValue = document.createElement('div');
                infoValue.className = 'info-value';
                infoValue.textContent = formatValue(key, value);
                
                infoItem.appendChild(infoLabel);
                infoItem.appendChild(infoValue);
                systemInfoContainer.appendChild(infoItem);
            }
        } catch (error) {
            systemInfoContainer.innerHTML = `<div class="error">Erro ao obter informações: ${error}</div>`;
            console.error("Erro ao obter informações do sistema:", error);
        }
    });
    
    // Função auxiliar para formatar as labels
    function formatLabel(key) {
        const labels = {
            "sistema": "Sistema Operacional",
            "versao": "Versão",
            "arquitetura": "Arquitetura",
            "processador": "Processador",
            "memoria_total": "Memória Total",
            "memoria_disponivel": "Memória Disponível",
            "cpu_uso": "Uso de CPU"
        };
        
        return labels[key] || key;
    }
    
    // Função auxiliar para formatar os valores
    function formatValue(key, value) {
        if (key === "memoria_total" || key === "memoria_disponivel") {
            return `${value} GB`;
        } else if (key === "cpu_uso") {
            return `${value}%`;
        } else {
            return value;
        }
    }
    
    // Permite enviar com a tecla Enter nos campos de texto
    nameInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    });
    
    calcInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            calcButton.click();
        }
    });
    
    // ======= Processamento de Mangás (Cubari) =======
    const processMangaBtn = document.getElementById('process-manga-btn');
    const processMangaOutput = document.getElementById('process-manga-output');

    if (processMangaBtn) {
        processMangaBtn.addEventListener('click', async function() {
            processMangaOutput.textContent = "Processando, aguarde...";
            try {
                const result = await eel.rodar_manga_processor()();
                if (result.success) {
                    processMangaOutput.textContent = "Processamento concluído!\n\n" + (result.stdout || "");
                } else {
                    processMangaOutput.textContent = "Erro no processamento:\n" + (result.stderr || result.error || "");
                }
            } catch (err) {
                processMangaOutput.textContent = "Erro ao executar processamento: " + err;
            }
        });
    }
    
    // Exibe mensagem indicando que a aplicação está pronta
    console.log("Interface web carregada com sucesso!");
});