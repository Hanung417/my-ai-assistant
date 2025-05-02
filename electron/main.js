const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let pyProc = null;

function startPythonServer() {
  const script = path.join(__dirname, '../backend/main.py');
  pyProc = spawn('python', [script]);

  pyProc.stdout.on('data', (data) => console.log(`PYTHON: ${data}`));
  pyProc.stderr.on('data', (data) => console.error(`PYTHON ERROR: ${data}`));
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: { nodeIntegration: true, contextIsolation: false }
  });

  win.loadURL('http://localhost:3000');
}

app.whenReady().then(() => {
  startPythonServer();
  createWindow();
});

app.on('window-all-closed', () => {
  if (pyProc) pyProc.kill();
  if (process.platform !== 'darwin') app.quit();
});
