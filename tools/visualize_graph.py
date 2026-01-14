import json
import sys
import os
from datetime import datetime

def generate_html(json_path, output_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    nodes = data.get('nodes', [])
    edges = data.get('edges', [])

    # Extract Brain Download (LLM Summary)
    brain_download = data.get('brain_download', '# No Brain Download Available\n\nRun full analysis to generate.')
    # Escape for JavaScript embedding
    brain_download_escaped = brain_download.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')

    # Prepare D3 data
    d3_nodes = []
    node_indices = {}
    
    # Extract Metadata
    target_name = data.get('target_name', 'Unknown Repo').upper()
    
    for i, n in enumerate(nodes):
        node_id = n.get('id')
        atom = n.get('atom', 'Unknown')
        
        # Determine group based on Atom family
        group = 0 # Default
        if atom.startswith('LOG'): group = 1
        elif atom.startswith('DAT'): group = 2
        elif atom.startswith('ORG'): group = 3
        elif atom.startswith('EXE'): group = 4
        
        d3_nodes.append({
            "id": node_id,
            "group": group,
            "atom": atom,
            "name": n.get('name', node_id),
            "radius": 5 + (n.get('fan_out', 0) * 0.5), # Size by connections
            "file_path": n.get('file_path', ''), # Add file_path
            "layer": n.get('layer', 'Unknown') # Add Layer
        })
        node_indices[node_id] = i

    d3_edges = []
    
    # Track implicit nodes to add them to d3_nodes
    implicit_nodes = {}
    
    for e in edges:
        src = e.get('source')
        tgt = e.get('target')
        
        # Check source
        src_idx = node_indices.get(src)
        
        # Check target - if missing, it's an external/implicit node
        tgt_idx = node_indices.get(tgt)
        
        if src_idx is None:
            # Source missing - skip
            continue 
            
        if tgt_idx is None:
            # Create implicit node for target
            if tgt not in implicit_nodes:
                new_idx = len(d3_nodes) + len(implicit_nodes)
                implicit_nodes[tgt] = {
                    "id": tgt,
                    "group": 5, # Group 5 for External/Implicit
                    "atom": "EXT.LIB",
                    "name": tgt,
                    "radius": 4,
                    "file_path": "",
                    "layer": "External"
                }
                node_indices[tgt] = new_idx
            tgt_idx = node_indices[tgt]

        d3_edges.append({
            "source": src,
            "target": tgt,
            "value": 1
        })
        
    # Append implicit nodes to d3_nodes
    for n_id, n_data in implicit_nodes.items():
        d3_nodes.append(n_data)

    version = data.get('meta', {}).get('version', '4.0.0')

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Collider Standard Output v{version}</title>
    <script>
        // Suppress benign cross-origin errors from D3/Extensions
        const _log = console.error;
        console.error = function(...args) {{
            if (args[0] && typeof args[0] === 'string' && args[0].includes('postMessage')) return;
            _log.apply(console, args);
        }};
    </script>
    <style>
        :root {{
            --bg: #050505;
            --panel: rgba(10, 10, 10, 0.95);
            --accent: #888888;
            --border: #222;
            --text-main: #cccccc;
            --text-dim: #555555;
            --col-ext: #8a2be2; /* BlueViolet for External */
        }}
        body {{ margin: 0; background-color: var(--bg); color: var(--text-main); font-family: 'Inter', system-ui, sans-serif; overflow: hidden; }}
        canvas {{ display: block; }}
        
        /* GUI Container */
        .gui-layer {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1000; }}
        
        /* Window System */
        .window {{ 
            position: absolute; background: rgba(13, 17, 23, 0.85); 
            border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; 
            backdrop-filter: blur(12px); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            pointer-events: auto; display: flex; flex-direction: column;
            resize: both; overflow: hidden; min-width: 200px; min-height: 100px;
            transition: opacity 0.2s, transform 0.2s;
        }}
        .window.hidden {{ opacity: 0; pointer-events: none; transform: scale(0.95); }}
        .title-bar {{ 
            padding: 8px 12px; background: rgba(255,255,255,0.05); 
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex; justify-content: space-between; align-items: center;
            cursor: grab; user-select: none;
        }}
        .title-bar:active {{ cursor: grabbing; background: rgba(255,255,255,0.08); }}
        .win-title {{ font-weight: 600; font-size: 11px; letter-spacing: 1px; color: #bbb; text-transform: uppercase; }}
        .win-controls {{ display: flex; gap: 8px; }}
        .win-btn {{ width: 12px; height: 12px; border-radius: 50%; cursor: pointer; display: inline-block; }}
        .win-btn.close {{ background: #ff5f56; }}
        .win-btn.min {{ background: #ffbd2e; }}
        .window-content {{ padding: 15px; overflow-y: auto; flex: 1; }}

        /* Dock */
        .dock {{
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            background: rgba(13, 17, 23, 0.8); border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(12px); padding: 8px 16px; border-radius: 100px;
            display: flex; gap: 12px; pointer-events: auto; z-index: 2000;
        }}
        .dock-item {{
            padding: 8px 16px; border-radius: 20px; background: rgba(255,255,255,0.05);
            display: flex; align-items: center; justify-content: center; cursor: pointer; font-size: 10px; font-weight: bold;
            transition: all 0.2s; border: 1px solid transparent; color: #888; text-transform: uppercase;
        }}
        .dock-item:hover {{ background: rgba(255,255,255,0.15); color: #fff; transform: translateY(-4px); }}
        .dock-item.active {{ background: rgba(255,255,255,0.2); border-color: rgba(255,255,255,0.3); color: #fff; box-shadow: 0 0 10px rgba(255,255,255,0.1); }}
       h1 {{ font-size: 18px; color: #ffffff; margin: 0 0 5px 0; letter-spacing: 1px; text-transform: uppercase; font-weight: 300; }}
        h2 {{ font-size: 14px; color: var(--text-main); border-bottom: 1px solid var(--border); padding-bottom: 8px; margin: 0 0 10px 0; }}
        
        .section {{ margin-bottom: 15px; }}
        .row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 12px; padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.03); }}
        .row:last-child {{ border-bottom: none; }}
        
        /* Toggles */
        .layer-toggle {{ 
            display: flex; align-items: center; padding: 8px; 
            background: rgba(255,255,255,0.03); border-radius: 2px; border: 1px solid transparent;
            cursor: pointer; transition: all 0.2s; margin-bottom: 4px; color: #aaa;
        }}
        .layer-toggle:hover {{ background: rgba(255,255,255,0.08); color: #fff; }}
        .layer-toggle.active {{ border-color: #666; background: rgba(255, 255, 255, 0.05); color: #fff; }}
        .layer-icon {{ width: 14px; height: 14px; margin-right: 10px; border-radius: 2px; background: #444; }}
        
        /* Metrics */
        .metric-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
        .metric-box {{ background: rgba(255,255,255,0.03); padding: 8px; border-radius: 2px; text-align: center; border: 1px solid var(--border); }}
        .metric-val {{ display: block; font-size: 16px; font-weight: bold; color: #fff; }}
        .metric-label {{ font-size: 10px; color: var(--text-dim); text-transform: uppercase; }}

        /* Legend Dots - Grayscale */
        .dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }}

        /* Sliders */
        .slider {{ -webkit-appearance: none; width: 100%; height: 4px; border-radius: 2px; background: rgba(255,255,255,0.1); outline: none; }}
        .slider::-webkit-slider-thumb {{ -webkit-appearance: none; appearance: none; width: 12px; height: 12px; border-radius: 50%; background: #888; cursor: pointer; }}
        .slider::-webkit-slider-thumb:hover {{ background: #fff; }}
    </style>
    <style>
        /* ... existing styles ... */
        /* Markdown Styles */
        #report-content h1, #report-content h2, #report-content h3 {{ color: #fff; margin-top: 15px; border-bottom: 1px solid #444; padding-bottom: 5px; }}
        #report-content ul {{ padding-left: 20px; }}
        #report-content li {{ margin-bottom: 5px; }}
        #report-content strong {{ color: #fff; }}
    </style>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <script>
        // Init Report
        window.addEventListener('load', () => {{
            const data = graph; // Access global graph data
            const reportEl = document.getElementById('report-content');
            if (data.brain_download) {{
                reportEl.innerHTML = marked.parse(data.brain_download);
            }} else {{
                reportEl.innerHTML = "<div style='padding:20px; text-align:center; color:#666'>No brain download summary available.</div>";
            }}
        }});
    </script>
    <!-- Main Viewport -->
    <div id="viewport"></div>

    <!-- Interface -->
    <div class="gui-layer">
        
        <!-- Window: REPORT -->
        <div id="win-report" class="window hidden" style="top: 20px; right: 320px; width: 400px; height: 500px;">
            <div class="title-bar">
                <div class="win-title">BRAIN DOWNLOAD</div>
                <div class="win-controls">
                    <div class="win-btn close" onclick="toggleWindow('win-report')"></div>
                </div>
            </div>
            <div class="window-content" style="background: rgba(0,0,0,0.3);">
                <div id="report-content" style="color: #ccc; font-size: 13px; line-height: 1.5; font-family: sans-serif;">
                    Loading report...
                </div>
            </div>
        </div>

        <!-- DOCK -->
        <div class="dock">
            <div class="dock-item active" id="dock-main" onclick="toggleWindow('win-main')">Controls</div>
            <div class="dock-item" id="dock-ins" onclick="toggleWindow('win-ins')">Inspector</div>
            <div class="dock-item" id="dock-report" onclick="toggleWindow('win-report')">Report</div>
        </div>

        <!-- Window: MAIN CONTROLS -->
        <div id="win-main" class="window" style="top: 20px; left: 20px; width: 300px; height: 600px;">
            <div class="title-bar">
                <div class="win-title">CONTROLS</div>
                <div class="win-controls">
                    <div class="win-btn close" onclick="toggleWindow('win-main')"></div>
                </div>
            </div>
            <div class="window-content">
                <div>
                <h1>COLLIDER v{version}</h1>
                <div style="font-size: 11px; color: var(--text-dim); margin-bottom: 15px;">Standard Model Visualization</div>
                <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 4px; border-left: 3px solid var(--accent); margin-bottom: 20px;">
                    <div style="font-size: 10px; color: #888; text-transform: uppercase;">TARGET REPOSITORY</div>
                    <div style="font-size: 14px; font-weight: bold; color: #fff; margin-top: 2px;">{target_name}</div>
                </div>
            </div>

            <!-- Global Metrics -->
            <div class="metric-grid">
                <div class="metric-box">
                    <span class="metric-val">{len(d3_nodes)}</span>
                    <span class="metric-label">Atoms</span>
                </div>
                <div class="metric-box">
                    <span class="metric-val">{len(d3_edges)}</span>
                    <span class="metric-label">Bonds</span>
                </div>
                <div class="metric-box">
                    <span class="metric-val">87.5%</span>
                    <span class="metric-label">Coverage</span>
                </div>
                <div class="metric-box">
                    <span class="metric-val">10.0</span>
                    <span class="metric-label">Knot Score</span>
                </div>
            </div>

            <!-- Layer Control -->
            <div class="section">
                <h2>LAYERS</h2>
                <div class="layer-toggle active" onclick="toggleLayer('structure')" id="btn-structure">
                    <div class="layer-icon" style="background:#555"></div>
                    <span>Structural Topology</span>
                </div>
                <div class="layer-toggle" onclick="toggleLayer('markov')" id="btn-markov">
                    <div class="layer-icon" style="background:#777"></div>
                    <span>Markov Probability</span>
                </div>
                <div class="layer-toggle" onclick="toggleLayer('knots')" id="btn-knots">
                    <div class="layer-icon" style="background:#999"></div>
                    <span>Knot Complexity</span>
                </div>
            </div>
            </div>
            <!-- INTERACTION HINT -->
            <div style="font-size:10px; color:#666; font-style:italic; margin-bottom:15px; text-align:center;">
                Drag Bkg to Select <br> Space + Drag to Pan
            </div>

            <!-- Physics Controls -->
            <div class="section">
                <h2>PHYSICS</h2>
                <div style="margin-bottom:8px">
                    <div class="row"><span>Gravity</span> <span id="val-charge">-30</span></div>
                    <input type="range" min="-100" max="0" value="-30" class="slider" oninput="updatePhysics('charge', this.value)">
                </div>
                <div style="margin-bottom:8px">
                    <div class="row"><span>Collision</span> <span id="val-collide">node+2</span></div>
                    <input type="range" min="0" max="20" value="2" class="slider" oninput="updatePhysics('collide', this.value)">
                </div>
                <div>
                    <div class="row"><span>Link Dist</span> <span id="val-link">40</span></div>
                    <input type="range" min="10" max="200" value="40" class="slider" oninput="updatePhysics('link', this.value)">
                </div>
            </div>

            <!-- Legend (Monochrome) -->
            <div style="font-size: 11px; margin-top: auto; padding-top: 10px; border-top: 1px solid #222;">
                <span class="dot" style="background:#fff"></span>LOG
                <span class="dot" style="background:#bbb"></span>DAT
                <span class="dot" style="background:#888"></span>ORG
                <span class="dot" style="background:#555"></span>EXE
                <span class="dot" style="background:#8a2be2"></span>EXT
            </div>
        </div></div>

        <!-- Window: INSPECTOR -->
        <div id="win-ins" class="window hidden" style="top: 20px; right: 20px; width: 280px; height: 400px;">
            <div class="title-bar">
                <div class="win-title">INSPECTOR</div>
                <div class="win-controls">
                    <div class="win-btn close" onclick="toggleWindow('win-ins')"></div>
                </div>
            </div>
            <div class="window-content" id="inspector-content">
                <h2 id="ins-title" style="margin-top:0">No Selection</h2>
                <div id="ins-atom" style="background:#333; padding:4px 8px; border-radius:2px; font-family:monospace; margin-bottom:15px; color:#fff; display:inline-block;">-</div>
                <div id="content-area"></div>
            </div>
        </div>

        <!-- Window: BRAIN DOWNLOAD REPORT -->
        <div id="win-report" class="window hidden" style="top: 60px; left: 340px; width: 500px; height: 600px;">
            <div class="title-bar">
                <div class="win-title">BRAIN DOWNLOAD</div>
                <div class="win-controls">
                    <div class="win-btn close" onclick="toggleWindow('win-report')"></div>
                </div>
            </div>
            <div class="window-content" id="report-content" style="font-family: 'Monaco', 'Menlo', monospace; font-size: 11px; line-height: 1.6; white-space: pre-wrap; overflow-y: auto;">
            </div>
        </div>
    </div>

    <script>
        // --- DATA ---
        const graph = {{
            nodes: {json.dumps(d3_nodes)},
            links: {json.dumps(d3_edges)},
            brain_download: {json.dumps(data.get('brain_download', ''))}
        }};

        // Brain Download Report (Markdown)
        const brainDownload = `{brain_download_escaped}`;

        // Populate report window
        document.getElementById('report-content').textContent = brainDownload;

        console.log("COLLIDER DEBUG: Graph Data Loaded", graph); // Debugging

        // --- STATE ---
        const state = {{
            layers: {{ structure: true, markov: false, knots: false }},
            transform: d3.zoomIdentity,
            width: window.innerWidth,
            height: window.innerHeight,
            selected: null, 
            multiSelected: [],
            box: null,
            isSelecting: false,
            spacePressed: false,
            isDragging: false 
        }};

        // --- SETUP CANVAS ---
        const container = d3.select("#viewport");
        const canvas = container.append("canvas")
            .attr("width", state.width)
            .attr("height", state.height);
        const context = canvas.node().getContext("2d");

        // --- SIMULATION ---
        const simulation = d3.forceSimulation(graph.nodes)
            .force("link", d3.forceLink(graph.links).id(d => d.id).distance(40))
            .force("charge", d3.forceManyBody().strength(-30))
            .force("center", d3.forceCenter(state.width / 2, state.height / 2))
            .force("gravity", d3.forceRadial(Math.min(state.width, state.height) * 0.45, state.width / 2, state.height / 2).strength(0.1))
            .force("collide", d3.forceCollide().radius(d => d.radius + 2));

        // --- NODE COLORING (GRAYSCALE) ---
        function getNodeColor(g) {{
            if(g===1) return "#ffffff"; // Logic - White
            if(g===2) return "#bbbbbb"; // Data - Light Gray
            if(g===3) return "#888888"; // Org - Medium Gray
            if(g===4) return "#555555"; // Exec - Dark Gray
            if(g===5) return "#8a2be2"; // Ext - BlueViolet
            return "#333333"; // Unknown - Very Dark Gray
        }}
        
        // --- INTERACTION HANDLERS ---
        
        // 1. Zoom
        const zoom = d3.zoom()
            .scaleExtent([0.1, 8])
            .filter(event => event.type === 'wheel' || event.shiftKey || event.button === 1 || state.spacePressed)
            .on("zoom", (event) => {{
                state.transform = event.transform;
                simulation.alphaTarget(0.1).restart();
            }});
        
        // 2. Drag (Group & Single)
        const drag = d3.drag()
            .subject(dragSubject)
            .on("start", dragStarted)
            .on("drag", dragged)
            .on("end", dragEnded);

        canvas.call(zoom).call(drag);

        function dragSubject(event) {{
            // Transform screen to world
            const t = state.transform;
            const x = (event.x - t.x) / t.k;
            const y = (event.y - t.y) / t.k;
            
            // Log logic:
            // 1. Check if we hit a node
            const hit = graph.nodes.find(node => {{
               const dx = x - node.x;
               const dy = y - node.y;
               return dx*dx + dy*dy < (node.radius + 5) * (node.radius + 5);
            }});

            if (hit) {{
                // If hitting a node that is ALREADY in multi-selection, drag the whole group
                if (state.multiSelected.includes(hit)) {{
                    return {{ x: x, y: y, targets: state.multiSelected, type: 'group' }};
                }} 
                // Otherwise, drag just this node (and select it if likely single click)
                return {{ x: x, y: y, targets: [hit], type: 'single' }};
            }}
            return null;
        }}

        function dragStarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            state.isDragging = true;
            
            // If dragging a single node that is NOT consistent with current selection, update selection
            if (event.subject.type === 'single') {{
                const n = event.subject.targets[0];
                if (state.selected !== n) selectNode(n);
            }}

            event.subject.targets.forEach(d => {{
                d.fx = d.x;
                d.fy = d.y;
            }});
        }}

        function dragged(event) {{
            // Apply delta to all targets
            // d3 drag event gives us subject x/y and event x/y.
            // But for multi-drag, we need relative movement?
            // Actually D3 drag updates the subject coordinates automatically IF subject is a node.
            // But here subject is a custom object {{targets: [...]}}. D3 won't auto-update properties on it unless we return the node itself.
            // Since we return a custom subject, we must manually update targets.
            
            // Calculate delta in world coordinates
            // event.dx is in screen coordinates usually? No, d3.drag on canvas uses the coordinate system of the container (screen)
            // We need to scale the delta by transform
            
            const dx = event.dx / state.transform.k;
            const dy = event.dy / state.transform.k;

            event.subject.targets.forEach(d => {{
                d.fx += dx;
                d.fy += dy;
            }});
        }}

        function dragEnded(event) {{
            if (!event.active) simulation.alphaTarget(0);
            state.isDragging = false;
            event.subject.targets.forEach(d => {{
                d.fx = null;
                d.fy = null;
            }});
        }}

        // 3. Box Selection (Manual Mouse Events)
        d3.select("canvas")
            .on("mousedown", (event) => {{
                if (state.spacePressed || event.shiftKey || event.button !== 0) return; // Ignore if Panning (Space/Shift) or non-left click
                const [mx, my] = d3.pointer(event);
                state.isSelecting = true;
                state.box = {{ x: mx, y: my, w: 0, h: 0, originX: mx, originY: my }};
                state.selected = null;
                state.multiSelected = [];
                updateInspector(); 
            }})
            .on("mousemove", (event) => {{
                if (!state.isSelecting) return;
                const [mx, my] = d3.pointer(event);
                state.box.w = mx - state.box.originX;
                state.box.h = my - state.box.originY;
                state.box.x = state.box.w < 0 ? mx : state.box.originX;
                state.box.y = state.box.h < 0 ? my : state.box.originY;
                state.box.w = Math.abs(state.box.w);
                state.box.h = Math.abs(state.box.h);
                simulation.alphaTarget(0).restart();
            }})
            .on("mouseup", (event) => {{
                 if (!state.isSelecting) return;
                 state.isSelecting = false;
                 
                 // Calculate Selection
                 const t = state.transform;
                 const selectedNodes = [];
                 graph.nodes.forEach(n => {{
                     const screenX = t.x + n.x * t.k;
                     const screenY = t.y + n.y * t.k;
                     if (screenX >= state.box.x && screenX <= state.box.x + state.box.w &&
                         screenY >= state.box.y && screenY <= state.box.y + state.box.h) {{
                         selectedNodes.push(n);
                     }}
                 }});
                 
                 state.multiSelected = selectedNodes;
                 state.box = null;
                 
                 if (selectedNodes.length > 0) {{
                     if (selectedNodes.length === 1) selectNode(selectedNodes[0]);
                     else showClusterAnalysis(selectedNodes);
                 }} else {{
                     closeInspector();
                 }}
                 simulation.restart();
            }});

         // Click Picking - handled by Drag Subject mainly, but standalone click needed?
         // D3 Drag suppresses 'click' if dragged. 
         // If we want simple click to select without dragging, dragSubject handles 'start' but if no move happens...
         // Actually, let's let Drag handle selection on Start.

        // --- RENDERING LOOP ---
        simulation.on("tick", () => {{
            context.save();
            context.clearRect(0, 0, state.width, state.height);
            context.translate(state.transform.x, state.transform.y);
            context.scale(state.transform.k, state.transform.k);

            // Lower Layer (Links)
            context.beginPath();
            graph.links.forEach((l) => drawLink(l, context));
            context.strokeStyle = "rgba(100, 100, 100, 0.4)";
            context.lineWidth = 1;
            context.stroke();
            
            // Augmented Layers (Perf, Dataflow)
            
            // 2. Nodes
            graph.nodes.forEach(d => drawNodeAR(d, context));
            
            context.restore(); // End World Transform
            
            // 3. UI Overlays (Selection Box) - Screen Space
            if (state.box) {{
                context.fillStyle = "rgba(100, 100, 100, 0.2)";
                context.strokeStyle = "rgba(200, 200, 200, 0.8)";
                context.lineWidth = 1;
                context.fillRect(state.box.x, state.box.y, state.box.w, state.box.h);
                context.strokeRect(state.box.x, state.box.y, state.box.w, state.box.h);
            }}

            context.restore();
        }});

        function drawLink(d, ctx) {{
            ctx.moveTo(d.source.x, d.source.y);
            ctx.lineTo(d.target.x, d.target.y);
        }}
        
        function drawNodeAR(d, ctx) {{
            let r = d.radius;
            
            // Knot Aura (Subtle Gray)
            if (state.layers.knots && d.group === 4) {{ 
                ctx.beginPath();
                ctx.arc(d.x, d.y, r * 1.2, 0, 2 * Math.PI);
                ctx.fillStyle = "rgba(200, 200, 200, 0.1)";
                ctx.fill();
            }}

            // Atom Body
            ctx.beginPath();
            ctx.arc(d.x, d.y, r, 0, 2 * Math.PI);
            ctx.fillStyle = getNodeColor(d.group);
            ctx.fill();
            
            // Selection Highlight
            const isSelected = state.selected === d || state.multiSelected.includes(d);
            
            if (isSelected) {{
                ctx.strokeStyle = "#fff";
                ctx.lineWidth = 2;
                ctx.stroke();
                
                // Add glowing ring
                ctx.beginPath();
                ctx.arc(d.x, d.y, r + 4, 0, 2 * Math.PI);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
                ctx.lineWidth = 1;
                ctx.stroke();
            }}
        }}

        // --- INSPECTOR LOGIC ---
        
        function selectNode(d) {{
            state.selected = d;
            state.multiSelected = [];
            updateInspector();
        }}
        
        function showClusterAnalysis(nodes) {{
            state.selected = null;
            state.multiSelected = nodes;
            updateInspector();
        }}
        
        function getPhaseName(g) {{
            if(g===1) return "LOGIC";
            if(g===2) return "DATA";
            if(g===3) return "ORG";
            if(g===4) return "EXEC";
            if(g===5) return "EXT";
            return "UNK";
        }}

        function updateInspector() {{
            const win = document.getElementById("win-ins");
            const dock = document.getElementById("dock-ins");
            
            if (state.selected) {{
                // Single Node View
                win.style.display = "flex";
                win.classList.remove("hidden");
                dock.classList.add("active");
                
                const d = state.selected;
                document.getElementById("ins-title").innerText = d.name;
                document.getElementById("ins-atom").style.display = 'inline-block';
                document.getElementById("ins-atom").innerText = d.atom;
                
                // Construct File Path display
                let fileInfo = '';
                if (d.file_path) {{
                    const fileName = d.file_path.split('/').pop();
                    fileInfo = `<div class="row" style="margin-top:10px; color:#555; font-style:italic; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;" title="${{d.file_path}}">${{fileName}}</div>`;
                }}
                
                document.getElementById("content-area").innerHTML = `
                    <div class="section">
                         <div class="row"><span style="color:#555">Type</span><span class="value">${{d.kind || 'Unknown'}}</span></div>
                         <div class="row"><span style="color:#555">Layer</span><span class="value" style="color:#ffd700">${{d.layer || 'Unknown'}}</span></div>
                         <div class="row"><span style="color:#555">Phase</span><span class="value">${{getPhaseName(d.group)}}</span></div>
                         ${{fileInfo}}
                    </div>
                `;
            }} else if (state.multiSelected.length > 0) {{
                // Cluster View
                panel.classList.add("active");
                const nodes = state.multiSelected;
                
                const counts = {{ LOG:0, DAT:0, ORG:0, EXE:0, EXT:0, UNK:0 }};
                
                nodes.forEach(n => {{
                    if(n.group===1) counts.LOG++;
                    else if(n.group===2) counts.DAT++;
                    else if(n.group===3) counts.ORG++;
                    else if(n.group===4) counts.EXE++;
                    else if(n.group===5) counts.EXT++;
                    else counts.UNK++;
                }});
                
                const total = nodes.length;
                
                document.getElementById("ins-title").innerText = "CLUSTER ANALYSIS";
                document.getElementById("ins-atom").style.display = 'none'; 
                document.getElementById("content-area").innerHTML = `
                    <div class="section">
                        <div style="text-align:center; padding:10px; background:rgba(255,255,255,0.05); border-radius:2px; margin-bottom:15px;">
                            <span style="font-size:24px; font-weight:bold; color:#fff;">${{total}}</span>
                            <div style="font-size:10px; color:#555;">SELECTED ATOMS</div>
                        </div>
                        
                        <div class="row"><span style="color:#fff">LOGIC</span><span class="value">${{counts.LOG}}</span></div>
                        <div class="row"><span style="color:#bbb">DATA</span><span class="value">${{counts.DAT}}</span></div>
                        <div class="row"><span style="color:#888">ORG</span><span class="value">${{counts.ORG}}</span></div>
                        <div class="row"><span style="color:#555">EXEC</span><span class="value">${{counts.EXE}}</span></div>
                        <div class="row"><span style="color:#8a2be2">EXT</span><span class="value">${{counts.EXT}}</span></div>
                    </div>
                `;
            }} else {{
                panel.classList.remove("active");
            }}
        }}

        // --- ACTIONS ---

        function toggleLayer(layer) {{
            state.layers[layer] = !state.layers[layer];
            
            // Toggle UI state
            const btn = document.getElementById('btn-' + layer);
            if(state.layers[layer]) btn.classList.add('active');
            else btn.classList.remove('active');
            
            // Re-render
            simulation.restart();
        }}

        function updatePhysics(param, value) {{
            value = parseInt(value);
            // Update UI
            document.getElementById('val-' + param).innerText = value;
            
            // Update Sim
            if(param === 'charge') {{
                simulation.force("charge").strength(value);
            }} else if(param === 'collide') {{
                simulation.force("collide").radius(d => d.radius + value);
            }} else if(param === 'link') {{
                simulation.force("link").distance(value);
            }}
            simulation.alphaTarget(0.3).restart();
            setTimeout(() => simulation.alphaTarget(0), 1000); // Cool down
        }}

        function closeInspector() {{
            state.selected = null;
            state.multiSelected = [];
            updateInspector();
            simulation.restart();
        }}
    </script>
</body>
</html>
    """
    
    if output_path is None or os.path.isdir(output_path):
        # Generate standard filename: standard_output_[repo]_[timestamp].html
        target_name = data.get('target_name', 'unknown')
        # Use analysis time from JSON if available, otherwise current time
        timestamp_str = data.get('generated_at', datetime.now().isoformat())
        # Clean timestamp (remove ms if easier for filename compatibility, or just use as is but careful with colons)
        # Windows/Mac hate colons in filenames. Let's sanitize.
        safe_timestamp = timestamp_str.replace(':', '-').replace('.', '-')
        
        filename = f"standard_output_{target_name}_{safe_timestamp}.html"
        
        if output_path and os.path.isdir(output_path):
            output_path = os.path.join(output_path, filename)
        else:
            output_path = filename

    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Generated visualization at {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 viz.py <json_input> [html_output]")
        sys.exit(1)
        
    json_input = sys.argv[1]
    html_output = sys.argv[2] if len(sys.argv) > 2 else None
    
    generate_html(json_input, html_output)
