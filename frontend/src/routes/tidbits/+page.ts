import type { PageLoad } from './$types';

const API_BASE = 'http://localhost:8000/api';

export const load: PageLoad = async ({ fetch }) => {
    try {
        const [luckRes, recordsRes] = await Promise.all([
            fetch(`${API_BASE}/luck`),
            fetch(`${API_BASE}/records`)
        ]);

        const luck = luckRes.ok ? (await luckRes.json()).luck_rankings : [];
        const records = recordsRes.ok ? (await recordsRes.json()).records : [];

        return { luck, records, error: null };
    } catch (error) {
        console.error('Failed to load tidbits:', error);
        return { luck: [], records: [], error: 'Failed to load data' };
    }
};
