#!/usr/bin/env python3
"""
Chart Viewer - HTML Report Generator

Generates a standalone HTML page displaying all generated charts
with interactive navigation and style switching.
"""

import base64
from pathlib import Path
from typing import List, Optional
from datetime import datetime


def encode_image(path: Path) -> str:
    """Encode image to base64 data URI."""
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    suffix = path.suffix.lower()
    mime = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.svg': 'image/svg+xml',
        '.gif': 'image/gif',
    }.get(suffix, 'image/png')
    return f'data:{mime};base64,{data}'


def generate_chart_viewer(
    chart_dirs: List[str],
    output_path: str,
    title: str = "Collider Scientific Charts"
) -> str:
    """
    Generate HTML viewer for charts.

    Args:
        chart_dirs: List of directories containing charts (one per style)
        output_path: Output HTML file path
        title: Page title

    Returns:
        Path to generated HTML file
    """
    # Collect charts from all directories
    styles = {}
    for dir_path in chart_dirs:
        dir_p = Path(dir_path)
        if not dir_p.exists():
            continue

        style_name = dir_p.name.replace('charts_', '').replace('charts', 'publication')
        if style_name == '':
            style_name = 'publication'

        charts = []
        for img in sorted(dir_p.glob('*.png')):
            charts.append({
                'name': img.stem.replace('_', ' ').title(),
                'filename': img.name,
                'data_uri': encode_image(img),
            })

        if charts:
            styles[style_name] = charts

    if not styles:
        raise ValueError("No charts found in provided directories")

    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg-primary: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-hover: #79c0ff;
            --border: #30363d;
            --success: #3fb950;
            --warning: #d29922;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
        }}

        header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        h1::before {{
            content: '📊';
        }}

        .style-selector {{
            display: flex;
            gap: 0.5rem;
        }}

        .style-btn {{
            padding: 0.5rem 1rem;
            border: 1px solid var(--border);
            background: var(--bg-tertiary);
            color: var(--text-secondary);
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }}

        .style-btn:hover {{
            border-color: var(--accent);
            color: var(--text-primary);
        }}

        .style-btn.active {{
            background: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }}

        main {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 1.5rem;
        }}

        .chart-card {{
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}

        .chart-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}

        .chart-header {{
            padding: 1rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .chart-title {{
            font-weight: 600;
            font-size: 1rem;
        }}

        .chart-actions {{
            display: flex;
            gap: 0.5rem;
        }}

        .chart-action {{
            padding: 0.25rem 0.5rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 4px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .chart-action:hover {{
            background: var(--accent);
            color: var(--bg-primary);
            border-color: var(--accent);
        }}

        .chart-image {{
            padding: 1rem;
            background: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 400px;
        }}

        .chart-image.dark-bg {{
            background: #1a1a2e;
        }}

        .chart-image img {{
            max-width: 100%;
            height: auto;
            max-height: 500px;
        }}

        .style-content {{
            display: none;
        }}

        .style-content.active {{
            display: block;
        }}

        /* Modal for full-size view */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 2rem;
        }}

        .modal.active {{
            display: flex;
        }}

        .modal img {{
            max-width: 95%;
            max-height: 95%;
            object-fit: contain;
        }}

        .modal-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: var(--bg-tertiary);
            border: none;
            color: var(--text-primary);
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1.5rem;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-secondary);
            font-size: 0.875rem;
            border-top: 1px solid var(--border);
            margin-top: 2rem;
        }}

        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}

            .header-content {{
                flex-direction: column;
                gap: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <h1>{title}</h1>
            <div class="style-selector">
'''

    # Add style buttons
    for i, style_name in enumerate(styles.keys()):
        active = 'active' if i == 0 else ''
        html += f'                <button class="style-btn {active}" data-style="{style_name}">{style_name.title()}</button>\n'

    html += '''            </div>
        </div>
    </header>

    <main>
'''

    # Add chart sections for each style
    for i, (style_name, charts) in enumerate(styles.items()):
        active = 'active' if i == 0 else ''
        dark_bg = 'dark-bg' if style_name == 'dark' else ''

        html += f'        <div class="style-content {active}" data-style="{style_name}">\n'
        html += '            <div class="charts-grid">\n'

        for chart in charts:
            html += f'''                <div class="chart-card">
                    <div class="chart-header">
                        <span class="chart-title">{chart['name']}</span>
                        <div class="chart-actions">
                            <button class="chart-action" onclick="openModal(this.closest('.chart-card').querySelector('img').src)">Expand</button>
                            <button class="chart-action" onclick="downloadChart(this.closest('.chart-card').querySelector('img').src, '{chart['filename']}')">Download</button>
                        </div>
                    </div>
                    <div class="chart-image {dark_bg}">
                        <img src="{chart['data_uri']}" alt="{chart['name']}" loading="lazy">
                    </div>
                </div>
'''

        html += '            </div>\n'
        html += '        </div>\n'

    html += f'''    </main>

    <div class="modal" id="modal">
        <button class="modal-close" onclick="closeModal()">&times;</button>
        <img id="modal-img" src="" alt="Full size chart">
    </div>

    <footer>
        Generated by Collider Scientific Charts Engine | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </footer>

    <script>
        // Style switching
        document.querySelectorAll('.style-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const style = btn.dataset.style;

                // Update buttons
                document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Update content
                document.querySelectorAll('.style-content').forEach(c => c.classList.remove('active'));
                document.querySelector(`.style-content[data-style="${{style}}"]`).classList.add('active');
            }});
        }});

        // Modal functions
        function openModal(src) {{
            document.getElementById('modal-img').src = src;
            document.getElementById('modal').classList.add('active');
        }}

        function closeModal() {{
            document.getElementById('modal').classList.remove('active');
        }}

        // Close modal on escape or click outside
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'Escape') closeModal();
        }});

        document.getElementById('modal').addEventListener('click', (e) => {{
            if (e.target === document.getElementById('modal')) closeModal();
        }});

        // Download function
        function downloadChart(dataUri, filename) {{
            const link = document.createElement('a');
            link.href = dataUri;
            link.download = filename;
            link.click();
        }}
    </script>
</body>
</html>
'''

    # Write output
    output_p = Path(output_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
    output_p.write_text(html)

    return str(output_p)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python chart_viewer.py <output.html> <chart_dir1> [chart_dir2] ...")
        sys.exit(1)

    output_path = sys.argv[1]
    chart_dirs = sys.argv[2:]

    result = generate_chart_viewer(chart_dirs, output_path)
    print(f"Generated: {result}")
