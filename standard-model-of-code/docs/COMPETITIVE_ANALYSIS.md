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

#### M7: Compliance Modules (Enterprise Requirement)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **OWASP Top 10** | HIGH | All major tools | Security vulnerability rules |
| **PCI-DSS Rules** | MEDIUM | Veracode, Checkmarx | Payment card compliance |
| **GDPR Data Flow** | MEDIUM | Snyk, SonarQube | Privacy compliance tracking |
| **Code Smell Rules** | HIGH | SonarQube, CodeClimate | Maintainability rules |
| **False Positive Tuning** | HIGH | All tools | Suppress/configure rules |

**Why needed:** Enterprise customers require compliance certifications. Without OWASP/PCI-DSS rules, Collider cannot be adopted in regulated industries.

---

#### M8: Cloud/SaaS Modules (Deployment Options)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Hosted SaaS** | HIGH | All major tools | Cloud-hosted analysis |
| **Multi-tenant** | MEDIUM | SonarCloud, Snyk | Organization support |
| **Multi-repo Support** | MEDIUM | All major tools | Monorepo + multi-repo |
| **Self-hosted Docker** | HIGH | SonarQube | On-prem deployment |

**Why needed:** Currently Collider is CLI-only. Teams need shared dashboards and centralized analysis.

---

#### M9: Collaboration Modules (Team Features)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **PR Comments** | HIGH | All CI tools | Auto-comment on PRs |
| **Issue Assignment** | MEDIUM | SonarQube, Snyk | Assign findings to devs |
| **Team Dashboards** | MEDIUM | CodeClimate | Aggregate team metrics |
| **Annotations API** | LOW | GitHub | In-file annotations |

**Why needed:** Individual analysis is useful; team-wide visibility drives adoption.

---

#### M10: Historical/Trends Modules (Time-Series)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Trend Charts** | HIGH | CodeClimate, SonarQube | Metrics over time |
| **Regression Detection** | HIGH | All CI tools | Alert on degradation |
| **Technical Debt Tracker** | MEDIUM | SonarQube | Debt accumulation |
| **Custom Dashboards** | LOW | Enterprise tools | Build custom reports |

**Why needed:** Point-in-time analysis is insufficient. Teams need to see improvement/degradation trends.

---

#### M11: Quality Gates Modules (CI Blocking)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Pass/Fail Thresholds** | HIGH | All CI tools | Block merge on violations |
| **Custom Gate Rules** | MEDIUM | SonarQube | Define custom criteria |
| **Baseline Comparison** | MEDIUM | Snyk | Compare to baseline |
| **Branch Policies** | LOW | GitHub/GitLab | Enforce on specific branches |

**Why needed:** Without quality gates, Collider is advisory-only. Teams need enforcement.

---

#### M12: Incremental Analysis Modules (Performance)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Diff-only Analysis** | HIGH | Semgrep, SonarQube | Analyze only changed files |
| **Result Caching** | MEDIUM | All tools | Cache unchanged results |
| **Parallel Processing** | MEDIUM | Built-in potential | Multi-core analysis |
| **Streaming Results** | LOW | Large codebase need | Progressive output |

**Why needed:** Full analysis on every PR is slow. Incremental mode enables CI adoption.

---

#### M13: API/SDK Modules (Programmatic Access)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **REST API** | HIGH | All SaaS tools | Programmatic access |
| **GraphQL API** | LOW | Modern tools | Flexible queries |
| **Webhooks** | MEDIUM | All CI tools | Event notifications |
| **Python SDK** | MEDIUM | Snyk, Semgrep | Native integration |

**Why needed:** Enables custom tooling, dashboards, and integration with internal systems.

---

#### M14: Duplicate Detection Modules (Code Quality)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Clone Detection** | MEDIUM | SonarQube, PMD | Find copy-pasted code |
| **Near-duplicate** | LOW | Advanced tools | Similar but not identical |
| **Cross-repo Clones** | LOW | Enterprise need | Duplicates across repos |

**Why needed:** DRY violations are a common code smell. Most competitors detect them.

---

#### M15: Test Coverage Modules (Quality Metrics)

| Module | Priority | Competitors | Description |
|--------|----------|-------------|-------------|
| **Coverage Import** | HIGH | CodeClimate | Import lcov/cobertura |
| **Coverage Overlay** | MEDIUM | Unique to Collider | Show coverage on 3D graph |
| **Uncovered Complexity** | HIGH | Unique | High complexity + low coverage |
| **Test Gap Analysis** | MEDIUM | SonarQube | Identify untested areas |

**Why needed:** Coverage data combined with complexity creates powerful insights unique to Collider.

---

## COMPLETE GAP COVERAGE MATRIX

| Gap | Module | Priority |
|-----|--------|----------|
| Languages (5 → 15+) | M1 | HIGH |
| SAST/Security Rules | M2 | HIGH |
| CI/CD Integration | M3 | HIGH |
| IDE Plugins | M3 | HIGH |
| Export Formats (SARIF) | M4 | HIGH |
| Coupling/Cohesion | M5 | HIGH |
| Diff Visualization | M6 | HIGH |
| OWASP/PCI-DSS Compliance | M7 | HIGH |
| Code Smell Rules | M7 | HIGH |
| Cloud/SaaS Deployment | M8 | HIGH |
| PR Comments | M9 | HIGH |
| Team Dashboards | M9 | MEDIUM |
| Trend Charts | M10 | HIGH |
| Regression Detection | M10 | HIGH |
| Quality Gates | M11 | HIGH |
| Incremental Analysis | M12 | HIGH |
| REST API | M13 | HIGH |
| Clone Detection | M14 | MEDIUM |
| Test Coverage Import | M15 | HIGH |
| Coverage Overlay | M15 | MEDIUM |

**Total Gaps Identified:** 24
**Gaps Covered by M1-M15:** 24 (100%)

---

## IMPLEMENTATION PRIORITY MATRIX

```
                           HIGH VALUE
                               │
      ┌────────────────────────┼────────────────────────┐
      │                        │                        │
      │  M3: GitHub CI    ★    │   ★   M1: Languages    │
      │  M4: SARIF             │       M3: VS Code      │
      │  M11: Quality Gates    │       M8: Docker       │
      │  M12: Incremental      │       M2: SAST         │
      │                        │                        │
 LOW ─┼────────────────────────┼────────────────────────┼─ HIGH
EFFORT                         │                        EFFORT
      │                        │                        │
      │  M6: Diff View         │       M7: Compliance   │
      │  M15: Coverage Import  │       M8: SaaS         │
      │  M9: PR Comments       │       M10: Dashboards  │
      │                        │       M13: REST API    │
      │                        │                        │
      └────────────────────────┼────────────────────────┘
                               │
                           LOW VALUE
```

**Recommended Implementation Phases:**

### Phase 1: CI Adoption (M3, M4, M11, M12)
Quick wins that enable CI/CD integration:
1. **M3: GitHub Actions** - Low effort, high visibility
2. **M4: SARIF Export** - Enables GitHub Security tab
3. **M11: Quality Gates** - Pass/fail thresholds
4. **M12: Incremental** - Fast re-analysis for PRs

### Phase 2: Developer Experience (M1, M3-IDE, M6)
Expand reach and usability:
5. **M1: Java/C++ Support** - Largest language gaps
6. **M3: VS Code Extension** - IDE integration
7. **M6: Diff Visualization** - Compare analyses

### Phase 3: Security & Compliance (M2, M7)
Enterprise requirements:
8. **M2: SAST Scanner** - Security rules
9. **M7: OWASP/PCI-DSS** - Compliance certification

### Phase 4: Platform Features (M8, M9, M10, M13)
Team and enterprise scale:
10. **M8: Cloud/SaaS** - Hosted deployment
11. **M9: Collaboration** - PR comments, team dashboards
12. **M10: Historical Trends** - Time-series analysis
13. **M13: REST API** - Programmatic access

### Phase 5: Advanced Features (M5, M14, M15)
Differentiation and depth:
14. **M5: Coupling/Cohesion** - Architecture metrics
15. **M14: Clone Detection** - DRY violations
16. **M15: Test Coverage** - Coverage overlay on 3D graph

---

## SUCCESS METRICS

### Current Baseline

| Metric | Current | Target (6mo) | Target (12mo) | Target (24mo) |
|--------|---------|--------------|---------------|---------------|
| Languages | 5 | 10 | 15 | 20 |
| CI/CD Integrations | 0 | 2 | 4 | 4 |
| IDE Plugins | 0 | 1 | 2 | 3 |
| Security Rules | 0 | 50 | 200 | 500 |
| Export Formats | 2 (JSON, HTML) | 4 | 6 | 8 |
| Modules Implemented | 0/15 | 4/15 | 8/15 | 15/15 |
| API Endpoints | 0 | 0 | 10 | 50 |
| Team Features | 0 | 0 | 3 | 10 |

### Module Implementation Tracking

| Module | Status | Target |
|--------|--------|--------|
| M1: Languages | 5/20 | 6mo: 10, 12mo: 15 |
| M2: Security | 0% | 6mo: SAST basics |
| M3: Integrations | 0% | 6mo: GitHub Actions + SARIF |
| M4: Export | 33% | 6mo: SARIF |
| M5: Analysis | 0% | 12mo: Coupling |
| M6: Visualization | 0% | 6mo: Diff view |
| M7: Compliance | 0% | 12mo: OWASP Top 10 |
| M8: Cloud/SaaS | 0% | 12mo: Docker |
| M9: Collaboration | 0% | 12mo: PR comments |
| M10: Trends | 0% | 18mo: Basic charts |
| M11: Quality Gates | 0% | 6mo: Pass/fail |
| M12: Incremental | 0% | 6mo: Diff-only |
| M13: API/SDK | 0% | 12mo: REST API |
| M14: Duplicates | 0% | 18mo: Clone detection |
| M15: Coverage | 0% | 12mo: Import |

### Competitive Parity Checklist

**Phase 1 (CI Adoption):**
- [ ] GitHub Actions integration (M3)
- [ ] SARIF export for GitHub Security (M4)
- [ ] Quality gates - pass/fail thresholds (M11)
- [ ] Incremental analysis for PRs (M12)

**Phase 2 (Developer Experience):**
- [ ] Language coverage ≥ 15 (M1)
- [ ] VS Code extension (M3)
- [ ] Diff visualization (M6)

**Phase 3 (Security & Compliance):**
- [ ] Basic SAST rules - OWASP Top 10 (M2)
- [ ] Compliance rules - PCI-DSS basics (M7)
- [ ] False positive tuning (M7)

**Phase 4 (Platform Features):**
- [ ] Docker self-hosted deployment (M8)
- [ ] PR auto-comments (M9)
- [ ] Historical trend charts (M10)
- [ ] REST API (M13)

**Phase 5 (Advanced Features):**
- [ ] Coupling/cohesion metrics (M5)
- [ ] Clone detection (M14)
- [ ] Test coverage overlay (M15)

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
| 2026-01-22 | Initial creation with competitive analysis and 6-module roadmap |
| 2026-01-22 | Expanded to 15 modules (M1-M15) covering all 24 identified gaps |
