import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch, params }) => {
    try {
        const [managerRes, rivalriesRes, weeklyRes] = await Promise.all([
            fetch(`${API_BASE}/manager/${encodeURIComponent(params.name)}`),
            fetch(`${API_BASE}/rivalries/${encodeURIComponent(params.name)}`),
            fetch(`${API_BASE}/weekly-results/${encodeURIComponent(params.name)}`)
        ]);

        if (!managerRes.ok) {
            return { manager: null, rivalries: [], weeklyResults: [], error: 'Manager not found' };
        }

        const manager = await managerRes.json();
        const rivalries = rivalriesRes.ok ? (await rivalriesRes.json()).rivalries : [];
        const weeklyResults = weeklyRes.ok ? (await weeklyRes.json()).weekly_results : [];

        return { manager, rivalries, weeklyResults, error: null };
    } catch (error) {
        console.error('Failed to load manager:', error);
        return { manager: null, rivalries: [], weeklyResults: [], error: 'Failed to load manager data' };
    }
};
