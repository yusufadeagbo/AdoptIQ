<script>
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { user } from '$lib/stores/auth';

	let subscription = null;
	let payments = [];
	let projects = [];
	let selectedProject = null;
	let loading = true;
	let showUpgradeModal = false;

	const plans = {
		starter: {
			name: 'Starter',
			price: 500,
			features: [
				'3 missions per month',
				'1 audit per month',
				'1,000 participants per mission',
				'Basic analytics',
				'Email support'
			]
		},
		growth: {
			name: 'Growth',
			price: 1500,
			features: [
				'10 missions per month',
				'3 audits per month',
				'10,000 participants per mission',
				'Advanced analytics',
				'Priority support',
				'WebSocket real-time updates'
			]
		},
		enterprise: {
			name: 'Enterprise',
			price: 5000,
			features: [
				'Unlimited missions',
				'10 audits per month',
				'Unlimited participants',
				'Custom analytics',
				'24/7 dedicated support',
				'API access',
				'White-label options'
			]
		}
	};

	async function loadBillingData() {
		loading = true;
		try {
			const projectsResponse = await api.projects.list();
			projects = projectsResponse.data.results || projectsResponse.data;

			if (projects.length > 0) {
				selectedProject = projects[0];

				try {
					const subResponse = await api.billing.subscription(selectedProject.id);
					subscription = subResponse.data;

					const paymentsResponse = await api.billing.payments();
					payments = paymentsResponse.data.results || paymentsResponse.data;
				} catch (error) {
					console.log('No subscription found');
				}
			}
		} catch (error) {
			console.error('Failed to load billing data:', error);
		} finally {
			loading = false;
		}
	}

	function getStatusColor(status) {
		const colors = {
			active: 'bg-green-100 text-green-800',
			paused: 'bg-yellow-100 text-yellow-800',
			canceled: 'bg-red-100 text-red-800',
			grace_period: 'bg-orange-100 text-orange-800'
		};
		return colors[status] || 'bg-gray-100 text-gray-800';
	}

	onMount(() => {
		loadBillingData();
	});
</script>

<div>
	<div class="mb-8">
		<h1 class="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
		<p class="text-gray-600 mt-1">Manage your subscription and payment methods</p>
	</div>

	{#if loading}
		<div class="flex items-center justify-center h-64">
			<div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
		</div>
	{:else if !subscription}
		<div class="card text-center py-12 mb-8">
			<div class="text-6xl mb-4">💳</div>
			<h3 class="text-xl font-semibold text-gray-900 mb-2">No active subscription</h3>
			<p class="text-gray-600 mb-6">Choose a plan to get started with AdoptIQ</p>
		</div>

		<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
			{#each Object.entries(plans) as [key, plan]}
				<div class="card hover:shadow-xl transition-shadow {key === 'growth' ? 'border-2 border-primary-600' : ''}">
					{#if key === 'growth'}
						<div class="bg-primary-600 text-white text-sm font-semibold py-1 px-3 rounded-full inline-block mb-4">
							Most Popular
						</div>
					{/if}

					<h3 class="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
					<div class="mb-6">
						<span class="text-4xl font-bold text-gray-900">${plan.price}</span>
						<span class="text-gray-600">/month</span>
					</div>

					<ul class="space-y-3 mb-8">
						{#each plan.features as feature}
							<li class="flex items-start">
								<svg class="w-5 h-5 text-green-500 mr-2 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
									<path
										fill-rule="evenodd"
										d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
										clip-rule="evenodd"
									/>
								</svg>
								<span class="text-gray-700">{feature}</span>
							</li>
						{/each}
					</ul>

					<button class="{key === 'growth' ? 'btn-primary' : 'btn-outline'} w-full">
						Subscribe to {plan.name}
					</button>
				</div>
			{/each}
		</div>
	{:else}
		<div class="card mb-6">
			<div class="flex justify-between items-start">
				<div>
					<h2 class="text-2xl font-bold text-gray-900 mb-2">
						{plans[subscription.plan_tier].name} Plan
					</h2>
					<p class="text-gray-600">
						${subscription.amount_per_cycle} / {subscription.billing_cycle_days} days
					</p>
					<div class="mt-3">
						<span class="badge {getStatusColor(subscription.status)}">
							{subscription.status}
						</span>
					</div>
				</div>

				<div class="text-right">
					<button on:click={() => (showUpgradeModal = true)} class="btn-outline mb-2">
						Upgrade Plan
					</button>
					<p class="text-sm text-gray-600">
						Next billing: {new Date(subscription.next_billing_date).toLocaleDateString()}
					</p>
				</div>
			</div>

			<div class="mt-6 pt-6 border-t border-gray-200">
				<h3 class="font-semibold text-gray-900 mb-3">Current Features</h3>
				<ul class="grid grid-cols-2 gap-3">
					{#each plans[subscription.plan_tier].features as feature}
						<li class="flex items-center text-sm text-gray-700">
							<svg class="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
									clip-rule="evenodd"
								/>
							</svg>
							{feature}
						</li>
					{/each}
				</ul>
			</div>
		</div>

		<div class="card">
			<h2 class="text-xl font-semibold text-gray-900 mb-4">Payment History</h2>

			{#if payments.length === 0}
				<p class="text-gray-600">No payments yet</p>
			{:else}
				<div class="overflow-x-auto">
					<table class="w-full">
						<thead>
							<tr class="border-b border-gray-200">
								<th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">Date</th>
								<th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">Amount</th>
								<th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">Token</th>
								<th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">Status</th>
								<th class="text-left py-3 px-4 text-sm font-semibold text-gray-700">Transaction</th>
							</tr>
						</thead>
						<tbody>
							{#each payments as payment}
								<tr class="border-b border-gray-100">
									<td class="py-3 px-4 text-sm text-gray-900">
										{new Date(payment.billing_date).toLocaleDateString()}
									</td>
									<td class="py-3 px-4 text-sm font-medium text-gray-900">
										{payment.amount}
									</td>
									<td class="py-3 px-4 text-sm text-gray-600">{payment.token}</td>
									<td class="py-3 px-4">
										<span
											class="badge {payment.status === 'confirmed'
												? 'badge-success'
												: payment.status === 'pending'
													? 'badge-warning'
													: 'badge-danger'}"
										>
											{payment.status}
										</span>
									</td>
									<td class="py-3 px-4 text-sm text-gray-600 font-mono">
										{payment.transaction_hash.slice(0, 10)}...
									</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			{/if}
		</div>
	{/if}
</div>
