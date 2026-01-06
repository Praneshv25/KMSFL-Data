import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const res = await fetch(`${API_BASE}/managers`);
        const data = await res.json();
        return { managers: data.managers };
    } catch (error) {
        console.error('Failed to load managers:', error);
        return { managers: [] };
    }
};
