import logging
import os
from pathlib import Path
from datetime import datetime

# ログディレクトリ
LOG_DIR = Path("logs")

def setup_logger():
    """アプリケーションのロガーをセットアップ"""
    # ログディレクトリが存在しない場合は作成
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True)
    
    # 日付でログファイル名を生成
    log_file = LOG_DIR / f"apex_overlay_{datetime.now().strftime('%Y%m%d')}.log"
    
    # ロガーのセットアップ
    logger = logging.getLogger("apex_overlay")
    logger.setLevel(logging.INFO)
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # コンソールハンドラー
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # フォーマッター
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ハンドラーをロガーに追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger():
    """アプリケーションのロガーを取得"""
    return logging.getLogger("apex_overlay")