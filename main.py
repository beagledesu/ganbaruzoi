import asyncio
import websockets
import http.server
import socketserver
import threading
import os
import json
from pathlib import Path
from apex_api import ApexAPI
from utils.name_override import NameOverrideTool
from utils.settings import SettingsManager
from server.http_server import OverlayHTTPHandler
from server.api_routes import init_api_routes

# クライアント接続を保持するセット
connected_clients = set()

# 設定マネージャーの作成
settings_manager = SettingsManager("settings.json")

# ApexAPIのインスタンス
apex_api = ApexAPI()

# Name Override Toolのインスタンス
name_override_tool = NameOverrideTool()

# APIルートを初期化
init_api_routes(settings_manager, name_override_tool)

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

# メイン処理
async def main():
    # 設定の読み込み
    websocket_settings = settings_manager.get_websocket_settings()
    http_settings = settings_manager.get_http_settings()
    
    host = websocket_settings.get("host", "localhost")
    ws_port = websocket_settings.get("port", 7777)
    http_port = http_settings.get("port", 8080)
    
    # APEXの設定
    apex_api.setup()
    
    # Name Override Toolのセットアップ
    name_override_tool.setup()
    
    print(f"Apex Legends Python Overlay Tool")
    print(f"================================")
    
    # HTTPサーバーの起動
    handler = lambda *args, **kwargs: OverlayHTTPHandler(*args, directory="client", **kwargs)
    http_server = socketserver.ThreadingTCPServer((host, http_port), handler)
    http_thread = threading.Thread(target=http_server.serve_forever)
    http_thread.daemon = True
    http_thread.start()
    print(f"HTTPサーバーを起動しました - http://{host}:{http_port}")
    print(f"設定ページ: http://{host}:{http_port}/settings.html")
    
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