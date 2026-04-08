import webview
import subprocess
import socket
import time
import threading
import sys
import os

def is_n8n_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', 5678)) == 0

def launch_n8n():
    if not is_n8n_running():
        try:
            # Essayer 'n8n start'
            try:
                subprocess.Popen(['n8n', 'start'], creationflags=0x08000000) # CREATE_NO_WINDOW
            except FileNotFoundError:
                # Essayer 'npx n8n start'
                subprocess.Popen(['npx.cmd', 'n8n', 'start'], creationflags=0x08000000)
        except Exception:
            return False
    return True

def check_and_load(window):
    success = launch_n8n()
    
    if not success:
        time.sleep(2)
        window.load_html(\"\"\"
            <body style='background-color: #1a1a1a; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;'>
                <h1 style='color: #ff6d5a;'>n8n n'est pas installé</h1>
                <p>Veuillez installer n8n via la commande : <strong>npm install n8n -g</strong></p>
                <button onclick='window.pywebview.api.close()' style='padding: 10px 20px; cursor: pointer;'>Fermer</button>
            </body>
        \"\"\")
        return

    # Attente que le port soit prêt
    retries = 40
    while not is_n8n_running() and retries > 0:
        time.sleep(1)
        retries -= 1
    
    if is_n8n_running():
        window.load_url('http://localhost:5678')
    else:
        window.load_html(\"\"\"
            <body style='background-color: #1a1a1a; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh;'>
                <h1 style='color: #ff6d5a;'>Erreur de démarrage</h1>
                <p>n8n a mis trop de temps à répondre ou a échoué à se lancer.</p>
            </body>
        \"\"\")

loading_html = \"\"\"
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background-color: #1a1a1a; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .loader { border: 6px solid #333; border-top: 6px solid #ff6d5a; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .progress-container { width: 300px; background-color: #333; border-radius: 10px; overflow: hidden; height: 8px; }
        .progress-bar { width: 0%; height: 100%; background-color: #ff6d5a; transition: width 0.3s; }
        h2 { font-weight: 300; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="loader"></div>
    <h2>Initialisation de n8n...</h2>
    <div class="progress-container"><div id="bar" class="progress-bar"></div></div>
    <script>
        let p = 0;
        setInterval(() => { 
            if(p < 95) { 
                p += (100 - p) * 0.1; 
                document.getElementById('bar').style.width = p + '%'; 
            } 
        }, 800);
    </script>
</body>
</html>
\"\"\"

if __name__ == '__main__':
    window = webview.create_window('n8n Launcher', html=loading_html, width=1280, height=800)
    threading.Thread(target=check_and_load, args=(window,), daemon=True).start()
    webview.start()
