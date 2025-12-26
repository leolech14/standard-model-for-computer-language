# THE OCTAHEDRAL ATOM

> *Every code atom is an octahedron. Its 8 faces are its 8 dimensions.*

---

## The Shape of an Atom

```
           ◢ STATE ◣
          /    |    \
         /     |     \
      WHAT ────┼──── ROLE
         \     |     /
          \    |    /
           ◤ EFFECT ◥

     (+ LAYER, BOUNDARY, LIFECYCLE, TRUST on remaining faces)
```

---

## Geometry

| Property | Count | Meaning |
|----------|-------|---------|
| **Faces** | 8 | The 8 dimensions of analysis |
| **Vertices** | 6 | Maximum intersection points |
| **Edges** | 12 | Relationships between dimensions |

---

## The 8 Faces (Dimensions)

Each face of the octahedron carries one dimension of metadata:

| Face | Dimension | Question | Data Type |
|------|-----------|----------|-----------|
| **1** | WHAT | What is this? | Atom type (1 of 200) |
| **2** | LAYER | Where in architecture? | Interface/App/Core/Infra/Test |
| **3** | ROLE | What's its purpose? | Role name (1 of 33) |
| **4** | BOUNDARY | Does it cross boundaries? | Internal/Input/I-O/Output |
| **5** | STATE | Does it maintain state? | Stateful/Stateless |
| **6** | EFFECT | Does it have side effects? | Pure/Read/Write/ReadModify |
| **7** | LIFECYCLE | In what phase? | Create/Use/Destroy |
| **8** | TRUST | What's the confidence? | 0-100% |

---

## The 6 Vertices (Intersection Points)

The vertices represent maximum dimensional overlap:

| Vertex | Position | Intersecting Dimensions |
|--------|----------|-------------------------|
| **V1** | Top | STATE + LAYER + WHAT + ROLE |
| **V2** | Bottom | EFFECT + BOUNDARY + LIFECYCLE + TRUST |
| **V3** | Front | WHAT + STATE + EFFECT + BOUNDARY |
| **V4** | Back | ROLE + STATE + EFFECT + TRUST |
| **V5** | Left | LAYER + STATE + EFFECT + LIFECYCLE |
| **V6** | Right | BOUNDARY + STATE + EFFECT + TRUST |

---

## The 12 Edges (Dimensional Relationships)

Each edge represents a valid question combining two dimensions:

1. STATE ↔ WHAT: "What state does this type hold?"
2. STATE ↔ ROLE: "How does state relate to purpose?"
3. STATE ↔ EFFECT: "What effects does state cause?"
4. EFFECT ↔ WHAT: "What effects does this type produce?"
5. EFFECT ↔ ROLE: "How do effects serve purpose?"
6. WHAT ↔ ROLE: "What types fulfill this role?"
7. LAYER ↔ BOUNDARY: "Which layers cross which boundaries?"
8. LAYER ↔ LIFECYCLE: "How does layer affect lifecycle?"
9. BOUNDARY ↔ TRUST: "What trust for boundary-crossing code?"
10. LIFECYCLE ↔ TRUST: "How does lifecycle affect confidence?"
11. ROLE ↔ LAYER: "What roles exist at each layer?"
12. WHAT ↔ LAYER: "What atom types at each layer?"

---

## Opposed Faces (Dual Dimensions)

Opposite faces represent complementary perspectives:

| Face 1 | Face 2 | Duality |
|--------|--------|---------|
| STATE | EFFECT | Internal ↔ External |
| WHAT | ROLE | Structure ↔ Purpose |
| LAYER | BOUNDARY | Position ↔ Transition |
| LIFECYCLE | TRUST | Time ↔ Confidence |

---

## Visual Representation

### Flat Projection (Net)

```
         ┌─────────┐
         │ LIFECYCLE│
┌────────┼─────────┼────────┐
│ LAYER  │  STATE  │ BOUNDARY│
├────────┼─────────┼────────┤
│  WHAT  │ (center)│  ROLE   │
├────────┼─────────┼────────┤
│        │ EFFECT  │        │
└────────┼─────────┼────────┘
         │  TRUST  │
         └─────────┘
```

### Side View (Diamond)

```
       STATE
         ◆
        /|\
       / | \
      /  |  \
     ◇───┼───◇
      \  |  /
       \ | /
        \|/
         ◆
       EFFECT
```

---

## Why Octahedron?

1. **Exactly 8 faces** - Perfect for 8 dimensions
2. **Dual of cube** - Mathematical elegance (cube has 8 vertices, 6 faces)
3. **Symmetric** - All faces are equilateral triangles
4. **No privileged face** - All dimensions are equally accessible
5. **Natural for visualization** - Easy to render, rotate, inspect

---

## Atom Data Structure

```json
{
  "id": "example_function",
  "type": "Function",
  "octahedron": {
    "WHAT": "LOG.FNC.M",
    "LAYER": "Application",
    "ROLE": "Controller",
    "BOUNDARY": "Input",
    "STATE": "Stateless",
    "EFFECT": "ReadModify",
    "LIFECYCLE": "Use",
    "TRUST": 0.87
  }
}
```

---

## Implications

### 1. Every Atom is Complete
Every atom carries all 8 dimensions. No dimension is optional.

### 2. Analysis is Rotation
Analyzing code through different dimensions is like rotating the octahedron to see different faces.

### 3. Unknown is Valid
A face value of "Unknown" means that dimension hasn't been analyzed yet, not that it doesn't exist.

### 4. Edges are Questions
The 12 edges generate 12 cross-dimensional questions we can ask about any atom.

---

> *"The octahedron is not the territory. It is the shape of our understanding."*

**Version:** 2.1.0  
**Formalized:** 2025-12-26
