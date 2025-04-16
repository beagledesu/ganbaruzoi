import json
import os
from pathlib import Path

# 設定ファイルのパス
SETTINGS_FILE = Path("settings.json")

# デフォルト設定
DEFAULT_SETTINGS = {
    "overlay": {
        "theme": "dark",
        "opacity": 0.8,
        "fontSize": "medium"
    },
    "websocket": {
        "host": "localhost",
        "port": 7777
    },
    "http": {
        "host": "localhost",
        "port": 8080
    }
}

def load_settings():
    """設定を読み込む"""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        else:
            # 設定ファイルが存在しない場合はデフォルト設定を保存
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS
    except Exception as e:
        print(f"設定の読み込みに失敗しました: {str(e)}")
        return DEFAULT_SETTINGS

def save_settings(settings):
    """設定を保存する"""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=4)
        print(f"設定を保存しました: {SETTINGS_FILE}")
        return True
    except Exception as e:
        print(f"設定の保存に失敗しました: {str(e)}")
        return False