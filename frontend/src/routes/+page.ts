import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const [seasonsRes, championsRes, managersRes] = await Promise.all([
            fetch(`${API_BASE}/seasons`),
            fetch(`${API_BASE}/champions`),
            fetch(`${API_BASE}/managers`)
        ]);

        const seasons = await seasonsRes.json();
        const champions = await championsRes.json();
        const managers = await managersRes.json();

        // Get latest year standings
        const latestYear = seasons.seasons[0];
        const teamsRes = await fetch(`${API_BASE}/teams?year=${latestYear}`);
        const teams = await teamsRes.json();

        return {
            seasons: seasons.seasons,
            champions: champions.champions,
            managers: managers.managers,
            latestStandings: teams.teams,
            latestYear
        };
    } catch (error) {
        console.error('Failed to load data:', error);
        return {
            seasons: [],
            champions: [],
            managers: [],
            latestStandings: [],
            latestYear: 2024
        };
    }
};
