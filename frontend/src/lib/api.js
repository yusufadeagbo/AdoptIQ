import axios from 'axios';
import { get } from 'svelte/store';
import { accessToken } from './stores/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
	baseURL: `${API_BASE_URL}/api`,
	headers: {
		'Content-Type': 'application/json'
	}
});

apiClient.interceptors.request.use((config) => {
	const token = get(accessToken);
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

apiClient.interceptors.response.use(
	(response) => response,
	(error) => {
		if (error.response?.status === 401) {
			accessToken.set(null);
			localStorage.removeItem('access_token');
			window.location.href = '/login';
		}
		return Promise.reject(error);
	}
);

export const api = {
	auth: {
		challenge: (walletAddress) =>
			apiClient.post('/auth/challenge/', { wallet_address: walletAddress }),
		verify: (walletAddress, signature, nonce) =>
			apiClient.post('/auth/verify/', { wallet_address: walletAddress, signature, nonce }),
		refresh: (refreshToken) =>
			apiClient.post('/auth/refresh/', { refresh_token: refreshToken }),
		logout: () => apiClient.post('/auth/logout/')
	},

	users: {
		me: () => apiClient.get('/users/me/'),
		updateProfile: (data) => apiClient.put('/users/me/', data),
		stats: () => apiClient.get('/users/me/stats/'),
		achievements: () => apiClient.get('/users/me/achievements/')
	},

	projects: {
		list: () => apiClient.get('/users/projects/'),
		create: (data) => apiClient.post('/users/projects/', data),
		get: (id) => apiClient.get(`/users/projects/${id}/`),
		update: (id, data) => apiClient.put(`/users/projects/${id}/`, data),
		delete: (id) => apiClient.delete(`/users/projects/${id}/`)
	},

	missions: {
		list: (params) => apiClient.get('/missions/', { params }),
		create: (data) => apiClient.post('/missions/', data),
		get: (id) => apiClient.get(`/missions/${id}/`),
		update: (id, data) => apiClient.put(`/missions/${id}/`, data),
		delete: (id) => apiClient.delete(`/missions/${id}/`),
		activate: (id) => apiClient.post(`/missions/${id}/activate/`),
		pause: (id) => apiClient.post(`/missions/${id}/pause/`),
		complete: (id) => apiClient.post(`/missions/${id}/complete/`),
		participants: (id, params) => apiClient.get(`/missions/${id}/participants/`, { params }),
		analytics: (id) => apiClient.get(`/missions/${id}/analytics/`),
		join: (id) => apiClient.post(`/missions/${id}/join/`),
		submitAction: (id, transactionHash) =>
			apiClient.post(`/missions/${id}/submit_action/`, { transaction_hash: transactionHash })
	},

	participations: {
		list: (params) => apiClient.get('/missions/participations/', { params }),
		get: (id) => apiClient.get(`/missions/participations/${id}/`)
	},

	audits: {
		list: (params) => apiClient.get('/audits/', { params }),
		request: (data) => apiClient.post('/audits/', data),
		get: (id) => apiClient.get(`/audits/${id}/`),
		report: (id) => apiClient.get(`/audits/${id}/report/`),
		findings: (id, params) => apiClient.get(`/audits/${id}/findings/`, { params }),
		dispute: (id, findingId, reason) =>
			apiClient.post(`/audits/${id}/dispute/`, { finding_id: findingId, reason })
	},

	billing: {
		subscription: (projectId) =>
			apiClient.get('/billing/subscriptions/my_subscription/', { params: { project_id: projectId } }),
		subscribe: (data) => apiClient.post('/billing/subscriptions/subscribe/', data),
		updatePlan: (id, planTier) =>
			apiClient.put(`/billing/subscriptions/${id}/update_plan/`, { plan_tier: planTier }),
		cancel: (id) => apiClient.post(`/billing/subscriptions/${id}/cancel/`),
		setAllowance: (id, transactionHash) =>
			apiClient.post(`/billing/subscriptions/${id}/set_allowance/`, {
				transaction_hash: transactionHash
			}),
		payments: (params) => apiClient.get('/billing/payments/', { params }),
		invoices: (params) => apiClient.get('/billing/invoices/', { params })
	},

	analytics: {
		dashboard: (range) => apiClient.get('/analytics/dashboard/', { params: { range } }),
		project: (projectId, range) =>
			apiClient.get(`/analytics/project/${projectId}/`, { params: { range } }),
		platform: (range) => apiClient.get('/analytics/platform/', { params: { range } })
	}
};

export default api;
