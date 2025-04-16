import asyncio
import websockets
import http.server
import socketserver
import threading
import os
import json
from pathlib import Path
from apex_api import ApexAPI
from simple_settings import load_settings, save_settings
from simple_name_override import SimpleNameOverride

# クライアント接続を保持するセット
connected_clients = set()

# 設定を読み込み
settings = load_settings()

# ApexAPIのインスタンス
apex_api = ApexAPI()

# Name Override Toolのインスタンス
name_override = SimpleNameOverride()

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
class SimpleHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="client", **kwargs)
    
    def log_message(self, format, *args):
        print(format % args)
    
    def do_GET(self):
        # 設定ファイルへのリクエスト
        if self.path == '/settings.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(settings).encode())
            return
        
        # その他のリクエスト
        return super().do_GET()
    
    def do_POST(self):
        # 設定保存リクエスト
        if self.path == '/save-settings':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                new_settings = json.loads(post_data)
                save_settings(new_settings)
                
                # レスポンス
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(str(e).encode())
            
            return
        
        # その他のPOSTリクエスト
        self.send_error(404)

# メイン処理
async def main():
    # 設定から接続情報を取得
    host = settings.get("websocket", {}).get("host", "localhost")
    ws_port = settings.get("websocket", {}).get("port", 7777)
    http_port = settings.get("http", {}).get("port", 8080)
    
    # APEXの設定
    apex_api.setup()
    
    # Name Override Toolのセットアップ
    if name_override.setup():
        # サンプルのオーバーライドファイルを作成（デモ用）
        name_override.create_sample_override()
    
    print(f"Apex Legends Python Overlay Tool")
    print(f"================================")
    
    # HTTPサーバーの起動
    handler = SimpleHTTPHandler
    http_server = socketserver.ThreadingTCPServer((host, http_port), handler)
    http_thread = threading.Thread(target=http_server.serve_forever)
    http_thread.daemon = True
    http_thread.start()
    print(f"HTTPサーバーを起動しました - http://{host}:{http_port}")
    
    # WebSocketサーバーの起動
    async with websockets.serve(handle_client, host, ws_port):
        print(f"WebSocketサーバーを起動しました - ws://{host}:{ws_port}")
        print(f"ブラウザで http://{host}:{http_port} にアクセスしてください")
        print(f"設定ページ: http://{host}:{http_port}/settings.html")
        print(f"Alt+Oでオーバーレイの表示/非表示を切り替えられます")
        print(f"Ctrl+Cで終了します")
        
        # サーバーを永続的に実行
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nサーバーを終了します")