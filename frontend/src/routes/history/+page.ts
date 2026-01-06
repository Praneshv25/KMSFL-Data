import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const [seasonsRes, teamsRes] = await Promise.all([
            fetch(`${API_BASE}/seasons`),
            fetch(`${API_BASE}/teams?year=2024`)  // Default to 2024
        ]);

        const seasons = await seasonsRes.json();
        const teams = await teamsRes.json();

        return {
            years: seasons.seasons,
            standings: teams.teams
        };
    } catch (error) {
        console.error('Failed to load history:', error);
        return { years: [], standings: [] };
    }
};
