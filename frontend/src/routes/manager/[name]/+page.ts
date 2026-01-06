import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch, params }) => {
    try {
        const res = await fetch(`${API_BASE}/manager/${encodeURIComponent(params.name)}`);

        if (!res.ok) {
            return { manager: null, error: 'Manager not found' };
        }

        const data = await res.json();
        return { manager: data, error: null };
    } catch (error) {
        console.error('Failed to load manager:', error);
        return { manager: null, error: 'Failed to load manager data' };
    }
};
