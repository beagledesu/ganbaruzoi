document.addEventListener('DOMContentLoaded', function() {
    // タブ切り替え
    const navLinks = document.querySelectorAll('.settings-nav a');
    const sections = document.querySelectorAll('.settings-section');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // アクティブなタブとセクションを削除
            navLinks.forEach(l => l.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));
            
            // クリックされたタブとそれに対応するセクションをアクティブに
            this.classList.add('active');
            const targetId = this.getAttribute('href').substring(1);
            document.getElementById(targetId).classList.add('active');
        });
    });
    
    // オパシティスライダーの値表示
    const opacitySlider = document.getElementById('opacity');
    const opacityValue = document.getElementById('opacity-value');
    
    opacitySlider.addEventListener('input', function() {
        opacityValue.textContent = this.value;
    });
    
    // Name Override設定の表示/非表示
    const enableNameOverride = document.getElementById('enable-name-override');
    const nameOverrideSettings = document.getElementById('name-override-settings');
    
    enableNameOverride.addEventListener('change', function() {
        nameOverrideSettings.classList.toggle('hidden', !this.checked);
    });
    
    // 設定の読み込み
    loadSettings();
    
    // 設定保存ボタン
    document.getElementById('save-settings').addEventListener('click', function() {
        saveSettings();
    });
    
    // 名前オーバーライド追加ボタン
    document.getElementById('add-name-override').addEventListener('click', function() {
        addNameOverride();
    });
    
    // プリセット操作ボタン
    document.getElementById('save-preset').addEventListener('click', function() {
        saveNamePreset();
    });
    
    document.getElementById('load-preset').addEventListener('click', function() {
        loadNamePreset();
    });
    
    document.getElementById('delete-preset').addEventListener('click', function() {
        deleteNamePreset();
    });
});

// 設定の読み込み
function loadSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            // 外観設定
            document.getElementById('theme').value = settings.overlay.theme || 'dark';
            document.getElementById('opacity').value = settings.overlay.opacity || 0.8;
            document.getElementById('opacity-value').textContent = settings.overlay.opacity || 0.8;
            document.getElementById('font-size').value = settings.overlay.fontSize || 'medium';
            
            // 表示要素設定
            const showElements = settings.overlay.showElements || {};
            document.getElementById('show-player-info').checked = showElements.playerInfo !== false;
            document.getElementById('show-squad-info').checked = showElements.squadInfo !== false;
            document.getElementById('show-game-state').checked = showElements.gameState !== false;
            document.getElementById('show-kills').checked = showElements.kills !== false;
            document.getElementById('show-damage').checked = showElements.damage !== false;
            
            // 色設定
            const colors = settings.overlay.colors || {};
            document.getElementById('background-color-text').value = colors.background || 'rgba(0, 0, 0, 0.7)';
            document.getElementById('text-color-text').value = colors.text || '#ffffff';
            document.getElementById('health-color-text').value = colors.health || '#2ecc71';
            document.getElementById('shield-color-text').value = colors.shield || '#3498db';
            document.getElementById('accent-color-text').value = colors.accent || '#f39c12';
            
            // カラーピッカーの更新
            updateColorPickers();
            
            // 接続設定
            document.getElementById('websocket-host').value = settings.websocket?.host || 'localhost';
            document.getElementById('websocket-port').value = settings.websocket?.port || 7777;
            document.getElementById('http-host').value = settings.http?.host || 'localhost';
            document.getElementById('http-port').value = settings.http?.port || 8080;
            
            // Name Override設定
            const nameOverride = settings.nameOverride || {};
            document.getElementById('enable-name-override').checked = nameOverride.enabled || false;
            document.getElementById('name-override-settings').classList.toggle('hidden', !nameOverride.enabled);
            
            // プリセットの読み込み
            loadNamePresets(nameOverride.presets || {});
        })
        .catch(error => {
            console.error('設定の読み込みに失敗しました:', error);
            alert('設定の読み込みに失敗しました。');
        });
}

// 色設定の更新
function updateColorPickers() {
    // カラーピッカーの値をテキストフィールドから更新
    updateColorPicker('background-color', 'background-color-text');
    updateColorPicker('text-color', 'text-color-text');
    updateColorPicker('health-color', 'health-color-text');
    updateColorPicker('shield-color', 'shield-color-text');
    updateColorPicker('accent-color', 'accent-color-text');
}

// カラーピッカーの更新
function updateColorPicker(colorPickerId, textFieldId) {
    const textField = document.getElementById(textFieldId);
    const colorPicker = document.getElementById(colorPickerId);
    
    // RGBAから16進数形式に変換
    const rgbaValue = textField.value;
    if (rgbaValue.startsWith('rgba')) {
        // RGBAの場合は16進数に近似変換
        const rgba = rgbaValue.match(/rgba\((\d+),\s*(\d+),\s*(\d+),\s*([0-9.]+)\)/);
        if (rgba) {
            const [, r, g, b] = rgba;
            colorPicker.value = rgbToHex(parseInt(r), parseInt(g), parseInt(b));
        }
    } else {
        // 既に16進数の場合はそのまま設定
        colorPicker.value = rgbaValue;
    }
    
    // カラーピッカーの変更イベント
    colorPicker.addEventListener('input', function() {
        textField.value = this.value;
    });
}

// RGB値を16進数形式に変換
function rgbToHex(r, g, b) {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

// 設定の保存
function saveSettings() {
    // 設定オブジェクトの作成
    const settings = {
        overlay: {
            theme: document.getElementById('theme').value,
            opacity: parseFloat(document.getElementById('opacity').value),
            fontSize: document.getElementById('font-size').value,
            showElements: {
                playerInfo: document.getElementById('show-player-info').checked,
                squadInfo: document.getElementById('show-squad-info').checked,
                gameState: document.getElementById('show-game-state').checked,
                kills: document.getElementById('show-kills').checked,
                damage: document.getElementById('show-damage').checked
            },
            colors: {
                background: document.getElementById('background-color-text').value,
                text: document.getElementById('text-color-text').value,
                health: document.getElementById('health-color-text').value,
                shield: document.getElementById('shield-color-text').value,
                accent: document.getElementById('accent-color-text').value
            }
        },
        websocket: {
            host: document.getElementById('websocket-host').value,
            port: parseInt(document.getElementById('websocket-port').value)
        },
        http: {
            host: document.getElementById('http-host').value,
            port: parseInt(document.getElementById('http-port').value)
        },
        nameOverride: {
            enabled: document.getElementById('enable-name-override').checked,
            // プリセットは別で管理するので保存時は変更しない
        }
    };
    
    // サーバーに設定を送信
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings)
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert('設定を保存しました。変更を適用するにはページを再読み込みしてください。');
        } else {
            alert('設定の保存に失敗しました: ' + result.message);
        }
    })
    .catch(error => {
        console.error('設定の保存に失敗しました:', error);
        alert('設定の保存に失敗しました。');
    });
}

// 名前オーバーライドの表示
function loadNameOverrides(overrides = {}) {
    const listContainer = document.getElementById('name-override-list');
    listContainer.innerHTML = '';
    
    Object.entries(overrides).forEach(([id, name]) => {
        const item = document.createElement('div');
        item.className = 'name-override-item';
        item.innerHTML = `
            <div class="id">${id}</div>
            <div class="name">${name}</div>
            <button class="delete" data-id="${id}">&times;</button>
        `;
        
        item.querySelector('.delete').addEventListener('click', function() {
            deleteNameOverride(this.getAttribute('data-id'));
        });
        
        listContainer.appendChild(item);
    });
}

// 名前オーバーライドの追加
function addNameOverride() {
    const playerId = document.getElementById('player-id').value.trim();
    const displayName = document.getElementById('display-name').value.trim();
    
    if (!playerId || !displayName) {
        alert('プレイヤーIDと表示名を入力してください。');
        return;
    }
    
    fetch('/api/name-override/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            playerId: playerId,
            displayName: displayName
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // 入力フィールドをクリア
            document.getElementById('player-id').value = '';
            document.getElementById('display-name').value = '';
            
            // 名前オーバーライドリストを更新
            loadNameOverrides(result.overrides);
        } else {
            alert('名前オーバーライドの追加に失敗しました: ' + result.message);
        }
    })
    .catch(error => {
        console.error('名前オーバーライドの追加に失敗しました:', error);
        alert('名前オーバーライドの追加に失敗しました。');
    });
}

// 名前オーバーライドの削除
function deleteNameOverride(playerId) {
    fetch('/api/name-override/remove', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            playerId: playerId
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            // 名前オーバーライドリストを更新
            loadNameOverrides(result.overrides);
        } else {
            alert('名前オーバーライドの削除に失敗しました: ' + result.message);
        }
    })
    .catch(error => {
        console.error('名前オーバーライドの削除に失敗しました:', error);
        alert('名前オーバーライドの削除に失敗しました。');
    });
}

// 名前プリセットの読み込み
function loadNamePresets(presets = {}) {
    const presetSelect = document.getElementById('preset-select');
    presetSelect.innerHTML = '<option value="">-- 選択 --</option>';
    
    Object.keys(presets).forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name;
        presetSelect.appendChild(option);
    });
}

// 名前プリセットの保存
function saveNamePreset() {
    const presetName = document.getElementById('preset-name').value.trim();
    
    if (!presetName) {
        alert('プリセット名を入力してください。');
        return;
    }
    
    fetch('/api/name-override/get-all')
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                return fetch('/api/name-override/save-preset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        presetName: presetName,
                        overrides: result.overrides
                    })
                });
            } else {
                throw new Error('現在の名前オーバーライドの取得に失敗しました: ' + result.message);
            }
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert(`プリセット "${presetName}" を保存しました。`);
                loadNamePresets(result.presets);
                document.getElementById('preset-name').value = '';
            } else {
                alert('プリセットの保存に失敗しました: ' + result.message);
            }
        })
        .catch(error => {
            console.error('プリセットの保存に失敗しました:', error);
            alert('プリセットの保存に失敗しました。');
        });
}

// 名前プリセットの読み込み
function loadNamePreset() {
    const presetName = document.getElementById('preset-select').value;
    
    if (!presetName) {
        alert('プリセットを選択してください。');
        return;
    }
    
    fetch('/api/name-override/load-preset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            presetName: presetName
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert(`プリセット "${presetName}" を読み込みました。`);
            loadNameOverrides(result.overrides);
        } else {
            alert('プリセットの読み込みに失敗しました: ' + result.message);
        }
    })
    .catch(error => {
        console.error('プリセットの読み込みに失敗しました:', error);
        alert('プリセットの読み込みに失敗しました。');
    });
}

// 名前プリセットの削除
function deleteNamePreset() {
    const presetName = document.getElementById('preset-select').value;
    
    if (!presetName) {
        alert('プリセットを選択してください。');
        return;
    }
    
    if (!confirm(`プリセット "${presetName}" を削除してもよろしいですか？`)) {
        return;
    }
    
    fetch('/api/name-override/delete-preset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            presetName: presetName
        })
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert(`プリセット "${presetName}" を削除しました。`);
            loadNamePresets(result.presets);
            document.getElementById('preset-select').value = '';
        } else {
            alert('プリセットの削除に失敗しました: ' + result.message);
        }
    })
    .catch(error => {
        console.error('プリセットの削除に失敗しました:', error);
        alert('プリセットの削除に失敗しました。');
    });
}