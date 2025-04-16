// WebSocket接続
const socket = new WebSocket('ws://localhost:8765');
const statusEl = document.getElementById('status');
const playerNameEl = document.querySelector('.name');
const healthFillEl = document.querySelector('.health-fill');
const shieldFillEl = document.querySelector('.shield-fill');

// 接続イベント
socket.onopen = function() {
    statusEl.textContent = '接続しました';
    
    // テスト用メッセージ送信
    socket.send(JSON.stringify({
        type: 'hello',
        message: 'オーバーレイUIが接続しました'
    }));
};

// 切断イベント
socket.onclose = function() {
    statusEl.textContent = '切断されました';
};

// エラーイベント
socket.onerror = function(error) {
    statusEl.textContent = 'エラーが発生しました';
    console.error('WebSocket Error:', error);
};

// メッセージ受信イベント
socket.onmessage = function(event) {
    try {
        const data = JSON.parse(event.data);
        
        // プレイヤー情報の更新
        if (data.player) {
            playerNameEl.textContent = data.player.name || '--';
            
            if (data.player.health !== undefined && data.player.maxHealth) {
                const healthPercent = (data.player.health / data.player.maxHealth) * 100;
                healthFillEl.style.width = `${healthPercent}%`;
            }
            
            if (data.player.shields !== undefined && data.player.maxShields) {
                const shieldPercent = (data.player.shields / data.player.maxShields) * 100;
                shieldFillEl.style.width = `${shieldPercent}%`;
            }
        }
    } catch (e) {
        console.error('JSONパースエラー:', e);
    }
};

// ドラッグ可能にする
let isDragging = false;
let offsetX, offsetY;
const overlay = document.getElementById('overlay');

overlay.addEventListener('mousedown', function(e) {
    isDragging = true;
    offsetX = e.clientX - overlay.getBoundingClientRect().left;
    offsetY = e.clientY - overlay.getBoundingClientRect().top;
    overlay.style.cursor = 'grabbing';
});

document.addEventListener('mousemove', function(e) {
    if (isDragging) {
        overlay.style.left = (e.clientX - offsetX) + 'px';
        overlay.style.top = (e.clientY - offsetY) + 'px';
    }
});

document.addEventListener('mouseup', function() {
    isDragging = false;
    overlay.style.cursor = 'grab';
});

overlay.style.cursor = 'grab';