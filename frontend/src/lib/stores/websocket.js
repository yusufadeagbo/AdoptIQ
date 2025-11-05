import { writable } from 'svelte/store';
import { get } from 'svelte/store';
import { accessToken } from './auth';

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000';

class WebSocketManager {
	constructor() {
		this.connections = new Map();
		this.reconnectIntervals = new Map();
	}

	connect(channel, onMessage) {
		if (this.connections.has(channel)) {
			return this.connections.get(channel);
		}

		const token = get(accessToken);
		const wsUrl = `${WS_BASE_URL}/ws/${channel}/?token=${token}`;

		const ws = new WebSocket(wsUrl);
		const store = writable({ connected: false, data: null });

		ws.onopen = () => {
			console.log(`WebSocket connected: ${channel}`);
			store.update((s) => ({ ...s, connected: true }));

			const heartbeatInterval = setInterval(() => {
				if (ws.readyState === WebSocket.OPEN) {
					ws.send(JSON.stringify({ type: 'ping' }));
				}
			}, 30000);

			ws.heartbeatInterval = heartbeatInterval;
		};

		ws.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				if (data.type !== 'pong') {
					store.update((s) => ({ ...s, data }));
					if (onMessage) {
						onMessage(data);
					}
				}
			} catch (error) {
				console.error('WebSocket message parse error:', error);
			}
		};

		ws.onerror = (error) => {
			console.error(`WebSocket error: ${channel}`, error);
		};

		ws.onclose = () => {
			console.log(`WebSocket closed: ${channel}`);
			store.update((s) => ({ ...s, connected: false }));

			if (ws.heartbeatInterval) {
				clearInterval(ws.heartbeatInterval);
			}

			this.connections.delete(channel);

			const reconnectInterval = setTimeout(() => {
				console.log(`Reconnecting to ${channel}...`);
				this.connect(channel, onMessage);
			}, 5000);

			this.reconnectIntervals.set(channel, reconnectInterval);
		};

		this.connections.set(channel, { ws, store });
		return { ws, store };
	}

	disconnect(channel) {
		const connection = this.connections.get(channel);
		if (connection) {
			connection.ws.close();
			this.connections.delete(channel);
		}

		const reconnectInterval = this.reconnectIntervals.get(channel);
		if (reconnectInterval) {
			clearTimeout(reconnectInterval);
			this.reconnectIntervals.delete(channel);
		}
	}

	disconnectAll() {
		for (const channel of this.connections.keys()) {
			this.disconnect(channel);
		}
	}
}

export const wsManager = new WebSocketManager();

export const connectDashboard = (onMessage) => wsManager.connect('dashboard', onMessage);
export const connectMission = (missionId, onMessage) =>
	wsManager.connect(`missions/${missionId}`, onMessage);
export const connectAudit = (auditId, onMessage) => wsManager.connect(`audits/${auditId}`, onMessage);
