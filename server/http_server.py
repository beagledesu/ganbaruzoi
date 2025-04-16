import os
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from utils.logger import get_logger
from server.api_routes import handle_api_request

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
        # APIリクエストの処理
        if self.path.startswith('/api/'):
            self.handle_api_request(None)
            return
        
        # ルートパスへのリクエストを/index.htmlにリダイレクト
        if self.path == "/" or self.path == "":
            self.path = "/index.html"
        
        # 通常のファイル処理を続行
        return super().do_GET()
    
    def do_POST(self):
        """POSTリクエストの処理"""
        # APIリクエストの処理
        if self.path.startswith('/api/'):
            # リクエストボディを取得
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                request_data = json.loads(post_data)
                self.handle_api_request(request_data)
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            
            return
        
        # その他のPOSTリクエスト
        self.send_error(404)
    def handle_api_request(self, request_data):
    """
    APIリクエストの処理
    
    Parameters:
        request_data (dict): POSTリクエストのデータ（GETの場合はNone）
    """
    try:
        # APIルートハンドラを呼び出し
        response = handle_api_request(self.path, request_data)
        
        # レスポンスヘッダー
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        # レスポンスボディ
        self.wfile.write(json.dumps(response).encode())
    
    except Exception as e:
        logger.error(f"APIリクエストの処理中にエラーが発生しました: {str(e)}")
        
        # エラーレスポンス
        self.send_response(500)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        error_response = {
            'success': False,
            'message': f"サーバーエラー: {str(e)}"
        }
        self.wfile.write(json.dumps(error_response).encode())