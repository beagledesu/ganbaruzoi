import json
import os
import shutil
from pathlib import Path
from utils.logger import get_logger

# ロガーの取得
logger = get_logger()

# Apex LegendsのLiveAPI設定ファイルのパス
def get_apex_liveapi_path():
    """Apex Legends LiveAPIのパスを取得"""
    username = os.environ.get('USERNAME', 'YourUsername')
    return Path(f"C:/Users/{username}/Saved Games/Respawn/Apex/assets/temp/live_api")

async def setup_apex_config():
    """Apex LegendsのLiveAPI設定を準備"""
    # LiveAPIのパス
    liveapi_path = get_apex_liveapi_path()
    
    # ディレクトリが存在しない場合は作成
    if not liveapi_path.exists():
        logger.info(f"LiveAPIディレクトリを作成します: {liveapi_path}")
        liveapi_path.mkdir(parents=True, exist_ok=True)
    
    # 設定ファイルのパス
    config_file = liveapi_path / "config.json"
    
    # 設定ファイルが存在しない場合は作成
    if not config_file.exists():
        logger.info(f"LiveAPI設定ファイルを作成します: {config_file}")
        
        # デフォルト設定
        default_config = {
            "websocket": {
                "ip": "127.0.0.1",
                "port": 8765
            },
            "features": {
                "player": True,
                "squad": True,
                "match": True,
                "gamestate": True
            },
            "debug": False
        }
        
        # 設定ファイルを書き込み
        with open(config_file, "w") as f:
            json.dump(default_config, f, indent=4)
        
        logger.info("LiveAPI設定ファイルが作成されました。")
    else:
        logger.info(f"既存のLiveAPI設定ファイルを使用します: {config_file}")
    
    logger.info("Apex Legends LiveAPI設定が完了しました。")
    return config_file