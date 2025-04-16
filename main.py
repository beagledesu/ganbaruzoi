import asyncio
import websockets
import http.server
import socketserver
import threading
import os
import json
from pathlib import Path
from apex_api import ApexAPI

# クライアント接続を保持するセット
connected_clients = set()

# ApexAPIのインスタンス
apex_api = ApexAPI()

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
                
                # APEXデータの処理
                processed_data = apex_api.process_data(data)
                
                # クライアントに送信
                await websocket.send(json.dumps(processed_data))
            except Exception as e:
                print(f"エラー: {e}")
                error_response = {
                    "type": "error",
                    "message": str(e)
                }
                await websocket.send(json.dumps(error_response))
    
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
        <div id="game-state" class="panel">
            <div id="match-status">マッチ外</div>
            <div id="remaining-squads"></div>
        </div>
        <div id="player-info" class="panel">
            <div class="player-header">
                <div id="player-name" class="name">--</div>
                <div id="player-legend" class="legend">--</div>
            </div>
            <div class="stat-row">
                <div class="stat-label">HP:</div>
                <div class="health-bar">
                    <div id="health-fill" class="health-fill"></div>
                    <div id="health-text" class="bar-text">0/0</div>
                </div>
            </div>
            <div class="stat-row">
                <div class="stat-label">シールド:</div>
                <div class="shield-bar">
                    <div id="shield-fill" class="shield-fill"></div>
                    <div id="shield-text" class="bar-text">0/0</div>
                </div>
            </div>
            <div class="stat-row kills-damage">
                <div class="kills">キル: <span id="kills-value">0</span></div>
                <div class="damage">ダメージ: <span id="damage-value">0</span></div>
            </div>
        </div>
        <div id="squad-container" class="panel">
            <h2>スクワッド</h2>
            <div id="squad-members">
                <!-- スクワッドメンバーが動的に追加される -->
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
    width: 300px;
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

#game-state {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

#match-status {
    color: #f39c12;
}

#remaining-squads {
    color: #e74c3c;
}

h2 {
    font-size: 16px;
    margin: 0 0 10px 0;
    color: #ccc;
}

.player-header {
    margin-bottom: 10px;
}

.name {
    font-weight: bold;
    font-size: 18px;
}

.legend {
    font-size: 14px;
    color: #f39c12;
}

.stat-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.stat-label {
    width: 70px;
    font-size: 14px;
}

.health-bar, .shield-bar {
    height: 16px;
    background-color: #333;
    border-radius: 4px;
    flex: 1;
    position: relative;
    overflow: hidden;
}

.health-fill {
    background-color: #2ecc71;
    height: 100%;
    width: 0%;
    transition: width 0.3s ease;
}

.shield-fill {
    background-color: #3498db;
    height: 100%;
    width: 0%;
    transition: width 0.3s ease;
}

.bar-text {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    text-shadow: 1px 1px 1px rgba(0,0,0,0.7);
}

.kills-damage {
    display: flex;
    justify-content: space-between;
}

#squad-members {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.squad-member {
    background-color: rgba(0, 0, 0, 0.4);
    border-radius: 3px;
    padding: 8px;
}

.squad-member .name {
    font-size: 14px;
}

.squad-member .legend {
    font-size: 12px;
    margin-bottom: 5px;
}

.squad-member .health-bar,
.squad-member .shield-bar {
    height: 8px;
    margin-bottom: 4px;
}

.squad-member .bar-text {
    font-size: 9px;
}""")
    
    # script.js
    with open(client_dir / "script.js", "w", encoding="utf-8") as f:
        f.write("""// WebSocket接続
const socket = new WebSocket('ws://localhost:8765');
const statusEl = document.getElementById('status');

// プレイヤー要素
const matchStatusEl = document.getElementById('match-status');
const remainingSquadsEl = document.getElementById('remaining-squads');
const playerNameEl = document.getElementById('player-name');
const playerLegendEl = document.getElementById('player-legend');
const healthFillEl = document.getElementById('health-fill');
const healthTextEl = document.getElementById('health-text');
const shieldFillEl = document.getElementById('shield-fill');
const shieldTextEl = document.getElementById('shield-text');
const killsValueEl = document.getElementById('kills-value');
const damageValueEl = document.getElementById('damage-value');
const squadMembersEl = document.getElementById('squad-members');

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
        
        // ゲーム状態の更新
        if (data.gameState) {
            // TODO: ゲーム状態に応じた表示の更新
        }
        
        // マッチ情報の更新
        if (data.match) {
            const match = data.match;
            
            if (match.inProgress) {
                matchStatusEl.textContent = 'マッチ中';
                
                if (match.remainingSquads) {
                    remainingSquadsEl.textContent = `残り ${match.remainingSquads} スクワッド`;
                    remainingSquadsEl.style.display = 'block';
                }
            } else {
                matchStatusEl.textContent = 'マッチ外';
                remainingSquadsEl.style.display = 'none';
            }
            
            if (match.squadEliminated) {
                matchStatusEl.textContent = 'スクワッド敗退';
                matchStatusEl.style.color = '#e74c3c';
            } else {
                matchStatusEl.style.color = '';
            }
        }
        
        // プレイヤー情報の更新
        if (data.player) {
            const player = data.player;
            
            // 名前とレジェンド
            playerNameEl.textContent = player.name || '--';
            playerLegendEl.textContent = player.legend || '--';
            
            // HP
            if (player.health !== undefined && player.maxHealth) {
                const healthPercent = (player.health / player.maxHealth) * 100;
                healthFillEl.style.width = `${healthPercent}%`;
                healthTextEl.textContent = `${player.health}/${player.maxHealth}`;
            }
            
            // シールド
            if (player.shields !== undefined && player.maxShields) {
                const shieldPercent = (player.shields / player.maxShields) * 100;
                shieldFillEl.style.width = `${shieldPercent}%`;
                shieldTextEl.textContent = `${player.shields}/${player.maxShields}`;
            } else {
                shieldFillEl.style.width = '0%';
                shieldTextEl.textContent = '0/0';
            }
            
            // キルとダメージ
            killsValueEl.textContent = player.kills || 0;
            damageValueEl.textContent = player.damage || 0;
        }
        
        // スクワッド情報の更新
        if (data.squad) {
            const squad = data.squad;
            
            // スクワッドメンバーの表示をクリア
            squadMembersEl.innerHTML = '';
            
            // 各メンバーの情報を表示
            squad.forEach(member => {
                // 自分自身はスキップ（playerNameElの内容と一致するかチェック）
                if (member.name === playerNameEl.textContent) {
                    return;
                }
                
                const memberEl = document.createElement('div');
                memberEl.className = 'squad-member';
                
                // HPとシールドの計算
                const healthPercent = member.maxHealth ? (member.health / member.maxHealth) * 100 : 0;
                const shieldPercent = member.maxShields ? (member.shields / member.maxShields) * 100 : 0;
                
                memberEl.innerHTML = `
                    <div class="name">${member.name || '--'}</div>
                    <div class="legend">${member.legend || '--'}</div>
                    <div class="health-bar">
                        <div class="health-fill" style="width: ${healthPercent}%"></div>
                        <div class="bar-text">${member.health || 0}/${member.maxHealth || 0}</div>
                    </div>
                    <div class="shield-bar">
                        <div class="shield-fill" style="width: ${shieldPercent}%"></div>
                        <div class="bar-text">${member.shields || 0}/${member.maxShields || 0}</div>
                    </div>
                `;
                
                squadMembersEl.appendChild(memberEl);
            });
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

overlay.style.cursor = 'grab';

// キーボードショートカット
document.addEventListener('keydown', function(e) {
    // Alt+Oでオーバーレイの表示/非表示を切り替え
    if (e.altKey && e.key === 'o') {
        if (overlay.style.display === 'none') {
            overlay.style.display = 'block';
        } else {
            overlay.style.display = 'none';
        }
    }
});""")

# メイン処理
async def main():
    host = "localhost"
    ws_port = 7777  # APEX Legendsの設定に合わせて変更
    http_port = 8080
    
    # APEXの設定
    apex_api.setup()
    
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
        print(f"Alt+Oでオーバーレイの表示/非表示を切り替えられます")
        print(f"Ctrl+Cで終了します")
        
        # サーバーを永続的に実行
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nサーバーを終了します")