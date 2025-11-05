import { writable } from 'svelte/store';

export const walletAddress = writable(null);
export const walletConnected = writable(false);
export const chainId = writable(null);
export const provider = writable(null);
export const signer = writable(null);

export const connectWallet = async () => {
	if (typeof window.ethereum === 'undefined') {
		throw new Error('MetaMask not installed');
	}

	try {
		const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
		const account = accounts[0];

		walletAddress.set(account);
		walletConnected.set(true);

		const chainIdHex = await window.ethereum.request({ method: 'eth_chainId' });
		chainId.set(parseInt(chainIdHex, 16));

		window.ethereum.on('accountsChanged', (accounts) => {
			if (accounts.length > 0) {
				walletAddress.set(accounts[0]);
			} else {
				disconnectWallet();
			}
		});

		window.ethereum.on('chainChanged', (chainIdHex) => {
			chainId.set(parseInt(chainIdHex, 16));
		});

		return account;
	} catch (error) {
		console.error('Error connecting wallet:', error);
		throw error;
	}
};

export const disconnectWallet = () => {
	walletAddress.set(null);
	walletConnected.set(false);
	chainId.set(null);
};

export const signMessage = async (message) => {
	if (typeof window.ethereum === 'undefined') {
		throw new Error('MetaMask not installed');
	}

	const accounts = await window.ethereum.request({ method: 'eth_accounts' });
	if (accounts.length === 0) {
		throw new Error('No wallet connected');
	}

	const signature = await window.ethereum.request({
		method: 'personal_sign',
		params: [message, accounts[0]]
	});

	return signature;
};

export const switchChain = async (targetChainId) => {
	if (typeof window.ethereum === 'undefined') {
		throw new Error('MetaMask not installed');
	}

	const chainIdHex = `0x${targetChainId.toString(16)}`;

	try {
		await window.ethereum.request({
			method: 'wallet_switchEthereumChain',
			params: [{ chainId: chainIdHex }]
		});
	} catch (error) {
		if (error.code === 4902) {
			throw new Error('Chain not added to MetaMask');
		}
		throw error;
	}
};
