# Research: We have two 3D tree layout algorithms to choose between for file system visualization:

**Option A: ...

> **Date:** 2026-01-23 17:06:14
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:7f4ab1f65ae30f4f7a31e56d80c6fb23f7c6f3cf9b3b3d2d266578d56df56ec3`
> **Raw JSON:** `raw/20260123_170614_we_have_two_3d_tree_layout_algorithms_to_choose_be.json`

---

## Query

We have two 3D tree layout algorithms to choose between for file system visualization:

**Option A: Cone Tree (Xerox PARC style)**
- Parent at apex, children spread conically below
- Uses full 3D space
- Good for exploring deep hierarchies
- Already implemented in our codebase

**Option B: Classic 2.5D Tree (Reingold-Tilford)**
- Root at top, children below in layers
- "Thick layers" per depth level
- Standard convention (macOS Finder, VS Code, Unix tree)
- Matches user mental model of "enter directory = go down"

**Questions:**
1. For file system navigation, which layout is more intuitive for users?
2. Can we have BOTH and switch between them? (Cone for exploration, Classic for navigation)
3. In d3-hierarchy, what's the difference between tree() vs cluster() for our use case?
4. Any UX research on 3D file managers (e.g., FSN from Jurassic Park, BumpTop)?

---

## Response

## File System Visualization Layout Comparison

**For file system navigation, the classic 2D tree layout (Reingold-Tilford style) is more intuitive than Cone Trees.** Research shows that when users interact with traditional tree interfaces versus 3D Cone Trees, they perform significantly better with the standard hierarchical layout.[2] In empirical evaluation, the traditional tree layout has proven to be the objectively preferred choice when compared to other visualization styles, with much of this performance advantage attributed to user familiarity with the standard representation.[7]

### Why Cone Trees Underperform for File Systems

Cone Trees have important limitations for your use case. While they maximize available screen space and provide an overall view of hierarchical structure, the traditional Cone Tree could only handle roughly 1,000 nodes before visual clutter hindered its usefulness.[2] Even with improvements that added graphical and interaction techniques, the fundamental issue remains: users follow paths more quickly with normal-tree interfaces than with Cone Tree interfaces.[2] This matters for file system navigation, where users need to efficiently locate and access specific directories.

### Hybrid Approach Feasibility

**Yes, providing both layouts with switching capability is viable and has precedent.** One documented system implements exactly this pattern: "portions of the tree are drawn as either nested or node-link representations dependent on screen space and user interaction."[7] This adaptive approach allows you to preserve the benefits of each representation—using Cone Trees for high-level exploration and the classic layout for precise navigation.

Additionally, the **EncCon technique combines enclosure and node-link approaches across an entire tree**, demonstrating that hybrid visualization methods work in practice for hierarchical data.[7]

### d3-hierarchy: tree() vs cluster()

The search results do not contain specific technical documentation comparing `tree()` vs `cluster()` in d3-hierarchy. However, based on the general principles discussed: `tree()` typically produces a Reingold-Tilford-style layout with variable spacing between nodes based on the tree structure, while `cluster()` produces a layout where leaf nodes are evenly spaced (creating the "thick layers per depth level" effect you described). For file system visualization matching user expectations, `tree()` is likely the better foundation, as it preserves the hierarchical depth relationships that users expect when navigating directories.

### 3D File Managers Research

The search results do not contain documented UX research on FSN, BumpTop, or other specific 3D file managers. The available research focuses on abstract hierarchical visualization systems rather than production file manager implementations. To properly evaluate those systems, you would need to consult specialized HCI literature or user studies specific to those applications.

---

## Citations

1. https://diglib.eg.org/bitstreams/9da99c58-7a7a-4c73-bfec-362d03bd9b50/download
2. https://scholarwolf.unr.edu/server/api/core/bitstreams/8074f8ce-d943-4cfa-a965-d4c23267076d/content
3. https://dl.acm.org/doi/pdf/10.5555/1082121.1082131
4. https://treevis.net/treevis.bib
5. https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf
6. https://opus.lib.uts.edu.au/bitstream/10453/20340/4715/02Whole.pdf
7. http://cluster.cis.drexel.edu/~cchen/ivs/sample.pdf
8. https://www.cs.kent.edu/~jmaletic/cs63903/papers/Herman00.pdf
9. https://graphics.stanford.edu/papers/munzner_thesis/allbw.pdf

---

## Usage Stats

- Prompt tokens: 222
- Completion tokens: 530
- Total tokens: 752
