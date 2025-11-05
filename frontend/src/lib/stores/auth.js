import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const storedToken = browser ? localStorage.getItem('access_token') : null;
const storedUser = browser ? JSON.parse(localStorage.getItem('user') || 'null') : null;

export const accessToken = writable(storedToken);
export const user = writable(storedUser);
export const isAuthenticated = writable(!!storedToken);

if (browser) {
	accessToken.subscribe((value) => {
		if (value) {
			localStorage.setItem('access_token', value);
			isAuthenticated.set(true);
		} else {
			localStorage.removeItem('access_token');
			isAuthenticated.set(false);
		}
	});

	user.subscribe((value) => {
		if (value) {
			localStorage.setItem('user', JSON.stringify(value));
		} else {
			localStorage.removeItem('user');
		}
	});
}

export const logout = () => {
	accessToken.set(null);
	user.set(null);
	if (browser) {
		localStorage.clear();
	}
};
