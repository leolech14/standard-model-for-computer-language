# Benchmark Error Log

Generated: 2025-12-23

## Summary

| Metric | Value |
|--------|-------|
| **Total Errors** | 23 |
| **Clone Timeouts** | 2 |
| **Markdown-Only** | ~8 |
| **Other** | ~13 |

---

## Error Details

| Rank | Repo | Language | Error |
|------|------|----------|-------|
| 1 | `codecrafters-io/build-your-own-x` | Markdown | Unknown |
| 3 | `sindresorhus/awesome` | Unknown | Unknown |
| 7 | `jwasham/coding-interview-university` | Unknown | Unknown |
| 11 | `awesome-selfhosted/awesome-selfhosted` | Unknown | Unknown |
| 12 | `practical-tutorials/project-based-learning` | Unknown | Unknown |
| 17 | `trimstray/the-book-of-secret-knowledge` | Unknown | Unknown |
| 18 | `ossu/computer-science` | HTML | Unknown |
| 21 | `getify/You-Dont-Know-JS` | Unknown | Unknown |
| 29 | `github/gitignore` | Unknown | Unknown |
| 32 | `massgravel/Microsoft-Activation-Scripts` | Batchfile | Unknown |
| 33 | `jlevy/the-art-of-command-line` | Unknown | Unknown |
| 49 | `labuladong/fucking-algorithm` | Markdown | Unknown |
| 59 | `ripienaar/free-for-dev` | HTML | Unknown |
| 60 | `justjavac/free-programming-books-zh_CN` | Unknown | Unknown |
| 70 | `goldbergyoni/nodebestpractices` | Dockerfile | Unknown |
| 74 | `microsoft/generative-ai-for-beginners` | Jupyter Notebook | Clone timeout - repo too large |
| 77 | `Hack-with-Github/Awesome-Hacking` | Unknown | Unknown |
| 79 | `x1xhlol/system-prompts-and-models-of-ai-tools` | Unknown | Unknown |
| 80 | `papers-we-love/papers-we-love` | Shell | Unknown |
| 88 | `mtdvio/every-programmer-should-know` | Unknown | Unknown |
| 89 | `jaywcjlove/awesome-mac` | JavaScript | Unknown |
| 95 | `microsoft/Web-Dev-For-Beginners` | JavaScript | Clone timeout |
| 96 | `ryanmcdermott/clean-code-javascript` | JavaScript | Unknown |

---

## Categories for Future Analysis

### 1. Clone Timeouts
Large repos that exceeded 120s clone timeout. Consider:
- Increasing timeout for mega-repos
- Pre-caching popular repos
- Using shallow clones more aggressively

### 2. Markdown-Only Repos
Repos like `sindresorhus/awesome` that contain no code:
- These are expected errors
- Could detect earlier via GitHub API (primary language = None)
- Should be excluded from benchmark

### 3. Analysis Errors
Repos that failed during code analysis:
- May indicate parser bugs
- May need language-specific handling
- Worth investigating individually

---

## Action Items

1. [ ] Investigate "other" errors for patterns
2. [ ] Add GitHub API pre-check for primary language
3. [ ] Consider longer timeout for repos > 500MB
4. [ ] Create exclusion list for known non-code repos
