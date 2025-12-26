#!/bin/bash
# Regenerate deduplicated insights and browser
# Usage: ./tools/regenerate_insights.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/output/chat_summaries"
ELEMENTS_DIR="/Users/lech/PROJECTS_all/PROJECT_elements"

cd "$PROJECT_ROOT"

echo "=== Regenerating Chat Insights ==="
echo ""

# Run deduplication
python3 tools/dedupe_insights.py \
  "$ELEMENTS_DIR/0-Code's Unified Theory.md" \
  "$ELEMENTS_DIR/0-Defining Code Cosmology.md" \
  "$ELEMENTS_DIR/0-EXPANDED-MAP.md" \
  "$ELEMENTS_DIR/0-Refining Code Visual Language.md" \
  --output "$OUTPUT_DIR"

# Embed data in HTML
echo ""
echo "Embedding data in HTML..."
python3 << 'EOPY'
import json
from pathlib import Path

json_path = Path('output/chat_summaries/deduplicated.json')
html_path = Path('output/chat_summaries/index.html')

if not json_path.exists():
    print("Error: deduplicated.json not found")
    exit(1)

# Create fresh HTML with embedded data
json_data = json_path.read_text()

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Insights - Standard Model of Code (Deduplicated)</title>
    <style>
        :root {
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --border-color: #30363d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --accent-blue: #58a6ff;
            --accent-green: #3fb950;
            --accent-purple: #a371f7;
            --accent-orange: #d29922;
            --accent-red: #f85149;
            --accent-cyan: #39c5cf;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
        }
        .container { display: flex; min-height: 100vh; }
        .sidebar {
            width: 260px;
            background: var(--bg-secondary);
            border-right: 1px solid var(--border-color);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            padding: 20px 0;
        }
        .sidebar-header { padding: 0 20px 20px; border-bottom: 1px solid var(--border-color); }
        .sidebar-header h1 { font-size: 18px; margin-bottom: 5px; }
        .sidebar-header p { font-size: 12px; color: var(--text-secondary); }
        .sidebar-header .dedup-badge {
            display: inline-block;
            background: var(--accent-green);
            color: #000;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            margin-top: 8px;
        }
        .nav-section { padding: 15px 0; border-bottom: 1px solid var(--border-color); }
        .nav-section-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
            padding: 0 20px 10px;
        }
        .nav-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 20px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
        .nav-item.active {
            background: var(--bg-tertiary);
            color: var(--accent-blue);
            border-left: 2px solid var(--accent-blue);
        }
        .nav-item .count {
            background: var(--bg-primary);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
        }
        .main {
            margin-left: 260px;
            flex: 1;
            padding: 30px 40px;
            max-width: 1100px;
        }
        .search-bar { margin-bottom: 25px; }
        .search-bar input {
            width: 100%;
            padding: 12px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-primary);
            font-size: 14px;
        }
        .search-bar input:focus { outline: none; border-color: var(--accent-blue); }
        .search-bar input::placeholder { color: var(--text-secondary); }
        .content-section { display: none; }
        .content-section.active { display: block; }
        .section-header { margin-bottom: 25px; }
        .section-header h2 { font-size: 24px; margin-bottom: 8px; }
        .section-header p { color: var(--text-secondary); font-size: 14px; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-bottom: 25px;
        }
        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .stat-value { font-size: 28px; font-weight: 700; }
        .stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
        .stat-card.request .stat-value { color: var(--accent-blue); }
        .stat-card.decision .stat-value { color: var(--accent-green); }
        .stat-card.finding .stat-value { color: var(--accent-purple); }
        .stat-card.action .stat-value { color: var(--accent-orange); }
        .stat-card.dedup .stat-value { color: var(--accent-cyan); }
        .card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
        }
        .card-header {
            padding: 14px 18px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .card-header h3 { font-size: 15px; font-weight: 600; }
        .card-body { padding: 0; }
        .tag {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 500;
        }
        .tag-blue { background: rgba(88, 166, 255, 0.15); color: var(--accent-blue); }
        .tag-green { background: rgba(63, 185, 80, 0.15); color: var(--accent-green); }
        .tag-purple { background: rgba(163, 113, 247, 0.15); color: var(--accent-purple); }
        .tag-orange { background: rgba(210, 153, 34, 0.15); color: var(--accent-orange); }
        .tag-cyan { background: rgba(57, 197, 207, 0.15); color: var(--accent-cyan); }
        .insight-item {
            padding: 14px 18px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 12px;
            align-items: flex-start;
        }
        .insight-item:last-child { border-bottom: none; }
        .insight-item:hover { background: var(--bg-tertiary); }
        .insight-icon {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            flex-shrink: 0;
            font-size: 12px;
            font-weight: 600;
        }
        .insight-content { flex: 1; min-width: 0; }
        .insight-title { font-size: 13px; margin-bottom: 6px; word-wrap: break-word; line-height: 1.5; }
        .insight-meta { display: flex; gap: 12px; flex-wrap: wrap; font-size: 11px; color: var(--text-secondary); }
        .source-badge { background: var(--bg-primary); padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .importance-badge { padding: 2px 8px; border-radius: 4px; font-weight: 600; }
        .importance-high { background: rgba(248, 81, 73, 0.2); color: var(--accent-red); }
        .importance-med { background: rgba(210, 153, 34, 0.2); color: var(--accent-orange); }
        .importance-low { background: rgba(88, 166, 255, 0.2); color: var(--accent-blue); }
        .overlap-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; padding: 16px; }
        .overlap-item { background: var(--bg-primary); padding: 12px; border-radius: 6px; font-size: 12px; }
        .overlap-item .files { color: var(--text-secondary); margin-bottom: 4px; }
        .overlap-item .percent { font-size: 20px; font-weight: 700; color: var(--accent-cyan); }
        .filter-pills { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
        .filter-pill {
            padding: 6px 14px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            font-size: 12px;
            color: var(--text-secondary);
            cursor: pointer;
        }
        .filter-pill:hover { border-color: var(--accent-blue); color: var(--accent-blue); }
        .filter-pill.active { background: var(--accent-blue); border-color: var(--accent-blue); color: white; }
        mark { background: var(--accent-orange); color: black; padding: 0 2px; border-radius: 2px; }
        @media (max-width: 768px) {
            .sidebar { display: none; }
            .main { margin-left: 0; padding: 20px; }
            .overlap-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <nav class="sidebar">
            <div class="sidebar-header">
                <h1>Chat Insights</h1>
                <p>Standard Model of Code</p>
                <span class="dedup-badge">DEDUPLICATED</span>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Overview</div>
                <a class="nav-item active" data-section="overview">Dashboard</a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Categories</div>
                <a class="nav-item" data-section="requests">Requests <span class="count" id="count-requests">-</span></a>
                <a class="nav-item" data-section="decisions">Decisions <span class="count" id="count-decisions">-</span></a>
                <a class="nav-item" data-section="findings">Findings <span class="count" id="count-findings">-</span></a>
                <a class="nav-item" data-section="actions">Actions <span class="count" id="count-actions">-</span></a>
            </div>
            <div class="nav-section">
                <div class="nav-section-title">Source Files</div>
                <div id="file-nav"></div>
            </div>
        </nav>
        <main class="main">
            <div class="search-bar">
                <input type="text" id="search" placeholder="Search insights...">
            </div>
            <section class="content-section active" id="overview"></section>
            <section class="content-section" id="requests"></section>
            <section class="content-section" id="decisions"></section>
            <section class="content-section" id="findings"></section>
            <section class="content-section" id="actions"></section>
            <section class="content-section" id="file-view"></section>
            <section class="content-section" id="search-results"></section>
        </main>
    </div>
    <script>
        const data = ''' + json_data + ''';

        document.getElementById('count-requests').textContent = data.stats.by_category.request || 0;
        document.getElementById('count-decisions').textContent = data.stats.by_category.decision || 0;
        document.getElementById('count-findings').textContent = data.stats.by_category.finding || 0;
        document.getElementById('count-actions').textContent = data.stats.by_category.action || 0;

        const fileNav = document.getElementById('file-nav');
        Object.entries(data.stats.file_stats).forEach(([name, stats]) => {
            const shortName = name.length > 22 ? name.substring(0, 22) + '...' : name;
            fileNav.innerHTML += `<a class="nav-item" data-section="file-view" data-file="${name}">${shortName} <span class="count">${Math.round(stats.file_size_kb)}KB</span></a>`;
        });

        function escapeHtml(t) { const d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
        function highlightMatch(t, q) { return escapeHtml(t).replace(new RegExp(`(${q.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&')})`, 'gi'), '<mark>$1</mark>'); }

        function renderInsightList(items) {
            if (!items.length) return '<div style="padding:20px;color:var(--text-secondary)">No items</div>';
            return items.map(item => {
                const iconClass = {request:'tag-blue',decision:'tag-green',finding:'tag-purple',action:'tag-orange'}[item.category]||'tag-blue';
                const impClass = item.importance >= 8 ? 'importance-high' : item.importance >= 5 ? 'importance-med' : 'importance-low';
                const content = escapeHtml((item.content||'').replace(/\\n/g,' ').substring(0,200));
                const sources = (item.sources||[]).slice(0,2).map(s=>`<span class="source-badge">${(s.file||'').replace('0-','').substring(0,15)}:L${s.line}</span>`).join(' ');
                const more = (item.sources||[]).length > 2 ? ` +${item.sources.length-2}` : '';
                return `<div class="insight-item"><div class="insight-icon ${iconClass}">${(item.category||'?')[0].toUpperCase()}</div><div class="insight-content"><div class="insight-title">${content}</div><div class="insight-meta"><span class="importance-badge ${impClass}">${item.importance}</span>${sources}${more}</div></div></div>`;
            }).join('');
        }

        function renderOverview() {
            const s = data.stats;
            document.getElementById('overview').innerHTML = `
                <div class="section-header"><h2>Deduplicated Insights</h2><p>${s.files_processed} files, 367 unique insights</p></div>
                <div class="stats-grid">
                    <div class="stat-card dedup"><div class="stat-value">${s.total_unique}</div><div class="stat-label">Unique</div></div>
                    <div class="stat-card request"><div class="stat-value">${s.by_category.request||0}</div><div class="stat-label">Requests</div></div>
                    <div class="stat-card decision"><div class="stat-value">${s.by_category.decision||0}</div><div class="stat-label">Decisions</div></div>
                    <div class="stat-card finding"><div class="stat-value">${s.by_category.finding||0}</div><div class="stat-label">Findings</div></div>
                    <div class="stat-card action"><div class="stat-value">${s.by_category.action||0}</div><div class="stat-label">Actions</div></div>
                </div>
                <div class="card"><div class="card-header"><h3>File Overlap</h3><span class="tag tag-cyan">Similarity</span></div><div class="card-body"><div class="overlap-grid">${Object.entries(s.overlap_matrix).map(([p,v])=>`<div class="overlap-item"><div class="files">${p.replace(' <-> ',' ↔ ').replace(/0-/g,'')}</div><div class="percent">${v}</div></div>`).join('')}</div></div></div>
                <div class="card"><div class="card-header"><h3>Top Insights</h3></div><div class="card-body">${renderInsightList(data.insights.slice(0,15))}</div></div>`;
        }

        function renderCategory(cat, title) {
            const items = data.insights.filter(i=>i.category===cat);
            const sec = document.getElementById(cat+'s');
            sec.innerHTML = `<div class="section-header"><h2>${title}</h2><p>${items.length} unique</p></div>
                <div class="filter-pills"><span class="filter-pill active" data-i="all">All</span><span class="filter-pill" data-i="high">High</span><span class="filter-pill" data-i="med">Med</span><span class="filter-pill" data-i="low">Low</span></div>
                <div class="card"><div class="card-body" id="${cat}-list">${renderInsightList(items)}</div></div>`;
            sec.querySelectorAll('.filter-pill').forEach(p=>p.onclick=()=>{
                sec.querySelectorAll('.filter-pill').forEach(x=>x.classList.remove('active'));
                p.classList.add('active');
                const f = p.dataset.i;
                let fl = items;
                if(f==='high')fl=items.filter(i=>i.importance>=8);
                else if(f==='med')fl=items.filter(i=>i.importance>=5&&i.importance<8);
                else if(f==='low')fl=items.filter(i=>i.importance<5);
                document.getElementById(cat+'-list').innerHTML=renderInsightList(fl);
            });
        }

        function showSection(id, file=null) {
            document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
            (file?document.querySelector(`[data-file="${file}"]`):document.querySelector(`[data-section="${id}"]`))?.classList.add('active');
            document.querySelectorAll('.content-section').forEach(s=>s.classList.remove('active'));
            if(id==='file-view'&&file){
                const st=data.stats.file_stats[file];
                const ins=data.insights.filter(i=>i.sources.some(s=>s.file===file));
                document.getElementById('file-view').innerHTML=`<div class="section-header"><h2>${file.replace('0-','')}</h2><p>${Math.round(st.file_size_kb)}KB</p></div><div class="stats-grid"><div class="stat-card"><div class="stat-value">${st.sections.user_inputs}</div><div class="stat-label">Inputs</div></div><div class="stat-card"><div class="stat-value">${ins.length}</div><div class="stat-label">Insights</div></div></div><div class="card"><div class="card-body">${renderInsightList(ins.slice(0,30))}</div></div>`;
            } else if(id==='requests')renderCategory('request','Requests');
            else if(id==='decisions')renderCategory('decision','Decisions');
            else if(id==='findings')renderCategory('finding','Findings');
            else if(id==='actions')renderCategory('action','Actions');
            document.getElementById(id).classList.add('active');
        }

        document.querySelectorAll('.nav-item').forEach(i=>i.onclick=()=>showSection(i.dataset.section,i.dataset.file));

        document.getElementById('search').oninput=e=>{
            const q=e.target.value.toLowerCase().trim();
            if(q.length<2){showSection('overview');return;}
            const r=data.insights.filter(i=>(i.content||'').toLowerCase().includes(q));
            document.getElementById('search-results').innerHTML=`<div class="section-header"><h2>Search: "${escapeHtml(q)}"</h2><p>${r.length} results</p></div><div class="card"><div class="card-body">${renderInsightList(r.slice(0,50))}</div></div>`;
            document.querySelectorAll('.content-section').forEach(s=>s.classList.remove('active'));
            document.getElementById('search-results').classList.add('active');
        };

        renderOverview();
    </script>
</body>
</html>'''

html_path.write_text(html_template)
print(f"Created index.html ({len(html_template)/1024:.1f} KB)")
EOPY

echo ""
echo "=== Done ==="
echo "Open: output/chat_summaries/index.html"
