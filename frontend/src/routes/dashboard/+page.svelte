<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { connectDashboard } from '$lib/stores/websocket';

	let stats = null;
	let loading = true;
	let timeRange = '30d';

	async function loadDashboard() {
		loading = true;
		try {
			const response = await api.analytics.dashboard(timeRange);
			stats = response.data;
		} catch (error) {
			console.error('Failed to load dashboard:', error);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadDashboard();

		const { store } = connectDashboard((data) => {
			console.log('Dashboard update:', data);
			loadDashboard();
		});
	});
</script>

<div>
	<div class="flex justify-between items-center mb-8">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
			<p class="text-gray-600 mt-1">Welcome back! Here's your overview.</p>
		</div>

		<select bind:value={timeRange} on:change={loadDashboard} class="input w-auto">
			<option value="7d">Last 7 days</option>
			<option value="30d">Last 30 days</option>
			<option value="90d">Last 90 days</option>
		</select>
	</div>

	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
		</div>
	{:else if stats}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-600 text-sm">Total Projects</p>
						<p class="text-3xl font-bold text-gray-900 mt-1">
							{stats.overview.total_projects}
						</p>
					</div>
					<div class="bg-primary-100 p-3 rounded-lg">
						<span class="text-2xl">📁</span>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-600 text-sm">Active Missions</p>
						<p class="text-3xl font-bold text-gray-900 mt-1">
							{stats.overview.active_missions}
						</p>
					</div>
					<div class="bg-green-100 p-3 rounded-lg">
						<span class="text-2xl">🎯</span>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-600 text-sm">Total Participants</p>
						<p class="text-3xl font-bold text-gray-900 mt-1">
							{stats.overview.total_participants.toLocaleString()}
						</p>
					</div>
					<div class="bg-blue-100 p-3 rounded-lg">
						<span class="text-2xl">👥</span>
					</div>
				</div>
			</div>

			<div class="card">
				<div class="flex items-center justify-between">
					<div>
						<p class="text-gray-600 text-sm">Completed Audits</p>
						<p class="text-3xl font-bold text-gray-900 mt-1">
							{stats.overview.completed_audits}
						</p>
					</div>
					<div class="bg-purple-100 p-3 rounded-lg">
						<span class="text-2xl">🔒</span>
					</div>
				</div>
			</div>
		</div>

		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			<div class="card">
				<h2 class="text-xl font-semibold mb-4">Mission Performance</h2>
				<div class="space-y-4">
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Total Missions</span>
						<span class="font-semibold">{stats.missions.total_missions}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Active</span>
						<span class="badge-success">{stats.missions.active_missions}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Completed</span>
						<span class="badge-info">{stats.missions.completed_missions}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Avg Completion Rate</span>
						<span class="font-semibold">{stats.missions.avg_completion_rate}%</span>
					</div>
				</div>
			</div>

			<div class="card">
				<h2 class="text-xl font-semibold mb-4">Audit Summary</h2>
				<div class="space-y-4">
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Total Audits</span>
						<span class="font-semibold">{stats.audits.total_audits}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Completed</span>
						<span class="badge-success">{stats.audits.completed_audits}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Pending</span>
						<span class="badge-warning">{stats.audits.pending_audits}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Total Findings</span>
						<span class="font-semibold">{stats.audits.total_findings}</span>
					</div>
					<div class="flex justify-between items-center">
						<span class="text-gray-600">Critical Findings</span>
						<span class="badge-danger">{stats.audits.critical_findings}</span>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
