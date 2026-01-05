// D/ST-specific display functions
function displayDSTCurrentSeasonStats(data) {
    const container = document.getElementById('currentSeasonTab');
    const viewingSeason = data.viewingSeason || new Date().getFullYear();
    const currentSeasonStats = data.seasons_data[viewingSeason] || [];

    if (currentSeasonStats.length === 0) {
        container.innerHTML = `<div class="no-data-message">No stats available for ${viewingSeason} season</div>`;
        return;
    }

    // Get season totals
    const totals = data.season_totals[viewingSeason] || {};

    // Build D/ST season summary
    let summaryHTML = '<div class="season-summary">';
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">Games</div><div class="season-summary-value">${totals.games || 0}</div></div>`;
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">Sacks</div><div class="season-summary-value">${totals.def_sacks || 0}</div></div>`;
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">INTs</div><div class="season-summary-value">${totals.def_interceptions || 0}</div></div>`;
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">Fumbles Rec</div><div class="season-summary-value">${totals.def_fumbles_recovered || 0}</div></div>`;
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">Def TDs</div><div class="season-summary-value">${totals.def_touchdowns || 0}</div></div>`;
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">ST TDs</div><div class="season-summary-value">${totals.special_teams_tds || 0}</div></div>`;
    summaryHTML += `<div class="season-summary-item"><div class="season-summary-label">Pts Allowed</div><div class="season-summary-value">${totals.points_allowed || 0}</div></div>`;
    summaryHTML += '</div>';

    // Build D/ST stats table
    let tableHTML = '<table class="stats-table"><thead><tr>';
    tableHTML += '<th>Week</th><th>Opp</th><th>Sacks</th><th>INTs</th><th>Fum Rec</th><th>Fum Forced</th><th>Def TDs</th><th>ST TDs</th><th>Safeties</th><th>Pts Allowed</th><th>Fant Pts</th>';
    tableHTML += '</tr></thead><tbody>';

    // Sort by week
    currentSeasonStats.sort((a, b) => a.week - b.week);

    currentSeasonStats.forEach(stat => {
        tableHTML += '<tr>';
        tableHTML += `<td><strong>${stat.week}</strong></td>`;
        tableHTML += `<td>${stat.opponent_team || '-'}</td>`;
        tableHTML += `<td>${stat.def_sacks || 0}</td>`;
        tableHTML += `<td>${stat.def_interceptions || 0}</td>`;
        tableHTML += `<td>${stat.def_fumbles_recovered || 0}</td>`;
        tableHTML += `<td>${stat.def_fumbles_forced || 0}</td>`;
        tableHTML += `<td>${stat.def_touchdowns || 0}</td>`;
        tableHTML += `<td>${stat.special_teams_tds || 0}</td>`;
        tableHTML += `<td>${stat.def_safeties || 0}</td>`;
        tableHTML += `<td>${stat.points_allowed || 0}</td>`;
        tableHTML += `<td><strong>${(stat.fantasy_points_ppr || 0).toFixed(1)}</strong></td>`;
        tableHTML += '</tr>';
    });

    tableHTML += '</tbody></table>';

    container.innerHTML = summaryHTML + tableHTML;
}

function displayDSTCareerStats(data) {
    const container = document.getElementById('careerStatsTab');
    const allStats = data.weekly_stats || [];

    if (allStats.length === 0) {
        container.innerHTML = '<div class="no-data-message">No career stats available</div>';
        return;
    }

    // Group by season
    const seasonTotals = data.season_totals || {};
    const seasons = Object.keys(seasonTotals).sort((a, b) => b - a);

    let html = '<div style="margin-bottom: 1rem;"><h3>Career Summary by Season</h3></div>';
    html += '<table class="stats-table"><thead><tr>';
    html += '<th>Season</th><th>Games</th><th>Sacks</th><th>INTs</th><th>Fum Rec</th><th>Def TDs</th><th>ST TDs</th><th>Safeties</th><th>Pts Allowed</th><th>Fant Pts (PPR)</th>';
    html += '</tr></thead><tbody>';

    seasons.forEach(season => {
        const totals = seasonTotals[season];
        html += '<tr>';
        html += `<td><strong>${season}</strong></td>`;
        html += `<td>${totals.games || 0}</td>`;
        html += `<td>${totals.def_sacks || 0}</td>`;
        html += `<td>${totals.def_interceptions || 0}</td>`;
        html += `<td>${totals.def_fumbles_recovered || 0}</td>`;
        html += `<td>${totals.def_touchdowns || 0}</td>`;
        html += `<td>${totals.special_teams_tds || 0}</td>`;
        html += `<td>${totals.def_safeties || 0}</td>`;
        html += `<td>${totals.points_allowed || 0} (${(totals.avg_points_allowed || 0).toFixed(1)} avg)</td>`;
        html += `<td><strong>${(totals.fantasy_points_ppr || 0).toFixed(1)}</strong></td>`;
        html += '</tr>';
    });

    html += '</tbody></table>';

    container.innerHTML = html;
}
