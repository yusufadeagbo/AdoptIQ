<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let missions = [];
	let loading = true;
	let statusFilter = '';
	let categoryFilter = '';

	async function loadMissions() {
		loading = true;
		try {
			const params = {};
			if (statusFilter) params.status = statusFilter;
			if (categoryFilter) params.category = categoryFilter;

			const response = await api.missions.list(params);
			missions = response.data.results || response.data;
		} catch (error) {
			console.error('Failed to load missions:', error);
		} finally {
			loading = false;
		}
	}

	function getStatusColor(status) {
		const colors = {
			active: 'bg-green-100 text-green-800',
			draft: 'bg-gray-100 text-gray-800',
			completed: 'bg-blue-100 text-blue-800',
			paused: 'bg-yellow-100 text-yellow-800'
		};
		return colors[status] || 'bg-gray-100 text-gray-800';
	}

	onMount(() => {
		loadMissions();
	});
</script>

<div>
	<div class="flex justify-between items-center mb-8">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Missions</h1>
			<p class="text-gray-600 mt-1">Manage your adoption campaigns</p>
		</div>

		<button on:click={() => goto('/missions/create')} class="btn-primary">
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 4v16m8-8H4"
				/>
			</svg>
			Create Mission
		</button>
	</div>

	<div class="card mb-6">
		<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
			<div>
				<label class="label">Status</label>
				<select bind:value={statusFilter} on:change={loadMissions} class="input">
					<option value="">All Statuses</option>
					<option value="active">Active</option>
					<option value="draft">Draft</option>
					<option value="completed">Completed</option>
					<option value="paused">Paused</option>
				</select>
			</div>

			<div>
				<label class="label">Category</label>
				<select bind:value={categoryFilter} on:change={loadMissions} class="input">
					<option value="">All Categories</option>
					<option value="nft_mint">NFT Minting</option>
					<option value="token_liquidity">Token Liquidity</option>
					<option value="staking">Staking</option>
					<option value="trading_volume">Trading Volume</option>
				</select>
			</div>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
		</div>
	{:else if missions.length === 0}
		<div class="card text-center py-12">
			<div class="text-6xl mb-4">🎯</div>
			<h3 class="text-xl font-semibold text-gray-900 mb-2">No missions yet</h3>
			<p class="text-gray-600 mb-6">Create your first mission to start driving adoption</p>
			<button on:click={() => goto('/missions/create')} class="btn-primary">Create Mission</button>
		</div>
	{:else}
		<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
			{#each missions as mission}
				<div class="card hover:shadow-lg transition-shadow cursor-pointer" on:click={() => goto(`/missions/${mission.id}`)}>
					<div class="flex justify-between items-start mb-4">
						<div>
							<h3 class="text-lg font-semibold text-gray-900">{mission.name}</h3>
							<p class="text-sm text-gray-500 mt-1">
								{mission.project_details?.name || 'Unknown Project'}
							</p>
						</div>
						<span class="badge {getStatusColor(mission.status)}">
							{mission.status}
						</span>
					</div>

					<p class="text-gray-600 mb-4 line-clamp-2">{mission.description}</p>

					<div class="space-y-2">
						<div class="flex justify-between text-sm">
							<span class="text-gray-600">Progress</span>
							<span class="font-medium">
								{mission.current_participants} / {mission.target_participants}
							</span>
						</div>
						<div class="w-full bg-gray-200 rounded-full h-2">
							<div
								class="bg-primary-600 h-2 rounded-full transition-all"
								style="width: {mission.progress_percentage}%"
							></div>
						</div>
					</div>

					<div class="mt-4 flex items-center justify-between text-sm">
						<span class="text-gray-600">
							{new Date(mission.start_date).toLocaleDateString()} - {new Date(mission.end_date).toLocaleDateString()}
						</span>
						<span class="badge-info">{mission.category.replace('_', ' ')}</span>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
