import json
import os
from pathlib import Path

class ApexAPI:
    def __init__(self):
        # ユーザー名を取得
        self.username = os.environ.get('USERNAME', 'YourUsername')
        
        # LiveAPIのパス
        self.liveapi_path = Path(f"C:/Users/{self.username}/Saved Games/Respawn/Apex/assets/temp/live_api")
        
        # 設定ファイルのパス
        self.config_file = self.liveapi_path / "config.json"
        
    def setup(self):
        """APIの設定を確認する（既存の設定は変更しない）"""
        # LiveAPIディレクトリが存在するか確認
        if not self.liveapi_path.exists():
            print(f"警告: LiveAPIディレクトリが見つかりません: {self.liveapi_path}")
            print(f"注意: この警告は無視しても構いません。APEXゲーム起動時に自動的に作成されます。")
        else:
            print(f"LiveAPIディレクトリが見つかりました: {self.liveapi_path}")
            
            if self.config_file.exists():
                print(f"既存のLiveAPI設定ファイルを使用します: {self.config_file}")
                try:
                    with open(self.config_file, "r") as f:
                        config = json.load(f)
                    print(f"WebSocket設定: {config.get('websocket', {})}")
                except Exception as e:
                    print(f"設定ファイルの読み込み中にエラーが発生しました: {str(e)}")
        
        print("APEX Legendsの起動オプションに +cl_liveapi_enabled 1 が設定されていることを確認してください")
        return True
    
    def process_data(self, data):
        """
        Apex Legendsから受信したデータを処理
        
        Parameters:
            data (dict): 受信したJSON形式のデータ
            
        Returns:
            dict: 処理済みのデータ
        """
        try:
            # データが存在しない場合は空のデータを返す
            if not data:
                return {
                    "type": "error",
                    "message": "データがありません"
                }
            
            # ゲーム状態の処理
            game_state = data.get("gameState", "")
            
            # プレイヤーデータの処理
            player_data = data.get("player", {})
            processed_player = {
                "name": player_data.get("name", ""),
                "health": player_data.get("health", 0),
                "maxHealth": player_data.get("maxHealth", 100),
                "shields": player_data.get("shields", 0),
                "maxShields": player_data.get("maxShields", 0),
                "kills": player_data.get("kills", 0),
                "damage": player_data.get("damage", 0),
                "legend": player_data.get("legendName", "")
            }
            
            # スクワッドデータの処理
            squad_data = data.get("squad", [])
            processed_squad = []
            
            for member in squad_data:
                processed_squad.append({
                    "name": member.get("name", ""),
                    "health": member.get("health", 0),
                    "maxHealth": member.get("maxHealth", 100),
                    "shields": member.get("shields", 0),
                    "maxShields": member.get("maxShields", 0),
                    "legend": member.get("legendName", "")
                })
            
            # マッチデータの処理
            match_data = data.get("match", {})
            processed_match = {
                "inProgress": match_data.get("inProgress", False),
                "squadEliminated": match_data.get("squadEliminated", False),
                "phase": match_data.get("phase", 0),
                "remainingTime": match_data.get("remainingTime", 0),
                "remainingSquads": match_data.get("remainingSquads", 0)
            }
            
            # 処理したデータを返す
            return {
                "type": "gameData",
                "gameState": game_state,
                "player": processed_player,
                "squad": processed_squad,
                "match": processed_match
            }
            
        except Exception as e:
            print(f"データ処理中にエラーが発生しました: {str(e)}")
            return {
                "type": "error",
                "message": f"データ処理エラー: {str(e)}"
            }