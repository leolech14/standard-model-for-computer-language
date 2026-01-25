# Research: I'm building a semantic code indexer based on the principle that PURPOSE = f(edges) - meaning a code...

> **Date:** 2026-01-23 21:24:05
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:40333ebf200add9bd7b971c6e5d6a52c744394102e89cec137e711e1ede9146d`
> **Raw JSON:** `raw/20260123_212405_i_m_building_a_semantic_code_indexer_based_on_the.json`

---

## Query

I'm building a semantic code indexer based on the principle that PURPOSE = f(edges) - meaning a code element's purpose is determined by its relationships (who calls it, what it calls, what module it's in) rather than its content.

I need state-of-the-art guidance on:

1. **Graph-based code analysis**: Best practices for using NetworkX or similar to analyze call graphs, dependency graphs. What graph metrics best reveal architectural purpose (utility functions, orchestrators, critical infrastructure)?

2. **Top-down context propagation**: Academic research on how parent/container context should inform child element analysis. How do expert developers comprehend code vs novices?

3. **Multi-modal intent extraction**: Research on extracting developer intent from multiple sources (code, commits, docs, issues). How much intent is lost in code alone?

4. **Local LLM for semantic analysis**: Can Ollama + small models (Qwen, CodeLlama) effectively do semantic role classification? What's the quality vs cloud LLM tradeoff?

Provide academic citations and practical implementation guidance.

---

## Response

# Semantic Code Indexing Through Relationship-Based Purpose Extraction: A Comprehensive Framework for Graph-Driven Code Analysis

## Overview

This report presents a state-of-the-art framework for building semantic code indexers that determine code element purpose through relationship analysis rather than content inspection. The fundamental principle that PURPOSE = f(edges) represents a paradigm shift in how developers and tools understand codebases. By analyzing who calls a function, what it calls, its module context, and its position within the system's dependency structure, we can extract meaningful purpose signatures without parsing implementation details. This approach combines graph theory, cognitive science research on program comprehension, multi-modal intent extraction, and modern small language models to create a practical, deployable system that scales beyond traditional syntax-based analysis. The integration of NetworkX for graph manipulation, edge-based centrality analysis to identify architectural roles, research on expert programmer cognition to guide hierarchical context propagation, and local LLMs for semantic classification creates a comprehensive solution that balances academic rigor with practical implementation concerns.

## Graph-Based Code Analysis: Foundations and Architectural Purpose Detection

### Theoretical Foundations of Code Graphs

Software dependency graphs represent relationships between code components through directed graph structures where vertices typically embody entities such as files, classes, functions, or modules, and directed edges capture dependencies such as module imports, API calls, or inheritance relationships[3]. The concept extends naturally to what are termed call graphs, which capture the dynamic flow of execution within systems by meticulously tracing sequences of service invocations[39]. In graph representation, a call graph is formally defined as a directed, labeled, and possibly weighted graph where the vertex set represents services or functions, edges indicate invocation relationships, and optional weights represent runtime metrics such as latency, throughput, or call frequency[39].

The foundational advantage of representing code as graphs lies in their ability to expose hidden architectural patterns and dependencies that remain invisible in linear source code examination[5]. When developers begin working on existing codebases, they encounter directories containing hundreds of files, where relationships exist implicitly in the structure of the code and explicitly in how components communicate[5]. Traditional documentation approaches fail to maintain these relationship maps over time, whereas graph-based representations provide what has been termed "living graphs" of code that remain current with the actual codebase[5]. This living quality is particularly critical because static documentation quickly becomes obsolete, but a graph constructed from current code always reflects the true structure of the system.

NetworkX provides the fundamental infrastructure for constructing and analyzing these code graphs[1]. The library enables creation of empty graphs with no initial nodes or edges, and subsequently allows incremental addition of nodes and edges through straightforward API operations[1]. The flexibility of NetworkX extends to creating hierarchical graph structures, where graphs can be incorporated as nodes within other graphs, enabling sophisticated representations such as graphs of graphs, graphs of files, or graphs of functions[1]. This capability proves particularly valuable for semantic code indexing because it allows representing code at multiple levels of abstraction simultaneously—a function exists within a class, which exists within a module, which exists within a service.

### Dependency Graph Theory and Circular Dependency Detection

A dependency graph represents dependencies through a directed graph where an edge from vertex *a* to vertex *b* indicates that *a* depends on *b*, requiring *b* to be evaluated or resolved before *a*[3]. The mathematical formalization defines a dependency graph as G=(S,T) where S is the set of objects, and T is the transitive reduction of R, the transitive relation modeling dependencies[3]. This formal structure proves critical for understanding code purpose because circular dependencies—situations where *a* depends on *b*, *b* depends on *c*, and *c* depends on *a*—fundamentally alter architectural purpose interpretation[3].

Circular dependencies create impossible evaluation orders because no object in the cycle can be evaluated first without its dependencies being resolved[3]. In code architecture, circular dependencies signal fundamental design problems that affect purpose interpretation: a circular dependency between modules suggests they are tightly coupled, making their individual purposes ambiguous[3]. Detection of circular dependencies during graph analysis provides immediate architectural insight—presence of cycles indicates architectural problems that should be addressed during refactoring efforts[3].

The concept of a correct evaluation order formalizes how dependencies must be structured: a numbering n:S→ℕ of objects forms a correct evaluation order when n(a)<n(b) implies (a,b)∉R for all a,b∈S[3]. This mathematical formalization provides a foundation for understanding code flow: if we can establish a correct evaluation order through topological sorting, the code architecture supports clean dependency flow. Conversely, if no evaluation order exists, circular dependencies block proper understanding of purpose relationships.

### Call Graph Analysis and Execution Flow Semantics

Call graphs extend dependency graphs by adding semantic labels to edges, typically representing endpoint names or operation identifiers[39]. The adjacency matrix representation of a call graph captures this rich relationship structure through a matrix of dimensions n×n, where each entry contains a set of labels or metrics associated with calls from node i to node j[39]. This representation enables sophisticated queries: examining row i tells you everything service i calls; examining column j tells you everything that calls service j.

In practical implementation, call graphs can be constructed through two distinct methodologies: static analysis examines source code without execution, while dynamic analysis runs the program and observes actual execution patterns[42]. Static call graphs provide a complete view of potential execution paths but may include unreachable code; dynamic call graphs show only paths actually executed but miss conditional branches not taken[42]. For semantic purpose detection, static analysis provides the more comprehensive foundation because purpose should encompass all potential roles a component might play, not just those manifested in particular test runs.

Service call chains—sequences of service invocations following a path through the call graph—represent the execution flows that implement system functionality[39]. By analyzing these chains, developers can identify performance bottlenecks, understand data flow, and recognize architectural patterns[39]. More importantly for semantic indexing, the structure of call chains reveals purpose: a function that appears early in many call chains likely serves orchestration or coordination roles; a function deep in chains likely performs specialized computation.

### Centrality Measures for Identifying Architectural Purpose

The most powerful aspect of graph analysis for purpose detection involves centrality measures—metrics that quantify how important or central each node is within the network[7]. Different centrality measures define importance differently, providing multiple perspectives on node roles. Understanding these perspectives reveals how code elements contribute to overall system purpose.

**Degree Centrality** represents the simplest centrality measure, assigning importance based on the number of direct connections a node possesses[7]. For code analysis, degree centrality identifies highly connected components—functions that are called by many other functions have high in-degree and represent potentially critical infrastructure or utilities[7]. Functions that call many other functions have high out-degree and may represent orchestrators or coordinators. A utility function computing mathematical operations might have extremely high in-degree if widely used, while a main function orchestrating system startup would have high out-degree. However, degree centrality alone proves insufficient for purpose detection because it ignores broader network structure.

**Betweenness Centrality** measures how frequently a node appears on shortest paths between other nodes in the network[7][11]. A node with high betweenness centrality acts as a bridge connecting otherwise disconnected or distant portions of the network[11]. In code architecture, functions with high betweenness centrality serve as critical junction points—removing them would fragment the system's ability to communicate. These functions typically represent infrastructure components: message routers, request dispatchers, or central coordinators that connect distinct subsystems. The algorithmic complexity of computing betweenness centrality involves calculating shortest paths between all pairs of nodes, which can be resource-intensive for large graphs[11]. However, the insights provided prove invaluable for understanding architectural structure because betweenness centrality directly identifies components whose failure would most disrupt system function.

**Closeness Centrality** scores each node based on its average distance to all other nodes in the network[7][10]. Nodes with high closeness centrality are positioned to influence the entire network quickly by propagating information through minimal hops[7]. In code architecture, closeness centrality identifies components that can coordinate widely dispersed functionality—high closeness indicates a node positioned to reach many other components efficiently. This centrality measure proves particularly valuable for identifying orchestration points or main entry points that coordinate distributed functionality[7].

**Eigenvector Centrality** extends degree centrality by recognizing that connections to highly important nodes matter more than connections to peripheral nodes[7][10]. A node is important not just because it has many connections, but because those connections are to other important nodes[7]. In code analysis, eigenvector centrality identifies components that interact with other critical components—a function that calls other widely-used utilities becomes itself more important than a function calling rarely-used components. This measure captures the idea that architectural importance propagates through the network.

**PageRank Centrality** adapts eigenvector centrality for directed graphs by normalizing how influence flows through edges[8][10]. Unlike eigenvector centrality, PageRank accounts for the fact that a node's outgoing connections distribute its influence among destinations[8]. In code graphs with directed edges from callers to callees, PageRank identifies components whose role propagates through influence distribution. The mathematical foundation involves iterative updates where each node's score reflects the propagated scores of nodes that reach it[8].

These multiple centrality perspectives combine to reveal architectural purpose. An entity with high in-degree and high betweenness likely represents critical infrastructure that many components depend upon. An entity with high out-degree and high closeness likely represents orchestration or coordination. An entity with high eigenvector centrality but modest degree likely represents a specialist component that interacts primarily with other specialists. By examining this multi-dimensional centrality profile, semantic indexers can assign purpose classifications without examining implementation.

### Practical Graph Construction with NetworkX

NetworkX provides straightforward mechanisms for building code graphs from various data sources[1]. Creating a graph begins with instantiating a graph object—either an undirected Graph for symmetric relationships or a DiGraph for directed relationships such as function calls[1]. Nodes can be added incrementally through `add_node()` or `add_nodes_from()` methods, with optional attributes attached to each node storing metadata such as node type, module context, or complexity metrics[1].

Edges similarly can be added through `add_edge()` or `add_edges_from()` methods, with optional edge attributes capturing relationship semantics[1]. For code graphs, edge attributes might include call frequency (weight), relationship type (invokes, inherits, depends on), or operation names in case of service call graphs[1]. The attribute-like access pattern provides convenient syntax for setting and retrieving data: `G.nodes["function_name"]["complexity"] = 8` stores complexity metrics[1].

NetworkX supports multiple input formats for graph construction[1]. Adjacency dictionaries mapping nodes to their neighbors provide an intuitive format where each node key maps to a sequence of neighbor nodes[1]. This format matches naturally with code structures where you can easily enumerate what each function calls. The library also supports creating graphs directly from edge lists or adjacency matrices, enabling integration with various code analysis tools that extract structure in these formats[1].

Graph visualization and analysis in NetworkX follows consistent patterns[1]. The `.nodes` accessor provides a view of all nodes with their attributes; `.edges` provides an edge view with optional data inclusion via `data=True` parameter[1]. Iteration over nodes and edges uses natural Python semantics, enabling analysis code such as examining all neighbors of a given node through `G.neighbors(node_name)` or accessing the adjacency structure via `G.adj[node]`[1].

Advanced graph operations in NetworkX support common code analysis tasks[1]. The library provides functions for computing connected components, finding shortest paths, identifying subgraphs induced by node sets, and combining multiple graphs through union or Cartesian product operations[1]. For semantic indexing, identifying connected components reveals clusters of interconnected functionality—strongly connected components in directed graphs represent groups of mutually dependent code that should be understood as coherent units[1].

## Top-Down Context Propagation and Code Comprehension Cognitive Foundations

### Expert versus Novice Programmer Comprehension Patterns

Understanding how expert developers comprehend code differs fundamentally from how novices approach the same task, with profound implications for top-down context propagation in semantic indexers. Research comparing expert and novice programmers reveals that experts focus on fewer source code elements than novices, covering less of the code while achieving better understanding[14]. When reading code for bug fixing tasks, expert programmers read approximately 21% of method signatures compared to novices who read 44%; experts examine 12% of keywords while novices examine 26%[14]. This difference reflects expert ability to quickly identify important code elements through pattern recognition—experts use fewer visual fixations to extract the same information.

The distinction between expert and novice reading patterns extends to comprehension accuracy. Experts finish code comprehension tasks using fewer source code elements than novices, indicating they extract relevant information more efficiently[14]. This efficiency derives from experience-based pattern recognition where experts recognize common code structures, design patterns, and architectural roles instantly, whereas novices must examine implementation details to deduce purpose[14]. For semantic indexers, this research suggests that purpose determination should operate at multiple abstraction levels, allowing users to drill down from high-level architectural roles to implementation details, mimicking how experts navigate code understanding.

A complementary line of research examining readability preferences reveals tensions between what developers perceive as readable versus what actually supports comprehension. When comparing novice versus expert code patterns, novices judged expert code snippets as having better style in 76% of cases, but only 64% ranked them as most readable[17]. Comprehension accuracy, however, showed a different pattern: novices actually achieved better comprehension when reading novice-style code, despite preferring expert patterns[17]. This finding suggests that novices understand simpler code structures better, even though they recognize that expert patterns represent better style. For semantic indexers, this implies that context propagation should adapt to user expertise level—providing detailed intermediate steps for novices while allowing expert users to jump to high-level architectural purpose.

The research reveals that novices struggle with both expert code and with large code chunks. Novices have difficulty perceiving and understanding large code chunks, relying more heavily on line-level details[17]. This suggests that top-down context propagation should proceed hierarchically, starting with method-level or function-level purpose, then allowing navigation to lower-level implementation details as understanding develops[17]. Experts, conversely, recognize larger perceptual chunks, focusing readily on overall program purpose, suggesting they benefit from immediately available architectural context[17].

### Cognitive Models of Program Comprehension

Multiple cognitive models describe how programmers build mental models of software during comprehension activities. These models, developed through decades of research, provide theoretical foundations for designing semantic indexers that support natural comprehension processes. The most influential models include Brooks' model emphasizing top-down, expectation-driven understanding; Soloway's model emphasizing bottom-up plan recognition; and integrated models combining both approaches[34].

**Brooks' Model of Program Comprehension** emphasizes the role of prior knowledge in understanding[34]. In this model, understanding a program is essentially reconstructing the mappings from task domain through intermediate domains to programming domain[34]. The programmer begins with high-level goals and expectations about what the program should accomplish, then verifies these hypotheses against the code. When reading code, programmers generate hypotheses about functionality, then look for evidence supporting or refuting these hypotheses. As hypotheses are confirmed or refined, the programmer builds a mental model that grows progressively more complete[34]. This top-down process relies heavily on the programmer's existing knowledge—domain knowledge about what problems the program solves, goal knowledge about computational objectives, and plan knowledge about programming techniques for achieving those objectives[34].

For semantic indexers, Brooks' model suggests that providing clear, high-level purpose information enables readers to form initial hypotheses quickly. When users understand that a function serves an orchestration role through its relationship signature (high out-degree, high closeness centrality), they can form accurate expectations about its behavior without examining implementation. The indexer should present this high-level purpose information first, allowing readers to employ top-down comprehension processes naturally[34].

**Soloway's Model of Program Comprehension** emphasizes plan recognition and the bottom-up process of identifying programming plans in code[34]. In this model, programmers recognize common programming patterns—plans—and combine them to understand program purpose. A plan in this sense represents a technique for realizing an intention: a plan for sorting data, a plan for searching a collection, or a plan for coordinating multiple components[34]. When programmers encounter code, they attempt to recognize which plans the code implements by examining the structure and operations. The assimilation process involves reading code, recognizing plans, combining plans, and building mental models representing the program as a collection of instantiated plans[34].

Soloway's research identified that programmers store plans independently of specific programming languages and implementations, suggesting that plan knowledge represents relatively abstract, generalizable programming strategies[34]. For semantic indexers, this implies that purpose detection should identify and classify architectural plans—is this function implementing a cache manager plan, a dispatcher plan, a validation plan, or an aggregation plan? By recognizing which architectural plans a component implements through its relationships and interactions, the indexer provides the conceptual framework experts naturally use for understanding.

**Integrated Models Combining Top-Down and Bottom-Up Approaches** recognize that comprehensive program comprehension requires both expectation-driven top-down reasoning and pattern recognition-driven bottom-up reasoning[34]. The programmer's mental model represents successful mapping between high-level goals (top-down expectations) and recognized implementation plans (bottom-up patterns). When inconsistencies emerge between expectations and observed patterns, the programmer must revise hypotheses and regenerate expectations[34]. For semantic indexers, this integration suggests that purpose detection should provide both top-level architectural expectations (high-level role based on centrality metrics and relationship patterns) and recognized implementation patterns (common code plans implemented by this component).

### Hierarchical Semantic Context Propagation

The cognitive research on program comprehension directly supports hierarchical context propagation, where parent or container context influences how child elements should be understood[34]. When programmers comprehend a function within a class, the class context shapes expectation about the function's purpose. A function called `validate` means something different in a security validation class than in a data format validation class[34]. The context propagates from higher levels of abstraction (module, class) down to lower levels (methods, statements).

Top-down processing in reading comprehension, studied extensively in cognitive psychology, demonstrates that readers use their prior knowledge and expectations about text to guide comprehension of specific passages[16]. When reading code, programmers similarly employ context clues, background knowledge, and patterns to guide understanding. A function named `process` in a data pipeline module has different expected purpose than a function named `process` in a UI event handling module[16]. The container module provides the high-level semantic context that disambiguates the purpose.

For semantic indexers, hierarchical context propagation means computing purpose at module level first, then propagating that context when analyzing functions within the module. Module-level centrality and relationship patterns establish the system purpose that functions serve. A module with high closeness centrality and high out-degree likely represents orchestration infrastructure; functions within that module are interpreted through that lens. A module with high betweenness centrality represents a critical junction; functions within that module are understood as junction-related. This top-down propagation enables more accurate purpose classification than analyzing isolated functions.

## Multi-Modal Intent Extraction: Beyond Code Content

### The Intentional Gap Between Code and Purpose

Developer intent—why code is structured as it is, what problems it solves, what architectural roles it plays—exists partially in code but substantially in external sources: commit messages, documentation, GitHub issues, pull request discussions, and team communications[21]. Traditional code indexers examining only implementation details capture partial intent. The semantic code indexer that PURPOSE = f(edges) begins capturing intent through relationships, but complete intent extraction requires analyzing multiple modalities.

Research on intention mining in developer discussions identifies six core intention categories that developers express: feature request, opinion asking, problem discovery, solution proposal, information seeking, and information giving[21]. When developers discuss code changes in commit messages, pull requests, and issue tracking systems, they express these intentions. An issue marked as "bug report" with "problem discovery" intent indicates the code addresses a specific problem. A pull request discussing "architectural refactoring" indicates intentional redesign. Comments in code expressing "solution proposal" intent indicate how developers intended functionality to evolve[21]. By mining these intentions, semantic indexers capture the "why" behind code structure.

Intent extraction from developer communications employs natural language processing techniques, particularly deep learning approaches using convolutional neural networks trained on intention classification tasks[21]. Research demonstrates that CNN-based approaches combined with batch normalization can automatically classify developer intent from discussion text with substantial accuracy, enabling automatic extraction of what problems code addresses and what solutions developers intended to implement[21]. For semantic indexers integrating multi-modal analysis, this capability enables annotating code elements with extracted intent: "This function was created to solve issue #427 (performance bottleneck in data loading)" or "This module was extracted to implement distributed caching architecture proposed in RFC-2023-04."

### Code Summarization and Intent Capture

The challenge of generating meaningful code summaries—concise natural language descriptions of code functionality—directly relates to intent capture[49][52]. Code summarization models must extract what code does at a semantic level, not just what its syntax describes[52]. Recent research explores code summarization beyond function level, investigating how class and repository context affects summary quality[49]. The critical finding: summarization quality improves significantly when models incorporate broader context—class context showing the module's purpose, repository context showing the system's architecture[49].

This context dependency mirrors how developers understand code: they don't read functions in isolation but understand them within class context, module context, and system context. For semantic indexing, this implies that intent extraction should operate hierarchically: understand repository-level intent (what is the system trying to accomplish?), then module-level intent (how does this module contribute to system purpose?), then function-level intent (how does this function serve module purpose?)[49]. The hierarchical intent flows downward, with higher-level intent shaping how lower-level code elements are understood.

Transformer-based language models fine-tuned on code summarization tasks demonstrate strong capabilities for semantic analysis when provided with adequate context[51][52]. Models such as CodeT5, which were specifically designed for code understanding tasks, outperform general-purpose language models at code-related tasks[51]. The effectiveness of code-specific models derives from their training on large code corpora, enabling them to learn patterns and relationships that generic models miss. However, even these specialized models show degraded performance on adversarial inputs—when function or variable names are systematically renamed to generic identifiers, models rely on remaining semantic features such as control flow structure and variable usage patterns[51].

### Multi-Modal Code Editing and Semantic Fusion

Recent research on multi-modal code editing—integrating heterogeneous inputs including code fragments, natural language descriptions, visual inputs, and input-output examples—reveals how multiple modalities combine to inform semantic understanding[19]. Multi-modal systems employ encoder-decoder Transformer architectures that learn cross-modal alignment, fusing information from diverse modalities to make more accurate predictions[19]. The key insight for semantic indexing: multiple modalities provide complementary semantic information that individually they cannot fully capture.

Causal analysis of multi-modal systems reveals that different modalities have varying causal effects on code generation outcomes[19]. Natural language specifications provide explicit intent; input-output examples provide behavioral constraints; code context provides structural guidance. The effects vary by task complexity and code type—simple tasks may be adequately specified by natural language alone, while complex architectural refactoring requires code context and behavioral examples[19]. For semantic indexers, this suggests that intent extraction should weight different modality sources appropriately: for utility functions, code patterns and usage relationships may provide sufficient intent; for complex coordinators, explicit documentation and issue discussions become critical.

### Commit Message and Documentation Analysis

Developers express significant intent in commit messages and pull request discussions[20][21]. An empirical study analyzing 28,524 multi-turn developer-LLM conversations in coding tasks identified prevalent intent categories in how developers refine their requests: missing specifications (developers realize they didn't fully specify requirements), different use cases (developers ask for handling multiple scenarios), and additional functionality (developers request feature extensions during conversations)[20]. By analyzing these patterns in commits and issues, semantic indexers can extract the real-world intent that drove code changes.

Documentation patterns also reveal intent. API documentation describes what code does; architecture decision records (ADRs) capture why decisions were made; design documents describe intended system behavior before implementation[23]. The "why" expressed in documentation directly captures developer intent that code alone cannot express. A function might have high centrality suggesting infrastructure role; documentation explaining "this component implements request routing with failover support" provides explicit intent that complements the graph-based inference.

## Local LLM Deployment for Semantic Code Analysis

### Small Model Performance Landscape

The landscape of large language models has shifted dramatically with the emergence of capable small models that rival much larger systems on specific tasks. Research comparing small language models with large models on zero-shot text classification reveals that small models (77M to 3B parameters) can effectively classify texts, matching or surpassing larger counterparts[29]. This finding contradicts the prevailing assumption that bigger models always perform better. When properly designed with appropriate scoring functions and prompt engineering, small models demonstrate "competitive performance across diverse classification tasks, challenging the dominance of large models"[29].

Fine-tuned small models demonstrate even more dramatic advantages over zero-shot large models. Comprehensive comparisons of fine-tuned BERT-style language models against zero-shot generative AI models (ChatGPT-3.5, ChatGPT-4, Claude Opus) consistently show that smaller, fine-tuned models outperform larger zero-shot models on text classification tasks[26]. In specialized domains requiring specific classification accuracy, "smaller, fine-tuned LLMs constitute the state-of-the-art," delivering superior performance while requiring orders of magnitude less computational resources[26]. The practical implication: for semantic code analysis tasks like classifying code elements into architectural roles, fine-tuned small models deployed locally may outperform cloud-based large models while providing better latency and privacy.

The trade-offs between local small models and cloud-based large models involve multiple dimensions beyond mere accuracy[30]. Cloud-based solutions provide immediate access to cutting-edge models without infrastructure investment but introduce data privacy concerns when sensitive code cannot leave the organization. Local small models provide complete privacy and control, lower latency (no network round-trips), and reduced operating costs at scale, but require maintaining local GPU infrastructure and managing model updates[30]. For enterprise code analysis where repositories contain proprietary algorithms and architectural patterns, local deployment with small models often represents the optimal trade-off[30].

### Ollama and Edge LLM Deployment

Ollama provides a practical infrastructure for deploying and managing open-source language models locally[25][28]. The tool simplifies model management through familiar Docker-like commands: `ollama pull modelname` downloads a model; `ollama run modelname` executes inference; configuration files specify model parameters[25]. This simplicity enables developers to quickly experiment with models without deep machine learning infrastructure expertise.

The Ollama model library includes code-specific models specifically optimized for semantic code tasks[28]. Qwen2.5-Coder models provide "significant improvements in code generation, code reasoning, and code fixing" compared to general-purpose models, achieving performance approaching CloudGPT-4o on code tasks with 7B to 14B parameters[28]. These models, trained on vast code corpora with explicit focus on code semantics, outperform general-purpose models substantially on code-related tasks despite their smaller size. For semantic classification tasks like determining whether a function serves coordination versus computation roles, code-specific models trained on code patterns provide better semantic understanding than general-purpose models.

Practical deployment of Ollama for semantic indexing involves several configuration considerations. Hardware requirements depend on model size: 7B parameter models typically require 8-16GB GPU memory; 14B models require 24GB+[25]. The memory management proves sophisticated—Ollama automatically loads and unloads models in the background to conserve resources, introducing slight latency on first invocation after model parking[25]. For development environments, this lazy loading enables running multiple models within constrained GPU memory by allowing Ollama to swap models as needed.

Integration with development tools occurs through Continue, a VSCode extension providing in-context LLM assistance through Ollama backends[25]. The integration pattern provides a template for semantic indexer deployment: the indexer processes code graphs and relationship data locally, invoking Ollama for semantic classification through carefully crafted prompts. The local Ollama instance executes inference without transmitting code outside the developer's system, providing privacy while maintaining performance.

### Fine-Tuning Strategies for Semantic Role Classification

While zero-shot classification with well-designed prompts can classify code elements into semantic roles, fine-tuning small models on domain-specific data provides superior performance when adequate training data is available[26]. The training procedure involves creating datasets of code elements annotated with their semantic roles, then fine-tuning a small model on this data. For semantic indexing, this might involve annotating functions with labels such as "orchestrator," "infrastructure," "computation," "validation," derived from both relationship patterns and manual expert review.

The fine-tuning procedure proves computationally efficient for small models. Training a 7B parameter model on a modestly-sized dataset (1000-5000 examples) typically requires only hours on consumer GPU hardware[26]. The resulting model provides specialized semantic understanding for the specific codebase domain. While general-purpose models might struggle with domain-specific architectural patterns in a particular company's codebase, a fine-tuned model learns those patterns through training data[26].

Active learning approaches can further optimize fine-tuning efficiency. Rather than manually annotating random code elements, active learning identifies the most informative examples—elements where the model's predictions are uncertain or where the model's predictions differ from patterns in labeled data. By prioritizing annotation of these informative examples, active learning reduces the annotation burden required to achieve target performance[26]. For semantic indexing, this means an indexer could initially use zero-shot classification, identify low-confidence predictions, and present those to developers for manual labeling, continuously improving the model's performance on their specific codebase.

### Prompt Engineering for Semantic Code Analysis

The quality of semantic classification using local LLMs depends critically on prompt design. A well-engineered prompt provides sufficient context about the code element and its relationships while guiding the model toward the desired classification. For semantic indexing, effective prompts incorporate the relationship signature—who calls the function, what it calls, its module context, its centrality metrics.

A structured prompt for semantic classification might follow this pattern:

```
Analyze the following function and classify its architectural role based on 
its relationships and context.

Function: {function_name}
Module: {module_name}
Module Purpose: {module_high_level_purpose}

Relationships:
- Called by: {list_of_callers}
- Calls: {list_of_callees}
- In-degree centrality: {in_degree_score}
- Out-degree centrality: {out_degree_score}
- Betweenness centrality: {betweenness_score}
- Closeness centrality: {closeness_score}

Classification: What role does this function play in the system architecture?
- Orchestrator (coordinates multiple components)
- Infrastructure (provides foundational services)
- Computation (performs domain logic)
- Validation (checks constraints)
- Utility (simple transformation or helper)
- Other: [specify]

Reasoning: Explain how the relationships and context support this classification.
```

This prompt structure provides the semantic information derived from graph analysis—centrality metrics, relationship counts, module context—enabling the model to reason about architectural role based on relationship patterns rather than implementation details. The prompt explicitly names possible roles and asks for reasoning, encouraging the model to explain its classification based on structural patterns.

Few-shot prompting—providing example classifications before requesting classification of target functions—further improves performance. By showing examples of orchestrators, infrastructure components, and utility functions with their relationship signatures, the prompt establishes patterns the model should recognize[29]. Few-shot prompting with retrieved examples—selecting examples similar to the target function for inclusion in the prompt—provides even better performance than random examples[29].

## Practical Implementation Architecture

### Graph Construction Pipeline

A semantic code indexer implementing PURPOSE = f(edges) requires a pipeline that constructs comprehensive code graphs from source code analysis. The pipeline begins with static code analysis to extract structure: identifying all functions, methods, classes, and modules; determining invocation relationships; identifying import dependencies; noting module organization. Tools like CodeRAG demonstrate this extraction at scale, automatically scanning and mapping classes, methods, interfaces, and dependencies across multiple programming languages[2].

The extraction phase produces structured data describing code entities and their relationships. For each function, the extractor determines: its full qualified name, module, class context (if applicable), return type, parameter types, and all functions it invokes. For each module, the extractor determines its dependencies on other modules. This structural information forms the foundation for graph construction.

Graph construction in NetworkX proceeds from this structured data. Functions and modules become nodes; invocation and dependency relationships become edges. Edge attributes capture relationship semantics: edge type (calls, depends_on, imports), relationship count (how many times called), and optional runtime metrics if available. For code-specific analysis, the graph might employ different edge types for different relationship categories, enabling separate analysis of data dependencies versus control flow dependencies.

The constructed graph enables sophisticated queries supporting semantic analysis. Querying the in-neighbors of a function reveals all functions calling it; querying out-neighbors reveals all functions it calls. Traversing the graph from root functions to leaves reveals call chains showing execution flow. Computing centrality metrics reveals architectural importance from multiple perspectives.

### Hierarchical Context Propagation Implementation

Context propagation implementation recognizes that code purpose exists at multiple levels of abstraction. Module-level purpose describes what the module contributes to overall system functionality. Class-level purpose describes what the class represents as a coherent abstraction. Function-level purpose describes what the specific function does within its container context.

The propagation process begins at the system level: analyzing the system dependency graph to understand modules' roles. Modules with high out-degree and high closeness centrality that reach many other modules likely coordinate system behavior. Modules with high in-degree represent infrastructure relied upon by other system components. Modules with high betweenness centrality connect otherwise disparate system portions. This system-level analysis establishes high-level architectural context.

Next, module-level analysis propagates context downward. Within each module, classes and major functions are analyzed. Classes whose methods are called primarily by external modules implement the module's public interface. Classes whose methods call many external dependencies represent internal implementation helpers. Functions with high eigenvector centrality within the module interact extensively with other important components within the module.

Finally, function-level analysis occurs with full context. A utility function with high in-degree is understood as an important helper throughout the module, not as peripheral code. A function with high out-degree calling many external dependencies is understood as a coordinator. A small function with low in-degree and out-degree is understood as peripheral or specialized. The hierarchical context transforms raw metrics into semantic understanding.

Implementation in code might follow this pattern:

```python
class SemanticCodeIndexer:
    def __init__(self, call_graph, dependency_graph):
        self.call_graph = call_graph
        self.dependency_graph = dependency_graph
        self.node_purposes = {}
    
    def analyze_system_level(self):
        """Compute system-level architectural roles"""
        # Compute metrics for all modules
        modules = self.extract_modules()
        for module in modules:
            subgraph = self.get_module_subgraph(module)
            module_in_degree = self.compute_in_degree(module)
            module_out_degree = self.compute_out_degree(module)
            module_betweenness = nx.betweenness_centrality(
                self.dependency_graph, normalized=True
            )[module]
            
            # Determine module role based on metrics
            if module_out_degree > 0.5 and module_in_degree < 0.3:
                role = "orchestrator"
            elif module_in_degree > 0.5 and module_out_degree < 0.3:
                role = "infrastructure"
            elif module_betweenness > 0.4:
                role = "critical_junction"
            else:
                role = "domain_logic"
            
            self.node_purposes[module] = {
                'level': 'module',
                'role': role,
                'metrics': {
                    'in_degree': module_in_degree,
                    'out_degree': module_out_degree,
                    'betweenness': module_betweenness
                }
            }
    
    def analyze_function_level(self, function_name):
        """Analyze function with full hierarchical context"""
        module = self.get_function_module(function_name)
        module_role = self.node_purposes[module]['role']
        
        # Compute function-level metrics
        in_degree = self.call_graph.in_degree(function_name)
        out_degree = self.call_graph.out_degree(function_name)
        
        # Construct semantic context
        context = {
            'function': function_name,
            'module': module,
            'module_role': module_role,
            'relationships': {
                'callers': list(self.call_graph.predecessors(function_name)),
                'callees': list(self.call_graph.successors(function_name)),
                'in_degree': in_degree,
                'out_degree': out_degree,
            }
        }
        
        # Classify with context
        classification = self.classify_function_role(context)
        return classification
    
    def classify_function_role(self, context):
        """Use LLM to classify function role with rich context"""
        prompt = self.construct_classification_prompt(context)
        classification = self.llm_client.classify(prompt)
        return classification
```

### Multi-Modal Intent Integration

The indexer integrates multiple information sources beyond call graphs. Git commits, GitHub issues, pull request discussions, and documentation provide intent signals that graphs alone cannot capture. The integration process extracts intent from each modality, assigns confidence scores, and combines signals to enhance purpose understanding.

Commit message analysis extracts developer intent. The semantic classifier identifies intention categories in commit messages: "Fixed data loading bottleneck" expresses problem discovery and solution proposal; "Refactored caching layer for architectural clarity" expresses intentional redesign[21]. Functions modified in commits with high intent confidence receive annotations capturing extracted intent. Over time, functions accumulate intent annotations reflecting the problems they've solved and the architectural intentions they've manifested.

Documentation analysis provides explicit intent. Docstrings, design documents, and architecture decision records express what developers intended. A function with docstring "Coordinates request processing across availability zones" provides explicit orchestration intent. A function with architecture decision record reference "Implements exponential backoff retry pattern per RFC-2023-05" provides explicit pattern intent. The indexer extracts and associates these explicit intents with code elements.

Issue analysis connects code elements to problems they address. When commits reference issues ("fixes #427"), the indexer associates code modifications with those issues. Issues expressing performance problems, architectural concerns, or feature requests connect to code elements addressing them. This creates a traceability link from code elements to the real-world problems they solve.

The combined multi-modal analysis produces rich semantic annotations. Rather than inferring purpose purely from relationships, the indexer can state: "This function serves as infrastructure providing central request routing (based on relationship metrics: high in-degree=487, high out-degree=23, high betweenness=0.62), explicitly documented as 'Central request dispatcher' with architectural intent to 'improve request distribution latency' (from issue #427), with history of modifications addressing performance and reliability concerns."

## Implementation Considerations and System Design

### Language Coverage and Static Analysis Integration

Semantic indexing across multi-language codebases requires language-specific static analysis. CodeRAG demonstrates comprehensive language detection and analysis for TypeScript/JavaScript, Java, Python, and C# with planned expansion[2]. Each language requires specialized parsing to extract structure accurately: Python's dynamic typing requires different analysis than Java's static types; JavaScript's prototype-based inheritance differs from class-based systems; C#'s async/await patterns differ from Java's threading models.

The static analysis integration point determines what information becomes available for graph construction. Language-specific AST (Abstract Syntax Tree) parsers extract function signatures, call relationships, and type information[44]. ASTs provide the syntactic structure of source code, abstracting away stylistic details while preserving essential structure[44]. By traversing ASTs and extracting call relationships, static analyzers build accurate call graphs even in the presence of language-specific features like closures, higher-order functions, or dynamic invocations[44].

For multi-language systems, the indexer maintains separate graphs per language or creates a unified graph with language-specific edge labels. Language boundaries themselves become meaningful: cross-language service calls versus within-language function calls represent qualitatively different relationships. A Java service calling a Python worker through message queues differs from a Java method calling another Java method directly.

### Scalability Considerations for Large Systems

Graph analysis operations scale as either linear (O(n)) or quadratic (O(n²)) depending on the operation. Computing degrees for all nodes scales linearly; computing all-pairs shortest paths scales quadratically. For systems with millions of functions, quadratic operations become computationally prohibitive. Practical implementations employ several techniques to manage scale.

Sampling approaches approximate metrics for large graphs. Rather than computing exact betweenness centrality (which requires all-pairs shortest paths), approximation algorithms compute betweenness on a random sample of node pairs, providing good estimates in significantly reduced time[11]. For semantic indexing, approximate metrics often provide sufficient information to classify roles: a rough estimate that a function is highly central usually suffices; precise ranking of top functions matters less.

Hierarchical analysis decomposes large graphs into subgraphs enabling separate analysis. System-level analysis examines module relationships; module-level analysis examines function relationships within modules; class-level analysis examines method relationships within classes. This decomposition reduces problem size at each analysis level. Computing centrality within a module containing 100 functions requires far less computation than computing centrality over 1 million system functions.

Incremental analysis updates metrics when code changes rather than recomputing everything. When a developer modifies a function's call relationships, the indexer incrementally updates affected metrics rather than recomputing the entire system's metrics. This incremental approach scales linearly with change size rather than system size, enabling real-time indexing as code evolves[3].

### Handling Dynamic and Distributed Code

Traditional static analysis limitations emerge in dynamic and distributed systems. Function pointers, reflection, and plugin architectures create call relationships visible only at runtime. Distributed service calls through message queues or HTTP requests appear nowhere in call graphs constructed from local code analysis. Protocol buffers, gRPC definitions, and REST API specifications define cross-system relationships that static analysis might miss.

Handling dynamic code requires dynamic analysis: running the code and observing actual call relationships. Call graph tools monitor execution and record all function invocations, producing dynamic call graphs showing actual runtime behavior[42]. The trade-off: dynamic graphs show only code paths executed during observation, missing conditional code paths not exercised. For semantic indexing, dynamic analysis complements static analysis: static graphs show all potential call relationships; dynamic graphs show which relationships are actually used[42].

Distributed systems require API specification analysis. GraphQL schemas, OpenAPI specifications, and protocol buffer definitions define relationships between distributed components. The indexer should parse these specifications and build cross-service call graphs, enabling understanding of distributed purpose. A service defined with high out-degree in API specifications toward other services plays coordination roles; services with high in-degree provide infrastructure services[39].

## Conclusion and Future Directions

### Synthesis of Integrated Approach

Building semantic code indexers around the principle that PURPOSE = f(edges) creates a fundamentally different approach to code understanding than content-based analysis. By combining graph theory providing relationship analysis, cognitive science research guiding hierarchical context propagation, multi-modal analysis capturing developer intent, and local LLMs enabling semantic classification, the indexer captures purpose without analyzing implementation details.

The graph-based foundation provides objective relationship metrics: centrality measures revealing architectural importance, call chain analysis revealing execution flows, dependency patterns revealing system organization[5][6][7]. These metrics offer quantifiable insights into how code elements contribute to system function. Combined with centrality analysis identifying infrastructure versus orchestrators versus specialized computation, relationship analysis provides robust purpose inference[7][11].

Cognitive research ensures the indexer aligns with how developers naturally understand code. Hierarchical context propagation mimics expert comprehension patterns where developers understand functions within class context, classes within module context, modules within system context[31][34]. Top-down analysis proceeds from high-level architectural roles to low-level implementation, matching expert developer cognition[14][34].

Multi-modal intent extraction adds semantic richness that graphs alone cannot provide. Extracting intent from commits, documentation, and issues captures why code is structured as it is, not just what relationships exist[21][49]. The combined signal—relationship patterns indicating infrastructure role, documentation explicitly stating "foundational service," commits addressing architectural concerns—creates confidence in semantic classification.

Local LLMs enable practical deployment within organizational boundaries. Fine-tuned small models achieve state-of-the-art performance on semantic classification tasks, delivering superior results compared to zero-shot large models while preserving code privacy[26][29]. Ollama deployment simplifies infrastructure requirements, enabling developers to run semantic indexers locally without cloud dependencies[25][28].

### Recommended Implementation Approach

An organization building a semantic code indexer following this framework should:

Begin with graph construction using static analysis extracting call and dependency relationships, building NetworkX graphs capturing system structure. Start with a single programming language and demonstrate capability before expanding to multi-language systems. Implement basic centrality metric computation (in-degree, out-degree, betweenness) providing initial purpose signals.

Extend with hierarchical context propagation analyzing system-level metrics first, then propagating context to module and function levels. Implement top-down analysis presenting high-level architectural purpose before drilling into implementation details. Validate that purpose inferences align with expert developer understanding through user studies.

Integrate multi-modal analysis extracting intent from commits, documentation, and issues. Start with commit message analysis since this source is readily available in all systems. Gradually add documentation analysis and issue tracking analysis. Develop mapping from extracted intents to code element annotations creating observable intent patterns.

Deploy local LLMs for semantic classification using Ollama infrastructure. Begin with zero-shot classification using well-engineered prompts incorporating relationship and context information. As usage patterns emerge, fine-tune models on organization-specific code with manual purpose annotations. Use active learning to prioritize annotation effort on high-uncertainty classifications.

Validate system accuracy through developer surveys and click-through analysis. Do developers find the inferred purposes accurate? Do they use the semantic index to navigate code more effectively? Does understanding architectural roles through relationship analysis improve onboarding time for new developers?

### Future Research Directions

Several promising research directions extend this work. First, **graph neural networks** applied to code graphs could learn purpose representations without explicit rule-based feature extraction[50]. Rather than computing centrality metrics manually, graph neural networks could learn which structural patterns predict purpose roles, automatically discovering relevant features[50][53]. This approach might capture subtler architectural patterns that centrality metrics alone cannot express.

Second, **causal analysis of multi-modal systems** could quantify how much each information source contributes to accurate purpose inference[19]. Does code structure alone provide sufficient information for accurate purpose classification? How much does documentation improve accuracy? Do commit messages provide additional signal beyond code structure? Answering these questions optimizes resource allocation for intent extraction.

Third, **longitudinal analysis of code evolution** could track how purpose changes over time. Does a utility function gradually become infrastructure? Does an orchestrator become specialized? How do refactoring efforts change purpose relationships? Temporal analysis could identify architectural drift and provide early warning of technical debt accumulation.

Fourth, **cross-project transfer learning** could enable training semantic classifiers on open-source codebases and transferring the model to proprietary code. If purpose patterns generalize across systems, models trained on public code might classify proprietary code accurately, reducing annotation burden. Research on domain adaptation techniques could improve transfer efficiency.

Finally, **interactive semantic debugging** could combine semantic code indexing with development tools. As developers write code, the indexer provides real-time feedback on architecture consistency: "This function has 500 callers (infrastructure role) but is in a domain-logic module. Is this intentional?" Such feedback could help developers maintain architectural coherence as code evolves.

The semantic code indexer framework presented here provides a foundation for understanding software architecture through relationship analysis, cognitive science principles, and multi-modal learning. By implementing PURPOSE = f(edges), organizations can build tools that help developers understand and maintain complex systems more effectively, identifying architectural patterns and roles without requiring manual code reading or documentation maintenance.

---

## Citations

1. https://networkx.org/documentation/stable/tutorial.html
2. https://github.com/JonnoC/CodeRAG
3. https://en.wikipedia.org/wiki/Dependency_graph
4. https://github.com/aider-ai/aider/issues/4538
5. https://www.falkordb.com/blog/code-graph-analysis-visualize-source-code/
6. https://www.puppygraph.com/blog/software-dependency-graph
7. https://www.turing.com/kb/graph-centrality-measures
8. https://pro.arcgis.com/en/pro-app/3.6/help/data/knowledge/compute-centrality-scores-to-measure-the-importance-of-link-chart-entities.htm
9. https://learning-gate.com/index.php/2576-8484/article/view/8672
10. https://cambridge-intelligence.com/keylines-faqs-social-network-analysis/
11. https://graphable.ai/blog/betweenness-centrality-algorithm/
12. https://web-backend.simula.no/sites/default/files/publications/Simula.SE.503.pdf
13. https://pmc.ncbi.nlm.nih.gov/articles/PMC2099308/
14. https://www.cs.kent.edu/~jmaletic/papers/EMIP2021.pdf
15. https://pmc.ncbi.nlm.nih.gov/articles/PMC10827785/
16. https://www.structural-learning.com/post/top-down-processing-and-bottom-up-processing
17. https://acelab.berkeley.edu/wp-content/papercite-data/pdf/autostyle-readability-comprehension-icse2019.pdf
18. https://www.lrdc.pitt.edu/schunn/papers/mosschunnetal2011.pdf
19. https://www.emergentmind.com/topics/multi-modal-code-editing-mce
20. https://arxiv.org/html/2509.10402v1
21. https://xin-xia.github.io/publication/tse185.pdf
22. https://www.worldscientific.com/doi/10.1142/S0218194024500050
23. https://getdx.com/blog/developer-documentation/
24. https://dl.acm.org/doi/10.1145/3715780
25. https://gist.github.com/othyn/42e67d7b6116d88d6c9c83e7d84b20c0
26. https://arxiv.org/html/2406.08660v1
27. https://nexla.com/ai-readiness/llm-comparison/
28. https://ollama.com/library/
29. https://aclanthology.org/2024.lrec-main.1299.pdf
30. https://www.onlogic.com/blog/edge-llms-vs-cloud-llms/
31. https://sites.cc.gatech.edu/reverse/repository/cogmodels.pdf
32. https://www.oreateai.com/blog/understanding-architecture-diagrams-a-visual-language-for-software-design/0eed74c35c96047a4a4a682d0991490c
33. https://www.baytechconsulting.com/blog/software-maintenance-evolution-guide
34. https://www.cs.kent.edu/~jmaletic/cs69995-PC/papers/von_mayrhauser95.pdf
35. https://software-architecture-guild.com/guide/architecture/fundamentals/visualizing-architecture/
36. https://www.bridge-global.com/blog/software-maintenance-and-support-guide/
37. https://getstream.io/glossary/ai-agent-orchestration/
38. https://arxiv.org/html/2509.23686v1
39. https://www.abhishek-tiwari.com/unveiling-graph-structures-in-microservices-service-dependency-graph-call-graph-and-causal-graph/
40. https://www.databricks.com/blog/types-ai-agents-definitions-roles-and-examples
41. https://faculty.ist.psu.edu/wu/papers/fid.pdf
42. https://www.freecodecamp.org/news/how-to-automate-call-graph-creation/
43. https://github.com/Jaso1024/Semantic-Code-Embeddings
44. https://dev.to/balapriya/abstract-syntax-tree-ast-explained-in-plain-english-1h38
45. https://uwspace.uwaterloo.ca/bitstreams/59c99986-b24c-4970-8d45-1b702d7ee792/download
46. https://arxiv.org/abs/2008.03731
47. https://arxiv.org/abs/2312.00413
48. https://arxiv.org/abs/1803.09473
49. https://arxiv.org/html/2502.16704v1
50. https://distill.pub/2021/gnn-intro
51. https://aclanthology.org/2023.genbench-1.5.pdf
52. https://www.ibm.com/think/tutorials/code-summarization-with-granite
53. https://www.datacamp.com/tutorial/comprehensive-introduction-graph-neural-networks-gnns-tutorial
54. https://poloclub.github.io/transformer-explainer/
55. https://www.catchpoint.com/api-monitoring-tools/api-architecture
56. https://opsera.ai/blog/13-code-quality-metrics-that-you-must-track/
57. https://pmc.ncbi.nlm.nih.gov/articles/PMC10019629/
58. https://blog.bytebytego.com/p/software-architecture-patterns
59. https://www.geeksforgeeks.org/dsa/complexity-metrics/
60. https://www.emergentmind.com/topics/semantic-guided-hierarchical-codebooks-semhitok

---

## Usage Stats

- Prompt tokens: 216
- Completion tokens: 10062
- Total tokens: 10278
