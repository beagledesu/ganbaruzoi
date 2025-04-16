import os
import json
from pathlib import Path
from utils.logger import get_logger

# ロガーの取得
logger = get_logger()

class NameOverrideTool:
    """
    Apex LegendsのName Override Tool機能を実装するクラス
    
    この機能を使用すると、オブザーバーはマッチ内のプレイヤー名を変更できます。
    主に配信用にクリーンな名前を提供するために使用されます。
    """
    
    def __init__(self):
        # ユーザー名を取得
        self.username = os.environ.get('USERNAME', 'YourUsername')
        
        # Apexのtempフォルダのパス
        self.temp_path = Path(f"C:/Users/{self.username}/Saved Games/Respawn/Apex/assets/temp")
        
        # override_names.txtのパス
        self.override_file = self.temp_path / "override_names.txt"

    def setup(self):
        """Name Override Toolのセットアップ"""
        # tempフォルダが存在するか確認
        if not self.temp_path.exists():
            logger.warning(f"Apexのtempフォルダが見つかりません: {self.temp_path}")
            return False
        
        logger.info(f"Name Override Tool: {self.override_file}")
        return True

    def create_override_file(self, names_dict=None):
        """
        Name Override Fileを作成
        
        Parameters:
            names_dict (dict): オーバーライドする名前のディクショナリ
                              {"platform_id or steam_id": "desired_name"}
        """
        if names_dict is None:
            names_dict = {}
        
        # 基本的なテンプレート
        override_content = "names\n{\n"
        
        # 名前のエントリを追加
        for player_id, desired_name in names_dict.items():
            override_content += f'    {player_id} "{desired_name}"\n'
        
        override_content += "}\n"
        
        # ファイルに書き込み
        with open(self.override_file, "w") as f:
            f.write(override_content)
        
        logger.info(f"Name Override Fileを作成しました: {self.override_file}")
        return True

    def add_override(self, player_id, desired_name):
        """
        Name Override Fileに新しいオーバーライドエントリを追加
        
        Parameters:
            player_id (str): プレイヤーのプラットフォームIDまたはSteam ID
            desired_name (str): 表示したい名前
        
        Returns:
            bool: 操作が成功したかどうか
        """
        # ファイルが存在するか確認
        if not self.override_file.exists():
            # 存在しない場合は新規作成
            return self.create_override_file({player_id: desired_name})
        
        try:
            # 現在のファイル内容を読み込み
            with open(self.override_file, "r") as f:
                content = f.read()
            
            # 既存の内容を解析
            names_dict = {}
            in_names_block = False
            for line in content.split("\n"):
                line = line.strip()
                if line == "names":
                    in_names_block = True
                elif line == "{":
                    continue
                elif line == "}" and in_names_block:
                    in_names_block = False
                elif in_names_block and line and line != "{" and line != "}":
                    # IDと名前を抽出
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        id_part = parts[0].strip()
                        name_part = parts[1].strip().strip('"')
                        names_dict[id_part] = name_part
            
            # 新しいエントリを追加または更新
            names_dict[player_id] = desired_name
            
            # ファイルを更新
            return self.create_override_file(names_dict)
        
        except Exception as e:
            logger.error(f"Name Override Fileの更新中にエラーが発生しました: {str(e)}")
            return False

    def remove_override(self, player_id):
        """
        Name Override Fileから特定のプレイヤーのオーバーライドを削除
        
        Parameters:
            player_id (str): 削除するプレイヤーのID
        
        Returns:
            bool: 操作が成功したかどうか
        """
        # ファイルが存在するか確認
        if not self.override_file.exists():
            logger.warning("Name Override Fileが存在しません")
            return False
        
        try:
            # 現在のファイル内容を読み込み
            with open(self.override_file, "r") as f:
                content = f.read()
            
            # 既存の内容を解析
            names_dict = {}
            in_names_block = False
            for line in content.split("\n"):
                line = line.strip()
                if line == "names":
                    in_names_block = True
                elif line == "{":
                    continue
                elif line == "}" and in_names_block:
                    in_names_block = False
                elif in_names_block and line and line != "{" and line != "}":
                    # IDと名前を抽出
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        id_part = parts[0].strip()
                        name_part = parts[1].strip().strip('"')
                        names_dict[id_part] = name_part
            
            # 指定されたIDが存在する場合は削除
            if player_id in names_dict:
                del names_dict[player_id]
                logger.info(f"プレイヤーID {player_id} のオーバーライドを削除しました")
            else:
                logger.warning(f"プレイヤーID {player_id} のオーバーライドが見つかりません")
                return False
            
            # ファイルを更新
            return self.create_override_file(names_dict)
        
        except Exception as e:
            logger.error(f"Name Override Fileの更新中にエラーが発生しました: {str(e)}")
            return False

    def get_all_overrides(self):
        """
        現在のすべての名前オーバーライドを取得
        
        Returns:
            dict: {player_id: desired_name} の形式の辞書
        """
        # ファイルが存在するか確認
        if not self.override_file.exists():
            logger.warning("Name Override Fileが存在しません")
            return {}
        
        try:
            # 現在のファイル内容を読み込み
            with open(self.override_file, "r") as f:
                content = f.read()
            
            # 既存の内容を解析
            names_dict = {}
            in_names_block = False
            for line in content.split("\n"):
                line = line.strip()
                if line == "names":
                    in_names_block = True
                elif line == "{":
                    continue
                elif line == "}" and in_names_block:
                    in_names_block = False
                elif in_names_block and line and line != "{" and line != "}":
                    # IDと名前を抽出
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        id_part = parts[0].strip()
                        name_part = parts[1].strip().strip('"')
                        names_dict[id_part] = name_part
            
            return names_dict
        
        except Exception as e:
            logger.error(f"Name Override Fileの読み込み中にエラーが発生しました: {str(e)}")
            return {}

    def save_preset(self, preset_name, names_dict, settings_manager):
        """
        名前プリセットを設定に保存
        
        Parameters:
            preset_name (str): プリセット名
            names_dict (dict): 名前オーバーライド辞書
            settings_manager: 設定マネージャーのインスタンス
        
        Returns:
            bool: 操作が成功したかどうか
        """
        try:
            # 現在の設定を取得
            name_override_settings = settings_manager.get_setting("nameOverride")
            
            # プリセットを更新
            if "presets" not in name_override_settings:
                name_override_settings["presets"] = {}
            
            name_override_settings["presets"][preset_name] = names_dict
            
            # 設定を保存
            settings_manager.save_settings()
            logger.info(f"名前プリセット '{preset_name}' を保存しました")
            return True
        
        except Exception as e:
            logger.error(f"名前プリセットの保存中にエラーが発生しました: {str(e)}")
            return False

    def load_preset(self, preset_name, settings_manager):
        """
        名前プリセットを読み込んでオーバーライドファイルに適用
        
        Parameters:
            preset_name (str): プリセット名
            settings_manager: 設定マネージャーのインスタンス
        
        Returns:
            bool: 操作が成功したかどうか
        """
        try:
            # 現在の設定を取得
            name_override_settings = settings_manager.get_setting("nameOverride")
            
            # プリセットが存在するか確認
            if "presets" not in name_override_settings or preset_name not in name_override_settings["presets"]:
                logger.warning(f"名前プリセット '{preset_name}' が見つかりません")
                return False
            
            # プリセットを取得
            preset = name_override_settings["presets"][preset_name]
            
            # オーバーライドファイルに適用
            return self.create_override_file(preset)
        
        except Exception as e:
            logger.error(f"名前プリセットの読み込み中にエラーが発生しました: {str(e)}")
            return False