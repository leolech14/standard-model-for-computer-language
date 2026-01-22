/**
 * @module TowerRenderer
 * @description Visual engine for the 3D Axial Holarchy. Handles Three.js scene, geometry, and animation loop.
 * @see visualization_architecture.md
 */

const TowerRenderer = (function () {
    'use strict';

    // Visual Themes
    const THEME = {
        background: 0x000000,
        gridColor: 0x0044aa,
        nodeColors: {
            L7: 0xffffff, // System (White)
            L6: 0xcccccc, // Package
            L5: 0xaaaaaa, // File
            L4: 0x8888ff, // Class (Blueish)
            L3: 0x44ccff, // Function (Cyan)
            L2: 0x00ff00, // Block (Green)
            L1: 0x008800, // Statement
            L0: 0x004400  // Token
        },
        linkOpacity: 0.2
    };

    /**
     * Initializes the Three.js scene and starts the render loop.
     * @param {HTMLElement} container - The DOM element to append canvas to.
     * @param {Object} graphData - The processed graph data.
     * @returns {Object} Public API (dispose, update).
     */
    function init(container, graphData) {
        console.log('TowerRenderer: Initializing 3D Context...');

        // 1. Scene Setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(THEME.background);
        scene.fog = new THREE.FogExp2(THEME.background, 0.001); // Depth cue

        // 2. Camera
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 1, 10000);
        camera.position.set(1000, 800, 1000); // Look from above/side
        camera.lookAt(0, 400, 0);

        // 3. Renderer
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        container.appendChild(renderer.domElement);

        // 4. Controls (Orbit)
        // Note: Assuming THREE.OrbitControls is available globally or we import it
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;

        // Custom Mappings: Right=Rotate, Space+Left=Pan, Left=Select(Default)
        controls.mouseButtons = {
            LEFT: THREE.MOUSE.DOLLY, // Default to Zoom or Nothing (allows Selection)
            MIDDLE: THREE.MOUSE.DOLLY,
            RIGHT: THREE.MOUSE.ROTATE
        };

        // Spacebar Toggle for Panning
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                controls.mouseButtons.LEFT = THREE.MOUSE.PAN;
            }
        });

        window.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                controls.mouseButtons.LEFT = THREE.MOUSE.DOLLY; // Revert
            }
        });

        // 5. Build Construct (Geometry)
        const nodeMeshes = [];
        const geometry = new THREE.BoxGeometry(10, 10, 10); // Base unit cube

        graphData.nodes.forEach(node => {
            if (!node.holarchy) return;

            // Material based on Level
            const color = THEME.nodeColors['L' + node.holarchy.level] || 0xff00ff;
            const material = new THREE.MeshBasicMaterial({ color: color });

            const mesh = new THREE.Mesh(geometry, material);
            mesh.userData = node; // Link back to data

            // Initial position (will be updated by layout)
            mesh.position.set(0, node.holarchy.level * 100, 0);

            // Scale based on importance (optional)
            mesh.scale.setScalar(1 + (node.holarchy.level * 0.5));

            scene.add(mesh);
            nodeMeshes.push(mesh);
        });

        // 6. Substrate Grid (Floor)
        const gridHelper = new THREE.GridHelper(2000, 50, THEME.gridColor, 0x112233);
        scene.add(gridHelper);

        // 7. Lighting (Cinematic)
        const ambientLight = new THREE.AmbientLight(0x404040); // Soft white
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.5);
        dirLight.position.set(500, 1000, 500);
        scene.add(dirLight);

        // 8. Animation Loop
        function animate() {
            requestAnimationFrame(animate);

            // Sync Meshes with Data (Physics)
            nodeMeshes.forEach(mesh => {
                const node = mesh.userData;
                // D3 uses x,y, (and checks z if 3d). AxialLayout writes to .x, .y, .z
                if (node.x !== undefined) mesh.position.x = node.x;
                if (node.y !== undefined) mesh.position.z = node.y; // Swap Y/Z for Three.js (Y is up)
                if (node.z !== undefined) mesh.position.y = node.z; // Z in data is Height (Y in Three)
            });

            controls.update();
            renderer.render(scene, camera);
        }

        animate();

        // Resize Handler
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        return {
            scene,
            camera,
            renderer
        };
    }

    return {
        init,
        THEME
    };

})();

// Export
if (typeof window !== 'undefined') window.TowerRenderer = TowerRenderer;
if (typeof module !== 'undefined') module.exports = TowerRenderer;
