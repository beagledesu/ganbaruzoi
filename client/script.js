// WebSocket接続
const socket = new WebSocket('ws://localhost:8765');
const statusEl = document.getElementById('status');

// プレイヤー要素
const matchStatusEl = document.getElementById('match-status');
const remainingSquadsEl = document.getElementById('remaining-squads');
const playerNameEl = document.getElementById('player-name');
const playerLegendEl = document.getElementById('player-legend');
const healthFillEl = document.getElementById('health-fill');
const healthTextEl = document.getElementById('health-text');
const shieldFillEl = document.getElementById('shield-fill');
const shieldTextEl = document.getElementById('shield-text');
const killsValueEl = document.getElementById('kills-value');
const damageValueEl = document.getElementById('damage-value');
const squadMembersEl = document.getElementById('squad-members');

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
        
        // ゲーム状態の更新
        if (data.gameState) {
            // TODO: ゲーム状態に応じた表示の更新
        }
        
        // マッチ情報の更新
        if (data.match) {
            const match = data.match;
            
            if (match.inProgress) {
                matchStatusEl.textContent = 'マッチ中';
                
                if (match.remainingSquads) {
                    remainingSquadsEl.textContent = `残り ${match.remainingSquads} スクワッド`;
                    remainingSquadsEl.style.display = 'block';
                }
            } else {
                matchStatusEl.textContent = 'マッチ外';
                remainingSquadsEl.style.display = 'none';
            }
            
            if (match.squadEliminated) {
                matchStatusEl.textContent = 'スクワッド敗退';
                matchStatusEl.style.color = '#e74c3c';
            } else {
                matchStatusEl.style.color = '';
            }
        }
        
        // プレイヤー情報の更新
        if (data.player) {
            const player = data.player;
            
            // 名前とレジェンド
            playerNameEl.textContent = player.name || '--';
            playerLegendEl.textContent = player.legend || '--';
            
            // HP
            if (player.health !== undefined && player.maxHealth) {
                const healthPercent = (player.health / player.maxHealth) * 100;
                healthFillEl.style.width = `${healthPercent}%`;
                healthTextEl.textContent = `${player.health}/${player.maxHealth}`;
            }
            
            // シールド
            if (player.shields !== undefined && player.maxShields) {
                const shieldPercent = (player.shields / player.maxShields) * 100;
                shieldFillEl.style.width = `${shieldPercent}%`;
                shieldTextEl.textContent = `${player.shields}/${player.maxShields}`;
            } else {
                shieldFillEl.style.width = '0%';
                shieldTextEl.textContent = '0/0';
            }
            
            // キルとダメージ
            killsValueEl.textContent = player.kills || 0;
            damageValueEl.textContent = player.damage || 0;
        }
        
        // スクワッド情報の更新
        if (data.squad) {
            const squad = data.squad;
            
            // スクワッドメンバーの表示をクリア
            squadMembersEl.innerHTML = '';
            
            // 各メンバーの情報を表示
            squad.forEach(member => {
                // 自分自身はスキップ（playerNameElの内容と一致するかチェック）
                if (member.name === playerNameEl.textContent) {
                    return;
                }
                
                const memberEl = document.createElement('div');
                memberEl.className = 'squad-member';
                
                // HPとシールドの計算
                const healthPercent = member.maxHealth ? (member.health / member.maxHealth) * 100 : 0;
                const shieldPercent = member.maxShields ? (member.shields / member.maxShields) * 100 : 0;
                
                memberEl.innerHTML = `
                    <div class="name">${member.name || '--'}</div>
                    <div class="legend">${member.legend || '--'}</div>
                    <div class="health-bar">
                        <div class="health-fill" style="width: ${healthPercent}%"></div>
                        <div class="bar-text">${member.health || 0}/${member.maxHealth || 0}</div>
                    </div>
                    <div class="shield-bar">
                        <div class="shield-fill" style="width: ${shieldPercent}%"></div>
                        <div class="bar-text">${member.shields || 0}/${member.maxShields || 0}</div>
                    </div>
                `;
                
                squadMembersEl.appendChild(memberEl);
            });
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


// 設定を読み込む関数
async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (data.success) {
            return data.settings.overlay;
        } else {
            console.error('設定の読み込みに失敗しました:', data.message);
            return null;
        }
    } catch (error) {
        console.error('設定の読み込みに失敗しました:', error);
        return null;
    }
}

// 設定を適用する関数
function applySettings(settings) {
    if (!settings) return;
    
    const overlay = document.getElementById('overlay');
    
    // テーマ設定
    document.body.className = `theme-${settings.theme || 'dark'}`;
    
    // 不透明度設定
    const opacity = settings.opacity !== undefined ? settings.opacity : 0.8;
    const panels = document.querySelectorAll('.panel');
    panels.forEach(panel => {
        const bg = window.getComputedStyle(panel).backgroundColor;
        if (bg.startsWith('rgba')) {
            const rgbaValues = bg.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)/);
            if (rgbaValues) {
                const [, r, g, b] = rgbaValues;
                panel.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${opacity})`;
            }
        } else if (bg.startsWith('rgb')) {
            const rgbValues = bg.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
            if (rgbValues) {
                const [, r, g, b] = rgbValues;
                panel.style.backgroundColor = `rgba(${r}, ${g}, ${b}, ${opacity})`;
            }
        }
    });
    
    // フォントサイズ設定
    const fontSize = settings.fontSize || 'medium';
    document.body.style.fontSize = fontSize === 'small' ? '12px' : fontSize === 'large' ? '16px' : '14px';
    
    // 表示要素設定
    const showElements = settings.showElements || {};
    document.getElementById('player-info').style.display = showElements.playerInfo !== false ? 'block' : 'none';
    document.getElementById('squad-container').style.display = showElements.squadInfo !== false ? 'block' : 'none';
    document.getElementById('game-state').style.display = showElements.gameState !== false ? 'block' : 'none';
    
    const killsEl = document.querySelector('.kills');
    const damageEl = document.querySelector('.damage');
    if (killsEl) killsEl.style.display = showElements.kills !== false ? 'block' : 'none';
    if (damageEl) damageEl.style.display = showElements.damage !== false ? 'block' : 'none';
    
    // 色設定
    const colors = settings.colors || {};
    document.documentElement.style.setProperty('--color-background', colors.background || 'rgba(0, 0, 0, 0.7)');
    document.documentElement.style.setProperty('--color-text', colors.text || '#ffffff');
    document.documentElement.style.setProperty('--color-health', colors.health || '#2ecc71');
    document.documentElement.style.setProperty('--color-shield', colors.shield || '#3498db');
    document.documentElement.style.setProperty('--color-accent', colors.accent || '#f39c12');
}

// WebSocket接続
async function connectWebSocket() {
    // 設定からWebSocketの接続情報を取得
    let settings;
    try {
        const response = await fetch('/api/settings');
        const data = await response.json();
        
        if (data.success) {
            settings = data.settings;
        }
    } catch (error) {
        console.error('設定の読み込みに失敗しました:', error);
    }
    
    // WebSocket接続の設定
    const host = settings?.websocket?.host || 'localhost';
    const port = settings?.websocket?.port || 7777;
    const wsUrl = `ws://${host}:${port}`;
    
    const socket = new WebSocket(wsUrl);
    const statusEl = document.getElementById('status');
    
    // プレイヤー要素
    const matchStatusEl = document.getElementById('match-status');
    const remainingSquadsEl = document.getElementById('remaining-squads');
    const playerNameEl = document.getElementById('player-name');
    const playerLegendEl = document.getElementById('player-legend');
    const healthFillEl = document.getElementById('health-fill');
    const healthTextEl = document.getElementById('health-text');
    const shieldFillEl = document.getElementById('shield-fill');
    const shieldTextEl = document.getElementById('shield-text');
    const killsValueEl = document.getElementById('kills-value');
    const damageValueEl = document.getElementById('damage-value');
    const squadMembersEl = document.getElementById('squad-members');
    
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
        
        // 再接続を試みる
        setTimeout(connectWebSocket, 5000);
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
            
            // ゲーム状態の更新
            if (data.gameState) {
                // TODO: ゲーム状態に応じた表示の更新
            }
            
            // マッチ情報の更新
            if (data.match) {
                const match = data.match;
                
                if (match.inProgress) {
                    matchStatusEl.textContent = 'マッチ中';
                    
                    if (match.remainingSquads) {
                        remainingSquadsEl.textContent = `残り ${match.remainingSquads} スクワッド`;
                        remainingSquadsEl.style.display = 'block';
                    }
                } else {
                    matchStatusEl.textContent = 'マッチ外';
                    remainingSquadsEl.style.display = 'none';
                }
                
                if (match.squadEliminated) {
                    matchStatusEl.textContent = 'スクワッド敗退';
                    matchStatusEl.style.color = 'var(--color-accent)';
                } else {
                    matchStatusEl.style.color = '';
                }
            }
            
            // プレイヤー情報の更新
            if (data.player) {
                const player = data.player;
                
                // 名前とレジェンド
                playerNameEl.textContent = player.name || '--';
                playerLegendEl.textContent = player.legend || '--';
                
                // HP
                if (player.health !== undefined && player.maxHealth) {
                    const healthPercent = (player.health / player.maxHealth) * 100;
                    healthFillEl.style.width = `${healthPercent}%`;
                    healthTextEl.textContent = `${player.health}/${player.maxHealth}`;
                }
                
                // シールド
                if (player.shields !== undefined && player.maxShields) {
                    const shieldPercent = (player.shields / player.maxShields) * 100;
                    shieldFillEl.style.width = `${shieldPercent}%`;
                    shieldTextEl.textContent = `${player.shields}/${player.maxShields}`;
                } else {
                    shieldFillEl.style.width = '0%';
                    shieldTextEl.textContent = '0/0';
                }
                
                // キルとダメージ
                killsValueEl.textContent = player.kills || 0;
                damageValueEl.textContent = player.damage || 0;
            }
            
            // スクワッド情報の更新
            if (data.squad) {
                const squad = data.squad;
                
                // スクワッドメンバーの表示をクリア
                squadMembersEl.innerHTML = '';
                
                // 各メンバーの情報を表示
                squad.forEach(member => {
                    // 自分自身はスキップ（playerNameElの内容と一致するかチェック）
                    if (member.name === playerNameEl.textContent) {
                        return;
                    }
                    
                    const memberEl = document.createElement('div');
                    memberEl.className = 'squad-member';
                    
                    // HPとシールドの計算
                    const healthPercent = member.maxHealth ? (member.health / member.maxHealth) * 100 : 0;
                    const shieldPercent = member.maxShields ? (member.shields / member.maxShields) * 100 : 0;
                    
                    memberEl.innerHTML = `
                        <div class="name">${member.name || '--'}</div>
                        <div class="legend">${member.legend || '--'}</div>
                        <div class="health-bar">
                            <div class="health-fill" style="width: ${healthPercent}%"></div>
                            <div class="bar-text">${member.health || 0}/${member.maxHealth || 0}</div>
                        </div>
                        <div class="shield-bar">
                            <div class="shield-fill" style="width: ${shieldPercent}%"></div>
                            <div class="bar-text">${member.shields || 0}/${member.maxShields || 0}</div>
                        </div>
                    `;
                    
                    squadMembersEl.appendChild(memberEl);
                });
            }
            
        } catch (e) {
            console.error('JSONパースエラー:', e);
        }
    };
    
    return socket;
}

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', async function() {
    // 設定の読み込みと適用
    const settings = await loadSettings();
    if (settings) {
        applySettings(settings);
    }
    
    // WebSocket接続
    const socket = await connectWebSocket();
    
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
    
    // キーボードショートカット
    document.addEventListener('keydown', function(e) {
        // Alt+Oでオーバーレイの表示/非表示を切り替え
        if (e.altKey && e.key === 'o') {
            if (overlay.style.display === 'none') {
                overlay.style.display = 'block';
            } else {
                overlay.style.display = 'none';
            }
        }
    });
});