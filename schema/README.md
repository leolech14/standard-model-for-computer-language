# Canonical Data Directory

> **Single source of truth** for all Standard Model data.

## Structure

```
canonical/
├── fixed/      # 🔒 IMMUTABLE - Theory axioms
└── learned/    # 📈 MUTABLE - Edit here when learning
```

## Rules

### fixed/ - NEVER EDIT
These files define the theory's coordinate system. Changing them breaks existing classifications.

| File | Contains | Count |
|------|----------|-------|
| `atoms.json` | 167 atom taxonomy | Fixed |
| `dimensions.json` | 8 semantic dimensions | Fixed |
| `roles.json` | 33 canonical roles | Fixed |

### learned/ - EDIT HERE
These files grow with learning. This is the ONLY place to add new patterns.

| File | Contains | Dynamic |
|------|----------|---------|
| `patterns.json` | Prefix/suffix/path patterns | Yes |
| `ledger.md` | Changelog of what was added | Yes |

## How to Add a New Pattern

1. Edit `canonical/learned/patterns.json`
2. Add entry to `canonical/learned/ledger.md`
3. Run tests to verify

## 🔄 Update Checklists

### When Adding a NEW PATTERN

1. Edit `learned/patterns.json`
   - Add to `prefix_patterns`, `suffix_patterns`, or `path_patterns`
   - Set `role` and `confidence`
2. Log in `learned/ledger.md`
   - Date, pattern, type, role, confidence
3. Verify: Run `python3 -c "from core.registry.pattern_repository import get_pattern_repository; r=get_pattern_repository(); print(len(r.get_prefix_patterns()))"`

### When Adding a NEW ROLE

1. Edit `fixed/roles.json`
   - Add role name and purpose
2. Update `docs/DIMENSIONS.md` if needed

### When Adding a NEW ATOM

> ⚠️ This is rare - only if AST coverage is incomplete

1. Edit `fixed/atoms.json`
2. Update `docs/ATOMS_REFERENCE.md`

---

## 📁 File Map

| File | Edit When... |
|------|-------------|
| `learned/patterns.json` | Learning new patterns |
| `learned/ledger.md` | Logging pattern changes |
| `fixed/atoms.json` | Never (167 is complete) |
| `fixed/dimensions.json` | Never (8D is stable) |
| `fixed/roles.json` | Rarely (33 roles) |

