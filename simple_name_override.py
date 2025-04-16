import os
from pathlib import Path

class SimpleNameOverride:
    """単純なName Override機能"""
    
    def __init__(self):
        # ユーザー名を取得
        self.username = os.environ.get('USERNAME', 'YourUsername')
        
        # Apexのtempフォルダのパス
        self.temp_path = Path(f"C:/Users/{self.username}/Saved Games/Respawn/Apex/assets/temp")
        
        # override_names.txtのパス
        self.override_file = self.temp_path / "override_names.txt"
    
    def setup(self):
        """セットアップ（単にフォルダが存在するか確認）"""
        if not self.temp_path.exists():
            print(f"警告: Apexのtempフォルダが見つかりません: {self.temp_path}")
            return False
        
        print(f"Name Override Tool: {self.override_file}")
        return True
    
    def create_sample_override(self):
        """サンプルのオーバーライドファイルを作成"""
        try:
            # 簡単なサンプル
            sample_content = """names
{
    1234567890 "Player1"
    9876543210 "Player2"
}
"""
            # ファイルに書き込み
            with open(self.override_file, "w") as f:
                f.write(sample_content)
            
            print(f"サンプルのName Override Fileを作成しました: {self.override_file}")
            return True
        except Exception as e:
            print(f"サンプルファイルの作成に失敗しました: {str(e)}")
            return False