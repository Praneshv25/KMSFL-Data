import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const res = await fetch(`${API_BASE}/records`);
        const data = await res.json();
        return { records: data.records };
    } catch (error) {
        console.error('Failed to load records:', error);
        return { records: [] };
    }
};
