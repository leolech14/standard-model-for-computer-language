---
audit_metadata:
  model: "sonar-pro"
  model_version: "2026-01"
  prompt_file: "tools/research/prompts/finding_1_perplexity.txt"
  prompt_hash: "sha256:ce182385ae54c4d148277988d353c095d1496a1636fc9e3a97967f6e035967d9"
  analysis_set: "N/A (external web)"
  repo_commit: "43f2b6f"
  date_utc: "2026-01-22T15:45:00Z"
  tool_version: "mcp__perplexity__perplexity_ask"
  status: "COMPLETED"
---

# Perplexity External Context: Finding 1

## Query Summary

Searched for academic research on Pareto/power-law distributions in software code structure, specifically:
- Distribution of code elements (functions, classes, variables)
- Whether small number of code types dominate structure
- Universal patterns across programming languages

## External Context Found

### Relevant Research

**1. Source Code File Size Distributions**
- Paper finds **source code file sizes follow a double Pareto distribution**
- Analyzed ~1.4 million files across C, C++, Java, Python, Lisp (Debian GNU/Linux)
- Large files appear more frequently than lognormal models predict
- **Citation:** https://www.scitepress.org/PublishedPapers/2011/34262/34262.pdf

**2. Repository Growth Patterns**
- Study examines Pareto principle in code repository growth over time (GitHub)
- Focuses on aggregate metrics rather than code structures
- **Citation:** https://annals-csis.org/Volume_35/drp/pdf/5221.pdf

**3. Developer Contribution Patterns**
- Confirms Pareto principle (80/20 rule) applies to developer activity
- Small percentage of core developers produce large proportion of code
- **Citations:**
  - https://ceur-ws.org/Vol-708/sqm2011-goeminne-mens-11-pareto.pdf
  - https://rebels.cs.uwaterloo.ca/papers/iwpse2015_yamashita.pdf

**4. Software Feature Distributions**
- Pareto distributions of features in top-performing software
- **Citation:** https://dl.acm.org/doi/10.1145/3486949.3486964

### Gap Identified

The available research does NOT directly address:
- Distributions of specific code elements (functions, classes, variables) within codebases
- Universal structural patterns across languages at the micro level

Studies focus on **macro-level metrics** (file sizes, repository growth, developer activity) rather than **fine-grained code structure analysis**.

## Implications for Finding 1

| Aspect | Assessment |
|--------|------------|
| Prior art exists | YES - for macro-level Pareto in software |
| Direct prior art | NO - for element-level distribution claims |
| Claim is novel | PARTIALLY - applies Pareto to code element types |
| Contradicting evidence | NOT FOUND |

## Scope Boundary Reminder

> This external context does NOT validate our internal metrics.
> Perplexity provides literature context only.

## Suggested Follow-up Searches

- "function size distributions in software"
- "class hierarchy patterns"
- "code complexity distributions"
- "AST node type frequencies"

---

*External context only - not evidence for internal measurements.*
