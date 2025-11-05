<script>
	import '../app.css';
	import { isAuthenticated } from '$lib/stores/auth';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	let showSidebar = true;

	const navItems = [
		{ name: 'Dashboard', path: '/dashboard', icon: '📊' },
		{ name: 'Missions', path: '/missions', icon: '🎯' },
		{ name: 'Audits', path: '/audits', icon: '🔒' },
		{ name: 'Billing', path: '/billing', icon: '💳' },
		{ name: 'Profile', path: '/profile', icon: '👤' }
	];

	onMount(() => {
		if (!$isAuthenticated && !$page.url.pathname.includes('/login')) {
			goto('/login');
		}
	});
</script>

<div class="min-h-screen bg-gray-50">
	{#if $isAuthenticated}
		<nav class="bg-white border-b border-gray-200 fixed w-full z-30 top-0">
			<div class="px-6 py-4">
				<div class="flex items-center justify-between">
					<div class="flex items-center space-x-8">
						<button on:click={() => (showSidebar = !showSidebar)} class="text-gray-500 hover:text-gray-700">
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 6h16M4 12h16M4 18h16"
								/>
							</svg>
						</button>
						<h1 class="text-2xl font-bold text-primary-600">AdoptIQ</h1>
					</div>

					<div class="flex items-center space-x-4">
						<button class="text-gray-500 hover:text-gray-700">
							<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
								/>
							</svg>
						</button>
					</div>
				</div>
			</div>
		</nav>

		<div class="pt-16 flex">
			{#if showSidebar}
				<aside class="w-64 bg-white border-r border-gray-200 fixed h-full overflow-y-auto">
					<nav class="p-4 space-y-2">
						{#each navItems as item}
							<a
								href={item.path}
								class="flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors {$page.url
									.pathname === item.path
									? 'bg-primary-50 text-primary-600'
									: 'text-gray-700 hover:bg-gray-100'}"
							>
								<span class="text-xl">{item.icon}</span>
								<span class="font-medium">{item.name}</span>
							</a>
						{/each}
					</nav>
				</aside>
			{/if}

			<main class="{showSidebar ? 'ml-64' : 'ml-0'} flex-1 p-8">
				<slot />
			</main>
		</div>
	{:else}
		<slot />
	{/if}
</div>
