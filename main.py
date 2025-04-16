import asyncio
import websockets
import http.server
import socketserver
import threading
import os
import json
from pathlib import Path

# クライアント接続を保持するセット
connected_clients = set()

# WebSocketハンドラー
async def handle_client(websocket, path):
    print(f"クライアント接続: {websocket.remote_address}")
    connected_clients.add(websocket)
    
    try:
        async for message in websocket:
            print(f"メッセージ受信: {message}")
            try:
                # JSONデータの処理
                data = json.loads(message)
                # ここで実際のAPEX APIデータを処理します
                
                # テスト用の応答
                response = {
                    "type": "status",
                    "player": {
                        "name": "TestPlayer",
                        "health": 75,
                        "maxHealth": 100,
                        "shields": 50,
                        "maxShields": 100
                    }
                }
                
                await websocket.send(json.dumps(response))
            except Exception as e:
                print(f"エラー: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        print("クライアント切断")
    finally:
        connected_clients.remove(websocket)

# HTTPサーバーハンドラー
class HttpHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="client", **kwargs)
    
    def log_message(self, format, *args):
        print(format % args)

# クライアントフォルダとファイルの作成
def create_client_files():
    client_dir = Path("client")
    if not client_dir.exists():
        client_dir.mkdir()
    
    # index.html
    with open(client_dir / "index.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Legends オーバーレイ</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="overlay">
        <div id="status">接続中...</div>
        <div id="player-info" class="panel">
            <h2>プレイヤー情報</h2>
            <div id="player-data">
                <div class="name">--</div>
                <div class="health-bar">
                    <div class="health-fill"></div>
                </div>
                <div class="shield-bar">
                    <div class="shield-fill"></div>
                </div>
            </div>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>""")
    
    # style.css
    with open(client_dir / "style.css", "w", encoding="utf-8") as f:
        f.write("""body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
    background-color: transparent;
    color: white;
    overflow: hidden;
}

#overlay {
    position: fixed;
    top: 20px;
    left: 20px;
    z-index: 9999;
    user-select: none;
}

.panel {
    background-color: rgba(0, 0, 0, 0.7);
    border-radius: 5px;
    padding: 10px;
    margin-bottom: 10px;
}

#status {
    font-size: 12px;
    color: #999;
    margin-bottom: 5px;
}

h2 {
    font-size: 16px;
    margin: 0 0 10px 0;
    color: #ccc;
}

.name {
    font-weight: bold;
    margin-bottom: 5px;
}

.health-bar, .shield-bar {
    height: 8px;
    background-color: #333;
    border-radius: 4px;
    margin-bottom: 5px;
    overflow: hidden;
}

.health-fill {
    background-color: #2ecc71;
    height: 100%;
    width: 75%;
}

.shield-fill {
    background-color: #3498db;
    height: 100%;
    width: 50%;
}""")
    
    # script.js
    with open(client_dir / "script.js", "w", encoding="utf-8") as f:
        f.write("""// WebSocket接続
const socket = new WebSocket('ws://localhost:8765');
const statusEl = document.getElementById('status');
const playerNameEl = document.querySelector('.name');
const healthFillEl = document.querySelector('.health-fill');
const shieldFillEl = document.querySelector('.shield-fill');

// 接続イベント
socket.onopen = function() {
    statusEl.textContent = '接続しました';
    
    // テスト用メッセージ送信
    socket.send(JSON.stringify({
        type: 'hello',
        message: 'オーバーレイUIが接続しました'
    }));
};

// 切断イベント
socket.onclose = function() {
    statusEl.textContent = '切断されました';
};

// エラーイベント
socket.onerror = function(error) {
    statusEl.textContent = 'エラーが発生しました';
    console.error('WebSocket Error:', error);
};

// メッセージ受信イベント
socket.onmessage = function(event) {
    try {
        const data = JSON.parse(event.data);
        
        // プレイヤー情報の更新
        if (data.player) {
            playerNameEl.textContent = data.player.name || '--';
            
            if (data.player.health !== undefined && data.player.maxHealth) {
                const healthPercent = (data.player.health / data.player.maxHealth) * 100;
                healthFillEl.style.width = `${healthPercent}%`;
            }
            
            if (data.player.shields !== undefined && data.player.maxShields) {
                const shieldPercent = (data.player.shields / data.player.maxShields) * 100;
                shieldFillEl.style.width = `${shieldPercent}%`;
            }
        }
    } catch (e) {
        console.error('JSONパースエラー:', e);
    }
};

// ドラッグ可能にする
let isDragging = false;
let offsetX, offsetY;
const overlay = document.getElementById('overlay');

overlay.addEventListener('mousedown', function(e) {
    isDragging = true;
    offsetX = e.clientX - overlay.getBoundingClientRect().left;
    offsetY = e.clientY - overlay.getBoundingClientRect().top;
    overlay.style.cursor = 'grabbing';
});

document.addEventListener('mousemove', function(e) {
    if (isDragging) {
        overlay.style.left = (e.clientX - offsetX) + 'px';
        overlay.style.top = (e.clientY - offsetY) + 'px';
    }
});

document.addEventListener('mouseup', function() {
    isDragging = false;
    overlay.style.cursor = 'grab';
});

overlay.style.cursor = 'grab';""")

# メイン処理
async def main():
    host = "localhost"
    ws_port = 8765
    http_port = 8080
    
    # クライアントファイルの作成
    create_client_files()
    
    print(f"Apex Legends Python Overlay Tool")
    print(f"================================")
    
    # HTTPサーバーの起動
    handler = HttpHandler
    http_server = socketserver.ThreadingTCPServer((host, http_port), handler)
    http_thread = threading.Thread(target=http_server.serve_forever)
    http_thread.daemon = True
    http_thread.start()
    print(f"HTTPサーバーを起動しました - http://{host}:{http_port}")
    
    # WebSocketサーバーの起動
    async with websockets.serve(handle_client, host, ws_port):
        print(f"WebSocketサーバーを起動しました - ws://{host}:{ws_port}")
        print(f"ブラウザで http://{host}:{http_port} にアクセスしてください")
        print(f"Ctrl+Cで終了します")
        
        # サーバーを永続的に実行
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nサーバーを終了します")