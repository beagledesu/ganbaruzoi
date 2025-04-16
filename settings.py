import json
import os
from pathlib import Path
from utils.logger import get_logger

# ロガーの取得
logger = get_logger()

class SettingsManager:
    """設定管理クラス"""
    
    def __init__(self, settings_file="settings.json"):
        self.settings_file = Path(settings_file)
        self.settings = self._load_default_settings()
        
        # 設定ファイルが存在する場合は読み込む
        if self.settings_file.exists():
            self._load_settings()
        else:
            # 存在しない場合はデフォルト設定を保存
            self.save_settings()
    
    def _load_default_settings(self):
        """デフォルト設定を取得"""
        return {
            "overlay": {
                "theme": "dark",  # dark, light, custom
                "position": {
                    "top": "20px",
                    "left": "20px"
                },
                "opacity": 0.8,
                "fontSize": "medium",  # small, medium, large
                "showElements": {
                    "playerInfo": True,
                    "squadInfo": True,
                    "gameState": True,
                    "kills": True,
                    "damage": True
                },
                "colors": {
                    "background": "rgba(0, 0, 0, 0.7)",
                    "text": "#ffffff",
                    "health": "#2ecc71",
                    "shield": "#3498db",
                    "accent": "#f39c12"
                }
            },
            "websocket": {
                "host": "localhost",
                "port": 7777
            },
            "http": {
                "host": "localhost",
                "port": 8080
            },
            "nameOverride": {
                "enabled": False,
                "presets": {}  # { "preset1": { "1234567890": "PlayerName1", ... } }
            }
        }
    
    def _load_settings(self):
        """設定ファイルから設定を読み込む"""
        try:
            with open(self.settings_file, "r") as f:
                loaded_settings = json.load(f)
            
            # 読み込んだ設定をデフォルト設定にマージ
            self._merge_settings(self.settings, loaded_settings)
            logger.info(f"設定を読み込みました: {self.settings_file}")
        except Exception as e:
            logger.error(f"設定ファイルの読み込みに失敗しました: {str(e)}")
    
    def _merge_settings(self, default, loaded):
        """設定をマージする（欠けている設定はデフォルト値で補完）"""
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                self._merge_settings(value, loaded[key])
        
        # デフォルトにない余分な設定を削除
        keys_to_remove = [k for k in loaded.keys() if k not in default]
        for key in keys_to_remove:
            del loaded[key]
    
    def save_settings(self):
        """設定をファイルに保存"""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=4)
            logger.info(f"設定を保存しました: {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"設定の保存に失敗しました: {str(e)}")
            return False
    
    def get_setting(self, path, default=None):
        """
        指定パスの設定値を取得
        
        Parameters:
            path (str): ドット区切りの設定パス (例: "overlay.theme")
            default: 設定が存在しない場合のデフォルト値
            
        Returns:
            設定値またはデフォルト値
        """
        current = self.settings
        for part in path.split('.'):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def set_setting(self, path, value):
        """
        指定パスの設定値を設定
        
        Parameters:
            path (str): ドット区切りの設定パス (例: "overlay.theme")
            value: 設定する値
            
        Returns:
            bool: 設定が成功したかどうか
        """
        try:
            parts = path.split('.')
            current = self.settings
            
            # 最後の部分以外をたどる
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # 最後の部分を設定
            current[parts[-1]] = value
            return True
        except Exception as e:
            logger.error(f"設定の変更に失敗しました: {str(e)}")
            return False
    
    def get_overlay_settings(self):
        """オーバーレイ設定をJSON文字列で取得（クライアント用）"""
        return json.dumps(self.settings["overlay"])
    
    def get_websocket_settings(self):
        """WebSocket設定を取得"""
        return self.settings["websocket"]
    
    def get_http_settings(self):
        """HTTP設定を取得"""
        return self.settings["http"]
    
    def get_name_override_settings(self):
        """Name Override設定を取得"""
        return self.settings["nameOverride"]