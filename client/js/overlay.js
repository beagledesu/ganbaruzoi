/**
 * オーバーレイアプリケーションのメインモジュール
 */
document.addEventListener('DOMContentLoaded', () => {
    // WebSocketサーバーに接続
    wsManager.connect();
    
    // WebSocketイベントハンドラー
    wsManager.on('connect', () => {
        console.log('サーバーに接続しました');
    });
    
    wsManager.on('disconnect', () => {
        console.log('サーバーから切断されました');
    });
    
    wsManager.on('message', (data) => {
        // エラーメッセージの処理
        if (data.error) {
            console.error('サーバーエラー:', data.error);
            return;
        }
        
        // UI更新
        uiManager.updateGameState(data.gameState, data.match);
        uiManager.updatePlayerInfo(data.player);
        uiManager.updateSquadInfo(data.squad);
    });
    
    // キーボードショートカット
    document.addEventListener('keydown', (e) => {
        // Alt + O: オーバーレイの表示/非表示切り替え
        if (e.altKey && e.key === 'o') {
            const overlay = document.getElementById('overlay-container');
            overlay.style.display = overlay.style.display === 'none' ? 'block' : 'none';
        }
    });
});