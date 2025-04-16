import json
from utils.logger import get_logger

# ロガーの取得
logger = get_logger()

def process_game_data(data):
    """
    Apex LegendsのAPIからのデータを処理する
    
    Parameters:
        data (dict): APIから受け取ったJSONデータ
        
    Returns:
        dict: 処理済みのデータ
    """
    try:
        # データの検証
        if not isinstance(data, dict):
            logger.warning(f"予期しないデータ形式です: {type(data)}")
            return {"error": "予期しないデータ形式です"}
        
        # 必要なデータを抽出
        processed_data = {
            "gameState": data.get("gameState", ""),
            "player": extract_player_data(data),
            "squad": extract_squad_data(data),
            "match": extract_match_data(data)
        }
        
        return processed_data
    
    except Exception as e:
        logger.error(f"データ処理中にエラーが発生しました: {str(e)}")
        return {"error": str(e)}

def extract_player_data(data):
    """プレイヤーデータの抽出"""
    player_data = data.get("player", {})
    return {
        "name": player_data.get("name", ""),
        "health": player_data.get("health", 0),
        "maxHealth": player_data.get("maxHealth", 100),
        "shields": player_data.get("shields", 0),
        "maxShields": player_data.get("maxShields", 0),
        "kills": player_data.get("kills", 0),
        "damage": player_data.get("damage", 0),
        "legend": player_data.get("legendName", ""),
        "position": player_data.get("position", {"x": 0, "y": 0, "z": 0})
    }

def extract_squad_data(data):
    """スクワッドデータの抽出"""
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
    
    return processed_squad

def extract_match_data(data):
    """マッチデータの抽出"""
    match_data = data.get("match", {})
    return {
        "inProgress": match_data.get("inProgress", False),
        "squadEliminated": match_data.get("squadEliminated", False),
        "phase": match_data.get("phase", 0),
        "remainingTime": match_data.get("remainingTime", 0),
        "remainingSquads": match_data.get("remainingSquads", 0)
    }