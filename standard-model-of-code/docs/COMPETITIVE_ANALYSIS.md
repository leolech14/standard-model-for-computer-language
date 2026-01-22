# COMPETITIVE ANALYSIS & MODULE ROADMAP

> Collider's market position and extensibility roadmap.
>
> **Created:** 2026-01-22
> **Status:** Living document

---

## CURRENT STATE (v1.0)

### What Collider Does Uniquely

| Capability | Status | Competitors |
|------------|--------|-------------|
| 8-Dimensional Classification | ✅ Implemented | None |
| Standard Model Theory (200 atoms, 33 roles) | ✅ Implemented | None |
| 3D Force-Directed Graph Visualization | ✅ Implemented | None |
| Purity Scoring (D6:EFFECT) | ✅ Implemented | None |
| RPBL Character Analysis | ✅ Implemented | None |
| Graph Centrality (PageRank, Betweenness) | ✅ Implemented | None |
| Topology Role Detection | ✅ Implemented | None |
| UPB Visual Property Binding | ✅ Implemented | None |
| Tree-sitter AST Analysis | ✅ Implemented | Partial (Semgrep) |

### Current Metrics (Self-Analysis)

```
Nodes analyzed:        2,107
Edges extracted:       5,860
Files processed:       173
Processing time:       18.1s
Dimension coverage:    99.7%
Tree-sitter coverage:  82.6%
Languages supported:   5 (Python, JS/TS, Go, Rust)
```

---

## COMPETITIVE LANDSCAPE

### Market Leaders

| Tool | Focus | Price | Strengths |
|------|-------|-------|-----------|
| **SonarQube** | Code Quality + Security | $500+/yr | 30+ languages, CI/CD, enterprise |
| **Semgrep** | Custom Rules + Security | Free-$100/mo | Flexible, fast, open source |
| **Snyk Code** | Security-First | $57+/user/mo | Real-time, AI fixes |
| **CodeClimate** | Engineering Intelligence | $15+/user/mo | Team metrics, maintainability |
| **Coverity** | Enterprise Security | Enterprise | Deep analysis, compliance |
| **Veracode** | Compliance | Enterprise | OWASP, PCI-DSS, GDPR |

### Collider's Unique Position

```
Collider creates a NEW CATEGORY: Code Architecture Intelligence

Traditional tools ask: "Is this code secure/clean?"
Collider asks: "What IS this code? How does it behave? What role does it play?"
```

---

## FUTURE MODULE ROADMAP

### Architecture: Pluggable Modules

Collider's pipeline architecture supports pluggable modules at multiple extension points:

```
┌─────────────────────────────────────────────────────────────┐
│                    COLLIDER CORE                            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐    │
│  │ Parser  │→ │Analyzer │→ │Classifier│→ │ Visualizer │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬──────┘    │
│       │            │            │               │           │
│       ▼            ▼            ▼               ▼           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              EXTENSION POINTS                        │   │
│  │  • Language Modules    • Analysis Modules            │   │
│  │  • Security Modules    • Visualization Modules       │   │
│  │  • Integration Modules • Export Modules              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

### Module Opportunities

#### M1: Language Modules (Expand Coverage)

| Language | Priority | Effort | Tree-sitter Support |
|----------|----------|--------|---------------------|
| Java | HIGH | Medium | ✅ Available |
| C/C++ | HIGH | Medium | ✅ Available |
| C# | MEDIUM | Medium | ✅ Available |
| Ruby | MEDIUM | Low | ✅ Available |
| PHP | MEDIUM | Low | ✅ Available |
| Kotlin | MEDIUM | Low | ✅ Available |
| Swift | LOW | Low | ✅ Available |
| Scala | LOW | Medium | ✅ Available |

**Implementation Pattern:**
```
src/core/queries/{language}/
├── symbols.scm      # Required: function/class extraction
├── locals.scm       # Optional: scope analysis
├── patterns.scm     # Optional: atom detection
└── data_flow.scm    # Optional: purity analysis
```

---

#### M2: Security Modules (Address Gap)

| Module | Priority | Competitors | Integration Point |
|--------|----------|-------------|-------------------|
| **SAST Scanner** | HIGH | Semgrep, Snyk | Post-parse analysis |
| **Dependency Check** | HIGH | Snyk, OWASP | Import analysis |
| **Secret Detection** | MEDIUM | GitLeaks, Aikido | Pattern matching |
| **Taint Analysis** | MEDIUM | CodeQL | Data flow extension |
| **OWASP Top 10** | MEDIUM | All | Rule-based detection |

**Proposed Architecture:**
```python
# src/core/security/__init__.py
class SecurityModule:
    def analyze(self, nodes: List[Node], edges: List[Edge]) -> SecurityReport:
        """Run security checks on analyzed code."""
        pass

# Plugs into Stage 2.12 of pipeline
```

---

#### M3: Integration Modules (Enterprise Readiness)

| Integration | Priority | Effort | Value |
|-------------|----------|--------|-------|
| **GitHub Actions** | HIGH | Low | CI/CD automation |
| **GitLab CI** | HIGH | Low | CI/CD automation |
| **Jenkins Plugin** | MEDIUM | Medium | Enterprise CI |
| **VS Code Extension** | HIGH | Medium | Developer experience |
| **JetBrains Plugin** | MEDIUM | Medium | Developer experience |
| **Slack/Teams Alerts** | LOW | Low | Notifications |
| **Jira Integration** | LOW | Medium | Issue tracking |

**GitHub Action Example:**
```yaml
# .github/workflows/collider.yml
- name: Run Collider Analysis
  uses: collider/action@v1
  with:
    output: collider-report
    fail-on: critical-violations
```

---

#### M4: Export Modules (Interoperability)

| Format | Priority | Use Case |
|--------|----------|----------|
| **SARIF** | HIGH | GitHub Security, IDE integration |
| **SPDX** | MEDIUM | License compliance |
| **CycloneDX** | MEDIUM | SBOM generation |
| **GraphML** | LOW | Graph tool import |
| **DOT** | LOW | Graphviz visualization |

---

#### M5: Analysis Modules (Extend Theory)

| Module | Priority | Theory Link | Description |
|--------|----------|-------------|-------------|
| **Coupling Analyzer** | HIGH | Architecture | Afferent/efferent coupling |
| **Cohesion Analyzer** | HIGH | Architecture | LCOM metrics |
| **Change Risk** | MEDIUM | D7:LIFECYCLE | Churn + complexity hotspots |
| **Test Coverage Map** | MEDIUM | D8:TRUST | Coverage → graph overlay |
| **Performance Predictor** | LOW | Theory expansion | Complexity → runtime |
| **Refactoring Suggester** | LOW | All dimensions | AI-powered recommendations |

---

#### M6: Visualization Modules (Enhance UX)

| Module | Priority | Description |
|--------|----------|-------------|
| **Diff Visualization** | HIGH | Compare two analyses |
| **Time-lapse Mode** | MEDIUM | Animate codebase evolution |
| **AR/VR Export** | LOW | Spatial computing readiness |
| **Dependency Matrix** | MEDIUM | DSM (Design Structure Matrix) |
| **Treemap View** | LOW | Alternative to 3D graph |

---

## IMPLEMENTATION PRIORITY MATRIX

```
                        HIGH VALUE
                            │
     ┌──────────────────────┼──────────────────────┐
     │                      │                      │
     │   M2: Security    ★  │  ★  M1: Languages    │
     │   M3: GitHub CI      │     M3: VS Code      │
     │   M4: SARIF          │     M5: Coupling     │
     │                      │                      │
LOW ─┼──────────────────────┼──────────────────────┼─ HIGH
EFFORT                      │                      EFFORT
     │                      │                      │
     │   M6: Diff View      │     M5: AI Refactor  │
     │   M4: GraphML        │     M6: AR/VR        │
     │                      │                      │
     └──────────────────────┼──────────────────────┘
                            │
                        LOW VALUE
```

**Recommended Order:**
1. **M3: GitHub Actions** - Low effort, high visibility
2. **M4: SARIF Export** - Enables GitHub Security tab
3. **M1: Java Support** - Largest language gap
4. **M3: VS Code Extension** - Developer adoption
5. **M2: SAST Scanner** - Competitive necessity

---

## SUCCESS METRICS

### Current Baseline

| Metric | Current | Target (6mo) | Target (12mo) |
|--------|---------|--------------|---------------|
| Languages | 5 | 10 | 15 |
| CI/CD Integrations | 0 | 2 | 4 |
| IDE Plugins | 0 | 1 | 2 |
| Security Rules | 0 | 50 | 200 |
| Export Formats | 2 (JSON, HTML) | 4 | 6 |

### Competitive Parity Checklist

- [ ] Language coverage ≥ 15 (vs SonarQube 30)
- [ ] SARIF export for GitHub Security
- [ ] GitHub Actions integration
- [ ] VS Code extension
- [ ] Basic SAST rules (OWASP Top 10)
- [ ] Dependency vulnerability scanning

---

## STRATEGIC POSITIONING

### Don't Compete, Complement

Collider should NOT try to replace SonarQube/Snyk. Instead:

```
┌─────────────────────────────────────────────────────────────┐
│                    DEVELOPER WORKFLOW                        │
│                                                              │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Snyk    │    │ SonarQube│    │ Collider │              │
│  │ Security │    │ Quality  │    │ Architect│              │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘              │
│       │               │               │                     │
│       ▼               ▼               ▼                     │
│  "Is it secure?"  "Is it clean?" "What IS it?"             │
│                                   "How does it work?"       │
│                                   "What's the architecture?"│
└─────────────────────────────────────────────────────────────┘
```

### Unique Value Proposition

> **Collider is the only tool that treats code as a physical system with measurable properties across 8 dimensions, visualized in 3D, grounded in theory.**

This is NOT something SonarQube, Semgrep, or any competitor offers.

---

## DOCUMENT HISTORY

| Date | Change |
|------|--------|
| 2026-01-22 | Initial creation with competitive analysis and module roadmap |
