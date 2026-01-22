/**
 * @module CodomeHUD
 * @description Heads-Up Display for the 3D Axial Holarchy. Features Level Indicator and Node Inspector.
 * @see visualization_architecture.md
 */

const CodomeHUD = (function () {
    'use strict';

    let hudContainer = null;
    let rulerContainer = null;
    let inspectorContainer = null;

    // CSS Styles (injected)
    const STYLES = `
        #codome-hud {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none; /* Let clicks pass to canvas */
            font-family: 'Courier New', monospace;
            color: #00ff00;
        }

        #codome-ruler {
            position: absolute;
            left: 20px;
            top: 100px;
            bottom: 100px;
            width: 60px;
            border-left: 2px solid #0044aa;
            display: flex;
            flex-direction: column-reverse; /* Bottom (L0) up */
            justify-content: space-between;
            pointer-events: auto;
        }

        .ruler-tick {
            font-size: 10px;
            padding-left: 5px;
            border-bottom: 1px solid rgba(0, 68, 170, 0.5);
            opacity: 0.7;
        }

        #codome-inspector {
            position: absolute;
            right: 20px;
            top: 20px;
            width: 300px;
            padding: 15px;
            background: rgba(0, 10, 20, 0.9);
            border: 1px solid #0044aa;
            box-shadow: 0 0 10px #0044aa;
            display: none; /* Hidden by default */
            pointer-events: auto;
        }
        
        .inspector-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #ffffff;
            border-bottom: 1px solid #0044aa;
        }

        .inspector-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }
    `;

    function init(container) {
        // 1. Inject Styles
        const styleEl = document.createElement('style');
        styleEl.innerHTML = STYLES;
        document.head.appendChild(styleEl);

        // 2. Wrap Canvas (if needed) or just overlay
        // Assuming container is relative position

        hudContainer = document.createElement('div');
        hudContainer.id = 'codome-hud';
        container.appendChild(hudContainer);

        // 3. Create Ruler
        rulerContainer = document.createElement('div');
        rulerContainer.id = 'codome-ruler';
        hudContainer.appendChild(rulerContainer);

        // Populate Ruler with Levels
        // Needs access to HolarchyMapper, assuming global or passed?
        // Let's assume we know the 16 levels or pass them in update
        // Minimal set for now:
        const levels = [
            'L0: Token', 'L1: State', 'L2: Block', 'L3: Node',
            'L4: Cont', 'L5: File', 'L6: Pkg', 'L7: Sys'
        ]; // Simplified for visual space

        levels.forEach(lvl => {
            const tick = document.createElement('div');
            tick.className = 'ruler-tick';
            tick.innerText = lvl;
            rulerContainer.appendChild(tick);
        });

        // 4. Create Inspector
        inspectorContainer = document.createElement('div');
        inspectorContainer.id = 'codome-inspector';
        hudContainer.appendChild(inspectorContainer);
    }

    function showNodeDetails(node) {
        if (!node) {
            inspectorContainer.style.display = 'none';
            return;
        }

        inspectorContainer.style.display = 'block';
        inspectorContainer.innerHTML = `
            <div class="inspector-title">${node.id || 'Unknown Node'}</div>
            <div class="inspector-row"><span>Type:</span><span>${node.type}</span></div>
            <div class="inspector-row"><span>Level:</span><span>L${node.holarchy?.level || '?'}</span></div>
            <div class="inspector-row"><span>Module:</span><span>${node.module || 'N/A'}</span></div>
            <div class="inspector-row"><span>Dependencies:</span><span>${(node.in_degree || 0) + (node.out_degree || 0)} edges</span></div>
        `;
    }

    return {
        init,
        showNodeDetails
    };

})();

// Export
if (typeof window !== 'undefined') window.CodomeHUD = CodomeHUD;
if (typeof module !== 'undefined') module.exports = CodomeHUD;
