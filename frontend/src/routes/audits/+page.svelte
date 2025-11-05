<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let audits = [];
	let loading = true;
	let statusFilter = '';

	async function loadAudits() {
		loading = true;
		try {
			const params = {};
			if (statusFilter) params.status = statusFilter;

			const response = await api.audits.list(params);
			audits = response.data.results || response.data;
		} catch (error) {
			console.error('Failed to load audits:', error);
		} finally {
			loading = false;
		}
	}

	function getStatusColor(status) {
		const colors = {
			pending: 'bg-yellow-100 text-yellow-800',
			analyzing: 'bg-blue-100 text-blue-800',
			generating: 'bg-purple-100 text-purple-800',
			completed: 'bg-green-100 text-green-800',
			failed: 'bg-red-100 text-red-800'
		};
		return colors[status] || 'bg-gray-100 text-gray-800';
	}

	function getRiskColor(risk) {
		const colors = {
			low: 'text-green-600',
			medium: 'text-yellow-600',
			high: 'text-orange-600',
			critical: 'text-red-600'
		};
		return colors[risk] || 'text-gray-600';
	}

	onMount(() => {
		loadAudits();
	});
</script>

<div>
	<div class="flex justify-between items-center mb-8">
		<div>
			<h1 class="text-3xl font-bold text-gray-900">Smart Contract Audits</h1>
			<p class="text-gray-600 mt-1">Request and manage security audits</p>
		</div>

		<button on:click={() => goto('/audits/request')} class="btn-primary">
			<svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 4v16m8-8H4"
				/>
			</svg>
			Request Audit
		</button>
	</div>

	<div class="card mb-6">
		<div class="flex items-center space-x-4">
			<label class="label">Status Filter:</label>
			<select bind:value={statusFilter} on:change={loadAudits} class="input w-auto">
				<option value="">All Statuses</option>
				<option value="pending">Pending</option>
				<option value="analyzing">Analyzing</option>
				<option value="generating">Generating</option>
				<option value="completed">Completed</option>
				<option value="failed">Failed</option>
			</select>
		</div>
	</div>

	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
		</div>
	{:else if audits.length === 0}
		<div class="card text-center py-12">
			<div class="text-6xl mb-4">🔒</div>
			<h3 class="text-xl font-semibold text-gray-900 mb-2">No audits yet</h3>
			<p class="text-gray-600 mb-6">Request your first smart contract audit</p>
			<button on:click={() => goto('/audits/request')} class="btn-primary">Request Audit</button>
		</div>
	{:else}
		<div class="space-y-4">
			{#each audits as audit}
				<div class="card hover:shadow-lg transition-shadow cursor-pointer" on:click={() => goto(`/audits/${audit.id}`)}>
					<div class="flex items-start justify-between">
						<div class="flex-1">
							<div class="flex items-center space-x-3 mb-2">
								<h3 class="text-lg font-semibold text-gray-900">
									{audit.contract_address.slice(0, 10)}...{audit.contract_address.slice(-8)}
								</h3>
								<span class="badge {getStatusColor(audit.status)}">
									{audit.status}
								</span>
								{#if audit.overall_risk}
									<span class="text-sm font-medium {getRiskColor(audit.overall_risk)}">
										{audit.overall_risk.toUpperCase()} RISK
									</span>
								{/if}
							</div>

							<p class="text-sm text-gray-500 mb-3">
								{audit.project_details?.name || 'Unknown Project'} • {audit.contract_chain}
							</p>

							{#if audit.status === 'completed'}
								<div class="grid grid-cols-5 gap-4">
									<div class="text-center">
										<div class="text-2xl font-bold text-gray-900">{audit.findings_count}</div>
										<div class="text-xs text-gray-600">Total</div>
									</div>
									<div class="text-center">
										<div class="text-2xl font-bold text-red-600">{audit.critical_count}</div>
										<div class="text-xs text-gray-600">Critical</div>
									</div>
									<div class="text-center">
										<div class="text-2xl font-bold text-orange-600">{audit.high_count}</div>
										<div class="text-xs text-gray-600">High</div>
									</div>
									<div class="text-center">
										<div class="text-2xl font-bold text-yellow-600">{audit.medium_count}</div>
										<div class="text-xs text-gray-600">Medium</div>
									</div>
									<div class="text-center">
										<div class="text-2xl font-bold text-blue-600">{audit.low_count}</div>
										<div class="text-xs text-gray-600">Low</div>
									</div>
								</div>
							{/if}
						</div>

						<div class="text-right">
							<div class="text-sm text-gray-600">
								{new Date(audit.created_at).toLocaleDateString()}
							</div>
							{#if audit.price}
								<div class="text-lg font-semibold text-gray-900 mt-1">
									${audit.price}
								</div>
							{/if}
						</div>
					</div>
				</div>
			{/each}
		</div>
	{/if}
</div>
