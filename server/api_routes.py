import json
from pathlib import Path
from utils.logger import get_logger

# ロガーの取得
logger = get_logger()

# 設定マネージャーと名前オーバーライドツールへの参照
settings_manager = None
name_override_tool = None

def init_api_routes(app_settings, app_name_override):
    """APIルートの初期化"""
    global settings_manager, name_override_tool
    settings_manager = app_settings
    name_override_tool = app_name_override

def handle_api_request(path, request_data=None):
    """
    APIリクエストを処理
    
    Parameters:
        path (str): リクエストパス
        request_data (dict): リクエストデータ（POSTリクエストの場合）
        
    Returns:
        dict: レスポンスデータ
    """
    try:
        # 設定取得
        if path == '/api/settings' and request_data is None:
            return {
                'success': True,
                'settings': settings_manager.settings
            }
        # 設定保存
        elif path == '/api/settings' and request_data is not None:
            # 設定の更新
            if 'overlay' in request_data:
                settings_manager.settings['overlay'] = request_data['overlay']
            if 'websocket' in request_data:
                settings_manager.settings['websocket'] = request_data['websocket']
            if 'http' in request_data:
                settings_manager.settings['http'] = request_data['http']
            if 'nameOverride' in request_data:
                settings_manager.settings['nameOverride']['enabled'] = request_data['nameOverride']['enabled']
            
            # 設定を保存
            if settings_manager.save_settings():
                return {'success': True}
            else:
                return {'success': False, 'message': '設定の保存に失敗しました。'}
        # Name Override取得
        elif path == '/api/name-override/get-all':
            overrides = name_override_tool.get_all_overrides()
            return {
                'success': True,
                'overrides': overrides
            }
        # Name Override追加
        elif path == '/api/name-override/add' and request_data is not None:
            player_id = request_data.get('playerId')
            display_name = request_data.get('displayName')
            
            if not player_id or not display_name:
                return {'success': False, 'message': 'プレイヤーIDと表示名が必要です。'}
            
            if name_override_tool.add_override(player_id, display_name):
                # 更新された一覧を返す
                overrides = name_override_tool.get_all_overrides()
                return {
                    'success': True,
                    'overrides': overrides
                }
            else:
                return {'success': False, 'message': '名前オーバーライドの追加に失敗しました。'}
        # Name Override削除
        elif path == '/api/name-override/remove' and request_data is not None:
            player_id = request_data.get('playerId')
            
            if not player_id:
                return {'success': False, 'message': 'プレイヤーIDが必要です。'}
            
            if name_override_tool.remove_override(player_id):
                # 更新された一覧を返す
                overrides = name_override_tool.get_all_overrides()
                return {
                    'success': True,
                    'overrides': overrides
                }
            else:
                return {'success': False, 'message': '名前オーバーライドの削除に失敗しました。'}
        # プリセット保存
        elif path == '/api/name-override/save-preset' and request_data is not None:
            preset_name = request_data.get('presetName')
            overrides = request_data.get('overrides', {})
            
            if not preset_name:
                return {'success': False, 'message': 'プリセット名が必要です。'}
            
            if name_override_tool.save_preset(preset_name, overrides, settings_manager):
                return {
                    'success': True,
                    'presets': settings_manager.get_setting('nameOverride.presets', {})
                }
            else:
                return {'success': False, 'message': 'プリセットの保存に失敗しました。'}
        # プリセット読み込み
        elif path == '/api/name-override/load-preset' and request_data is not None:
            preset_name = request_data.get('presetName')
            
            if not preset_name:
                return {'success': False, 'message': 'プリセット名が必要です。'}
            
            name_override_settings = settings_manager.get_setting('nameOverride', {})
            presets = name_override_settings.get('presets', {})
            
            if preset_name not in presets:
                return {'success': False, 'message': f"プリセット '{preset_name}' が見つかりません。"}
            
            preset_overrides = presets[preset_name]
            
            if name_override_tool.create_override_file(preset_overrides):
                return {
                    'success': True,
                    'overrides': preset_overrides
                }
            else:
                return {'success': False, 'message': 'プリセットの適用に失敗しました。'}
        # プリセット削除
        elif path == '/api/name-override/delete-preset' and request_data is not None:
            preset_name = request_data.get('presetName')
            
            if not preset_name:
                return {'success': False, 'message': 'プリセット名が必要です。'}
            
            name_override_settings = settings_manager.get_setting('nameOverride', {})
            presets = name_override_settings.get('presets', {}).copy()
            
            if preset_name not in presets:
                return {'success': False, 'message': f"プリセット '{preset_name}' が見つかりません。"}
            
            # プリセットを削除
            del presets[preset_name]
            
            # 設定を更新
            settings_manager.set_setting('nameOverride.presets', presets)
            if settings_manager.save_settings():
                return {
                    'success': True,
                    'presets': presets
                }
            else:
                return {'success': False, 'message': 'プリセットの削除に失敗しました。'}
        else:
            return {'success': False, 'message': '無効なAPIリクエストです。'}
    except Exception as e:
        logger.error(f"APIリクエスト処理中にエラーが発生しました: {str(e)}")
        return {'success': False, 'message': f"エラー: {str(e)}"}