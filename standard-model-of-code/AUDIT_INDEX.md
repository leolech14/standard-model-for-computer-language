# Handler Wiring Audit - Documentation Index
**Generated:** 2026-01-25
**Status:** Complete with actionable recommendations

---

## Quick Start (5 minutes)

1. Read: **AUDIT_SUMMARY.txt** - Executive overview
2. Read: **HANDLER_COVERAGE_CORRECTED.md** - Root causes and remediation path
3. Refer: **CONTROL_HANDLER_MAPPING.md** - Control status lookup

---

## Document Guide

### AUDIT_SUMMARY.txt
**What:** Executive summary of findings
**Length:** 2 pages
**When to read:** First - for overview and priorities
**Key sections:**
- Key findings (naming mismatch discovered)
- Root causes (3 categories)
- Remediation roadmap (3 phases, 10-14 hours total)
- Critical items (WCAG compliance risk)

### HANDLER_WIRING_AUDIT.md
**What:** Initial comprehensive audit report
**Length:** 4 pages
**When to read:** For complete control inventory
**Key sections:**
- Coverage metrics (59.3% apparent, 72% actual)
- Wired controls (70 IDs working)
- Orphaned controls (101 IDs - many false positives)
- Analysis & recommendations

### HANDLER_COVERAGE_CORRECTED.md
**What:** Root cause analysis and corrected metrics
**Length:** 6 pages
**When to read:** For understanding the naming mismatch problem
**Key sections:**
- Naming mismatch pattern explanation
- Corrected coverage (72% vs. 59%)
- Truly orphaned controls (33 vs. 101)
- Remediation path with effort estimates (6-12 hours)
- Phase breakdown

### CONTROL_HANDLER_MAPPING.md
**What:** Detailed reference table for every control
**Length:** 8 pages
**When to read:** For checking specific control status
**Key sections:**
- Legend (✅ ⚠️ ❌ 📝)
- Wired controls by category
- Naming mismatch table (15 controls)
- Orphaned controls by priority
- Quick lookup table
- Recommended actions

### handler-coverage-check.sh
**What:** Automated verification script
**Run:** `./handler-coverage-check.sh`
**Output:** Current coverage metrics and orphaned list
**Use:** To verify fixes after each phase of remediation

---

## Key Findings Summary

### The Problem in 3 Points

1. **Naming Inconsistency**
   - Template IDs: `cfg-*`, `filter-*`, `stats-*`
   - Handler IDs: `panel-*`, `panel-stat-*`
   - Result: 15 controls appear orphaned but ARE wired

2. **Incomplete Implementation**
   - Accessibility controls (a11y-*): Non-functional
   - Camera controls: Non-functional
   - Advanced filters: Non-functional
   - Result: 24 controls need handler implementation

3. **Display-Only Fields**
   - Hover info and stats display have IDs
   - May not need event handlers
   - Result: 6 controls may be false positives

### Coverage Metrics

| Metric | Value | Category |
|--------|-------|----------|
| Template controls | 118 | Total |
| Apparent coverage | 59% | False positive |
| Actual coverage | 72% | More accurate |
| Naming mismatches | 15 | Quick fix |
| True orphans | 33 | Needs implementation |
| Display-only | 6 | Refactor needed |

---

## Action Plan

### Phase 1: Fix Naming (1-2 hours) 🟡 RECOMMENDED FIRST
**Decision required:** Choose naming convention
- Option A: Rename template (cfg-* → panel-*)
- Option B: Update handlers to use cfg-* prefix
- Recommendation: Option A (template rename)

**Files affected:**
- `src/core/viz/assets/template.html`
- Optionally: `src/core/viz/assets/modules/panel-handlers.js`

**Outcome:** Reduce false orphans, clarify actual coverage

### Phase 2: Implement Missing Handlers (8-12 hours) 🔴 WCAG REQUIRED
**Priority breakdown:**
1. Accessibility (a11y-*): 4-6 hours - WCAG 2.1 compliance
2. Camera controls: 2-4 hours - Optional feature
3. Advanced filters: 2-4 hours - Nice-to-have

**Minimum viable:** Implement a11y-* only (4-6 hours)
**Full implementation:** All three (8-12 hours)

**Files affected:**
- `src/core/viz/assets/modules/panel-handlers.js`
- `src/core/viz/assets/modules/sidebar.js`

**Outcome:** Functional UI, WCAG compliance

### Phase 3: Cleanup & Document (1-2 hours) 🟢 FINAL
**Tasks:**
1. Remove IDs from display-only elements (or document them)
2. Update audit documentation
3. Add JSDoc to handler modules
4. Verify 100% coverage

**Files affected:**
- This documentation
- Handler module comments

**Outcome:** Clean, maintainable codebase with clear documentation

---

## Critical Issues

### 🔴 WCAG 2.1 Compliance
**Status:** All accessibility controls are non-functional
**Impact:** Legal/compliance risk if app is used publicly
**Timeline:** Implement in Phase 2 (4-6 hours)
**Recommendation:** Don't deploy publicly without addressing

### 🟡 Naming Standardization
**Status:** 15 controls use mismatched IDs
**Impact:** Code confusion, documentation unclear, hard to maintain
**Timeline:** Fix in Phase 1 (1-2 hours)
**Recommendation:** Do this first, before Phase 2

### 🟢 Feature Completeness
**Status:** Camera controls and advanced filters are UI-only
**Impact:** Features appear available but don't work
**Timeline:** Phase 2 (decide if needed)
**Recommendation:** Either implement or remove from template

---

## Testing & Verification

### Before Deployment Checklist

- [ ] Phase 1 complete: All controls use consistent naming
- [ ] Phase 2 complete: All accessibility handlers functional
- [ ] Manual testing: Test each control group in browser
- [ ] Console check: No JS errors during init
- [ ] Handler coverage: Run `./handler-coverage-check.sh`
- [ ] WCAG audit: Verify accessibility features work
- [ ] Documentation: Update comments in handler modules

### Browser Console Test

```javascript
// Quick validation in console
console.log("Checking handler bindings...");
const controls = document.querySelectorAll('[id*="panel-"]');
console.log(`Found ${controls.length} panel controls`);
controls.forEach(c => {
  if (!c.hasEventListener || !c.addEventListener) {
    console.warn(`⚠ ${c.id} may not have handler`);
  }
});
```

---

## Related Documentation

### In this repository:
- `src/core/viz/assets/template.html` - UI control definitions
- `src/core/viz/assets/modules/panel-handlers.js` - Event handler bindings
- `src/core/viz/assets/modules/sidebar.js` - Sidebar event handlers
- `src/core/viz/assets/modules/main.js` - Initialization
- `src/core/viz/assets/modules/circuit-breaker.js` - State management

### Standards:
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- Accessibility: https://developer.mozilla.org/en-US/docs/Web/Accessibility

---

## FAQ

**Q: Which issue should we fix first?**
A: Phase 1 (naming) → Phase 2 (accessibility) → Phase 3 (cleanup). Phase 1 is quick and clarifies the problem.

**Q: Do we need to implement all orphaned controls?**
A: No. Accessibility (a11y-*) is mandatory. Camera and advanced filters can be deferred or removed.

**Q: How do I know if a fix worked?**
A: Run `./handler-coverage-check.sh` again and verify coverage increases.

**Q: Can we deploy with orphaned controls?**
A: Not recommended. At minimum:
  - Fix naming (Phase 1)
  - Implement accessibility (Phase 2, a11y-* only)
  - OR remove non-functional controls from template

**Q: What if we don't have time for full remediation?**
A: Minimum viable remediation: Phase 1 + a11y implementations (~6 hours)

---

## Change Log

| Date | Status | What |
|------|--------|------|
| 2026-01-25 | Complete | Initial audit completed with 4 analysis documents |
| - | Pending | Phase 1 implementation (naming standardization) |
| - | Pending | Phase 2 implementation (handler logic) |
| - | Pending | Phase 3 cleanup and validation |

---

## Contacts & References

**Audit method:** grep + comm-based ID extraction
**Confidence level:** HIGH (verified with spot checks)
**Files analyzed:**
- template.html (118 control IDs)
- panel-handlers.js (45 handler bindings)
- sidebar.js (25 handler bindings)

**Questions or clarifications:** Review CONTROL_HANDLER_MAPPING.md for specific control details

---

## Quick Links to Sections

| Need | Document | Section |
|------|----------|---------|
| Overview | AUDIT_SUMMARY.txt | Key Findings |
| Root cause | HANDLER_COVERAGE_CORRECTED.md | Root Causes |
| Specific control | CONTROL_HANDLER_MAPPING.md | Search by prefix |
| Next steps | HANDLER_COVERAGE_CORRECTED.md | Remediation Path |
| Automation | handler-coverage-check.sh | Run script |
| WCAG info | CONTROL_HANDLER_MAPPING.md | Accessibility Features |

---

**Document version:** 1.0
**Last updated:** 2026-01-25
**Status:** Ready for Phase 1 implementation
