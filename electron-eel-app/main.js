const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const isDevMode = process.env.NODE_ENV === 'development';

let mainWindow;
let pythonProcess;
let serverReady = false;

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

  // Aguarda o servidor Python estar pronto antes de carregar o conteúdo
  const checkServerInterval = setInterval(() => {
    if (serverReady) {
      // Carrega a URL do servidor Eel
      mainWindow.loadURL('http://localhost:8080/index.html');
      
      // Abre o DevTools em modo de desenvolvimento
      if (isDevMode) {
        mainWindow.webContents.openDevTools();
        console.log('Modo de desenvolvimento ativo');
      }
      
      clearInterval(checkServerInterval);
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
  
  // Inicia o processo Python
  pythonProcess = spawn(pythonPath, [scriptPath]);
  
  pythonProcess.stdout.on('data', (data) => {
    const output = data.toString();
    console.log(`Python: ${output}`);
    
    // Verifica se o servidor está pronto (mensagem específica ou porta aberta)
    if (output.includes('Bottle v') || output.includes('Running on http://')) {
      console.log('Servidor Python iniciado com sucesso!');
      serverReady = true;
    }
  });
  
  pythonProcess.stderr.on('data', (data) => {
    console.error(`Erro Python: ${data}`);
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