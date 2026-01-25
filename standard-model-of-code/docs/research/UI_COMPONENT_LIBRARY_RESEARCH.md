# UI Component Library Research

**Date:** 2026-01-25
**Phase:** Context Gathering for UI Overhaul
**Purpose:** Identify battle-tested, production-proven components to adapt for Collider

---

## Executive Summary

Instead of building from scratch, we can leverage components that power apps used by millions. This research identifies the best-in-class libraries for each UI component category we need.

**Key Finding:** The combination of **Blueprint UI** (Palantir) + **react-resizable-panels** + **react-arborist** + **cmdk** provides a complete, production-proven stack for IDE-like interfaces.

---

## Component Requirements Matrix

| Component | Our Need | Best Option | Backup |
|-----------|----------|-------------|--------|
| Sidebar panels | Collapsible left/right panels | Blueprint UI | Allotment |
| Resizable panes | Split view layout | react-resizable-panels | Allotment |
| Tree view | Node hierarchy explorer | react-arborist | react-complex-tree |
| Command palette | Ctrl+K quick actions | cmdk | kbar |
| Sliders/controls | Parameter adjustments | Blueprint UI | Radix + custom |
| Tabs | View switching | Blueprint UI | Radix Tabs |
| Property panel | Node inspector | Blueprint UI | Custom |
| Buttons/toggles | Basic controls | Blueprint UI | Shadcn/ui |

---

## Category 1: Full UI Frameworks

### Blueprint UI (Palantir) - RECOMMENDED

**The IDE-grade choice.** Built by Palantir for complex, data-dense desktop applications.

| Attribute | Value |
|-----------|-------|
| Package | `@blueprintjs/core`, `@blueprintjs/icons`, `@blueprintjs/select` |
| GitHub | [palantir/blueprint](https://github.com/palantir/blueprint) - 20k+ stars |
| Used by | Palantir Foundry, internal tools at major enterprises |
| Framework | React (required) |
| License | Apache 2.0 |

**Components included:**
- Tree, TreeNode (file explorer style)
- Tabs, Tab
- Slider, RangeSlider
- Button, ButtonGroup, Switch, Checkbox
- Popover, Dialog, Drawer
- Menu, MenuItem (context menus)
- Card, Collapse, Divider
- InputGroup, NumericInput
- Tag, TagInput
- Toaster (notifications)

**Why Blueprint:**
> "Optimized for building complex, data-dense web interfaces for desktop applications. This is NOT a mobile-first UI toolkit."

This matches Collider's needs exactly.

**Docs:** https://blueprintjs.com/

---

### Ant Design (AntD) - Alternative

**The enterprise choice.** Built by Alibaba for complex internal tools.

| Attribute | Value |
|-----------|-------|
| Package | `antd` |
| GitHub | [ant-design/ant-design](https://github.com/ant-design/ant-design) - 91k+ stars |
| Used by | Alibaba, Tencent, Baidu, many Chinese enterprises |
| Framework | React (required) |
| License | MIT |

**Components included:**
- Tree, TreeSelect, DirectoryTree
- Tabs
- Slider
- All basic controls
- Layout components (Sider, Content)

**Why consider:**
- Massive community
- Excellent documentation
- Strong TypeScript support

**Docs:** https://ant.design/

---

## Category 2: Resizable Panel Layout

### react-resizable-panels - RECOMMENDED

**The gold standard for IDE-like layouts.**

| Attribute | Value |
|-----------|-------|
| Package | `react-resizable-panels` |
| GitHub | [bvaughn/react-resizable-panels](https://github.com/bvaughn/react-resizable-panels) - 3.5k+ stars |
| Author | Brian Vaughn (former React core team) |
| Weekly downloads | 1M+ |

**Features:**
- Horizontal and vertical layouts
- Collapsible panels
- Min/max size constraints
- Snapping behavior
- Layout persistence (localStorage)
- Keyboard accessibility
- Works with React 18

**Usage:**
```jsx
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

<PanelGroup direction="horizontal">
  <Panel defaultSize={20} minSize={10}>
    {/* Left sidebar */}
  </Panel>
  <PanelResizeHandle />
  <Panel>
    {/* Main content - Three.js canvas */}
  </Panel>
  <PanelResizeHandle />
  <Panel defaultSize={25} minSize={15}>
    {/* Right sidebar */}
  </Panel>
</PanelGroup>
```

**Docs:** https://react-resizable-panels.vercel.app/

---

### Allotment - Alternative

| Attribute | Value |
|-----------|-------|
| Package | `allotment` |
| GitHub | [johnwalley/allotment](https://github.com/johnwalley/allotment) - 900+ stars |
| Used by | VS Code-like layouts |

**Features:**
- Split pane resizing
- Preferred size on double-click reset
- Snapping support
- Works with Next.js (with SSR workaround)

---

## Category 3: Tree View / File Explorer

### react-arborist - RECOMMENDED

**The VS Code sidebar experience.**

| Attribute | Value |
|-----------|-------|
| Package | `react-arborist` |
| GitHub | [brimdata/react-arborist](https://github.com/brimdata/react-arborist) - 2.8k+ stars |
| Used by | Brim Security, various IDEs |

**Features:**
- Virtualized (handles 10,000+ nodes)
- Drag-and-drop
- Multi-selection
- Inline editing (rename)
- Keyboard navigation
- Customizable node rendering

**Why react-arborist:**
> "Provides the React ecosystem with a complete solution to build the equivalent of a VSCode sidebar, Mac Finder, Windows Explorer, or Sketch/Figma layers panel."

**Usage:**
```jsx
import { Tree } from "react-arborist";

<Tree
  data={nodes}
  width={280}
  height={600}
  indent={24}
  rowHeight={28}
  onSelect={(nodes) => handleSelection(nodes)}
>
  {Node}
</Tree>
```

**Docs:** https://github.com/brimdata/react-arborist

---

### react-complex-tree - Alternative (Multi-tree scenarios)

| Attribute | Value |
|-----------|-------|
| Package | `react-complex-tree` |
| GitHub | [lukasbach/react-complex-tree](https://github.com/lukasbach/react-complex-tree) - 900+ stars |

**When to use instead:**
- Need W3C accessibility compliance
- Multiple trees sharing state
- Complex drag-and-drop between trees

**Note:** Successor library `headless-tree` is in beta with virtualization support.

---

## Category 4: Command Palette

### cmdk - RECOMMENDED

**The Vercel/Linear experience.**

| Attribute | Value |
|-----------|-------|
| Package | `cmdk` |
| GitHub | [pacocoursey/cmdk](https://github.com/pacocoursey/cmdk) - 9k+ stars |
| Used by | Vercel, Linear, Raycast-style apps |
| Author | Paco Coursey (Vercel) |

**Features:**
- Composable API
- Fuzzy search built-in
- Keyboard navigation
- Unstyled (you control appearance)
- Accessible

**Usage:**
```jsx
import { Command } from "cmdk";

<Command>
  <Command.Input placeholder="Type a command..." />
  <Command.List>
    <Command.Group heading="Navigation">
      <Command.Item onSelect={() => navigate('/atoms')}>
        Go to Atoms View
      </Command.Item>
      <Command.Item onSelect={() => navigate('/files')}>
        Go to Files View
      </Command.Item>
    </Command.Group>
    <Command.Group heading="Actions">
      <Command.Item onSelect={() => screenshot()}>
        Take Screenshot
      </Command.Item>
    </Command.Group>
  </Command.List>
</Command>
```

**Docs:** https://cmdk.paco.me/

---

### kbar - Alternative

| Attribute | Value |
|-----------|-------|
| Package | `kbar` |
| GitHub | [timc1/kbar](https://github.com/timc1/kbar) - 4.5k+ stars |

**When to use instead:**
- Need simpler plug-and-play setup
- Less customization required

**Docs:** https://kbar.vercel.app/

---

## Category 5: Sliders and Controls

### Blueprint UI Sliders - RECOMMENDED

Blueprint includes production-ready sliders:
- `Slider` - Single value
- `RangeSlider` - Min/max range
- `MultiSlider` - Multiple handles

**Features:**
- Label formatting
- Step increments
- Vertical orientation
- Disabled states

---

### Radix UI Slider - Alternative (Headless)

| Attribute | Value |
|-----------|-------|
| Package | `@radix-ui/react-slider` |

For maximum styling control with accessibility built-in.

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     react-resizable-panels                          │
│  ┌──────────────┬────────────────────────────┬──────────────────┐   │
│  │              │                            │                  │   │
│  │  react-      │                            │  Blueprint UI    │   │
│  │  arborist    │      Three.js Canvas       │  (Properties)    │   │
│  │  (Tree)      │      (Your graph)          │                  │   │
│  │              │                            │  - Sliders       │   │
│  │  Blueprint   │                            │  - Toggles       │   │
│  │  UI controls │                            │  - Tabs          │   │
│  │              │                            │                  │   │
│  └──────────────┴────────────────────────────┴──────────────────┘   │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    cmdk (Command Palette)                     │  │
│  │                    Ctrl+K / Ctrl+Shift+P                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Migration Consideration

**Current state:** Vanilla JS modules in `src/core/viz/assets/modules/*.js`

**Options:**

1. **Hybrid approach** - Keep Three.js canvas vanilla, wrap sidebars in React
   - Use `react-dom/client` to mount React components into specific divs
   - Three.js canvas remains untouched
   - Communicate via custom events or shared state

2. **Full React migration** - Migrate entire app to React
   - Higher effort
   - Better long-term maintainability
   - Use `@react-three/fiber` for Three.js

3. **Web Components** - Use libraries that export web components
   - Blueprint UI is React-only (not an option)
   - Some alternatives exist but less mature

**Recommendation:** Option 1 (Hybrid) for incremental migration.

---

## Package Summary

```bash
# Core UI framework
npm install @blueprintjs/core @blueprintjs/icons @blueprintjs/select

# Layout
npm install react-resizable-panels

# Tree view
npm install react-arborist

# Command palette
npm install cmdk

# React (if not already)
npm install react react-dom
```

---

## Next Steps

1. **Spike:** Create proof-of-concept with Blueprint + react-resizable-panels
2. **Evaluate:** Test react-arborist with our node data structure
3. **Design:** Map our 82 controls to Blueprint components
4. **Plan:** Determine hybrid vs full React migration path

---

## Sources

- [Blueprint UI - Palantir](https://blueprintjs.com/)
- [react-resizable-panels - GitHub](https://github.com/bvaughn/react-resizable-panels)
- [react-arborist - GitHub](https://github.com/brimdata/react-arborist)
- [cmdk - GitHub](https://github.com/pacocoursey/cmdk)
- [kbar - GitHub](https://github.com/timc1/kbar)
- [Ant Design](https://ant.design/)
- [Allotment - GitHub](https://github.com/johnwalley/allotment)
- [react-complex-tree - GitHub](https://github.com/lukasbach/react-complex-tree)
