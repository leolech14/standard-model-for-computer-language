// Palace Dashboard - Frontend Logic
// Auto-refresh, tab management, API calls

const API_BASE = '';  // Same origin
const REFRESH_INTERVAL = 10000;  // 10 seconds

let healthChart = null;

// ============================================================================
// TAB MANAGEMENT
// ============================================================================

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');

            // Update tab styling
            tabs.forEach(t => {
                t.classList.remove('border-blue-500', 'text-white');
                t.classList.add('text-gray-400');
            });
            tab.classList.add('border-blue-500', 'text-white');
            tab.classList.remove('text-gray-400');

            // Show/hide content
            contents.forEach(content => {
                content.classList.add('hidden');
            });
            document.getElementById(`tab-${targetTab}`).classList.remove('hidden');

            // Load content if needed
            if (targetTab === 'butlers') loadButlers();
            if (targetTab === 'cloud') loadCloudJobs();
            if (targetTab === 'health') loadHealthTrends();
            if (targetTab === 'files') loadFiles();
        });
    });
}

// ============================================================================
// API CALLS
// ============================================================================

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(API_BASE + endpoint);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`API error (${endpoint}):`, error);
        return null;
    }
}

async function postAPI(endpoint, data) {
    try {
        const response = await fetch(API_BASE + endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error(`API error (${endpoint}):`, error);
        return null;
    }
}

// ============================================================================
// SYSTEM OVERVIEW
// ============================================================================

async function loadSystemOverview() {
    const health = await fetchAPI('/api/health/current');
    const knowledge = await fetchAPI('/api/knowledge/stats');
    const automation = await fetchAPI('/api/automation/status');

    if (health) {
        document.getElementById('health-tier').textContent = health.health_tier || '--';
        const margin = health.stability_margin;
        const stability = margin !== undefined ? `${margin > 0 ? '+' : ''}${margin.toFixed(2)}` : '--';
        document.getElementById('stability').textContent = stability;
        document.getElementById('stability').className = margin > 0 ? 'text-2xl font-bold text-green-400' : 'text-2xl font-bold text-red-400';
    }

    if (knowledge) {
        document.getElementById('chunk-count').textContent = knowledge.total_chunks?.toLocaleString() || '--';
    }

    if (automation) {
        document.getElementById('automation-level').textContent = automation.automation_level || '--';
    }

    document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
}

// ============================================================================
// BUTLERS TAB
// ============================================================================

async function loadButlers() {
    const data = await fetchAPI('/api/butlers');
    if (!data) return;

    const container = document.getElementById('butlers-list');
    container.innerHTML = '';

    data.butlers.forEach(butler => {
        const div = document.createElement('div');
        div.className = 'card p-4 rounded flex justify-between items-center';

        const healthClass = butler.healthy === true ? 'butler-healthy' : butler.healthy === false ? 'butler-unhealthy' : 'butler-unknown';
        const healthIcon = butler.healthy === true ? '✅' : butler.healthy === false ? '❌' : '⚪';

        div.innerHTML = `
            <div class="flex items-center space-x-4">
                <span class="text-2xl">${healthIcon}</span>
                <div>
                    <div class="font-semibold ${healthClass}">${butler.name}</div>
                    <div class="text-sm text-gray-400">${butler.summary || 'No summary'}</div>
                </div>
            </div>
            <div class="text-sm text-gray-400">
                ${butler.last_update ? timeAgo(butler.last_update) : 'Never'}
            </div>
        `;

        container.appendChild(div);
    });
}

// ============================================================================
// KNOWLEDGE TAB
// ============================================================================

let searchTimeout = null;

function setupKnowledgeSearch() {
    const input = document.getElementById('search-input');
    input.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchKnowledge(e.target.value);
        }, 300);  // Debounce 300ms
    });
}

async function searchKnowledge(query) {
    if (!query.trim()) {
        document.getElementById('search-results').innerHTML = '<div class="text-gray-400">Enter search query above</div>';
        return;
    }

    const results = document.getElementById('search-results');
    results.innerHTML = '<div class="text-gray-400">Searching...</div>';

    const data = await fetchAPI(`/api/knowledge/search?q=${encodeURIComponent(query)}&limit=10`);

    if (!data || data.total_matches === 0) {
        results.innerHTML = `<div class="text-gray-400">No matches found for "${query}"</div>`;
        return;
    }

    results.innerHTML = `<div class="text-sm text-gray-400 mb-3">Found ${data.total_matches} matches</div>`;

    data.results.forEach((result, i) => {
        const div = document.createElement('div');
        div.className = 'card p-4 rounded';

        div.innerHTML = `
            <div class="flex justify-between items-start mb-2">
                <div class="font-semibold text-blue-400">${i + 1}. ${result.source_file.split('/').pop()}</div>
                <div class="text-xs text-gray-500">Line ${result.start_line}</div>
            </div>
            <div class="text-sm text-gray-400 mb-2">
                Type: ${result.chunk_type} | Relevance: ${result.relevance.toFixed(2)} | Matches: ${result.match_count}
            </div>
            <div class="text-sm bg-gray-800 p-2 rounded font-mono">
                ...${result.preview}...
            </div>
        `;

        results.appendChild(div);
    });
}

// ============================================================================
// CLOUD JOBS TAB
// ============================================================================

async function loadCloudJobs() {
    const data = await fetchAPI('/api/cloud/jobs');
    if (!data) return;

    const container = document.getElementById('cloud-jobs-list');
    container.innerHTML = '';

    data.jobs.forEach(job => {
        const div = document.createElement('div');
        div.className = 'card p-4 rounded';

        const statusClass = job.status === 'success' ? 'text-green-400' : 'text-red-400';

        div.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <div class="font-semibold">${job.name}</div>
                    <div class="text-sm text-gray-400">
                        Last run: ${timeAgo(job.last_run)} - <span class="${statusClass}">${job.status.toUpperCase()}</span>
                    </div>
                    <div class="text-sm text-gray-400">
                        Next: ${new Date(job.next_scheduled).toLocaleString()}
                    </div>
                </div>
                <div>
                    <button onclick="triggerJob('${job.name}')"
                            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm">
                        ▶ Run Now
                    </button>
                </div>
            </div>
        `;

        container.appendChild(div);
    });
}

async function triggerJob(jobName) {
    if (!confirm(`Trigger ${jobName}?`)) return;

    const result = await postAPI(`/api/cloud/jobs/${jobName}/execute`, {wait: false});

    if (result) {
        alert(`Job triggered: ${result.execution_id || 'Started'}`);
        loadCloudJobs();
    } else {
        alert('Failed to trigger job');
    }
}

// ============================================================================
// HEALTH TRENDS TAB
// ============================================================================

async function loadHealthTrends() {
    const data = await fetchAPI('/api/health/trends?hours=24');
    if (!data || data.data_points < 2) {
        document.getElementById('health-chart').parentElement.innerHTML =
            '<div class="text-gray-400">Insufficient data for trends</div>';
        return;
    }

    const ctx = document.getElementById('health-chart');
    const timestamps = data.series.map(s => new Date(s.ts).toLocaleTimeString());
    const margins = data.series.map(s => s.margin);

    if (healthChart) healthChart.destroy();

    healthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timestamps,
            datasets: [{
                label: 'Stability Margin',
                data: margins,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {labels: {color: '#e0e0e0'}},
                title: {display: true, text: 'Stability Margin (24h)', color: '#e0e0e0'}
            },
            scales: {
                x: {ticks: {color: '#9ca3af'}},
                y: {ticks: {color: '#9ca3af'}}
            }
        }
    });
}

// ============================================================================
// FILES TAB
// ============================================================================

async function loadFiles() {
    const path = document.getElementById('path-input').value || '';
    const data = await fetchAPI(`/api/files/list?path=${encodeURIComponent(path)}&limit=50`);

    if (!data) return;

    const container = document.getElementById('files-list');
    container.innerHTML = '';

    if (data.files.length === 0) {
        container.innerHTML = '<div class="text-gray-400">No files in this path</div>';
        return;
    }

    data.files.forEach(file => {
        const div = document.createElement('div');
        div.className = 'card p-3 rounded flex justify-between items-center';

        div.innerHTML = `
            <div>
                <div class="font-semibold">${file.name}</div>
                <div class="text-xs text-gray-400">${file.size_human}</div>
            </div>
            <a href="${file.download_url}"
               class="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm">
                Download
            </a>
        `;

        container.appendChild(div);
    });

    // Add summary
    const summary = document.createElement('div');
    summary.className = 'text-sm text-gray-400 mt-4';
    summary.textContent = `${data.total_count} files, ${data.total_size_human}`;
    container.appendChild(summary);
}

// ============================================================================
// UTILITIES
// ============================================================================

function timeAgo(isoString) {
    const date = new Date(isoString);
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
}

// ============================================================================
// AUTO-REFRESH
// ============================================================================

function startAutoRefresh() {
    setInterval(() => {
        loadSystemOverview();

        // Refresh active tab
        const activeTab = document.querySelector('.tab-btn.border-blue-500');
        if (activeTab) {
            const tabName = activeTab.getAttribute('data-tab');
            if (tabName === 'butlers') loadButlers();
            if (tabName === 'cloud') loadCloudJobs();
            if (tabName === 'health') loadHealthTrends();
        }
    }, REFRESH_INTERVAL);
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    setupKnowledgeSearch();

    // Initial load
    loadSystemOverview();
    loadButlers();

    // Start auto-refresh
    startAutoRefresh();

    // Path input for files
    document.getElementById('path-input')?.addEventListener('change', loadFiles);
});
