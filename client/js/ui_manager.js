/**
 * UI更新を管理するモジュール
 */
class UIManager {
    constructor() {
        // DOM要素の参照
        this.overlayContainer = document.getElementById('overlay-container');
        this.gameStateElement = document.getElementById('game-state');
        this.matchStateElement = document.getElementById('match-state');
        this.remainingSquadsElement = document.getElementById('remaining-squads');
        this.playerInfoElement = document.getElementById('player-info');
        this.squadContainerElement = document.getElementById('squad-container');
        
        // ドラッグ機能のセットアップ
        this._setupDraggable();
    }

    /**
     * ゲーム状態の更新
     */
    updateGameState(gameState, match) {
        if (match.inProgress) {
            this.matchStateElement.textContent = 'マッチ中';
            this.remainingSquadsElement.textContent = `残りスクワッド: ${match.remainingSquads}`;
            this.remainingSquadsElement.style.display = 'inline';
        } else {
            this.matchStateElement.textContent = 'マッチ外';
            this.remainingSquadsElement.style.display = 'none';
        }
        
        // マッチ終了時のハイライト表示
        if (match.squadEliminated) {
            this.matchStateElement.textContent = 'スクワッド敗退';
            this.matchStateElement.style.color = '#e74c3c';
        } else {
            this.matchStateElement.style.color = '';
        }
    }

    /**
     * プレイヤー情報の更新
     */
    updatePlayerInfo(player) {
        if (!player) return;
        
        const healthPercent = player.maxHealth > 0 
            ? (player.health / player.maxHealth) * 100 
            : 0;
        
        const shieldPercent = player.maxShields > 0 
            ? (player.shields / player.maxShields) * 100 
            : 0;
        
        this.playerInfoElement.innerHTML = `
            <div class="player-name">${player.name || 'Unknown'}</div>
            <div class="legend-name">${player.legend || ''}</div>
            
            <div class="health-status">
                HP: ${player.health}/${player.maxHealth}
                <div class="health-bar">
                    <div class="health-bar-inner" style="width: ${healthPercent}%"></div>
                </div>
            </div>
            
            <div class="shield-status">
                シールド: ${player.shields}/${player.maxShields}
                <div class="shield-bar">
                    <div class="shield-bar-inner" style="width: ${shieldPercent}%"></div>
                </div>
            </div>
            
            <div class="player-stats">
                <div>キル: ${player.kills}</div>
                <div>ダメージ: ${player.damage}</div>
            </div>
        `;
    }

    /**
     * スクワッド情報の更新
     */
    updateSquadInfo(squad) {
        if (!squad || !Array.isArray(squad) || squad.length === 0) {
            this.squadContainerElement.innerHTML = '';
            return;
        }
        
        this.squadContainerElement.innerHTML = '';
        
        squad.forEach(member => {
            // 自分自身は表示しない
            if (member.name === document.querySelector('.player-name')?.textContent) {
                return;
            }
            
            const healthPercent = member.maxHealth > 0 
                ? (member.health / member.maxHealth) * 100 
                : 0;
            
            const shieldPercent = member.maxShields > 0 
                ? (member.shields / member.maxShields) * 100 
                : 0;
            
            const memberElement = document.createElement('div');
            memberElement.className = 'squad-member';
            memberElement.innerHTML = `
                <div class="player-name">${member.name || 'Unknown'}</div>
                <div class="legend-name">${member.legend || ''}</div>
                
                <div class="health-status">
                    <div class="health-bar">
                        <div class="health-bar-inner" style="width: ${healthPercent}%"></div>
                    </div>
                </div>
                
                <div class="shield-status">
                    <div class="shield-bar">
                        <div class="shield-bar-inner" style="width: ${shieldPercent}%"></div>
                    </div>
                </div>
            `;
            
            this.squadContainerElement.appendChild(memberElement);
        });
    }

    /**
     * オーバーレイをドラッグ可能にする
     */
    _setupDraggable() {
        let isDragging = false;
        let offsetX, offsetY;
        
        this.overlayContainer.addEventListener('mousedown', (e) => {
            isDragging = true;
            offsetX = e.clientX - this.overlayContainer.getBoundingClientRect().left;
            offsetY = e.clientY - this.overlayContainer.getBoundingClientRect().top;
            this.overlayContainer.style.cursor = 'grabbing';
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            const x = e.clientX - offsetX;
            const y = e.clientY - offsetY;
            
            this.overlayContainer.style.left = `${x}px`;
            this.overlayContainer.style.top = `${y}px`;
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
            this.overlayContainer.style.cursor = 'grab';
        });
        
        this.overlayContainer.style.cursor = 'grab';
    }
}

// UIマネージャーのインスタンスを作成
const uiManager = new UIManager();