<script>
	import { connectWallet, signMessage } from '$lib/stores/wallet';
	import { accessToken, user, isAuthenticated } from '$lib/stores/auth';
	import { api } from '$lib/api';
	import { goto } from '$app/navigation';

	let loading = false;
	let error = null;

	async function handleWalletConnect() {
		loading = true;
		error = null;

		try {
			const walletAddress = await connectWallet();

			const challengeResponse = await api.auth.challenge(walletAddress);
			const { message, nonce } = challengeResponse.data;

			const signature = await signMessage(message);

			const verifyResponse = await api.auth.verify(walletAddress, signature, nonce);
			const { access_token, refresh_token, user: userData } = verifyResponse.data;

			accessToken.set(access_token);
			user.set(userData);
			isAuthenticated.set(true);

			localStorage.setItem('refresh_token', refresh_token);

			goto('/dashboard');
		} catch (err) {
			console.error('Authentication error:', err);
			error = err.response?.data?.error || err.message || 'Failed to connect wallet';
		} finally {
			loading = false;
		}
	}
</script>

<div class="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
	<div class="card max-w-md w-full">
		<div class="text-center mb-8">
			<h1 class="text-4xl font-bold text-primary-600 mb-2">AdoptIQ</h1>
			<p class="text-gray-600">Connect your wallet to get started</p>
		</div>

		{#if error}
			<div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
				{error}
			</div>
		{/if}

		<button
			on:click={handleWalletConnect}
			disabled={loading}
			class="btn-primary w-full text-lg py-4"
		>
			{#if loading}
				<div class="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
				Connecting...
			{:else}
				<svg class="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 24 24">
					<path
						d="M20.5 5.5H19V4c0-1.1-.9-2-2-2H3c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h1.5v1.5c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-12c0-1.1-.9-2-2-2zM3 16V4h14v12H3zm17.5 5.5h-14V18H17c1.1 0 2-.9 2-2V7.5h1.5v14z"
					/>
				</svg>
				Connect Wallet
			{/if}
		</button>

		<p class="mt-6 text-sm text-gray-500 text-center">
			By connecting, you agree to AdoptIQ's Terms of Service and Privacy Policy
		</p>
	</div>
</div>
