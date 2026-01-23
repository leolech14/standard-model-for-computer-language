---
audit_metadata:
  model: "sonar-pro"
  model_version: "2026-01"
  prompt_file: "tools/research/prompts/finding_1_adversarial_perplexity.json"
  prompt_hash: "sha256:9fd7f32366f863401346b9d3bef358aafed28f75b354123c1ca8d71ec273f34c"
  analysis_set: "N/A (external reasoning)"
  repo_commit: "8361d44"
  date_utc: "2026-01-22T16:20:00Z"
  tool_version: "mcp__perplexity__perplexity_ask"
  status: "COMPLETED"
  note: "Adversarial audit role executed via Perplexity (not ChatGPT)"
  independence_note: "Same provider as perplexity_finding_1.md - not independent audit"
---

# Adversarial Falsification Audit: Finding 1

## Query Summary

Adversarial research audit of Finding 1 (Pareto Distribution of Structural Atoms) with focus on:
- Implicit assumptions
- Methodology biases
- Statistical sufficiency
- Falsification test design
- Peer review readiness

## Perplexity Adversarial Response

### 1. Problematic Implicit Assumptions

**Definition ambiguity**: The finding never defines what constitutes a "structural atom" in the AST context. Are these node types (e.g., `Identifier`, `FunctionDef`)? If so, the classification scheme itself could be biased toward consolidating diverse code patterns into a handful of categories.

**Language universality**: The claim treats Python, Go, and TypeScript as equivalent despite their fundamentally different syntax and AST representations. Each language's grammar will produce different node type distributions naturally. Averaging across them obscures language-specific patterns rather than revealing universal structure.

**Equal significance assumption**: The metric treats all nodes as equally important. A single `Identifier` node and a complex `FunctionDeclaration` are counted identically, yet they contribute vastly different semantic information. High node-count atoms may simply be low-information filler (whitespace tokens, simple identifiers).

**Stationarity across codebases**: The finding assumes node distributions are stable across different project types (a machine learning library, HTTP client, bioinformatics tool, and schema validator are fundamentally different). This is unlikely.

### 2. Methodology Biases Inflating Results

**Tree-sitter's tokenization design**: Tree-sitter produces highly granular ASTs with frequent low-level node types (identifiers, literals, operators). This design *naturally* creates Zipfian distributions where a few categories dominate. The finding may be measuring tree-sitter's output characteristics, not actual code structure complexity.

**Pattern matching circularity**: If "atom classification" is performed via pattern matching, the researchers likely defined patterns that recognize only the most common structures, creating a self-fulfilling prophecy. Rare or irregular code patterns would be misclassified into common categories.

**Aggregation across heterogeneous repos**: Combining 4 different codebases into a single 4,971-node sample obscures important variation. If one repo (say, `cobra`) contains 2,000+ nodes while others have ~500, the distribution is dominated by that repo's characteristics, not a universal pattern.

**Unknown rate handling**: An "unknown rate of 0.3%" suggests ~15 nodes went unclassified. This is trivially small and raises questions: Were these legitimately ambiguous, or were they discarded post-hoc to inflate the top-4 percentage?

### 3. Statistical Credibility Issues

**Sample size (4 repos) is critically insufficient**:
- No replication across projects in the same language
- No statistical power to detect differences between languages
- No confidence intervals or variability estimates provided
- Cannot distinguish signal from noise at this scale

**The 96-100% range is suspicious** in multiple ways:

| Concern | Implication |
|---------|-------------|
| **No variance reported** | Are all 4 repos nearly identical? This contradicts the claim of measuring "structural universality"—if it's truly universal, why no error bars? |
| **Max value is 100%** | At least one repo had ALL nodes in just 4 categories. This suggests either the repo is trivially simple, the categories are overly broad, or the classification scheme is coarse to the point of uselessness. |
| **Median 98.81%** | This is suspiciously close to the maximum. A more realistic distribution would show greater spread. |
| **No outliers reported** | Real software diversity would produce at least one repo breaking the pattern. The absence of any deviation is a red flag for survivorship bias or cherry-picking. |

### 4. Falsification Tests (Specific Design)

**Test 1: Language-specific stratification**
- Hypothesis: The finding is an artifact of averaging incompatible language grammars.
- Method: Re-run the analysis separately for Python, Go, and TypeScript. If top-4 dominance holds within each language at 70-90%, the claim survives. If Python shows 60% and TypeScript shows 95%, the original finding is meaningless (it's measuring language differences, not universal structure).
- Prediction: Expect 15-25% variance between languages, disproving universality.

**Test 2: Repo complexity gradient**
- Hypothesis: The finding only holds for simple, well-structured code.
- Method: Test on deliberately chosen repos:
  - *Simple*: A Hello World or minimal library (expect 95%+ top-4 dominance)
  - *Complex*: Large, refactored codebases with many AST node types (expect 60-75%)
  - *Pathological*: Code with heavy metaprogramming, macros, or dynamic typing edge cases (expect <50%)
- Prediction: The 70-90% range breaks down at the extremes, revealing the metric is conflating multiple distinct patterns.

**Test 3: Node-weight sensitivity analysis**
- Hypothesis: The finding conflates high-frequency low-importance nodes with structural significance.
- Method: Recalculate top-4 mass using three weighting schemes:
  - *Unweighted* (current): All nodes = 1
  - *Depth-weighted*: Nodes deeper in AST receive higher weight (they encode more semantic structure)
  - *Leaf-weighted*: Only leaf nodes count (removing syntactic scaffolding)
- Prediction: If top-4 dominance persists across all three weightings at similar levels, the claim is robust. If the unweighted version is an outlier (e.g., 98% unweighted vs. 65% leaf-weighted), the finding is an artifact of how ASTs are counted.

### 5. Verdict: Unlikely to Survive Peer Review

**Verdict: UNLIKELY (2/10 confidence)**

**Reasoning:**

| Dimension | Assessment |
|-----------|------------|
| **Generalizability** | Sample of 4 repos is far below minimum standards for empirical claims about "codebases" broadly. Peer reviewers would demand n >= 50+ with stratification by language and domain. |
| **Methodological rigor** | No definition of "structural atom," no ablation studies, no comparison to baseline models (e.g., naive Zipfian distribution), no cross-validation. |
| **Statistical transparency** | No confidence intervals, no per-repo breakdown, no discussion of variability. The 96-100% range without error bars suggests either deliberate omission or lack of analytical depth. |
| **Causal claims** | The finding implies these atoms are structurally *essential*, but the evidence only shows they're *frequent*. Frequency != importance. |
| **Reproducibility** | Tree-sitter version, parsing options, and exact classification rules are not specified. Without this, independent replication is impossible. |

**What would improve credibility:**
1. Expand to 50+ repos with language-stratified analysis
2. Report full distributions and per-repo statistics
3. Provide explicit AST node definitions and classification rules
4. Compare against null hypotheses (random trees, Zipfian models)
5. Show that top-4 atoms remain dominant in different domains (e.g., compilers vs. web frameworks vs. data science)
6. Conduct ablation: measure code understanding loss when removing top-4 atoms

---

*Adversarial audit - designed to find flaws before L2 promotion.*
