import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from utils.logger import get_logger

# ロガーの取得
logger = get_logger()

class OverlayHTTPHandler(SimpleHTTPRequestHandler):
    """オーバーレイ用のHTTPサーバーハンドラー"""
    
    def __init__(self, *args, directory=None, **kwargs):
        # クライアントフォルダをドキュメントルートとして設定
        if directory is None:
            directory = str(Path.cwd() / "client")
        
        super().__init__(*args, directory=directory, **kwargs)
    
    def log_message(self, format, *args):
        """HTTPリクエストのログ出力をカスタマイズ"""
        logger.debug(format % args)
    
    def do_GET(self):
        """GETリクエストの処理"""
        # ルートパスへのリクエストを/index.htmlにリダイレクト
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        
        # 通常のファイル処理を続行
        return super().do_GET()

def start_http_server(host="localhost", port=8080, directory=None):
    """HTTPサーバーを起動する関数"""
    if directory is None:
        directory = str(Path.cwd() / "client")
    
    # ディレクトリが存在するか確認
    if not os.path.exists(directory):
        logger.error(f"クライアントディレクトリが見つかりません: {directory}")
        return False
    
    # HTTPサーバーの設定
    handler = lambda *args, **kwargs: OverlayHTTPHandler(*args, directory=directory, **kwargs)
    
    try:
        server = HTTPServer((host, port), handler)
        logger.info(f"HTTPサーバーを起動しました - http://{host}:{port}")
        
        # サーバーをバックグラウンドで実行
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True  # メインプログラム終了時にスレッドも終了
        server_thread.start()
        
        return server
    
    except Exception as e:
        logger.error(f"HTTPサーバーの起動中にエラーが発生しました: {str(e)}")
        return None