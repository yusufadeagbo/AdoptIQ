<script>
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { isAuthenticated } from '$lib/stores/auth';

	onMount(() => {
		if ($isAuthenticated) {
			goto('/dashboard');
		} else {
			goto('/login');
		}
	});
</script>

<div class="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center">
	<div class="text-center">
		<div class="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
		<p class="mt-4 text-gray-600">Loading AdoptIQ...</p>
	</div>
</div>
