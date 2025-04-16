/**
 * WebSocket接続を管理するモジュール
 */
class WebSocketManager {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000; // ms
        this.eventHandlers = {
            'message': [],
            'connect': [],
            'disconnect': [],
            'error': []
        };
    }

    /**
     * WebSocketサーバーに接続
     */
    connect() {
        this.socket = new WebSocket(this.url);
        
        this.socket.onopen = () => {
            console.log('WebSocketサーバーに接続しました');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this._triggerEvent('connect');
        };
        
        this.socket.onclose = (event) => {
            console.log('WebSocket接続が閉じられました', event);
            this.isConnected = false;
            this._triggerEvent('disconnect');
            this._attemptReconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocketエラー:', error);
            this._triggerEvent('error', error);
        };
        
        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this._triggerEvent('message', data);
            } catch (error) {
                console.error('メッセージの解析に失敗しました:', error);
            }
        };
    }

    /**
     * イベントリスナーを追加
     */
    on(event, callback) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].push(callback);
        }
        return this;
    }

    /**
     * サーバーにメッセージを送信
     */
    send(data) {
        if (this.isConnected && this.socket) {
            this.socket.send(typeof data === 'string' ? data : JSON.stringify(data));
        } else {
            console.warn('WebSocketが接続されていません。メッセージを送信できません。');
        }
    }

    /**
     * 接続を閉じる
     */
    disconnect() {
        if (this.socket) {
            this.socket.close();
        }
    }

    /**
     * 再接続を試みる
     */
    _attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`${this.reconnectDelay / 1000}秒後に再接続を試みます... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            
            setTimeout(() => {
                console.log('再接続を試みています...');
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error('最大再接続試行回数に達しました。手動での再接続が必要です。');
        }
    }

    /**
     * イベントハンドラーを実行
     */
    _triggerEvent(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(callback => callback(data));
        }
    }
}

// WebSocketマネージャーのインスタンスを作成
const wsManager = new WebSocketManager('ws://localhost:8765');