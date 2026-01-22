/**
 * @module InteractionManager
 * @description Handles user input (Raycasting, Clicks) for the 3D Axial Holarchy.
 * @see visualization_architecture.md
 */

const InteractionManager = (function () {
    'use strict';

    let raycaster;
    let mouse;
    let camera;
    let scene;
    let hud;
    let hoveredObject = null;

    function init(threeCamera, threeScene, threeRendererDom, hudInstance) {
        console.log('InteractionManager: Initializing Inputs...');

        camera = threeCamera;
        scene = threeScene;
        hud = hudInstance;

        raycaster = new THREE.Raycaster();
        mouse = new THREE.Vector2();

        // Event Listeners
        window.addEventListener('mousemove', onMouseMove, false);
        window.addEventListener('click', onMouseClick, false); // For expanding/focus (future)

        // Adjust mouse coords for canvas relative position if needed
        // For full screen, window coords match (mostly)
    }

    function onMouseMove(event) {
        // Calculate mouse position in normalized device coordinates (-1 to +1)
        mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
        mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

        // Perform Raycast
        raycaster.setFromCamera(mouse, camera);

        // Intersect objects (assume scene children are the meshes)
        // Optimization: Pass specific array of interactables instead of scene.children
        const intersects = raycaster.intersectObjects(scene.children);

        if (intersects.length > 0) {
            const firstHit = intersects[0].object;
            const nodeData = firstHit.userData;

            if (nodeData && nodeData.id) {
                // Highlight logic could go here (e.g., firstHit.material.color.setHex(...))

                if (hoveredObject !== firstHit) {
                    // Reset previous?
                    // Set new
                    hoveredObject = firstHit;
                    hud.showNodeDetails(nodeData);
                }
            }
        } else {
            if (hoveredObject) {
                hoveredObject = null;
                hud.showNodeDetails(null);
            }
        }
    }

    function onMouseClick(event) {
        // Future: Handle click selection, zoom to fit, etc.
        if (hoveredObject) {
            console.log('Clicked Node:', hoveredObject.userData);
        }
    }

    return {
        init
    };

})();

// Export
if (typeof window !== 'undefined') window.InteractionManager = InteractionManager;
if (typeof module !== 'undefined') module.exports = InteractionManager;
