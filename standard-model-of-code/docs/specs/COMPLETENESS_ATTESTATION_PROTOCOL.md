# Completeness Attestation Protocol (CAP)

> **Status:** DRAFT
> **Date:** 2026-01-23
> **Problem:** How do we PROVE we found all elementary particles in a codebase?

---

## The Epistemological Challenge

We cannot mathematically prove completeness. We can only maximize confidence through:

1. **Multiple independent detection methods** (triangulation)
2. **Statistical sampling** (confidence intervals)
3. **Adversarial testing** (red team our own parser)
4. **Cross-validator agreement** (multiple tools)

---

## Attestation Levels

| Level | Name | Confidence | Method |
|-------|------|------------|--------|
| **L0** | Unverified | 0-50% | Single parser, no validation |
| **L1** | Heuristic | 50-80% | AST + Regex fallback |
| **L2** | Cross-Validated | 80-95% | Multiple parsers agree |
| **L3** | Statistically Attested | 95-99% | Sampling + confidence interval |
| **L4** | Ground Truth Verified | 99%+ | Manual labeling of sample |

**Current system: L1 (Heuristic)** — We need L3 minimum for production.

---

## Protocol 1: Multi-Parser Triangulation

### Concept

If THREE independent parsers agree on the particle count, confidence increases.

```
Parser A (Tree-sitter)  → 800 nodes
Parser B (Regex)        → 812 nodes
Parser C (ESLint AST)   → 805 nodes
                          ─────────
Agreement Zone:           ~800 ±12 (98.5% agreement)
```

### Implementation

```python
def triangulate_particles(file_path: str) -> TriangulationResult:
    """Run multiple parsers and compare."""

    # Parser 1: Tree-sitter (our primary)
    ts_particles = tree_sitter_extract(file_path)

    # Parser 2: Regex patterns (our fallback)
    regex_particles = regex_extract(file_path)

    # Parser 3: External tool (e.g., ESLint, Babel)
    external_particles = external_extract(file_path)

    # Consensus
    all_names = set()
    for p in [ts_particles, regex_particles, external_particles]:
        all_names.update(particle['name'] for particle in p)

    # Agreement matrix
    agreement = {}
    for name in all_names:
        in_ts = any(p['name'] == name for p in ts_particles)
        in_regex = any(p['name'] == name for p in regex_particles)
        in_external = any(p['name'] == name for p in external_particles)

        agreement[name] = {
            'parsers_found': sum([in_ts, in_regex, in_external]),
            'unanimous': in_ts and in_regex and in_external,
            'disputed': not (in_ts and in_regex and in_external) and (in_ts or in_regex or in_external)
        }

    unanimous = [n for n, a in agreement.items() if a['unanimous']]
    disputed = [n for n, a in agreement.items() if a['disputed']]

    return TriangulationResult(
        unanimous_particles=len(unanimous),
        disputed_particles=len(disputed),
        agreement_rate=len(unanimous) / len(all_names) if all_names else 1.0,
        confidence=calculate_triangulation_confidence(agreement)
    )
```

### Confidence Formula

```
Triangulation Confidence = (Unanimous / Total) ^ (1 / NumParsers)

Example:
  790 unanimous / 812 total, 3 parsers
  = (790/812) ^ (1/3)
  = 0.973 ^ 0.333
  = 0.991 (99.1% confidence)
```

---

## Protocol 2: Statistical Sampling

### Concept

Manually verify a random sample. Extrapolate confidence interval.

```
Total files: 55
Sample size: 10 (18% sample)
Manual verification: 10/10 correct
Confidence interval: 95% CI [0.83, 1.00]
```

### Implementation

```python
import random
import math

def sample_for_attestation(
    files: list[str],
    sample_size: int = 10,
    confidence_level: float = 0.95
) -> SamplingResult:
    """
    Randomly sample files and prepare for manual verification.
    """
    sample = random.sample(files, min(sample_size, len(files)))

    return SamplingResult(
        sample_files=sample,
        sample_size=len(sample),
        total_files=len(files),
        sample_ratio=len(sample) / len(files),
        instructions="""
        For each file in sample_files:
        1. Open the file manually
        2. Count all function/class/variable definitions
        3. Compare to our particle count
        4. Record: matches / mismatches / missed
        """
    )

def calculate_attestation_confidence(
    verified_correct: int,
    verified_incorrect: int,
    sample_size: int,
    confidence_level: float = 0.95
) -> AttestationConfidence:
    """
    Calculate confidence interval using Wilson score interval.
    """
    n = sample_size
    p = verified_correct / n if n > 0 else 0
    z = 1.96 if confidence_level == 0.95 else 2.576  # 95% or 99%

    # Wilson score interval
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denominator
    margin = z * math.sqrt((p * (1-p) + z**2 / (4*n)) / n) / denominator

    return AttestationConfidence(
        point_estimate=p,
        lower_bound=max(0, center - margin),
        upper_bound=min(1, center + margin),
        confidence_level=confidence_level,
        verdict=get_verdict(center - margin)
    )

def get_verdict(lower_bound: float) -> str:
    if lower_bound >= 0.95:
        return "L4: GROUND_TRUTH_VERIFIED"
    elif lower_bound >= 0.90:
        return "L3: STATISTICALLY_ATTESTED"
    elif lower_bound >= 0.80:
        return "L2: CROSS_VALIDATED"
    elif lower_bound >= 0.50:
        return "L1: HEURISTIC"
    else:
        return "L0: UNVERIFIED"
```

### Sample Size Calculator

| Total Files | 90% Confidence | 95% Confidence | 99% Confidence |
|-------------|----------------|----------------|----------------|
| 50 | 8 | 10 | 15 |
| 100 | 10 | 14 | 20 |
| 500 | 15 | 22 | 35 |
| 1000 | 18 | 28 | 45 |

---

## Protocol 3: Adversarial Testing (Red Team)

### Concept

Create files that SHOULD break our parser. If they don't break it, confidence increases.

```python
ADVERSARIAL_PATTERNS = [
    # IIFE variants
    "(function() { function inner() {} })();",
    "(() => { const x = 1; })();",
    "(function named() { return {}; })();",

    # Dynamic patterns
    "window['func' + 'Name'] = function() {};",
    "eval('function dynamic() {}')",
    "new Function('return function() {}')",

    # Edge cases
    "var x = function y() { return y; };",  # Named function expression
    "class A { static { console.log('static block'); } }",  # Static initialization
    "const { fn: aliased } = { fn: function() {} };",  # Destructuring with rename

    # Minified-looking but not minified
    "function a(b,c){return b+c}",  # No spaces
    "var x=1,y=2,z=function(){};",  # Chained declarations

    # Comments that look like code
    "// function fake() {}",
    "/* class NotReal {} */",

    # String literals that look like code
    'const code = "function stringFunc() {}";',
    "const template = `class ${name} {}`;",
]

def run_adversarial_tests() -> AdversarialResult:
    """Test our parser against adversarial patterns."""
    results = []

    for pattern in ADVERSARIAL_PATTERNS:
        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as f:
            f.write(pattern.encode())
            temp_path = f.name

        # Parse
        particles = extract_particles(temp_path)

        # Verify
        expected = count_expected_definitions(pattern)
        actual = len(particles)

        results.append({
            'pattern': pattern[:50],
            'expected': expected,
            'actual': actual,
            'correct': expected == actual
        })

        os.unlink(temp_path)

    correct = sum(1 for r in results if r['correct'])
    return AdversarialResult(
        total_tests=len(results),
        passed=correct,
        failed=len(results) - correct,
        pass_rate=correct / len(results),
        failures=[r for r in results if not r['correct']]
    )
```

---

## Protocol 4: Coverage Fingerprinting

### Concept

For known codebases, we know exactly what should be found. Compare against fingerprint.

```yaml
# fingerprints/viz_assets.yaml
codebase: viz/assets
version: 1.0.0
verified_date: 2026-01-23
verified_by: manual_audit

files:
  modules/theory.js:
    expected_particles:
      - name: THEORY
        type: Module
        line: 1
      - name: getTheoryChunks
        type: Function
        line: 45
      - name: extractSummary
        type: Function
        line: 89
      # ... complete list

  modules/index.js:
    expected_particles:
      - name: VizModules
        type: Module
        line: 1
```

### Verification

```python
def verify_against_fingerprint(
    analysis_result: dict,
    fingerprint_path: str
) -> FingerprintVerification:
    """Compare analysis against known-good fingerprint."""

    with open(fingerprint_path) as f:
        fingerprint = yaml.safe_load(f)

    matches = 0
    missing = []
    extra = []

    for file_path, expected in fingerprint['files'].items():
        actual_particles = [
            n for n in analysis_result['nodes']
            if n['file_path'].endswith(file_path)
        ]

        for exp in expected['expected_particles']:
            found = any(
                p['name'] == exp['name'] and p['type'] == exp['type']
                for p in actual_particles
            )
            if found:
                matches += 1
            else:
                missing.append(f"{file_path}:{exp['name']}")

        # Check for unexpected particles
        expected_names = {e['name'] for e in expected['expected_particles']}
        for p in actual_particles:
            if p['name'] not in expected_names:
                extra.append(f"{file_path}:{p['name']}")

    total_expected = sum(
        len(f['expected_particles'])
        for f in fingerprint['files'].values()
    )

    return FingerprintVerification(
        matches=matches,
        missing=missing,
        extra=extra,
        recall=matches / total_expected if total_expected else 1.0,
        precision=matches / (matches + len(extra)) if (matches + len(extra)) else 1.0
    )
```

---

## The Attestation Report

Combine all protocols into a single attestation:

```yaml
# .collider/attestation_report.yaml
codebase: viz/assets
analysis_date: 2026-01-23T12:00:00Z
collider_version: 0.9.0

particles:
  total_found: 802
  files_analyzed: 58
  files_excluded: 4

attestation:
  level: L2  # Cross-Validated
  confidence: 0.95

  protocols:
    triangulation:
      parsers: [tree-sitter, regex, eslint]
      unanimous: 790
      disputed: 12
      agreement_rate: 0.985

    sampling:
      sample_size: 10
      verified_correct: 10
      verified_incorrect: 0
      confidence_interval: [0.83, 1.00]

    adversarial:
      tests_run: 15
      tests_passed: 13
      tests_failed: 2
      pass_rate: 0.867
      failures:
        - pattern: "eval('function dynamic() {}')"
        - pattern: "new Function('return function() {}')"

    fingerprint:
      available: false
      reason: "No fingerprint file for viz/assets"

gaps_identified:
  - type: DYNAMIC_EVAL
    description: "eval() and new Function() not detected"
    severity: LOW
    rationale: "Extremely rare in production code"

  - type: ANONYMOUS_IIFE
    description: "main.js has 0 particles (anonymous bootstrap)"
    severity: ACCEPTABLE
    rationale: "No reusable definitions to extract"

verdict: |
  Attestation Level L2 (Cross-Validated) achieved.
  Confidence: 95%

  Known blind spots:
  - Dynamic code generation (eval, new Function)
  - Anonymous IIFEs without exports

  These represent <0.1% of typical codebases.
```

---

## Implementation Roadmap

| Phase | Task | Status |
|-------|------|--------|
| 1 | Define attestation levels | ✅ DONE |
| 2 | Implement triangulation | TODO |
| 3 | Implement sampling framework | TODO |
| 4 | Create adversarial test suite | TODO |
| 5 | Build fingerprint system | TODO |
| 6 | Generate attestation report | TODO |

---

## The Philosophical Bottom Line

**We can never achieve 100% certainty.** But we can:

1. **Maximize coverage** through multiple detection methods
2. **Quantify uncertainty** with confidence intervals
3. **Document blind spots** explicitly (eval, dynamic code)
4. **Continuously improve** as new patterns are discovered

The goal is not perfection. The goal is **knowing what we don't know**.

```
Certainty is the enemy of growth.
Quantified uncertainty is the foundation of science.
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial draft |
