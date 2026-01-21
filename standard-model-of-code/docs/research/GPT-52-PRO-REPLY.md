You did get real, actionable signal out of that Perplexity dump — but a couple pieces need to be “snapped to” what tree-sitter actually implements so your Phase 1 + Phase 2 plan doesn’t drift.

 

Below is the clean synthesis you can hand to your agent as the spec.

1) The biggest correction: locals.scm is a real engine with more than 3 captures

Your research doc is right that these three captures are “special”:

@local.scope

@local.definition

@local.reference

Tree-sitter’s official highlighting system recognizes these capture names as part of its locals mechanism.

 

But it’s missing two critical details from the actual implementation:

A) There is an optional fourth capture you should support

The tree-sitter highlighter also recognizes:

@local.definition-value

This capture exists specifically so references in/around an initializer don’t incorrectly bind to the new definition (and to enforce “defined before use” when you want that behavior). You can see it explicitly wired into the highlighter.

B) There is an important per-scope property

The engine also reads a query property:

local.scope-inherits (default true)

If set false on a scope pattern, name resolution stops there instead of walking outward. That is implemented in-tree-sitter’s highlighter logic.

 

Net: your Phase 2 “ScopeAnalyzer” should implement:

local.scope

local.definition

local.definition-value (optional but strongly recommended)

local.reference

local.scope-inherits (optional but easy)

2) The real locals algorithm (this is what you should port)

Your Perplexity doc hand-waved “scope stack” — that’s correct, but here’s the exact behavior tree-sitter uses (from tree-sitter-highlight):

Maintain a stack of scopes, each with:

byte range

inherits flag

list of definitions in that scope

When you hit a @local.scope capture:

push a new scope with that node’s byte range

read local.scope-inherits property (default true)

When you hit a @local.definition capture:

add a definition with:

name = source text for captured node

value_range = byte range of @local.definition-value capture if present, else 0..0

(definitions are stored so the latest shadows earlier ones)

When you hit a @local.reference capture:

walk scopes from innermost → outermost

within each scope, walk defs from newest → oldest

match on name AND require: ref.start >= def.value_range.end

stop early if inherits == false

This is all directly visible in the upstream highlighter code.

Why this matters for Collider

This is the difference between:

“we have scopes” (nice)

and “we have predictable, deterministic name binding with shadowing + initializer safety” (the part that makes edge resolution stop being vibes)

3) Your Phase 1 architecture: what actually changes

From your earlier comparison (“flat files” vs “nested dirs”):

Use the nested layout — it matches the dominant ecosystem convention

Neovim’s query layout is queries/<lang>/<purpose>.scm (and it’s what most people expect).

 

So implement:

src/core/queries/
  python/
    symbols.scm
    calls.scm
    locals.scm
  javascript/
    symbols.scm
    calls.scm
    locals.scm
  go/
    symbols.scm
    calls.scm
    locals.scm   (optional)

QueryLoader: one line difference (but do it now)

Your loader should resolve:

base / language / f"{query_type}.scm"

instead of

base / f"{language}_{query_type}.scm"

That’s it structurally — but it unlocks Phase 2 cleanly.

4) Phase 2A: the minimal viable ScopeAnalyzer that actually helps edges

Here’s the MVP that will immediately improve call-edge resolution within a file:

Data model (keep it tiny)

Scope { id, parent_id, range, inherits, defs: list[Def] }

Def { name, def_node_id, available_after_byte }

Ref { name, ref_node_id, start_byte }

Where:

available_after_byte should usually be:

end of @local.definition-value range if present

else end of the definition identifier itself (your choice; see note below)

Analyzer steps

For each file:

Parse → tree

Run locals.scm query → captures

Sort capture events by node.start_byte (and stable-tie-break for same node)

Apply the stack algorithm above

Produce a lookup:

ref_node_id -> def_node_id | None

Integrate into edge_extractor

When you see a call like:

Python: (call function: (identifier) @callee)

JS: (call_expression function: (identifier) @callee)

You resolve @callee via the scope binding map:

if it resolves to a function definition particle → emit a precise edge

else → fall back to your current heuristic (“same name in file/module/global index”)

This gives you the “95% within-file” lift your Perplexity synthesis promised, without doing imports yet.

5) Python gotcha: your doc is right, and it’s non‑negotiable

Do not treat class bodies as lexical scopes for methods in Python.

 

PEP 227 is explicit: when resolving nested scopes, class scopes are skipped; you can’t access class-body names from a method by bare name — you must use attribute access (self.x or ClassName.x).

 

So your Python locals.scm design rule is correct:

✅ (function_definition) @local.scope

✅ (lambda) @local.scope

✅ comprehensions as scopes (practically useful)

❌ (class_definition) @local.scope (do not do this)

If you violate this, your “scope-aware edge resolution” will confidently produce wrong bindings in Python.

6) JavaScript gotchas: block scope + hoisting are not solved by locals.scm alone

Your Perplexity synthesis hinted at this (“tree-sitter can’t do TDZ/hoisting perfectly”). That’s accurate.

 

Also: the stock JS locals query shipped in the Rust crate is intentionally simple (it treats statement blocks as scopes and identifiers as refs).
That’s fine for highlighting, but for analysis you’ll want to add language-aware rules later:

let/const: block scoped + TDZ (position-sensitive)

var: function scoped (not block scoped)

function declarations: hoisted

function expressions / arrow functions assigned to vars: not hoisted like declarations

Practical path (don’t boil the ocean):

Phase 2A: get “good enough” within-file by resolving most identifier calls to nearest definition

Phase 2B: add JS-specific availability rules (hoist certain defs; restrict others by position)

7) The “no existing library” claim is not quite true

If someone told you “there’s no production-grade implementation to learn from,” that’s misleading.

 

There are production-grade systems that do scope graphs over tree-sitter, notably stack graphs and language-specific implementations built on them (Rust ecosystem). Your team may still decide to “roll your own” in Python (reasonable), but it’s worth studying because it encodes years of edge cases.

8) What I would tell your agent to do next (copy/paste task list)
Phase 1 (make Phase 2 cheap)

Create src/core/queries/<lang>/ structure.

Implement QueryLoader(language, query_type) with caching.

Move your existing inline queries into:

symbols.scm

calls.scm

Add a test that verifies:

queries compile

cache hit works

missing query file fails gracefully

Phase 2A (single-file scope binding)

Implement ScopeAnalyzer that ports the tree-sitter-highlight locals algorithm including:

@local.definition-value

local.scope-inherits


Add an integration point:

edge_extractor: “if callee is identifier → scope-resolve → emit precise edge”

Add 5–10 golden tests:

shadowing

nested functions (Python)

JS nested blocks (let/const)

initializer self-reference (let x = x + 1)

Python class body rule (PEP 227)

9) The one sentence “what does that change?”

It changes Phase 2 from “invent a scope algorithm” to “port a known-working algorithm (tree-sitter-highlight), but adapt it for call-edge resolution and later add language-specific semantics (Python class rule, JS var/let/hoist).”

If you want, I can also write you a drop-in Python ScopeAnalyzer skeleton that mirrors the upstream algorithm (scopes/defs/refs + resolution) and is structured so you can plug it into edge_extractor.py with minimal churn.













================================================================================================================










Git commit and sprint update
·
12m 58s

Pro thinking
Synthesizing new knowledge and proposing strategy
The user wants help synthesizing knowledge, particularly regarding Perplexity and RAG, with the context involving tools like Tree-sitter, nvim-treesitter, Helix, and Zed. I need to check sources, verify differences, and offer actionable advice. I’ll work on a strategy involving QueryLoader design, directory structure, integration, and addressing tasks now.

Gathering additional details and clarifying statements
Since we can't access the user's local repo, I can still offer patches or guidelines. I'll fetch relevant documentation for tree-sitter, query syntax, and related tools. I'll also confirm the semantics of locals.scm and clarify the performance numbers Perplexity reported—likely unsubstantiated—but I won't cite those as facts. I'll suggest using their own code to verify.

Exploring tree-sitter libraries and offering guidance
I need to clarify that while semgrep uses tree-sitter for parsing, it doesn't support locals.scm. There are other libraries like "tree-sitter-stack-graphs" by GitHub/Sourcegraph. I'll search for more details about them and help guide the user with trustable info. I'll also suggest adjustments to their proposed architecture, including a consolidated plan using Perplexity+RAG|LONG-CONTEXT, while mentioning the relevant commit (90c6d38).

Browsing for tree-sitter documentation and clarifications
Exploring tree-sitter docs for query details
The search results brought up some good info, like the Syntax Highlighting doc mentioning local.reference. Now, I need more details on query syntax for predicates and directives—official docs would be ideal. I’ll explore the Syntax Highlighting doc and look for further resources on queries, predicates, and directives.

Exploring official docs and resources for queries
Clarifying architecture choices and locals.scm algorithm
The user wants to make sense of the acquired knowledge, including insights about the architecture and editor differences. I should provide a clear, decisive Phase 1 architecture, and explain how locals.scm works in the tree-sitter system. I’ll share an algorithm to map definitions, highlight references, and clarify that locals.scm focuses on highlighting, not full semantic scoping, while suggesting reuse of the concept.

Clarifying approach to scope analysis and implementation
For the scope analysis, I’ll explain that it’s lexical, doesn’t handle things like hoisting or Python class behavior, and relies on captured scopes to define boundaries. I’ll suggest implementing a ScopeAnalyzer—starting with in-file resolution and later adding cross-file support. For Zed vs nvim, I’ll explain how Zed uses tree-sitter for syntax features but likely has a custom approach for scope analysis.

Clarifying implementation phases and query details
The approach will be to break it down into phases: Phase 1 focuses on externalizing queries with QueryLoader, while Phase 2 involves locals.scm, and Phase 2b handles cross-file resolution. I'll map new knowledge to specific action items, code changes, or tests. Sample queries for Python/JavaScript should be checked against actual tree-sitter node types. I'll confirm node names in tree-sitter-python and tree-sitter-javascript by browsing online grammar documentation.

Verifying JavaScript node types and grammar
For JavaScript, key nodes include function_declaration, function_expression, arrow_function, method_definition, statement_block, class_body, variable_declarator, import_specifier, namespace_import, and catch_clause. I'll verify these by searching for tree-sitter's official Python grammar node types to cross-check the actual list.

Analyzing Tree-Sitter locals.scm and Scope Resolution
Opening raw GitHub files manually
Some GitHub pages aren't loading due to caching issues, causing errors. To get around this, I'll try accessing the raw files directly through raw.githubusercontent.com, using the ?plain=1 if needed. I'll begin with the node-types.json from tree-sitter-python and the tree-sitter-javascript locals file.

Opening GitHub raw files via URL for cache issues
Opening raw URLs with a workaround
The tool doesn't allow us to open raw URLs directly unless they're from search results. So, I'll need to search specifically for the raw GitHub URLs and then open them from there. Let's go ahead with finding the raw GitHub user content link first and opening it after.

Searching for raw GitHubusercontent URLs
Handling raw URL access and alternatives
The GitHub HTML view isn't working because of an error, and raw URLs weren't in the search results. We may need to search specifically for raw GitHub URLs. However, there are mirrored sources like docs.rs and helix runtime queries we can use. Still, we can craft our own queries if needed.

Verifying Python local query sources
We should verify the names used in the Python locals query by checking the Tree-sitter Python grammar docs. There may be a 'queries/locals.scm' file in the repo, which I can try accessing through a mirror or other sites like JSDelivr. I’ll search specifically for the raw link to ensure accuracy.

Searching for raw links to Tree-sitter locals files
Creating internal design doc for locals.scm implementation
Since the search didn’t give raw links, I’ll rely on docs and create the locals.scm setup myself. I’ll produce an action-oriented design document, covering topics like scope analysis, integration, handling cross-file checks, and notes on the tree-sitter highlight library. I’ll also include patch-level suggestions, pseudo-code, testing, and caching advice.

Clarifying issues with hardcoded queries and call edges
We need to address the "topological knot" caused by hardcoded queries. Externalizing them can help. We could propose a modular approach to analyze call edges, resolving functions to definitions and handling local variables. Ambiguities with indirect calls, especially for variables holding functions, might need special handling.

Proposing algorithm for scope and import resolution
To avoid incorrect connections to function definitions, we can propose an algorithm for effective scope analysis. First, parse the tree in each file and run queries to extract symbols, call sites, and local scopes. Then, define local references and definitions, resolving them within their scopes, and address imports for cross-file resolution.

Resolution strategy for edge extraction and function calls
When processing call expressions like foo(), I resolve references by walking up the scope chain. If it's a function def, I connect the call to it; if it's a variable, it might be dynamic or indirect, so that needs more handling. Storing metadata like scope_id or is_local will help resolve ambiguities and make the analysis easier.

Clarifying tree-sitter’s approach to "local" variables and query assertions
Tree-sitter uses the "local" property to mark local variables in the locals query, and highlights can exclude them. For analyses like Collider, this property can be ignored unless highlights are used. In queries, we can assert properties like "#is?" to filter out irrelevant nodes, and also utilize proper quantifiers like *, +, and ?.

Designing Local Scope Analysis and Integration Plan
Navigating chapters and links for query syntax exploration
Navigating to Predicates and Directives Chapter
Verifying key claims from Perplexity vs documentation
We can confirm key claims from Perplexity by cross-referencing with the official docs. For example, the locals.scm does use fixed capture names (confirmed in the Syntax Highlighting doc), and the Tree-sitter highlight system tracks scopes and definitions as expected. Also, the locals query indeed uses @ignore captures.

Verifying documentation on predicates and directory structure
I’ve confirmed that the use of predicates and directives is supported by Tree-sitter, as outlined in the relevant docs. The directory structure for queries (e.g., queries/highlights.scm) is standard, and we can also cite PEP 227 for class scope information when discussing language-specific bindings. I'll fetch it now.

Verifying claims with documentation and creating truth table
Reviewing PEP 227 for class scope details
I have access to the PEP 227 source now. I'll open the section related to "class scope" or "class definition" and use a search function to pinpoint the relevant lines. This should help me gather the necessary information effectively.

Opening PEP 227 for class scope or definition
Citing class scope in PEP 227 and considering JS scoping
The class scope details in PEP 227 (lines 71-72, 94-99) are perfect for citation. Regarding JavaScript let/const and hoisting, I should mention the scoping differences at a high level. For deeper specifics, I may consider citing MDN, but it's not necessary unless making detailed claims. I'll check JS docs for scoping.

Browsing JavaScript scoping, hoisting, and tree-sitter analysis
Reviewing sources for scoping and queries
I have MDN sources for let/TDZ and hoisting, the Helix release note for locals, and the Zed blog for queries. I’ll open the Helix release and Zed blog to extract citations. These should help ground the explanation with concrete references.

Organizing resources for MDN, Helix, and Zed
Understanding locals in Helix, nvim, Zed
Helix uses a tree-sitter-based "Tree-house" for fast lookup of definitions at parse-time, which is similar to a parent-pointer method. For nvim, it uses query matches for scopes but doesn't fully implement locals for highlighting—locals are mainly used for text objects. Zed hasn’t been analyzed, but I'll implement scope analysis for Collider myself.

Searching for tree-sitter scope analysis libraries
Correcting the Perplexity claim with stack graphs
I found a production-grade library for stack graphs, such as tree-sitter-stack-graphs on GitHub, which contradicts the claim that no such library exists. To propose a solution, we’ll suggest a locals-like resolution for their use case, but recommend stack graphs for future cross-file robustness, likely through a CLI.

Exploring GitHub stack graphs and related libraries
Proposing stack graphs and Collider integration plan
I found details on stack graphs for name resolution at scale, which could be useful as an alternative. Despite no longer being officially supported by GitHub, it's still open-source and maintained by the community. We'll suggest integrating it with Collider, proposing a phased plan: query management, in-file scope analysis, and possibly stack graphs integration. Addressing Perplexity, I’ll point out which parts are accurate and which are incorrect.

Providing guidance for agent update and query handling
They need help updating their agent using new knowledge from Perplexity. I’ll suggest a consolidated architecture: nested queries in directories (queries/<lang>/<purpose>.scm) to prevent collisions, improve scalability, and simplify adding new query types, aligned with tree-sitter and tools like nvim/helix. I'll also propose a design for QueryLoader, include a QueryBundle concept for different types (symbols, calls, locals, etc.), and suggest using LanguageRegistry for handling tree-sitter languages.

Building TreeSitterEngine methods and scope analyzer
I'll create methods for TreeSitterEngine: one to parse a file and another to run a query, returning captures as text and range objects. A few considerations for Python: accessing text needs careful slicing of source bytes using nodes’ byte positions. For ScopeAnalyzer, I’ll implement it independently of the highlight engine, building a list of Scope objects by capturing and sorting @local.scope nodes. For things like Python/JS, I’ll define a root scope based on module or program.

Handling function definitions and references in scope analysis
I need to treat function_definition as both its scope and body. Local definitions capture parameters and assignments, while references capture identifiers. However, I must make sure references don't include definitions. I'll separate captures for definitions and references, checking byte ranges to avoid duplicates. The highlight engine does exclude duplicates automatically, but I need to confirm this in Tree-sitter’s docs since it doesn’t explicitly mention exclusion in the context I expect.

Handling reference and definition captures in highlight engine
The highlight engine likely doesn't treat definition nodes as references, but queries might capture the same node multiple times. To prevent duplicates, I can avoid capturing definitions as references by excluding them using specific patterns like @local.reference with exclusions. I’ll need to implement this by gathering all definitions and ignoring them during reference scans. This will mimic the "automatic exclusion" Tree-sitter claims but isn't actually handled by the query engine itself.

For calls, I’ll convert call patterns to reference nodes using appropriate resolution.

Improving import resolution and performance aspects
For now, I’ll treat unresolved call edges to method names as symbolic. For Python attribute calls like module.func(), I can resolve cross-file imports using an ImportTable that tracks alias mappings.

To improve performance, I'll suggest caching queries per file and considering parallel processing, though I need to manage thread safety issues. Additionally, I’ll avoid memory bloat by storing only necessary info for identifiers like string, range, scope id, and def id. I'll propose a performance and testing framework as well.

Clarifying details and crafting response
I’ll clarify that the correct URL for predicates should be 3-predicates-and-directives.html, not 2-predicates.html, to fix the doc fetch.

For improving the user’s agent, I’ll suggest an updated prompt for analyze.py, focusing on using nested queries, implementing QueryLoader, and treating Python classes as special.

I’ll also provide the directory structure and pseudocode for scopes, showing the necessary components and referencing relevant sources.

Clarifying approach and finalizing response
We’ll propose using upstream locals queries from tree-sitter, though the user can access them directly. There’s a point on “RAG|LONG

Thought for 12m 57s
Done

Sources
·
191

tree-sitter.github.io
Syntax Highlighting - Tree-sitter

docs.rs
highlight.rs - source

Neovim
Treesitter - Neovim docs
Nvim looks for queries as *.scm files in a queries directory under runtimepath , where each file contains queries for a specific language and purpose, e.g., ...Read more
Python Enhancement Proposals (PEPs)
PEP 227 – Statically Nested Scopes | peps.python.org
Nov 1, 2000 — If a class definition occurs in a chain of nested scopes, the resolution process skips class definitions. This rule prevents odd interactions ...Read more

docs.rs
LOCALS_QUERY in tree_sitter_javascript - Rust
GitHub
Use locals.scm for highlighting · Issue #3098
July 1, 2022 — Jul 1, 2022 — Currently only the highlights.scm is used to determine highlighting of a file. Tree-sitter also has a highlight command and that will also use ...

tree-sitter.github.io
Syntax Highlighting
locals — Path to a local variable query. Default: queries/locals.scm . injections — Path ... ; locals.scm (method) @local.scope (do_block) @local.scope ...Read more

tree-sitter.github.io
Query — py-tree-sitter 0.25.2 documentation
The following predicates are supported by default: #eq? , #not-eq? , #any-eq? , #any-not-eq? #match? , #not-match? , #any-match? , #any-not-match? #any-of? , # ...Read more

tree-sitter.github.io
Query Syntax
Query Syntax. A query consists of one or more patterns, where each pattern is an S-expression that matches a certain set of nodes in a syntax tree.Read more

tree-sitter.github.io
py-tree-sitter 0.25.2 documentation
The Tree-sitter library is generally backwards-compatible with languages generated using older CLI versions, but is not forwards-compatible. tree_sitter.Read more

tree-sitter.github.io
Tree-sitter: Introduction
Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source file and efficiently update the ...Read more

tree-sitter.github.io
Using Parsers
Using Parsers. This guide covers the fundamental concepts of using Tree-sitter, which is applicable across all programming languages.Read more

tree-sitter.github.io
Writing the Grammar
To produce a good Tree-sitter parser, you need to create a grammar with two important properties: An intuitive structure — Tree-sitter's output is a concrete ...Read more

tree-sitter.github.io
Queries - Tree-sitter
Tree-sitter provides a simple pattern-matching language for this purpose, similar to what's used in its unit test system. This allows you to express and search ...Read more
github.com
using and suggesting standardized Tree-sitter highlights ...
Mar 17, 2025 — Zed currently uses non-standard captures in its builtin extensions/languages and themes, which has led to community language and theme extensions doing so as ...Read more
github.com
Refactor module for nvim-treesitter
Nov 28, 2025 — You can install nvim-treesitter-refactor with your favorite package manager, or using the default pack feature of Neovim!Read more
github.com
tree-sitter-javascript/queries/locals.scm at master
Search code, repositories, users, issues, pull requests... · Provide feedback · Saved searches · Sponsor tree-sitter/tree-sitter-javascript · locals.scm · locals.scm.Read more
github.com
nvim-treesitter/nvim-treesitter-textobjects
Overriding or extending textobjects. Textobjects are defined in the textobjects.scm files. You can extend or override those files by following the instructions ...Read more
github.com
Support `locals` for highlighting · Issue #81 · nvim-treesitter ...
Jun 14, 2020 — A question is how to highlight imported names. When I use the highlights of semshi, nvim-treesitter looks almost the same. It can also highlight the imported ...Read more
github.com
Would you consider upstreaming the folds.scm and indents ...
Dec 7, 2022 — Hi there I work on tree-sitter's core, as well as various language grammars, as part of my work on GitHub's Semantic Code team.
github.com
`#select-adjacent!` not respected by queries · Issue #4261
Mar 4, 2025 — Problem. The documentation describes #select-adjacent! directive as something universal, not specific to the tags library.Read more
github.com
match or eq operators in Query are not working for python ...
Jan 29, 2020 — I think you may need to upgrade the tree_sitter/core submodule to the latest version of Tree-sitter. The query syntax has changed fairly recently.Read more
github.com
Query - quantification operators within an alternation #3144
I tried adding a quantification operator to the alternation ( [(comment)+ (multiline_comment)] @comment ), but it doesn't work. Any alternative ideas on how to ...Read more
github.com
Predicates in query don't work as expected. · Issue #4075
Jan 5, 2025 — Expected to match only the second number literal, not the first, because it's not equals to "0". Tree-sitter version (tree-sitter --version).Read more
github.com
Captures dont work with +/* quantifiers. · Issue #102 · nvim- ...
Aug 21, 2021 — I have added the below query search to textobjects.scm , but nvim-treesitter query seach does not work as expected. I am facing similar issue ...Read more
github.com
Using tree-sitter queries for language indents instead of ...
Jun 4, 2021 — We already use tree-sitter queries for highlights (check runtime/queries ) locals and injections, this issue is specifically about the indents ...Read more
github.com
Utilize tags.scm queries? #39166 - zed-industries zed
So I'd like to suggest a feature -- implementing use of a tree-sitter tags.scm if available, to allow easy implementation of features like those mentioned above ...Read more
github.com
Documentation request: predicates, directives, and captures
Sep 24, 2021 — Currently, Nvim-treesitter's predicates and directives are not documented. The predicates and directives defined by Neovim itself are documented ...Read more
github.com
Zed does not use the standard capture node and ...
Mar 21, 2024 — I currently have a PR up #9654, which makes zed use the standard captures, updates the injections.scm files, and updates all tests which ...Read more
github.com
Reverse tree-sitter query precedence ordering · Issue #9436
Jan 26, 2024 — Helix will currently treat the first pattern as a higher precedence than the second, so identifiers starting with capital letters will be ...Read more
github.com
Unable to override Python `highlights.scm` using a local ...
Nov 14, 2025 — Hi Zed Team,. I am trying to override the default Python syntax highlighting by providing a custom highlights.scm file via a local user ...Read more
github.com
tree-sitter/tree-sitter-graph: Construct graphs from parsed ...
The tree-sitter-graph library defines a DSL for constructing arbitrary graph structures from source code that has been parsed using tree-sitter.Read more
github.com
Nvim Treesitter configurations and abstraction layer
The nvim-treesitter plugin provides. functions for installing, updating, and removing tree-sitter parsers;; a collection of queries for enabling tree-sitter ...Read more
github.com
Explore whether stack graphs may be useful in this tool #534
Apr 4, 2024 — The tree-sitter-graph library defines a DSL for constructing arbitrary graph structures from source code that has been parsed using tree-sitter.Read more
github.com
create syntax-highlighted code using tree-sitter
Oct 23, 2019 — A low-level API layer for node-tree-sitter to: generate HTML snippets of syntax-highlighted source code, using Atom's scope mappings format ...Read more
github.com
Find definitions/references · Issue #72 · emacs-tree-sitter ...
Nov 12, 2020 — It would be nice if emacs-tree-sitter supported finding definitions and references of the symbol at point. It won't be as accurate as what ...Read more
github.com
Can't use rust bindings · Issue #421 · tree-sitter ...
Aug 11, 2019 — So I've modified tree-sitter-python into cargo crate and it builds successfully. But when I try to use it from main create I get error. = note: ...Read more
github.com
tree-sitter highlight has does not find the language. #732
Sep 13, 2020 — I wanted to try out tree-sitter highlight but it seems like it has a near impossible time figuring out what language to use.
github.com
Add highlights.scm #23 - ikatyang/tree-sitter-markdown
Jan 24, 2021 — There are 3 officially supported queries: highlights.scm , locals.scm , injections.scm .Read more
github.com
Examples for tree sitter and tree sitter highlights #4266
Mar 5, 2025 — I'm migrating a section of code from a regex based syntax highlighter to treesitter. Expected behavior. An example that shows the ast ...Read more
github.com
tree-sitter/highlight example doesn't work · Issue #3421
Jun 17, 2024 — Problem I was hoping to learn how to use tree sitter to get syntax highlighting but the example doesn't work.
github.com
tree-sitter-cpp/queries/highlights.scm at master
C++ grammar for tree-sitter. Contribute to tree-sitter/tree-sitter-cpp development by creating an account on GitHub.
github.com
python/locals.scm: class attribute captured as `@definition. ...
Nov 23, 2020 — Describe the bug. In queries/python/locals.scm , @definition.associated is the incorrect capture to use for class attributes/fields.Read more
github.com
CONTRIBUTING.md - atusy/kakehashi
4 days ago — Tree-sitter queries power the language features. Place them in: <searchPath>/queries/<language>/highlights.scm - Syntax highlighting; < ...Read more
github.com
Highlighting of python identifiers is erratic · Issue #871
Jan 24, 2021 — scm found. WARNING: No locals.scm query found for ocamllex. ADVICE: Open an issue at https://github.com/nvim-treesitter/nvim-treesitter.Read more
github.com
tree-sitter-langs/queries/python/highlights.scm at master
Language bundle for Emacs's tree-sitter package. Contribute to emacs-tree-sitter/tree-sitter-langs development by creating an account on GitHub ... scm. Copy path.
github.com
tree-sitter.json
... queries-src/highlights.scm", "injections": "queries-src/injections.scm", "locals": "queries-src/locals.scm", "injection-regex": "^(?i)just(file)?$", "first ...Read more
github.com
tree-sitter-javascript/queries/highlights.scm at master
Javascript grammar for tree-sitter. Contribute to tree-sitter/tree-sitter-javascript development by creating an account on GitHub.
github.com
Loading of query files much slower with 0.19.2 · Issue #973
Mar 7, 2021 — ... raw.githubusercontent.com/nvim-treesitter/nvim-treesitter/master/queries/kotlin/highlights.scm. ❯ tree-sitter --version tree-sitter 0.19.4 ...Read more
github.com
tree-sitter-tsx/package.json at master
Blame. 95 lines (95 loc) · 3.04 KB. Raw. Copy raw file. Download raw file ... "locals": "node_modules/tree-sitter-javascript/queries/locals.scm",. "tags ...Read more
github.com
Python grammar for tree-sitter
Python grammar for tree-sitter. Contribute to tree-sitter/tree-sitter-python development by creating an account on GitHub.
github.com
Type variables bound by a generic class make no sense in ...
Apr 13, 2017 — I think it'd be cleanest to forbid, and let people define instance variables using generics when they're actually using PEP526 syntax instead of faking it.Read more
github.com
peps/peps/pep-3104.rst at main · python/peps
Nov 1, 2006 — A proposal for scoping syntax appeared on Python-Dev as far back as 1994 [1]_, long before :pep:`227`'s support for nested scopes was adopted.Read more

docs.rs
Query in tree_sitter - Rust
Get the other user-defined predicates associated with the given index. This includes predicate with operators other than: match? eq? and not-eq? is ...Read more

docs.rs
tree_sitter_graph::reference - Rust
A graph DSL file consists of one or more stanzas. Each stanza starts with a tree-sitter query pattern, which identifies a portion of the concrete syntax tree.Read more

docs.rs
tree_sitter_scala - Rust
This crate provides Scala language support for the tree-sitter parsing library. Typically, you will use the LANGUAGE constant to add this language to a tree- ...Read more

docs.rs
tree_sitter_highlight - Rust
The last parameter to highlight is a language injection callback. This allows other languages to be retrieved when Tree-sitter detects an embedded document (for ...Read more

docs.rs
highlight.rs - source
Docs.rs. tree-sitter-highlight-0.26.3. tree-sitter-highlight 0.26.3; Permalink ... locals_query` - A string containing tree patterns for tracking local ...Read more

docs.rs
LOCALS_QUERY in tree_sitter_r - Rust
pub const LOCALS_QUERY: &str = "; locals.scm\n\n(function_definition) @local.scope\n\n(argument name: (identifier) @local.definition)\n(parameter name: ...Read more

docs.rs
lib.rs - source
1//! This crate provides JavaScript language support for the [tree-sitter] parsing library. 2//! 3//! Typically, you will use the [`LANGUAGE`] constant to ...

docs.rs
tree_sitter_javascript - Rust
This crate provides JavaScript language support for the tree-sitter parsing library. Typically, you will use the LANGUAGE constant to add this language to a ...Read more

docs.rs
LOCALS_QUERY in tree_sitter_kconfig - Rust
The local-variable syntax highlighting query for this language.

docs.rs
tree_sitter_foam - Rust
The source of the JavaScript tree-sitter grammar description. HIGHLIGHTS_QUERY · INJECTIONS_QUERY · LOCALS_QUERY · NODE_TYPES: The content of the node-types.Read more

docs.rs
tree_sitter_tags - Rust
Create a tag context. You need one of these for each thread that you're using for tag computation: use tree_sitter_tags::TagsContext; let context = TagsContext ...Read more

docs.rs
tree_sitter_go - Rust
This crate provides Go language support for the tree-sitter parsing library. Typically, you will use the LANGUAGE constant to add this language to a tree- ...Read more

docs.rs
tree_sitter_python - Rust
This crate provides Python language support for the tree-sitter parsing library. Typically, you will use the LANGUAGE constant to add this language to a tree- ...Read more

docs.rs
arborium_go - Rust
The locals query for go (empty - no locals available). Functions§. language: Returns the go tree-sitter language.Read more

docs.rs
LOCALS_QUERY in tree_sitter_objc - Rust
tree_sitter_objc3.0.2. Constants · FOLDS_QUERY · HIGHLIGHTS_QUERY · INDENTS_QUERY · INJECTIONS_QUERY · LANGUAGE · LOCALS_QUERY · NODE_TYPES.Read more

docs.rs
tree_sitter_vue/ lib.rs
This crate provides YOUR_LANGUAGE_NAME language support for the [tree-sitter][] parsing library. 2//! 3//! Typically, you will use the [language][language func ...Read more

docs.rs
tree_sitter - Rust
An opaque object that defines how to parse a particular language. The code for each Language is generated by the Tree-sitter CLI. LanguageMetadata: The metadata ...Read more

docs.rs
tree_sitter_rslox - Rust
This crate provides rslox language support for the tree-sitter parsing library. Typically, you will use the language function to add this language to a ...Read more

docs.rs
LANGUAGE in tree_sitter_javascript - Rust
tree_sitter_javascript0.25.0. Constants · HIGHLIGHT_QUERY · INJECTIONS_QUERY · JSX_HIGHLIGHT_QUERY · LANGUAGE · LOCALS_QUERY · NODE_TYPES · TAGS_QUERY.Read more

docs.rs
LOCALS_QUERY in tree_sitter_foam - Rust
API documentation for the Rust `LOCALS_QUERY` constant in crate `tree_sitter_foam`.

docs.rs
arborium_jinja2 - Rust
This crate packages a parser.c file generated by the tree-sitter CLI. It exports a language() function returning the tree-sitter Language for jinja2.Read more

docs.rs
tree_sitter_query - Rust
This crate provides query language support for the tree-sitter parsing library. Typically, you will use the language function to add this language to a tree- ...Read more

docs.rs
arborium_javascript - Rust
This crate packages a parser.c file generated by the tree-sitter CLI. It exports a language() function returning the tree-sitter Language for javascript.Read more

docs.rs
arborium_julia - Rust
This crate packages a parser.c file generated by the tree-sitter CLI. It exports a language() function returning the tree-sitter Language for julia.Read more

docs.rs
tree-sitter-python 0.25.0
Docs.rs · tree-sitter-python-0.25.0; Platform. i686-unknown-linux-gnu · x86_64 ... tree-sitter-python 0.25.0. Python grammar for tree-sitter. Crate · Source ...Read more

stackoverflow.com
How to create a new capture group with treesitter ...
I'm trying to update the priority defined by treesitter for the @lsp.typemod.variable.declaration.typescriptreact highlight group.Read more

stackoverflow.com
How to solve treesitter/highlighter: Error executing lua ...
I just solved it using :TSInstall vim. Actually, run :checkhealth and the error in there would help in figuring out what is missing.Read more

stackoverflow.com
How to use `or` logic in tree-sitter query syntax?
How to use or logic in tree-sitter query? I want to query out a class's properties and methods: I tried to use | : (class_declaration name: ( ...Read more

stackoverflow.com
Treesitter - Failed to load 'lua' parser
... Local\nvim-data\site\pack\packer\start\nvim-treesitter\queries\c\locals.scm", failed to load: ...eovim\share\nvim\runtime/lua/vim/treesitter ...Read more

stackoverflow.com
NeoVim Highlight .ts template as HTML / JSX
The typescript/injections.scm file tells Tree-sitter to inject HTML highlighting into template strings that are immediately preceded by a /*html ...Read more

stackoverflow.com
python - How to access class-scope variables without self?
Python doesn't let class variables fall into scope this way, there are two ways to do this, the first is to use a class method.Read more

stackoverflow.com
Python class scoping rules
TL;DR: This behaviour has existed since Python 2.1 PEP 227: Nested Scopes, and was known back then. If a name is assigned to within a class body ...Read more

helix-editor.com
Adding textobject queries
These textobjects require an accompanying tree-sitter grammar and a textobjects.scm query file to work properly. Tree-sitter allows us to query the source code ...Read more

helix-editor.com
Release 25.07 Highlights
Jul 15, 2025 — Locals. Another useful concept from tree-sitter-highlight is locals. locals.scm is a query used to tag nodes which should have their ...Read more

helix-editor.com
[editor.gutters.line-numbers] Section
How the indentation for a newly inserted line is computed: simple just copies the indentation level from the previous line, tree-sitter computes the indentation ...Read more

medium.com
Tree-sitter Syntax Highlighting
Tree-sitter tracks local definitions and references using fixed capture names: @local.scope : Marks a new scope; @local.definition : Marks ...Read more

medium.com
Neovim 101 —Tree-sitter Usage - alpha2phi - Medium
In this article, let's go through Tree-sitter usage to help us in coding. This article is part of the Neovim 101 series.Read more

medium.com
Understanding Tree-sitter Predicates and Directives
Tree-sitter's query syntax provides powerful tools to fine-tune pattern matching: #eq? , #match? , #any-of? , and #is? refine the match logic.Read more

medium.com
Tree-sitter Queries: Operators That Unlock Precision
This is a solid intro to Tree-sitter queries and their operators. It covers the essentials like captures and quantifiers clearly, which is great ...Read more

medium.com
5 Powerful Ways to Use Tree-sitter in Your Next Project
Tree-sitter is a parsing library that builds a structured tree of source code. This means we can easily inspect code structure without using ...Read more

reddit.com
Nvim-treesitter, highlighting issue variables in same scope
I'm facing an issue with highlighting same variable names in the same scope. I'm using nvchad 2.0 with nvim-treesitter built-in.Read more

reddit.com
Need help with scope textobject : r/neovim
If you use local captures, you'll be using these ones https://github.com/nvim-treesitter/nvim-treesitter/blob/master/queries/rust/locals.scm .Read more

reddit.com
nvim-treesitter - how to highlight imports/modules text
I want to get my imports to look like something similar to how VSCode has them - notice the green highlighted text ("math" and "random") after import in VSCode ...Read more

reddit.com
Looking for Tree-sitter query documentations and guides
I'm having a really hard time getting into tree-sitter's query API. I have read the official documentation numerous time but man ! The entry step feels huge !Read more

reddit.com
[Language Extension] Syntax Highlighting Trouble
I've gone so far as to try to define a simple highlights.scm with just one catch-all rule to color **everything**, but it has no effect.Read more

reddit.com
C++, member highlighting failed : r/HelixEditor
If you would like to change the color of particular element, please use the :tree-sitter-scopes command to diagnose what to change, and then ...Read more

reddit.com
TreeSitter: Example for add_directive() : r/neovim
Treesitter directives store metadata for a node or match and perform side effects. All of the buil-in treesiter directives set some value in the ...Read more

reddit.com
[AMA] Tree-sitter integration in neovim
Treesitter and lsp's are two, tools to analyse source code, so you can use them both to highlight a given file, they are just two "sources ...Read more

reddit.com
Configure Language Specific Highlighting with tree-sitter
My syntax highlighting highlights the `int64` cast as a function call (above). I'd like `int64` to be highlighted as a type (below).Read more

reddit.com
Help writing a custom treesitter query to highlight golang ...
Feels to me that the most robust way would be to write another TS parser for struct tags then make an injection. There are workarounds though.Read more

reddit.com
I don't get why treesitter is a big deal, and at this point I'm ...
I see so much hype for treesitter, but I've never had any issues with regular syntax highlighting in any languages or file formats.Read more

reddit.com
Treesitter and language highlighting : r/neovim
Your first step is to identify which semantic parts you want to change the highlights of. Next, locate the file ~/.local/share/nvim/plugged/nvim ...Read more

reddit.com
Treesitter Error: attempt to index local 'query' (a nil value)
Would make sure nvim-treesitter updated along with updating your tree-sitter parsers. Then check if you have any related query files for that ...Read more

reddit.com
Is it just me or is Treesitter actually pretty mid by default? ( ...
scm queries were in the first place (e.g., nvim-treesitter is still what decides that Ruby's self should be captured as a @variable.builtin ...Read more

reddit.com
Syntax highlighting for custom tree-sitter parser not working
I have a highlights.scm file and tried to load it but had no effects. Anyways, shouldn't some default syntax highlighting be visible without ...Read more

reddit.com
Help to build a treesitter query for "quotations" : r/neovim
I'm currently trying out building custom text objects with treesitter. First thing I'm aiming at - a text object mapped to iq/aq that lets me select anything ...Read more

reddit.com
What is the use of variables without self inside classes and ...
Without 'self', that attribute is limited to the scope of the function, in this case the 'innit' or initializer of the object. It doesn't make ...Read more

reddit.com
Why does python lack nested scopes? (a la blocks in C, or ...
In python, there is no non-ugly way to create a nested scope inside a function other than defining another function and then calling it.Read more

zed.dev
Syntax-Aware Task Spawning With Tree-Sitter — Zed's Blog
May 21, 2024 — Have you ever wanted to execute code from inside Zed? Run tests, or a linter, or the compiler, or maybe a script, or a shell one-liner?Read more

zed.dev
Enabling low-latency, syntax-aware editing using Tree-sitter
Mar 27, 2023 — In this post, I'll explain how Zed approaches syntax-aware editing, and show how some of Zed's syntax-related features are implemented.Read more

zed.dev
Language Extensions | Zed Code Editor Documentation
In Tree-sitter, the highlights.scm file defines syntax highlighting rules for a particular syntax. Here's an example from a highlights.scm for JSON:.Read more

zed.dev
Tree Sitter query — Zed Extension
An extension in Zed is a way to extend the editor's functionality with things such as language support, themes, MCP servers, debugger protocols, and others. How ...Read more

lobste.rs
syntax highlighting with tree-sitter | Lobsters
Mar 30, 2025 — A highlights.scm file is coupled to a specific tree-sitter grammar, and defines highlight names for specific nodes in the syntax tree. The "list ...Read more

lobste.rs
Tools built on tree-sitter's concrete syntax trees | Lobsters
May 31, 2025 — the TSG DSL is simply used to annotate the tree-sitter nodes with certain features: definition , reference and scope . so a file like so: // foo ...Read more

crates.io
tree-sitter-stack-graphs-python
Dec 13, 2024 — The command-line program for tree-sitter-stack-graphs-python lets you do stack graph based analysis and lookup from the command line. The ...Read more

crates.io
tree-sitter-highlight - crates.io: Rust Package Registry
Dec 13, 2025 — This allows other languages to be retrieved when Tree-sitter detects an embedded document (for example, a piece of JavaScript code inside a ...Read more

crates.io
tree-sitter-highlight - crates.io: Rust Package Registry
Oct 1, 2024 — tree-sitter-highlight v0.23.2. Library for performing syntax highlighting with Tree-sitter. #highlighting · #incremental · #parsing · #syntax.Read more

crates.io
syntastica-query-preprocessor
Jun 19, 2025 — The crate can be used to use queries designed for Neovim with the official tree-sitter rust bindings with minimal manual changes. ... scm (where ...Read more

crates.io
tree-sitter-pact - crates.io: Rust Package Registry
Jun 8, 2025 — ... queries/highlights.scm ~/.config/nvim/after/queries/pact/highlights.scm ln ./queries/locals.scm ~/.config/nvim/after/queries/pact/locals.scm ...Read more

go.dev
tree_sitter package - github.com/tree-sitter ...
Feb 2, 2025 — This repository contains Go bindings for the Tree-sitter parsing library. To use this in your Go project, run: go get github.com/tree-sitter/go-tree-sitter@ ...Read more

go.dev
highlight package - go.gopad.dev/go-tree-sitter-highlight
Dec 3, 2024 — Package highlight provides a simple way to highlight text via [tree-sitter](https://github.com/tree-sitter/tree-sitter).
lbl.gov
8 PEP 227: Nested Scopes
In 2.2 nested scopes no longer need to be specially enabled, and are now always present. The rest of this section is a copy of the description of nested scopes ...Read more

python.org
PEP 558: Defined semantics for locals() - Python Discussions
Dec 31, 2019 — place since PEP 227 introduced nested scopes in Python 2.1, the other benefit of restricting the write-through proxy support to theRead more

python.org
Initializing one static data member from another - Python Help
Nov 2, 2021 — If a class definition occurs in a chain of nested scopes, the resolution process skips class definitions. Even though the behavior is still ...Read more

python.org
Painful details of variable scope mixed with classes
Jul 29, 2022 — Next we can look at nested classes. When a class is nested inside another class, the surrounding class is not part of the variable search path.Read more

shadaj.me
Introducing Rust Sitter
Aug 11, 2022 — The first step in the Rust Sitter pipeline is to generate Tree Sitter grammar definitions based on the annotated Rust modules. Since the tool ...Read more

thecodingforums.com
Why no lexical scoping for a method within a class? | Python
Dec 17, 2008 — Because what you do is to create instance variables. Why do you expect them not working if you explicitly access them? The real analog of ...Read more
davisvaughan.github.io
Query matches and captures
String double quotes​​ The underlying tree-sitter predicate parser requires that strings supplied in a query must use double quotes, i.e. "string" not 'string' . ...Read more
davisvaughan.github.io
Queries — query • treesitter
query() lets you specify a query source string for use with query_captures() and query_matches(). The source string is written in a way that is somewhat ...

tomassetti.me
Incremental Parsing Using Tree-sitter - Strumenta
Tree-sitter comes with support for syntax highlighting and tagging elements. Both of these rely on defining rules inside specific files using query patterns.

ayats.org
The tree-sitter packaging mess
Aug 25, 2024 — We have 3 types of queries: highlights.scm , used for syntax highlights, injections.scm used for injecting one language into another, and locals ...Read more
jonashietala.se
Let's create a Tree-sitter grammar
Mar 19, 2024 — A Tree-sitter parser is actually a C program. The grammar we've seen has been described in JavaScript, but it's only used as a description to ...Read more

nova.app
Tree-sitter
The Tree-sitter library is used to create parsers which can provide rich syntax trees for languages both simple and complex.Read more

launchschool.com
Classes and Objects
Object scope refers to the methods and instance variables an object can access. This is akin to discussing global and local scope instead of identifier scope.Read more

rdrr.io
Query matches and captures in treesitter
Query matches and captures. Description. These two functions execute a query on a given node , and return the captures of the query for further use.Read more

lib.rs
tree-sitter-d2
We found out that Helix is using tree-sitter v0.22.x which makes it incompatible with this grammar, as it was built using tree-sitter v0.25.x . If ...Read more

lib.rs
tree-sitter-highlight-wasm
Dec 1, 2025 — Tree-sitter Highlight. crates.io badge. [!IMPORTANT] This crate is a fork of tree-sitter-highlight-wasm that works in a WebAssembly context.Read more

dev.to
Unraveling Tree-Sitter Queries: Your Guide to Code ...
May 8, 2025 — Queries can use predicates to add conditions to matches. For example, you might want to find function declarations with a specific name.Read more

dev.to
Digging Deeper into Code with Tree-Sitter: How to Query ...
May 13, 2025 — In this post, we'll go one step further and see how Tree-sitter can be used to make queries on your source text to understand and analyze various parts of the ...Read more

dev.to
Custom Parser Highlighting Not Working in nvim-treesitter? ...
Sep 19, 2025 — To make Neovim aware of this new after directory, you need to load the tree-sitter-unreal-cpp repository as a standalone plugin in lazy.nvim .Read more

dev.to
A Beginner's Guide to Tree-sitter
Apr 6, 2024 — Tree-sitter generates parsers based on a language and provides insights about the code as seen by the engine.Read more
andrewtbiehl.com
Syntax highlight your Jekyll site with Tree-sitter!
Sep 7, 2022 — A TextMate scope is a string that Tree-sitter uses to uniquely identify languages. For example, the scope string for Python is 'source.python', ...

documentation.help
4. Execution model - Python 3.6.1 Documentation
Mar 21, 2017 — The scope of names defined in a class block is limited to the class block; it does not extend to the code blocks of methods – this includes ...Read more

neovimcraft.com
nvim-treesitter-textobjects
Sep 20, 2020 — -- Below example nvim-treesitter's `locals.scm` and `folds.scm`. They also provide highlights.scm and indent.scm. ["]s"] = { query = "@local.Read more

youtube.com
Zed Decoded: Syntax-Aware Task Spawning With Tree-Sitter
This is the fourth video in our Zed Decoded series, in which we take a close look at how Zed works and how it's built. This is the companion ...

youtube.com
Neovim - Treesitter Syntax Highlighting
In this video we're going to be talking about tree sitter for neovim so you can head over to the neovim from scratch repository.

youtube.com
How to Use Tree Sitter Queries in Python
In this Python Tutorial I show you in detail how to use Tree Sitter to parse source code. I explain how to use Tree Sitter Queries to ...

dropstone.io
AST Parsing at Scale: Tree-sitter Across 40 Languages
Nov 20, 2025 — Our AST engine builds a Scope Graph alongside the syntax tree. Every identifier is linked to its definition site, and every definition knows all ...Read more

datadoghq.com
Static Code Analysis Custom Rule Guide
The Tree Sitter Query. A query contains one or more patterns, where each pattern is an expression that declares the shape of the nodes it matches. The query ...Read more
ser1.net
Adding a Tree-Sitter to Helix
Jan 12, 2023 — This is a walk- through of adding someone else's tree-sitter to Helix. Tree-sitters are a wonderful development in the editor space.Read more

nvkarta.com
Python Notes for Professionals
Mar 14, 2024 — You can download and install either version of Python here. See Python 3 vs. Python 2 for a comparison between.Read more

cursorless.org
Tree sitter query (SCM)
Tree sitter query (SCM). Below are visualizations of all our scope tests for this language. These were created primarily for testing purposes rather than as ...Read more

cursorless.org
Tree-sitter query syntax
We use the tree-sitter query language to define our parse tree patterns. In addition to the official tree-sitter query documentation, we support a couple of
jeffkreeftmeijer.com
Highlighting source code with tree-sitter
After installing tree-sitter, highlighting a Ruby file fails because there are no language grammars installed.

graph-sitter.com
Graph-sitter
Graph-sitter is a python library for manipulating codebases. It provides a scriptable interface to a powerful, multi-lingual language server built on top of ...Read more

nclab.com
Introduction to Python Programming
Jul 21, 2018 — We will show you how to work with text strings, variables, tuples, lists, dictionaries, functions, loops, conditions, files, exceptions, ...Read more

cycode.com
Tips for using tree sitter queries
Apr 6, 2022 — Tree sitter is a parser generator tool and an incremental parsing library. It enables you to generate concrete syntax tree from any language it supports.Read more
slackware.nl
tree-sitter-javascript
Package name: tree-sitter-javascript ; Package version: 0.25.0 ; Package arch: x86_64 ; Package build: 1cf.

realpython.com
nested scope | Python Glossary
In Python, a nested scope refers to the ability of an inner function to access variables from its containing or enclosing function.Read more

tessl.io
Pattern Matching and Queries
Pattern Matching and Queries. Tree-sitter's query system enables powerful pattern matching against syntax trees using a specialized query language.Read more
dbp.io
Python: The Full Monty - Daniel Patterson
by JG Politz · 2013 · Cited by 89 — We have now covered Python classes' scope seman- tics: function bodies do not close over the class body's scope, class bodies create their own local scope, ...Read...
josean.com
A Powerful Way To Make Editing Code In Neovim Even ...
Oct 4, 2023 — Treesitter is an experimental feature of Neovim that, through the help of language parsers, constructs a syntax tree for the files you work with.Read more

jhcha.app
The power of tree-sitter - Joohoon Cha
Nov 11, 2022 — Tree-sitter(or treesitter) is a parser generator tool and an incremental parsing library. It is important to note that it supports incremental parsing.Read more

pypi.org
tree-sitter-d2
... --grammar build; Add your queries to ~/.config/helix/runtime/queries/d2. ~/.config/helix/runtime/queries/d2 ├── highlights.scm ├── injections.scm └── locals.scm.Read more

slar.se
Syntax highlight anything with Tree-sitter
In this article, we explored the basics of Tree-sitter and how to apply it to provide syntax highlighting for a simple markup language. The full source code for ...Read more

sudomsg.com
https://git.sudomsg.com/mirror/nvim-treesitter/pla...
Each of these `scheme` files contains a *tree-sitter query* for a given purpose. ... scm`: used to define text objects. - `folds.scm`: used to define folds. For ...Read more

stackexchange.com
How to use tree-sitter parser for syntax highlighting?
Nov 27, 2023 — I'm trying to setup Emacs for editing Roc (https://www.roc-lang.org/) source code. I have an LSP server for Roc and tree-sitter parser for Roc ...Read more

tweag.io
Tree-sitter and its queries
From the Tree-sitter documentation: Tree-sitter is a parser generator tool and an incremental parsing library. It can build a concrete syntax tree for a source ...Read more
ycombinator.com
Take a look at Fossil too: https://www.fossil-scm.org/ It's the ...
Take a look at Fossil too: https://www.fossil-scm.org/. It's the distributed version control (and more) used by SQLite. Most people have no idea about how ...Read more
ycombinator.com
Tree-sitter: an incremental parsing system for programming ...
Feb 22, 2021 — Tree Sitter is amazing. The parsing is fast enough to run on every keystroke. The parse tree is extremely concise and readable.Read more
ycombinator.com
Stack Graphs
Dec 9, 2021 — We're porting them over to the open-source graph DSL (tree-sitter/tree-sitter-graph), and we'll add them to the tree-sitter-python repo as part of that effort.Read more
debian.org
lib.rs « src « highlight - tree-sitter
/// * `locals_query` - A string containing tree patterns for tracking local variable /// definitions and references. This can be empty if local variable ...Read more
debian.org
lib.rs « src « highlight - tree-sitter
/// * `locals_query` - A string containing tree patterns for tracking local variable /// definitions and references. This can be empty if local variable ...Read more
jntille.com
Tree-sitter: a parser generator and library for development tools
Every token class is mapped to a scope, which is referenced by themes to provide colors and styles for syntax highlighting. Purely relying on lexical pattern ...Read more

thevaluable.dev
Neovim and Tree-sitter: An Overview with Examples
Apr 30, 2023 — Tree-sitter is a library able to create a parse tree from some source code. Neovim can use it to implement different functionalities, like syntax highlighting ...Read more
indoorvivants.com
Smithy in Neovim: parsing, syntax highlighting, LSP
May 12, 2022 — A tooling package to transform Smithy service definitions into high performance HTTP server/client definition, backed by Cats Effect, Jsoniter, and Http4s.Read more

neovim.discourse.group
query that matches nodes in embedded language (Vue)
Oct 2, 2023 — ... treesitter/blob/master/queries/vue/injections.scm ; <script lang="ts ... Treesitter/highlighter error while parsing Python and Java (Markdown ...Read more
project-sora.github.io
Language | Sora Editor
Nov 12, 2025 — First, TsLanguageSpec should be created with tree-sitter language instance and scm source texts. You may also need to add a custom ...Read more

arxiv.org
Stack graphs: Name resolution at scale
by DA Creager · 2022 · Cited by 6 — The tree-sitter [1] and tree-sitter-graph. [14] libraries, the stack graph algorithms [4], and our initial language-specific stack graph.Read more

mzte.de
nvim-treesitter/queries/c/locals.scm at master - MZTE git
No results found. nvim-treesitter/queries/c/locals.scm. Pham Huy Hoang ... scope. Reference in a new issue View git blame Copy permalink. Powered by ...Read more

volito.digital
Using The Tree-Sitter Library In Python To Build A Custom ...
Feb 9, 2025 — Tree-sitter is a powerful incremental parsing library used to analyze and manipulate source code. It is widely employed in text editors ...Read more

archlinux.org
tree-sitter-javascript 0.25.0-1 File List
usr/share/tree-sitter/queries/javascript/injections.scm; usr/share/tree-sitter/queries/javascript/locals.scm; usr/share/tree-sitter/queries/javascript/tags.scm.

dzone.com
Building Call Graphs for Code Exploration Using Tree-Sitter
Jan 24, 2025 — This tutorial will guide you through setting up a tree-sitter parsing library in Python and using its different API for parsing the code for various use cases.Read more

r-project.org
Help for package treesitter
Jan 13, 2026 — The underlying tree-sitter predicate parser requires that strings supplied in a query must use double quotes, i.e. "string" not 'string' .Read more
eed3si9n.com
fast Scala 3 parsing with tree-sitter
Dec 20, 2022 — To get started, install the Tree-sitter command line tool called tree-sitter , which interprets your grammar.js to generate a parser code in C.Read more

researchgate.net
Blockchain-Enabled Supply Chain Management: A Review ...
May 4, 2025 — aiming to design resilient and trustworthy supply chain management (SCM) systems. Keywords: blockchain; supply chain management; security; ...Read more

pulsar-edit.dev
Modern Tree-sitter, part 3: syntax highlighting via queries
Oct 12, 2023 — If we can test for it in JavaScript, it can be used as a predicate in Tree-sitter queries. We call these custom predicates scope tests, and we' ...Read more

oulu.fi
An agile supply chain for a project-oriented steel ... - OuluREPO
Aug 18, 2006 — 3.1.1 SCM as a management concept. Many definitions of Supply Chain Management (SCM) have been presented (e.g