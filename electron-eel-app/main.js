const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDevMode = process.env.NODE_ENV === 'development';

let mainWindow;
let pythonProcess;
let serverReady = false;
let portasParaTentar = [3000, 3001, 3002, 3003, 3004, 3005];

// Cria e configura a janela principal do aplicativo
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    icon: path.join(__dirname, 'web', 'favicon.ico'),
    show: false, // Não mostrar até estar pronto
    backgroundColor: '#f5f5f5'
  });

  // Mostra um splash enquanto carrega
  mainWindow.loadFile(path.join(__dirname, 'web', 'splash.html'));

  // Configura eventos
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
  // Permite abrir links externos no navegador padrão
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
  
  // Configurações para conexão com servidor Eel
  let portaAtual = 0;
  let tentativasDeConexaoGeral = 0; // Renomeado para clareza
  const maxTentativasGeral = 30; // Mantém o limite de ~6 segundos (200ms * 30)
  let conexaoEstabelecida = false;

  // Aguarda o servidor Python estar pronto antes de carregar o conteúdo
  const checkServerInterval = setInterval(() => {
    if (conexaoEstabelecida) {
      clearInterval(checkServerInterval);
      return;
    }

    if (serverReady) {
      const url = `http://localhost:${portasParaTentar[portaAtual]}/manga_uploader.html`; // MODIFICADO AQUI
      console.log(`Tentando conectar em: ${url} (Tentativa geral: ${tentativasDeConexaoGeral + 1}/${maxTentativasGeral})`);

      mainWindow.loadURL(url)
        .then(() => {
          console.log(`Conectado com sucesso na porta ${portasParaTentar[portaAtual]}`);
          conexaoEstabelecida = true; // Marca que a conexão foi bem-sucedida

          if (isDevMode) {
            mainWindow.webContents.openDevTools();
            console.log('Modo de desenvolvimento ativo');
          }
          clearInterval(checkServerInterval); // Limpa o intervalo principal
        })
        .catch((error) => {
          console.log(`Erro ao conectar na porta ${portasParaTentar[portaAtual]}: ${error.message}`);
          portaAtual++;
          if (portaAtual >= portasParaTentar.length) {
            portaAtual = 0; // Volta para a primeira porta da lista para a próxima tentativa geral
            console.log('Todas as portas foram tentadas, reiniciando a lista de portas para a próxima tentativa geral.');
          }
        });
    }

    tentativasDeConexaoGeral++;
    if (tentativasDeConexaoGeral >= maxTentativasGeral && !conexaoEstabelecida) {
      clearInterval(checkServerInterval);
      console.error('Não foi possível conectar ao servidor Eel após várias tentativas em todas as portas configuradas.');
      mainWindow.loadFile(path.join(__dirname, 'web', 'error.html'))
        .catch(err => console.error('Erro ao carregar a página de erro:', err)); // Adiciona catch para loadFile
    }
  }, 200);

  mainWindow.on('closed', function () {
    mainWindow = null;
    // Mata o processo Python quando a janela for fechada
    if (pythonProcess) {
      pythonProcess.kill();
    }
  });
}

// Inicia o servidor Python com Eel
function startPythonServer() {
  // Ajuste para caminhos em diferentes sistemas operacionais
  const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
  const scriptPath = path.join(__dirname, 'python', 'main.py');
  
  console.log('Iniciando servidor Python...');
  console.log(`Caminho do script: ${scriptPath}`);
    // Inicia o processo Python com PYTHONIOENCODING=utf-8 e forçando codificação UTF-8
  pythonProcess = spawn(pythonPath, ['-X', 'utf8', scriptPath], {
    env: { 
      ...process.env, 
      PYTHONIOENCODING: 'utf-8',
      PYTHONLEGACYWINDOWSSTDIO: 'utf-8' // Ajuda com a codificação no Windows
    }
  });
  pythonProcess.stdout.on('data', (data) => {
    // Garantir que a codificação seja UTF-8
    const output = Buffer.isBuffer(data) ? data.toString('utf8') : String(data);
    console.log(`Python: ${output}`);
    
    // Verifica se o servidor está pronto (mensagem específica ou porta aberta)
    if (output.includes('Bottle v') || output.includes('Running on http://') || 
        output.includes('Eel iniciado') || output.includes('Aplicação Eel iniciada')) {
      console.log('Servidor Python iniciado com sucesso!');
      serverReady = true;
    }
      // Detecta a porta explicitamente marcada pelo script Python
    const eelPortMatch = output.match(/EEL_PORT:(\d+)/);
    if (eelPortMatch && eelPortMatch[1]) {
      const detectedPort = parseInt(eelPortMatch[1]);
      console.log(`Detectada porta explícita do Eel: ${detectedPort}`);
      
      // Move esta porta para o início da lista e remove duplicatas
      portasParaTentar = [detectedPort, ...portasParaTentar.filter(p => p !== detectedPort)];
      
      // Reset da porta atual para usar a detectada
      portaAtual = 0;
      
      // Marca o servidor como pronto já que recebemos a mensagem explícita
      console.log('Servidor Python iniciado com sucesso na porta ' + detectedPort);
      serverReady = true;
    }
    
    // Detecta mensagens no formato padrão "porta XXX"
    const portMatch = output.match(/porta (\d+)/);
    if (portMatch && portMatch[1]) {
      const detectedPort = parseInt(portMatch[1]);
      console.log(`Detectada porta do servidor: ${detectedPort}`);
      
      // Atualiza a porta para usar no mainWindow.loadURL
      portasParaTentar = [detectedPort, ...portasParaTentar.filter(p => p !== detectedPort)];
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    // Garantir que a codificação seja UTF-8 também para erros
    const errorOutput = Buffer.isBuffer(data) ? data.toString('utf8') : String(data);
    console.error(`Erro Python: ${errorOutput}`); 
  });
  
  pythonProcess.on('close', (code) => {
    console.log(`Processo Python finalizado com código: ${code}`);
    if (code !== 0 && mainWindow) {
      // Mostrar mensagem de erro no aplicativo
      mainWindow.loadFile(path.join(__dirname, 'web', 'error.html'));
    }
  });
}

// Manipula ativação do aplicativo
app.on('ready', () => {
  console.log('Aplicativo Electron iniciando...');
  startPythonServer();
  createWindow();
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});