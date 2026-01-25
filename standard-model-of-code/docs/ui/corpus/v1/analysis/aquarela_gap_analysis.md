# Aquarela Mockup vs Template.html Gap Analysis

**Date:** 2026-01-25
**Source:** `html-asset.html` (Mockup) vs `src/core/viz/assets/template.html` (Current)

---

## Executive Summary

The mockup introduces a "Watercolor Digitalism" light theme with significant structural and visual differences from the current dark-themed template. Implementation requires changes across layout, styling, and component architecture.

| Category | Gap Count | Effort |
|----------|-----------|--------|
| Layout Structure | 3 major | High |
| Visual Effects | 4 new | Medium |
| Component Styling | 6 different | Medium |
| Controls | 2 missing | Low |
| Typography | 1 change | Low |

---

## 1. Layout Structure Gaps

### 1.1 Icon Sidebar (MISSING in template)

**Mockup has:**
```html
<aside class="sidebar-left-icons">
    <div class="icon-btn">...</div>  <!-- Grid icon -->
    <div class="icon-btn active">...</div>  <!-- Layers icon (active) -->
    <div class="icon-btn">...</div>  <!-- Settings icon -->
</aside>
```

**Template has:** No icon sidebar. Left sidebar is full-width with text labels.

**Gap:** Need to add 48px icon rail before main left sidebar, or redesign left sidebar to include icon-only mode.

---

### 1.2 Grid Layout (DIFFERENT)

**Mockup:**
```css
.main-ui {
    display: grid;
    grid-template-columns: 280px 1fr 240px;
    grid-template-rows: auto 1fr;
}
```

**Template:**
```css
#left-sidebar { width: var(--sidebar-width); /* 300px */ }
#right-sidebar { width: var(--right-panel-width); /* 280px */ }
#3d-graph { position: fixed; left: var(--sidebar-width); right: var(--right-panel-width); }
```

**Gap:** Template uses fixed positioning with CSS variables. Mockup uses CSS Grid. Both achieve similar layout but mockup is more flexible.

---

### 1.3 Header Position (DIFFERENT)

**Mockup:** Header is inside the grid (`grid-column: 1 / -1`)
**Template:** Header is fixed at top (`position: fixed; top: 0;`)

**Gap:** Mockup header spans inside main content area. Template header is separate fixed bar.

---

## 2. Visual Effects Gaps

### 2.1 Watercolor Background (MISSING)

**Mockup has:**
```css
.canvas-bg {
    background:
        radial-gradient(circle at 20% 30%, oklch(88% 0.12 215), transparent 60%),
        radial-gradient(circle at 80% 40%, oklch(88% 0.12 160), transparent 60%),
        radial-gradient(circle at 50% 80%, oklch(88% 0.12 30), transparent 60%),
        radial-gradient(circle at 10% 90%, oklch(92% 0.1 80), transparent 40%);
    filter: contrast(1.1) brightness(1.05);
    mix-blend-mode: multiply;
}
```

**Template has:** Solid `--bg` color (`#0a0a0f`).

**Gap:** Need watercolor background layer with radial gradients. Added to tokens as `effects.watercolor-bg`.

---

### 2.2 Noise Overlay (MISSING)

**Mockup has:**
```css
.noise-overlay {
    opacity: 0.03;
    background-image: url('data:image/svg+xml,...feTurbulence...');
}
```

**Template has:** No noise texture.

**Gap:** SVG noise filter for organic texture. Token added as `effects.noise-opacity`.

---

### 2.3 Glass Morphism (MISSING)

**Mockup has:**
```css
.glass {
    backdrop-filter: blur(25px) saturate(120%);
    background: oklch(98% 0.01 250 / 15%);
    border: 1px solid oklch(100% 0 0 / 20%);
    box-shadow: 0 8px 32px 0 oklch(0% 0 0 / 5%);
    border-radius: 12px;
}
```

**Template has:** Solid surface colors with standard borders.

**Gap:** Panels need glassmorphism effect. Tokens added under `color.glass.*`.

---

### 2.4 Panel Color Tinting (MISSING)

**Mockup has:**
- `.panel-scope` → cyan tint (`oklch(94% 0.03 210 / 40%)`)
- `.panel-node-config` → yellow tint (`oklch(96% 0.04 95 / 40%)`)
- `.panel-selection` → peach tint (`oklch(95% 0.03 50 / 25%)`)

**Template has:** All panels use same `--surface` color.

**Gap:** Need semantic panel background colors. Tokens added as `bg.panel-*`.

---

## 3. Component Styling Gaps

### 3.1 Section Headers (DIFFERENT)

**Mockup:**
```css
.section-header::before {
    content: "●";
    margin-right: 8px;
    font-size: 8px;
}
```
- Bullet prefix
- Uppercase with letter-spacing
- Chevron on right

**Template:**
- Text with arrow
- Collapsed state rotates arrow
- No bullet prefix

---

### 3.2 Buttons (DIFFERENT)

**Mockup Pill Button:**
```css
.btn-pill {
    height: 36px;
    border-radius: 999px;
    background: linear-gradient(to right, oklch(82% 0.08 210), oklch(85% 0.12 180));
    box-shadow: 0 4px 12px oklch(72% 0.12 225 / 20%);
}
```

**Template:** Rectangular buttons with subtle hover states.

---

### 3.3 Sliders (DIFFERENT)

**Mockup:**
- Separate track and thumb elements
- Value displayed in box on right
- 2px track height

**Template:**
- Native `<input type="range">` with custom styling
- Number input paired with slider
- 4px track height

---

### 3.4 Toggle Switches (SIMILAR but different styling)

**Mockup:**
```css
.switch-ui {
    width: 36px;
    height: 20px;
    background: var(--accent-blue);
    border-radius: 10px;
}
```

**Template:**
```css
.toggle {
    width: 36px;
    height: 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}
```

**Gap:** Same structure, different colors. Template uses dark theme colors.

---

### 3.5 Stats Display (DIFFERENT)

**Mockup:**
- Grid of glass boxes at top of right sidebar
- Large value text with colored accents

**Template:**
- Stats panel at bottom of right sidebar
- Grid layout with muted styling

---

### 3.6 Tag/Chip Styling (DIFFERENT)

**Mockup:**
```css
.tag {
    padding: 4px 8px;
    background: oklch(100% 0 0 / 30%);
    border-radius: 4px;
}
```

**Template:**
```css
.chip {
    padding: 5px 10px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-radius: 14px;
}
```

---

## 4. Control Gaps

### 4.1 Floating Overlays (MISSING in template as styled elements)

**Mockup has:**
- `.perf-overlay` - Performance stats floating over canvas
- `.hw-overlay` - Hardware info floating over canvas

**Template has:**
- `#perf-hud` - Similar but hidden by default, different position

---

### 4.2 Footer Icon (MISSING)

**Mockup has:**
```html
<footer style="position: fixed; bottom: 12px; left: 12px;">
    <div class="icon-btn glass"><!-- logout icon --></div>
</footer>
```

**Template has:** No footer element.

---

## 5. Typography Gap

**Mockup:** `'Roboto Mono', monospace`
**Template:** `-apple-system, BlinkMacSystemFont, 'SF Pro Text', system-ui, sans-serif`

**Gap:** Mockup uses monospace throughout. Template uses system sans-serif.

---

## Implementation Roadmap

### Phase 1: Token Integration (DONE)
- [x] Add `aquarela` theme to `theme.tokens.json`
- [x] Extract all OKLCH color values
- [x] Add glass effect tokens
- [x] Add watercolor gradient tokens

### Phase 2: Theme Switcher
- [ ] Add theme selection control to UI
- [ ] Wire TokenResolver to inject aquarela theme CSS
- [ ] Test theme switching without page reload

### Phase 3: Structural Changes (High Effort)
- [ ] Add icon sidebar option to layout
- [ ] Implement glass panel styling
- [ ] Add watercolor background layer
- [ ] Add noise overlay

### Phase 4: Component Updates (Medium Effort)
- [ ] Update section headers for mockup style
- [ ] Add pill button variant
- [ ] Update slider styling
- [ ] Add floating overlay positioning

---

## Files to Modify

| File | Changes |
|------|---------|
| `template.html` | Add icon sidebar, watercolor background layers |
| `styles.css` | Add `.glass`, `.panel-*`, watercolor backgrounds |
| `sidebar.js` | Add theme switcher control |
| `token_resolver.py` | Handle new aquarela tokens |
| `app.js` | Apply theme-specific rendering options |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Performance (blur effects) | Feature-flag glassmorphism, fallback to solid |
| Browser support (OKLCH) | Already handled by color-engine.js fallbacks |
| Layout breaking | Incremental rollout, A/B test with current users |
