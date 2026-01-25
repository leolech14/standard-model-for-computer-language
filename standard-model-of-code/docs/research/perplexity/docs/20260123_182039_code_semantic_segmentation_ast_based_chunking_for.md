# Research: Code semantic segmentation AST-based chunking for RAG retrieval 2024 2025 2026. Looking for:

1. How...

> **Date:** 2026-01-23 18:20:39
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:5b2ffba4b052a55033add5192eadb55b0b541df34135242e32d0f7d5b1bec441`
> **Raw JSON:** `raw/20260123_182039_code_semantic_segmentation_ast_based_chunking_for.json`

---

## Query

Code semantic segmentation AST-based chunking for RAG retrieval 2024 2025 2026. Looking for:

1. How do modern code RAG systems (like GitHub Copilot, Cursor, Sourcegraph Cody) chunk source code for retrieval? Do they use AST boundaries, function-level, or something else?

2. Tree-sitter or AST-based code segmentation approaches for LLM context preparation

3. Code dependency graph extraction tools and compact representations (not verbose, efficient schemas)

4. Academic work from ICSE, FSE, ASE, or MSR conferences (2024-2026) on code understanding, code summarization at sub-file granularity

5. Any compact tagging/annotation schemas for code segments used in industry (like semantic type codes for functions, classes, etc.)

Context: Building incremental semantic indexer for codebase that produces compact chunk records with type codes, summaries, entity extraction, dependency links - to compile into ordered context for LLMs.

---

## Response

I cannot provide a comprehensive answer to your query based on these search results. While the results discuss high-level architectural differences between code AI assistants (GitHub Copilot's "suggest-first" vs. Sourcegraph Cody's "search-first" approach), they lack the technical depth you're seeking.

**What the search results do reveal:**

The results indicate that **Sourcegraph Cody uses semantic search and embeddings with RAG** (retrieval-augmented generation) for code context enrichment[1][2], and that modern assistants achieve varying accuracy rates partly based on their codebase understanding capabilities (Copilot achieved 68% accuracy while Cody achieved 82% on a 200-file service test)[1]. However, the results provide no details about:

- Specific chunking strategies (AST boundaries, function-level, or alternatives)
- Tree-sitter or AST implementation details
- Code dependency graph extraction methodologies
- Compact representation schemas
- Academic research from ICSE, FSE, ASE, or MSR conferences
- Industry tagging/annotation systems for code segments

**What you actually need:**

To build your incremental semantic indexer with type codes and dependency tracking, you'll need to search for:

1. Academic papers on code segmentation and AST-based chunking from recent software engineering conferences
2. Technical documentation from tree-sitter and language server protocol (LSP) projects
3. Industry white papers on code RAG systems (likely from Anthropic, OpenAI, or specialized code search vendors)
4. Open-source indexing tools that publish their chunking strategies

The current results are too high-level for your implementation-focused requirements.

---

## Citations

1. https://www.augmentcode.com/tools/github-copilot-vs-sourcegraph-cody-which-gets-your-codebase
2. https://dev.to/maximsaplin/-cursorsh-a-competitor-to-github-copilot-58k4
3. https://www.vincentschmalbach.com/copilot-vs-cursor-vs-cody-vs-supermaven-vs-aider/
4. https://forum.cursor.com/t/new-to-cursor-whats-the-big-deal/14664
5. https://redmonk.com/kholterhoff/2024/11/18/top-10-things-developers-want-from-their-ai-code-assistants-in-2024/
6. https://news.ycombinator.com/item?id=39965639
7. https://sourcegraph.com/compare

---

## Usage Stats

- Prompt tokens: 195
- Completion tokens: 326
- Total tokens: 521
