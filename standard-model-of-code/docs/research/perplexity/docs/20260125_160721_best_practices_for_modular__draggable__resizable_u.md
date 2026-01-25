# Research: Best practices for modular, draggable, resizable UI panel systems in vanilla JavaScript (no React/Vu...

> **Date:** 2026-01-25 16:07:21
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:72ef336b720a2f5b048652484684b310ebe5e2588bd1e36656a4815523761b26`
> **Raw JSON:** `raw/20260125_160721_best_practices_for_modular__draggable__resizable_u.json`

---

## Query

Best practices for modular, draggable, resizable UI panel systems in vanilla JavaScript (no React/Vue). Looking for: 1) Lightweight libraries for dockable panels (like golden-layout but simpler), 2) CSS Grid vs Flexbox for dynamic panel layouts, 3) How to implement drag-to-rearrange panels with localStorage persistence. Context: Building a data visualization control panel with 82 controls grouped into ~10 semantic categories. Need users to customize layout (resize, reorder, hide, combine panels).

---

## Response

### 1. Lightweight Libraries for Dockable Panels (Vanilla JS, Simpler than Golden Layout)

**Dockview** is the top recommendation: a zero-dependency layout manager with vanilla TypeScript support (no React required), offering dockable panels, splitviews, gridviews, collapsible panes, drag-and-drop tab positioning, floating groups, and serialization for persistence—ideal for your 10-panel control system with 82 controls.[1] It supports programmatic panel addition/removal, custom headers, and CSS customization without frameworks.

**jsPanel** is another strong vanilla JS option: supports docking, movable/resizable floating panels, and modal dialogs, suitable for tidy widget arrangements in editors like your data viz controls.[3]

Avoid heavier libraries like Syncfusion (145+ components, modular but not zero-dependency)[2] or jQuery-based ones like Collapsible.js[4] to stay lightweight and framework-free. ControlKit.js offers simple property controls but lacks full docking.[5]

### 2. CSS Grid vs Flexbox for Dynamic Panel Layouts

**Use CSS Grid** for your resizable/rearrangeable panels: it excels at 2D layouts with dynamic track sizing (`grid-template-columns: 1fr 2fr` or `repeat(auto-fit, minmax(300px, 1fr))`), perfect for splitting/combining ~10 panels with arbitrary resizing via `resize: both` on panel elements and `display: grid` on the container.[1] Grid handles complex, non-linear arrangements (e.g., nested docks) better than Flexbox.

Flexbox is simpler for 1D flows (e.g., horizontal toolbars) but struggles with true 2D resizing/reordering—use it only for panel headers or linear stacks within Grid cells. Combine them: Grid for overall layout, Flexbox inside panels for control alignment.

Example starter CSS for dynamic panels:
```css
.panel-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  grid-gap: 4px;
  height: 100vh;
}
.panel {
  resize: both;
  overflow: auto;
  border: 1px solid #ccc;
  display: flex;
  flex-direction: column;
}
```

### 3. Implementing Drag-to-Rearrange Panels with localStorage Persistence

Use the **HTML5 Drag and Drop API** (native vanilla JS) for lightweight dragging—no libraries needed beyond layout managers like Dockview (which has built-in DND).[1] Track panel order/positions in a data structure (array of panel configs: `{id, x, y, width, height, visible}`), update on drag end, and persist via `JSON.stringify/localStorage`.

**Core Implementation Steps:**
- Assign `draggable="true"` to panels; listen for `dragstart`, `dragover`, `dragenter`, `dragleave`, `drop`, `dragend`.
- On `drop`, reorder DOM via `insertBefore` or update Grid `order`/`grid-area` properties.
- For resize: Use `ResizeObserver` (native) to track `contentRect` changes and save dimensions.
- Hide/combine: Toggle `display: none` or merge via `appendChild`; persist visibility state.
- Save on changes: `localStorage.setItem('panelLayout', JSON.stringify(layoutState));`.
- Load on init: Parse JSON, recreate DOM/layout with Dockview API or manual Grid assignment.

**Vanilla JS Drag Example** (integrate with your panels):
```javascript
const container = document.querySelector('.panel-container');
let draggedElement = null;

container.addEventListener('dragstart', (e) => {
  draggedElement = e.target.closest('.panel');
  e.dataTransfer.effectAllowed = 'move';
});

container.addEventListener('dragover', (e) => {
  e.preventDefault(); // Allow drop
  e.dataTransfer.dropEffect = 'move';
});

container.addEventListener('drop', (e) => {
  e.preventDefault();
  if (draggedElement && e.target.closest('.panel') !== draggedElement) {
    container.insertBefore(draggedElement, e.target.closest('.panel'));
    saveLayout(); // Persist order
  }
  draggedElement = null;
});

function saveLayout() {
  const layout = Array.from(container.children).map((panel, i) => ({
    id: panel.id,
    order: i,
    // Add rect from getBoundingClientRect() or ResizeObserver
  }));
  localStorage.setItem('panelLayout', JSON.stringify(layout));
}

function loadLayout() {
  const saved = JSON.parse(localStorage.getItem('panelLayout') || '[]');
  // Reorder/resize panels based on saved data
}

// Init ResizeObserver for all panels
const resizeObserver = new ResizeObserver((entries) => {
  entries.forEach(entry => saveLayout());
});
document.querySelectorAll('.panel').forEach(p => resizeObserver.observe(p));
```

For your 82 controls: Group into panels semantically, use Dockview's serialization API for complex docks (e.g., `dockviewApi.saveLayoutAsJson()`), or stick to custom Grid + native APIs for minimalism. Test on ultrawide/non-standard screens with `minmax` and `overflow: auto`.[1][3]

---

## Citations

1. https://dockview.dev
2. https://www.syncfusion.com/javascript-ui-controls
3. https://discourse.threejs.org/t/three-js-editor-any-suggestion-js-libraries-for-docking-movable-widgets/45825
4. https://jordnkr.github.io/collapsible/
5. https://github.com/automat/controlkit.js
6. https://news.ycombinator.com/item?id=36343544
7. https://www.jointjs.com/jointjs-plus

---

## Usage Stats

- Prompt tokens: 102
- Completion tokens: 1079
- Total tokens: 1181
