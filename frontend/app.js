document.addEventListener('DOMContentLoaded', () => {
    const influencersTable = document.querySelector('#influencers-table tbody');
    const recommendationsList = document.getElementById('recommendations-list');
    const refreshBtn = document.getElementById('refresh-btn');
    const userIdInput = document.getElementById('user-id-input');
    const experimentBadge = document.getElementById('experiment-badge');
    const apiStatus = document.getElementById('api-status');
    const statusIndicator = document.querySelector('.status-indicator');
    const latencyVal = document.getElementById('latency-val');

    // Fetch API Health
    async function checkHealth() {
        try {
            const res = await fetch('/api/health');
            if (res.ok) {
                apiStatus.textContent = 'API Online';
                statusIndicator.className = 'status-indicator online';
            } else {
                throw new Error('Not OK');
            }
        } catch (e) {
            apiStatus.textContent = 'API Offline';
            statusIndicator.className = 'status-indicator offline';
        }
    }

    // Fetch Top Influencers
    async function fetchInfluencers() {
        try {
            const res = await fetch('/api/top-influencers?limit=5');
            if (!res.ok) throw new Error('API Error');
            const data = await res.json();
            
            influencersTable.innerHTML = '';
            
            if (data.top_influencers && data.top_influencers.length > 0) {
                const maxScore = Math.max(...data.top_influencers.map(i => parseFloat(i.pagerank_score)));
                
                data.top_influencers.forEach((user, index) => {
                    const rank = index + 1;
                    const rankClass = rank <= 3 ? `rank-${rank}` : '';
                    const score = parseFloat(user.pagerank_score).toFixed(4);
                    const percent = maxScore > 0 ? (score / maxScore) * 100 : 0;
                    
                    const tr = document.createElement('tr');
                    tr.className = rankClass;
                    tr.innerHTML = `
                        <td><div class="rank-badge">${rank}</div></td>
                        <td>
                            <div style="font-weight:600;">${user.name || ('User ' + user.user_id)}</div>
                            <div style="font-size:0.85rem; color:var(--text-muted)">@${user.username || 'user' + user.user_id}</div>
                        </td>
                        <td>
                            <div>${score} PR</div>
                            <div class="score-bar-container">
                                <div class="score-bar" style="width: 0%"></div>
                            </div>
                        </td>
                    `;
                    influencersTable.appendChild(tr);
                    
                    // Trigger animation
                    setTimeout(() => {
                        tr.querySelector('.score-bar').style.width = `${percent}%`;
                    }, 100);
                });
            } else {
                influencersTable.innerHTML = '<tr><td colspan="3" class="loading">No influencers found. Run Graph Engine.</td></tr>';
            }
        } catch (e) {
            console.error(e);
            influencersTable.innerHTML = '<tr><td colspan="3" class="loading">Failed to load data. API might be offline.</td></tr>';
        }
    }

    // Fetch Recommendations
    async function fetchRecommendations(userId) {
        recommendationsList.innerHTML = '<div class="loading">Loading...</div>';
        try {
            const startTime = performance.now();
            const res = await fetch(`/api/recommendations/${userId}`);
            
            if (!res.ok) throw new Error('API Error');
            const data = await res.json();
            const endTime = performance.now();
            
            // Update Latency UI
            latencyVal.textContent = `~${(endTime - startTime).toFixed(0)}ms`;
            
            recommendationsList.innerHTML = '';
            
            // Update UI badge
            experimentBadge.textContent = `Testing: ${data.experiment_variant.toUpperCase()}`;
            experimentBadge.style.background = data.experiment_variant === 'treatment' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(139, 92, 246, 0.2)';
            experimentBadge.style.color = data.experiment_variant === 'treatment' ? '#6ee7b7' : '#c4b5fd';
            experimentBadge.style.borderColor = data.experiment_variant === 'treatment' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(139, 92, 246, 0.4)';

            if (data.recommendations && data.recommendations.length > 0) {
                data.recommendations.forEach(rec => {
                    const initials = (rec.name || 'U').substring(0, 2).toUpperCase();
                    const score = parseFloat(rec.score).toFixed(2);
                    
                    const div = document.createElement('div');
                    div.className = 'rec-item';
                    div.innerHTML = `
                        <div class="avatar">${initials}</div>
                        <div class="rec-info">
                            <h4>${rec.name || 'User ' + rec.recommended_user_id}</h4>
                            <p>Match Score: ${score}</p>
                        </div>
                        <button class="btn-connect">Connect</button>
                    `;
                    recommendationsList.appendChild(div);
                });
            } else {
                recommendationsList.innerHTML = '<div class="loading">No recommendations available for this user.</div>';
            }
        } catch (e) {
            console.error(e);
            recommendationsList.innerHTML = '<div class="loading">Failed to load recommendations.</div>';
        }
    }

    // Initialization
    function refreshData() {
        const userId = userIdInput.value || 1;
        checkHealth();
        fetchInfluencers();
        fetchRecommendations(userId);
    }

    refreshBtn.addEventListener('click', refreshData);
    
    // Auto-refresh every 10 seconds for live demo feel
    setInterval(() => {
        checkHealth();
        fetchInfluencers();
    }, 10000);

    // Initial load
    refreshData();
});
