import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const res = await fetch(`${API_BASE}/champions`);
        const data = await res.json();
        return { champions: data.champions };
    } catch (error) {
        console.error('Failed to load champions:', error);
        return { champions: [] };
    }
};
