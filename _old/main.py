import asyncio
import json
import os
import sys
import argparse
from pathlib import Path
from server.websocket_server import start_websocket_server
from server.http_server import start_http_server
from utils.apex_config import setup_apex_config
from utils.name_override import NameOverrideTool
from utils.logger import setup_logger

# ロガーのセットアップ
logger = setup_logger()

async def main():
    # コマンドライン引数のパース
    parser = argparse.ArgumentParser(description="Apex Legends Python Overlay Tool")
    parser.add_argument("--host", default="localhost", help="ホスト名またはIPアドレス")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocketサーバーのポート")
    parser.add_argument("--http-port", type=int, default=8080, help="HTTPサーバーのポート")
    parser.add_argument("--debug", action="store_true", help="デバッグモードを有効にする")
    args = parser.parse_args()
    
    # 設定ファイルのパス
    config_path = Path("config.json")
    
    # 設定ファイルの読み込みまたは作成
    if not config_path.exists():
        # デフォルト設定の作成
        default_config = {
            "websocket": {
                "host": args.host,
                "port": args.ws_port
            },
            "http": {
                "host": args.host,
                "port": args.http_port
            },
            "overlay": {
                "position": "top-left",
                "opacity": 0.8,
                "show_health": True,
                "show_shields": True,
                "show_kills": True,
                "show_damage": True
            },
            "debug": args.debug
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        logger.info("デフォルト設定ファイルを作成しました。")
        config = default_config
    else:
        # 設定を読み込む
        with open(config_path, "r") as f:
            config = json.load(f)
    
    # デバッグモードの設定
    if args.debug:
        config["debug"] = True
    
    # Apex Legends APIの設定
    await setup_apex_config()
    
    # Name Override Toolのセットアップ
    name_override = NameOverrideTool()
    if name_override.setup():
        logger.info("Name Override Toolの準備が完了しました。")
    
    # HTTPサーバーの起動（オーバーレイUI用）
    http_host = config["http"]["host"]
    http_port = config["http"]["port"]
    http_server = start_http_server(http_host, http_port)
    
    if not http_server:
        logger.error("HTTPサーバーの起動に失敗しました。終了します。")
        return
    
    # WebSocketサーバーの起動
    ws_host = config["websocket"]["host"]
    ws_port = config["websocket"]["port"]
    
    logger.info(f"WebSocketサーバーを {ws_host}:{ws_port} で起動します...")
    logger.info(f"オーバーレイUIにアクセスするには: http://{http_host}:{http_port}")
    
    # アプリケーション情報を表示
    logger.info("================================================")
    logger.info("Apex Legends Python Overlay Tool")
    logger.info("================================================")
    logger.info(f"WebSocketサーバー: ws://{ws_host}:{ws_port}")
    logger.info(f"HTTPサーバー: http://{http_host}:{http_port}")
    logger.info("オーバーレイUIにアクセスするには上記のHTTPアドレスにブラウザからアクセスしてください")
    logger.info("Alt + O キーでオーバーレイの表示/非表示を切り替えられます")
    logger.info("オーバーレイはマウスでドラッグして移動できます")
    logger.info("================================================")
    
    # WebSocketサーバーを起動
    await start_websocket_server(ws_host, ws_port)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nアプリケーションを終了します。")
        sys.exit(0)