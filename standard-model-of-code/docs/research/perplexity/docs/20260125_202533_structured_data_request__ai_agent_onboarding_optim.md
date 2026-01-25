# Research: STRUCTURED DATA REQUEST: AI agent onboarding optimization - second pass.

Context: We redesigned an ...

> **Date:** 2026-01-25 20:25:33
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:79faf8704ed6be6772f7e30e64dbe7a3663828b0c6172f334ad07bca64b85e1a`
> **Raw JSON:** `raw/20260125_202533_structured_data_request__ai_agent_onboarding_optim.json`

---

## Query

STRUCTURED DATA REQUEST: AI agent onboarding optimization - second pass.

Context: We redesigned an AI agent onboarding system. First review cut required reading from 1,219 lines to 138 lines. Second review by fresh agent found new issues.

ISSUES FOUND:
1. Conflicting boot instructions (old doc says boot.sh, new doc says ./concierge)
2. Task inbox shows count (34 items) but no preview - agent can't prioritize
3. No value proposition - agent doesn't know WHY the system matters
4. Tutorial too skeletal (6 lines) vs theory docs (340+ lines)
5. Physics metaphors (Wave/Particle/Observer for code/context/agent) add cognitive load
6. Glossary overwhelming before first action

Provide STRUCTURED DATA:

1. PRIORITY MATRIX:
| Issue | Impact (1-10) | Effort (1-10) | Priority Score | Rationale |

2. MINIMUM VIABLE GLOSSARY:
| Term | Definition (1 sentence) | When Needed |
(What 5-10 terms does a day-1 agent ACTUALLY need?)

3. VALUE PROPOSITION TEMPLATE:
| Benefit | Pain it prevents | One-liner |

4. METAPHOR DECISION MATRIX:
| Metaphor | Keep/Remove | Where to Keep | Where to Remove |

5. INBOX PREVIEW SPEC:
| Field | Show in Preview? | Why |

No prose. Tables only.

---

## Response

### 1. PRIORITY MATRIX
| Issue | Impact (1-10) | Effort (1-10) | Priority Score | Rationale |
|-------|---------------|---------------|----------------|-----------|
| 1. Conflicting boot instructions | 10 | 2 | 8 | Blocks initial access; critical for day-1 start; quick fix aligns docs[1][3] |
| 2. Task inbox shows count but no preview | 9 | 3 | 6 | Prevents prioritization; real-time visibility boosts efficiency[1][2] |
| 3. No value proposition | 8 | 1 | 7 | Reduces motivation; clear benefits accelerate ramp-up[1][2] |
| 4. Tutorial too skeletal vs theory docs | 7 | 4 | 3 | Imbalances learning; embed structured paths[1][2] |
| 5. Physics metaphors add cognitive load | 6 | 1 | 5 | Increases confusion; simplify for clarity[1] |
| 6. Glossary overwhelming before first action | 5 | 2 | 3 | Delays action; defer to need[2][3] |

### 2. MINIMUM VIABLE GLOSSARY
| Term | Definition (1 sentence) | When Needed |
|------|--------------------------|-------------|
| Boot | Command to start the AI agent system (use ./concierge). | First login |
| Inbox | Queue of pending tasks with count and previews for prioritization. | Daily task review |
| Concierge | Primary executable for initializing the agent environment. | System startup |
| Wave/Particle/Observer | Conceptual model for code (wave), context (particle), agent (observer) interactions. | Advanced debugging |
| Ramp-up | Time to achieve full productivity via structured onboarding. | Progress tracking |
| Agent Assist | Real-time AI guidance during tasks. | Live interactions |
| Golden Dataset | Benchmark data for agent evaluation and onboarding. | Performance checks |

### 3. VALUE PROPOSITION TEMPLATE
| Benefit | Pain it prevents | One-liner |
|---------|------------------|-----------|
| Faster ramp-up | Prolonged confusion and errors | "Ramp 2X faster with AI-guided onboarding, reducing errors from day one."[1] |
| Clear task prioritization | Inbox overload without previews | "Preview tasks instantly to focus on high-impact work, not guesswork."[2] |
| Reduced cognitive load | Overwhelming docs and metaphors | "Streamlined guides deliver clarity, so you learn by doing, not reading."[1] |
| Consistent performance | Conflicting instructions | "Unified boot process ensures reliable starts every time."[3] |
| Ongoing support | Skeletal tutorials | "Embedded coaching turns theory into immediate productivity."[1][2] |

### 4. METAPHOR DECISION MATRIX
| Metaphor | Keep/Remove | Where to Keep | Where to Remove |
|----------|-------------|---------------|-----------------|
| Wave (code) | Remove | Advanced theory docs | Boot, tutorial, glossary |
| Particle (context) | Remove | Deep reference guides | Inbox, day-1 onboarding |
| Observer (agent) | Keep | Glossary (minimal) | Tutorials, initial instructions |

### 5. INBOX PREVIEW SPEC
| Field | Show in Preview? | Why |
|-------|-------------------|-----|
| Task Title | Yes | Quick identification and prioritization[1][2] |
| Priority Level | Yes | Enables focus on urgent items[2] |
| Snippet/Preview Text | Yes | Context without full open; reduces clicks[1] |
| Assignee | Yes | Clarity on ownership and handoffs[3] |
| Due Date | Yes | Time sensitivity for planning[2] |
| Status | Yes | Avoid duplicates; track progress[1] |
| Full Description | No | Prevents overload; expand on click |

---

## Citations

1. https://www.vonage.com/resources/articles/agent-onboarding/
2. https://www.moveworks.com/us/en/resources/blog/what-are-modern-employee-onboarding-best-practices
3. https://devblogs.microsoft.com/ise/agent-onboarding-process-for-agentic-systems/
4. https://www.moxo.com/blog/ai-onboarding-best-practices
5. https://blogs.nvidia.com/blog/onboarding-teams-ai-agents-productivity-revenue-businesses/
6. https://www.hrmorning.com/articles/onboarding-ai/
7. https://support.zendesk.com/hc/en-us/articles/8357751802138-Best-practices-for-testing-advanced-AI-agents

---

## Usage Stats

- Prompt tokens: 298
- Completion tokens: 821
- Total tokens: 1119
