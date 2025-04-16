import asyncio
import json
import websockets
from pathlib import Path
from utils.logger import get_logger
from server.api_handler import process_game_data

# ロガーの取得
logger = get_logger()

# 接続しているクライアント
connected_clients = set()

async def handle_client(websocket, path):
    """クライアント接続のハンドリング"""
    logger.info(f"新しいクライアント接続: {websocket.remote_address}")
    
    # クライアントをリストに追加
    connected_clients.add(websocket)
    
    try:
        async for message in websocket:
            try:
                # JSON形式のメッセージをパース
                data = json.loads(message)
                
                # ゲームデータの処理
                processed_data = process_game_data(data)
                
                # 処理結果をクライアントに送信
                await websocket.send(json.dumps(processed_data))
                
            except json.JSONDecodeError:
                logger.error("JSONのパースに失敗しました")
            except Exception as e:
                logger.error(f"メッセージ処理中にエラーが発生しました: {str(e)}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"クライアント接続が閉じられました: {websocket.remote_address}")
    finally:
        # クライアントをリストから削除
        connected_clients.remove(websocket)

async def broadcast_message(message):
    """全クライアントにメッセージをブロードキャスト"""
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients]
        )

async def start_websocket_server(host, port):
    """WebSocketサーバーの起動"""
    server = await websockets.serve(handle_client, host, port)
    logger.info(f"WebSocketサーバーを起動しました - {host}:{port}")
    
    # サーバーを永続的に実行
    await server.wait_closed()