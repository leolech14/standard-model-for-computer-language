# Research: STRUCTURED DATA ONLY. Technical implementation patterns for AI agent context engineering.

I need sp...

> **Date:** 2026-01-25 15:14:37
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:75c1878d06ecb6c08c0fe51de4d2fe1080529195283ff2a9cf58d0cf8b756941`
> **Raw JSON:** `raw/20260125_151437_structured_data_only__technical_implementation_pat.json`

---

## Query

STRUCTURED DATA ONLY. Technical implementation patterns for AI agent context engineering.

I need specific code patterns and configurations, not concepts.

1. CONTEXT INJECTION PATTERNS:
| Pattern Name | When to Use | Token Cost | Implementation Pseudocode |

2. POSITION OPTIMIZATION (for lost-in-the-middle):
| Info Type | Optimal Position | Attention Score | Reason |

3. CHUNKING STRATEGIES:
| Strategy | Chunk Size | Overlap | Best For | Retrieval Accuracy |

4. PROMPT STRUCTURE TEMPLATE:
| Section | Order | Token Budget % | Content Type |

5. CACHE INVALIDATION RULES:
| Trigger | Action | Staleness Threshold |

6. RETRIEVAL VS STATIC DECISION MATRIX:
| Content Type | Static? | Retrieval? | Hybrid? | Rationale |

Give me the data tables. No explanatory prose.

---

## Response

## 1. CONTEXT INJECTION PATTERNS

| Pattern Name | When to Use | Token Cost | Implementation Pseudocode |
|--------------|-------------|------------|---------------------------|
| Writing Context | Save info outside window for later reference (e.g., memory objects, files)[1][5] | Low (external storage) | `if context_length > threshold: save_to_memory(obj); return memory_id`[1] |
| Selecting Context | Retrieve only needed data via RAG/similarity search[1][5] | Medium (retrieval overhead) | `relevant_docs = rag_search(query, top_k=5); inject_into_prompt(relevant_docs)`[1] |
| Compressing Context | Summarize/trim past messages to avoid bloat[1][5] | Low (post-compression) | `summary = llm.summarize(history[-n:]); context = summary + current_input`[1] |
| Isolating Context | Scoped window per agent/sub-agent[1][4][5] | Variable (per scope) | `agent_context = filter_context(global_state, agent_role); call_agent(agent_context)`[1][4] |

## 2. POSITION OPTIMIZATION (for lost-in-the-middle)

| Info Type | Optimal Position | Attention Score | Reason |
|-----------|------------------|-----------------|--------|
| Instructions | Prefix (first 10%) | High | Stable prefix for role/scope adherence[3] |
| Critical Facts | Near prompt end (last 20%) | High | Avoids middle dilution; recent attention bias[5] |
| Tool Outputs | Append-only (end) | Medium-High | Maintains recency; prevents overwrite[3] |
| Historical Summary | Middle (compressed) | Low-Medium | Isolation reduces distraction if summarized[1][5] |

## 3. CHUNKING STRATEGIES

| Strategy | Chunk Size | Overlap | Best For | Retrieval Accuracy |
|----------|------------|---------|----------|--------------------|
| Fixed-size | 512-1024 tokens | 20% | General RAG/short docs | High (simple, consistent)[1] |
| Semantic | 500-2000 tokens | 10-15% | Long docs/research | Very High (context-aware)[4] |
| Hierarchical | Variable (summary + chunks) | N/A | Multi-agent/long-horizon | High (sub-agent distillation)[4] |
| Append-only | Incremental (no fixed) | 0% | Agent memory streams | Medium (needs compression)[3] |

## 4. PROMPT STRUCTURE TEMPLATE

| Section | Order | Token Budget % | Content Type |
|---------|-------|----------------|--------------|
| Role/Instructions | 1 | 10-15% | Stable prefix text[3] |
| Shared Assumptions | 2 | 5-10% | Task framing, filters[1] |
| Retrieved Context | 3 | 30-50% | RAG results, summaries[1][4] |
| Agent State/Memory | 4 | 10-20% | Condensed history[3][5] |
| Current Query/Tools | 5 (end) | 20-30% | Input + dynamic tools[1][3] |

## 5. CACHE INVALIDATION RULES

| Trigger | Action | Staleness Threshold |
|---------|--------|---------------------|
| New agent decision | Update shared memory | Immediate[1] |
| Tool output change | Recompress context | >5min or token delta >20%[1][3] |
| Task phase shift | Isolate new window | Phase boundary[4] |
| Contradiction detected | Flush conflicting chunks | Hallucination score >0.5[7] |

## 6. RETRIEVAL VS STATIC DECISION MATRIX

| Content Type | Static? | Retrieval? | Hybrid? | Rationale |
|--------------|---------|------------|---------|-----------|
| Instructions/Role | Yes | No | No | Stable prefix, no change[3] |
| Research Data | No | Yes | Yes (progressive) | Dynamic, just-in-time loading[4] |
| Agent History | No | No | Yes (summarized) | Append-only + compression[3][5] |
| Tools/Schemas | Hybrid | On-demand | Yes | Context-aware masking[3] |
| Task State | No | No | Yes (external memory) | Shared state for multi-agent[1][7] |

---

## Citations

1. https://www.vellum.ai/blog/multi-agent-systems-building-with-context-engineering
2. https://yeyu.substack.com/p/context-engineering-for-ai-agents
3. https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
4. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
5. http://rlancemartin.github.io/2025/06/23/context_engineering/
6. https://weaviate.io/blog/context-engineering
7. https://galileo.ai/blog/context-engineering-for-agents
8. https://docs.langchain.com/oss/python/langchain/context-engineering
9. https://docs.cloud.google.com/architecture/choose-design-pattern-agentic-ai-system

---

## Usage Stats

- Prompt tokens: 177
- Completion tokens: 952
- Total tokens: 1129
