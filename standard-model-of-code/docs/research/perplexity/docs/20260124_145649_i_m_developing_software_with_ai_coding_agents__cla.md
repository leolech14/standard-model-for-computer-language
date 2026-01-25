# Research: I'm developing software with AI coding agents (Claude, Copilot, Cursor, etc.) and facing a specific ...

> **Date:** 2026-01-24 14:56:49
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:2748c0fcec2b81c5ad4aa382f737b974fdd8f84b017b3429d8dd213851708bef`
> **Raw JSON:** `raw/20260124_145649_i_m_developing_software_with_ai_coding_agents__cla.json`

---

## Query

I'm developing software with AI coding agents (Claude, Copilot, Cursor, etc.) and facing a specific problem: multiple AI sessions make changes without committing, leading to 300+ uncommitted files that neither I nor the AI agents fully understand.

What are modern solutions for this problem? I'm looking for:

1. Git workflows or tools designed for AI-assisted development (auto-commit strategies, semantic commits)
2. Open-source tools that track AI agent changes and auto-checkpoint
3. Development environment configurations that enforce commit discipline
4. Any emerging best practices for human-AI pair programming hygiene
5. Tools that can retroactively analyze uncommitted changes and suggest logical commit groupings

I want practical solutions - could be git hooks, CLI tools, IDE plugins, workflow patterns, or configuration approaches. Preferably open-source or built into existing tools.

---

## Response

# Comprehensive Guide to Managing Uncommitted Changes in AI-Assisted Development Workflows

The emergence of AI coding assistants has fundamentally transformed how developers approach software engineering, yet it has simultaneously introduced a critical organizational challenge that mirrors the problem of context management at scale. When multiple AI sessions execute code modifications without enforcing a structured commit discipline, projects can accumulate hundreds of uncommitted changes that neither developers nor the AI agents themselves fully understand, creating a state of entropy that undermines the fundamental purpose of version control. This comprehensive research report examines modern solutions, emerging best practices, and practical implementations for maintaining commit hygiene in AI-assisted development workflows, drawing from cutting-edge tools, frameworks, and methodologies that are reshaping how teams collaborate with autonomous coding agents.

## AI-Integrated Version Control Systems as the Foundation

The most elegant solutions to the uncommitted changes problem originate from development platforms that have fundamentally reconceived version control to accommodate AI-assisted workflows rather than forcing AI agents into traditional Git paradigms designed exclusively for human developers. GitButler represents a paradigm shift in this regard, introducing what the platform calls **virtual branches**—a concept that dissolves the boundary between the workspace and version control by making every Git operation a first-class citizen within the development interface[1]. Rather than treating AI code generation as something that happens outside the development process, GitButler has integrated agent experiences directly into the workspace, creating automatic AI sessions per branch with automatic commits that include context-driven commit messages[1].

The architectural elegance of this approach lies in its recognition that the problem isn't really about Git itself, but rather about organizational structure. When an AI agent operates in isolation without clear boundaries, its changes accumulate in an undifferentiated workspace. GitButler solves this by ensuring that each AI session runs inside a branch, where changes are tracked, committed, and visible just like human-written code[1]. This transforms code generation from an external process into a parallel development activity that shares the same organizational principles as human contributions. The platform manages context automatically, tracks file modifications, generates commit messages through analysis of the actual changes, and maintains context for subsequent AI interactions[1].

GitHub has similarly advanced its approach through the Copilot coding agent, which now operates within an enterprise-ready framework that leverages GitHub's native control layer[25]. The agent starts work when developers assign a GitHub issue to Copilot or request it to begin working through chat in VS Code, and crucially, it pushes commits to a **draft pull request** rather than directly to the main branch[25]. This architecture provides visibility into agent work through session logs, allows developers to give feedback through pull request reviews, and maintains branch protections as a safety mechanism[25]. The agent's pull requests require human approval before CI/CD workflows execute, creating an explicit checkpoint that prevents uncommitted or poorly organized changes from propagating downstream[25].

Cursor, another leading AI code editor, has implemented agent functionality that produces code changes directly editable in the IDE, with a CLI option that allows running the agent entirely from the terminal for integration into CI pipelines[42]. The platform emphasizes developer control through the ability to approve or undo changes stepwise, while providing rules files that steer the AI's coding style and conventions[42]. This combination of immediate feedback (line-by-line approval in the IDE) with structural guidance (coding rules) creates a workflow where developers maintain continuous visibility and control over agent-generated code.

## Conventional Commits and Semantic Versioning for Automated Organization

While AI-integrated platforms handle the structural problems of code organization, the semantic problem of explaining **what** each commit accomplishes remains critical. The Conventional Commits specification has emerged as the de facto standard for structuring commit messages in a way that machines can parse and humans can understand[2][5]. This is particularly important for AI-assisted workflows because conventional commits enable downstream automation—the same message that explains the change to a human reviewer can trigger semantic version bumping, changelog generation, and release coordination.

OpenCommit, an open-source tool that generates commit messages using OpenAI's APIs, demonstrates how AI can be directed to follow conventional commit conventions[20]. The tool operates by staging files, scanning the diff, and sending the complete diff to a language model with instructions to generate a detailed but brief overview of the changes[34]. Critically, the tool supports multiple prompt modules—developers can configure it to use either the default conventional-commit format or switch to @commitlint, which respects local configuration rules[20]. This allows teams to enforce their own commit message standards while gaining the productivity benefits of automatic generation.

The git-autocommit-hook tool takes a different architectural approach, using Mistral's API with Retrieval-Augmented Generation (RAG) to provide context to the language model[7]. By maintaining a vector database of the codebase and optionally using function-calling APIs to access other files, this approach can generate more contextually aware commit messages while respecting team conventions[7]. The tool operates as a git hook, automatically pre-filling commit messages without requiring developers to change their workflow substantially.

Tools like semantic-release automate the entire downstream chain: analyzing commits according to conventional commit rules, determining the next semantic version, generating release notes, and publishing packages—all triggered by commit history[5]. This creates a powerful flywheel where human developers (or AI agents) writing properly formatted commits automatically produce versioned releases with changelogs, eliminating manual release management and ensuring consistency[5].

## Git Hooks as Enforcement Mechanisms for Commit Discipline

Pre-commit hooks represent a critical layer of automation that can enforce commit standards before changes enter version control, preventing malformed or uncommitted code from accumulating in the first place. The pre-commit framework provides a declarative configuration system where teams can specify which checks to run, in what order, and against which file patterns[10]. Unlike ad-hoc shell scripts, pre-commit automatically manages dependencies, handles language-specific tools, and provides clear output when checks fail, giving developers immediate feedback about what needs to be fixed.

Husky, paired with lint-staged, creates a particularly elegant workflow for Node.js projects[8][11]. Husky manages git hooks by creating shell scripts that run automatically at git lifecycle events like pre-commit, pre-push, and prepare-commit-msg[8]. Lint-staged takes the list of staged files and runs configured tools only on those files, rather than the entire codebase, which dramatically accelerates feedback loops[11]. A developer can configure eslint, prettier, and unit tests to run automatically against only the files they're committing, receiving feedback in seconds rather than minutes, which maintains the cognitive flow that's essential to productive development[8].

The distinction between pre-commit and post-commit hooks becomes particularly important in AI-assisted workflows. Pre-commit hooks can prevent obviously malformed code from being committed, but they execute before the commit message is finalized. The prepare-commit-msg hook, by contrast, runs after the user specifies what they're committing but before they leave the editor, making it the ideal place to auto-generate or validate commit messages[10]. Tools like commitlint can be configured to validate that commit messages follow conventional commit format, rejecting commits that don't meet standards and providing immediate feedback about the expected format[2][11].

## Checkpoint and Session-Based Tracking Systems

For developers working with AI coding assistants that don't integrate directly with Git, checkpoint systems provide a secondary mechanism for capturing work at meaningful intervals. Claude Code's checkpointing feature automatically captures code state before each edit, creating a timeline that developers can navigate with the `/rewind` command to restore code to prior states while keeping or discarding conversation history as desired[26]. This provides a safety net for experimental changes without requiring explicit commits.

CCheckpoints, an open-source tool designed specifically for Claude Code CLI, extends this concept by automatically saving checkpoints every time the user interacts with Claude Code, creating a timeline that developers can view in a beautiful web dashboard[29]. The tool hooks into Claude Code's lifecycle to track every message submission and session completion, storing data in a local SQLite database that persists across sessions[29]. This enables developers to understand their entire coding journey, compare changes between checkpoints, and quickly revert to prior states if an agent exploration didn't work out.

The architectural advantage of checkpoint systems is that they operate orthogonally to version control—a developer can maintain checkpoints for experimental work while only committing polished, tested changes to Git. This separation allows for lower-friction capture of work in progress without polluting commit history with intermediate states. However, checkpoints should be understood as complementary to, not replacements for, version control; the sources explicitly recommend continuing to use Git for permanent history and collaboration[26].

## Git Worktrees for Parallel Agent Isolation

When managing multiple AI agents working on different tasks simultaneously, or when humans and AI agents need to work in parallel, Git worktrees provide a lightweight mechanism for maintaining completely isolated working directories while sharing a single Git database[43]. A worktree is essentially a separate checkout of a repository at a different path, allowing multiple branches to be worked on simultaneously without context switching in a single terminal[43].

The workflow described in several sources involves creating an agent worktree on a new branch, letting the agent work in isolation in that directory, then removing the worktree and optionally deleting the branch when the work is complete[43]. The beauty of this approach is that each worktree is isolated—changes in one don't affect others—yet they share the same Git database, making them lightweight and fast compared to maintaining multiple full clones[43]. If an agent makes a mess, the developer can simply delete that worktree and try again without affecting their main working directory[43].

For teams coordinating multiple agents, this pattern becomes particularly powerful. One developer can be working on primary features in the main worktree while multiple AI agents each work in their own worktrees on parallel tasks[43]. Because each worktree has its own branch, there's automatic protection against conflicting changes to the same files—Git prevents checking out the same branch twice, preventing the worst-case merge disasters[43]. The worktree approach complements rather than competes with tools like GitButler; while GitButler uses virtual branches within a single workspace, worktrees are better for scenarios requiring true filesystem isolation or when working across multiple projects.

## Monorepo Tooling and Workspace-Aware AI Context

As AI agents become more sophisticated, their effectiveness depends critically on having sufficient context about the codebase architecture. In monorepos containing dozens or hundreds of projects, file-level context becomes inadequate—an AI agent needs to understand project relationships, dependency graphs, and architectural patterns to make intelligent cross-project changes[33][56]. Modern monorepo tools increasingly provide Model Context Protocol (MCP) servers that give AI assistants structured information about workspace architecture.

Nx's MCP server, for example, exposes tools for workspace analysis, code generation, and documentation lookup that enable AI assistants to move beyond file-level reasoning to understand high-level architecture[56]. When an AI agent has access to project graphs showing which projects depend on which others, ownership information identifying who's responsible for each project, and documentation about architectural patterns, it can make more intelligent decisions about where to implement functionality and how to coordinate changes across the monorepo[56].

This architectural context prevents a category of errors that would otherwise occur: an agent generating code in one project that violates dependency constraints, introduces circular dependencies, or duplicates functionality that exists elsewhere in the monorepo[56]. By providing the "map view" of the codebase rather than just individual files, MCP-aware tooling dramatically improves agent effectiveness and reduces the need for human review and correction[56].

## Intelligent Commit Grouping and Retroactive Analysis

For situations where uncommitted changes have already accumulated, tools like TensorZero's evaluation framework provide a methodology for retroactively understanding what an AI agent produced and linking inferences to commits. The core challenge is that a single commit might contain code generated from multiple inferences, each inference might have affected multiple commits, and the relationship between LLM output and final committed code is often indirect and complex[4].

TensorZero addresses this through tree-edit distance (TED) analysis: for each snippet generated by the AI, the system searches through the committed code to find the subtree with the smallest tree-edit distance, calculating a normalized distance ratio where 1.0 represents a perfect match and lower scores indicate partial matches or transformations[4]. By analyzing every inference against the committed code, the system builds a dataset linking specific prompts and model configurations to their actual impact on the codebase[4].

While TED analysis is most useful prospectively as part of a feedback loop to optimize prompts and models, the underlying principle suggests an approach for retroactive analysis: compute tree-edit distances between uncommitted changes and previous committed code to identify logical groupings. Changes with high similarity to existing code in a specific area of the codebase probably belong in a commit focused on that area. Changes that transform existing code in specific ways might indicate refactoring that should be grouped together. This could enable development tools to suggest "you made changes in three separate logical areas that might warrant three separate commits" based on analyzing the actual code modifications.

## Best Practices for Sustainable AI-Assisted Development

Several synthesis principles emerge from examining successful AI-assisted development workflows. The first critical practice involves **planning before generation**: rather than asking an AI agent to build a complete feature and then reviewing the result, sophisticated teams write explicit plans in markdown, ask the AI to critique the plan before implementation, and save the plan as a reference document for all subsequent prompts[3]. This single practice eliminates approximately eighty percent of "the AI got confused halfway through" moments because the AI maintains consistent context throughout the development process[3].

The second practice involves **edit-test loops rather than pure generation**: instead of asking the AI to write complete implementations, ask it to write failing tests that capture desired behavior, review those tests to ensure they test the right things, then ask the AI to make the tests pass[3]. This transforms AI code generation from a creative task (which is error-prone) to an implementation task (which is more reliable). The AI gets incremental feedback about whether its changes actually work, not just whether they compile.

Version control discipline represents the third pillar: commit granularly with `git add -p` to stage small logical changes, never let uncommitted changes pile up as they become increasingly difficult to untangle, and use meaningful commit messages that help both humans and AI understand context[3]. When working with AI agents, this becomes even more critical—each logical agent contribution should be tracked as a separate branch or commit so that if problems emerge, they can be reverted cleanly and the cause diagnosed accurately[3].

The fourth practice involves **context management and incremental re-indexing**: after major changes to the codebase, tell the AI agent to re-index its understanding through tools like gitingest.com for codebase summaries or re-running initial analysis commands[3]. AI agents can hallucinate about what exists in the codebase if working from stale context, and explicitly refreshing context prevents subtle bugs where the agent generates code based on outdated assumptions[3].

The fifth practice is **treating AI output like junior developer pull requests**[3]: security reviews checking for injection vulnerabilities and hardcoded secrets, performance reviews looking for N+1 queries and unnecessary allocations, correctness reviews testing edge cases and verifying error handling. The AI is intelligent but not wise; human developers must bring experience and judgment to the review process[3].

## Development Environment Configurations and Workflow Integration

Beyond tool choices, the way development environments are configured shapes team behavior around commits. GitButler provides a complete reimagining of this through its virtual branches interface, which makes branches as visible and manageable as files in an editor[1]. Developers can drag and drop commits between branches, edit commit messages, and squash or split commits through point-and-click interfaces rather than command-line tools that many developers find cumbersome[1]. This lower friction around commit management means developers are more likely to maintain clean history.

IDEs like IntelliJ IDEA support changelists, which allow developers to group uncommitted changes related to different tasks, then commit them independently[12]. This feature is particularly valuable when working on multiple features in parallel or when an AI agent has made changes touching multiple logical areas. Rather than committing everything together, developers can organize changes into logical groupings before committing.

GitHub's Agent Sessions feature in VS Code provides centralized visibility into what coding agents are doing, showing rationale behind Copilot's commits as they happen, right in context[14][28]. This in-IDE visibility means developers don't need to context-switch to understand what agents have accomplished or to provide corrections and feedback. The ability to see, comment on, and guide agent work in real-time prevents the situation where an agent runs unsupervised and produces work that diverges significantly from requirements.

## Emerging Specialized Tools for AI-Assisted Workflows

Beyond the mainstream tools, a ecosystem of specialized implementations addresses specific aspects of the uncommitted-changes problem. Aider, a terminal-based AI pair programming tool, automatically commits changes with sensible commit messages, allowing developers to use familiar git tools to diff, manage, and undo AI changes[37]. By committing after each AI-assisted code block, Aider creates a natural checkpoint structure that prevents changes from accumulating.

OpenCode, a Go-based CLI application with a TUI interface, tracks file changes during sessions and provides session management capabilities that let developers save and resume conversations while maintaining awareness of what changed[15]. The tool integrates with Language Server Protocol for code intelligence and supports custom commands that developers can create to quickly send predefined prompts.

AI-Commit goes beyond simple commit message generation by adding an AI code review subcommand that provides basic feedback on staged changes before committing, combined with a semantic release mode that can automatically determine version bumps[31]. The tool's interactive TUI allows developers to refine commit messages, change commit types, or regenerate messages based on changes to the staged content, maintaining developer control while leveraging AI efficiency.

GitPilotAI, a Go CLI tool, maintains focus on the core problem: a developer stages files, GitPilotAI scans the diff, generates a logical description through OpenAI's API, and immediately pushes the commit and change to the remote[34]. By automating the investigation step that interrupts developer flow—going through each changed file to construct a coherent narrative of what changed—the tool helps developers stay in the zone while still maintaining meaningful commits[34].

## Changelog and Release Automation for Organized History

Once commits are organized according to conventional commit format, the downstream benefits multiply through tools that parse commit history to generate changelogs and manage releases. Git-cliff, a highly customizable changelog generator written in Rust, uses regex-powered custom parsers to group commits by type and generate formatted changelogs[21][24]. The tool can be configured with Keep a Changelog format or custom templates, and when integrated into CI/CD pipelines, automatically generates and commits changelog updates alongside version tags[21].

Commitizen provides both a CLI tool for generating standardized commits and automation for calculating version bumps and generating changelogs[44]. By analyzing commit history since the last release, Commitizen determines whether changes warrant a major, minor, or patch version bump according to semantic versioning rules, then updates version files and generates release notes[44].

The practical effect is that teams maintaining conventional commit discipline and integrating these tools into their CI/CD get automated releases with changelogs that accurately reflect changes, without manual work[21][44]. For teams working with AI agents, this means the agent-generated commits that follow conventional format automatically contribute to organized, versioned releases that communicate clearly with users about what changed and why.

## Multi-Agent Orchestration and Coordination

As AI-assisted development evolves toward scenarios where multiple agents work in parallel on different aspects of the same system, orchestration becomes critical. Agent orchestration enables multiple AI agents to work together efficiently, coordinating tasks, sharing context, and driving complex workflows without manual intervention between steps[57]. Centralized orchestration, where a single orchestrator agent manages other agents, works well for linear, predictable workflows[57]. Decentralized orchestration, where agents make local decisions and communicate with peers, works better for parallel, experimental tasks[57].

In the context of uncommitted changes, orchestration provides a mechanism for ensuring that parallel agent work remains organized. Rather than multiple agents all writing to the same uncommitted changes, an orchestration layer can assign each agent to a specific branch or worktree, collect their outputs as commits, and coordinate integration back to main. GitButler's approach to this—using agent hooks to detect when agents modify files and automatically committing those changes to agent-specific branches—provides a concrete example of how orchestration prevents change accumulation[49].

## Review and Quality Enforcement in Hybrid Workflows

The role of code review changes fundamentally when AI agents are contributors alongside humans. Rather than manual review of everything, an effective pattern is "AI reviews first": the human author requests an AI code review in their IDE or after opening a PR, receives feedback and suggestions, addresses those comments, and only then requests human review[51]. This can reduce back-and-forth communication by about a third while ensuring that obviously fixable issues don't consume human reviewer time[51].

However, important caveats apply: AI excels at mechanical correctness issues—catching unused imports, typos, missing error handling, basic security issues—but struggles with architectural decisions, business logic alignment, and understanding implicit requirements[51]. Human reviewers must focus on these higher-level concerns while letting AI handle routine checks. Branch protections and required reviews remain critical even with AI contributors, ensuring that at least one human approves changes before they merge[25][51].

## Preventing and Managing Uncommitted Change Accumulation

The most straightforward prevention strategy combines several mechanisms: enforce commits at regular intervals through automation, maintain clear branch organization so developers understand what each branch contains, and provide UI/UX that makes committing easy and low-friction. GitButler's virtual branches interface, where developers can see at a glance what's on each branch and quickly commit changes through the UI, addresses the UX problem directly[1].

For teams using more traditional setups, configuring git hooks to warn developers when uncommitted changes reach a threshold (e.g., more than 20 files modified) can trigger awareness. While developers can override warnings, the explicit notice prevents the common situation where uncommitted changes accumulate without the developer realizing it. Combining warnings with pre-commit hooks that validate commit messages ensures that when developers finally commit, the message meets team standards.

When uncommitted changes have accumulated to problematic levels, the retroactive solution involves several steps. First, run `git status` to see what's changed and `git diff` to examine actual modifications. Second, use `git add -p` to selectively stage changes by hunk, reading each hunk and deciding whether it belongs in the same logical group. Third, commit frequently with clear messages as changes are staged. This approach, while labor-intensive, forces deliberate thinking about what changes belong together and produces a cleaner commit history than trying to commit everything at once.

For more sophisticated analysis, tools scanning code changes could identify natural commit boundaries by looking for groups of files that have high dependency connections versus low connections across groups. Changes within a feature module are likely related and should be committed together; changes that span feature modules might need more careful review. While such analysis tools aren't yet widely available, the tree-edit distance approaches used by TensorZero point toward their feasibility.

## Conclusion and Emerging Best Practices

Managing uncommitted changes in AI-assisted development requires attention at multiple layers: the version control system itself must accommodate AI workflows rather than forcing AI into human-centric paradigms, commit conventions must be standardized and enforced so that downstream automation can extract meaning, development environments must make committing frictionless and provide visibility into what's committed versus pending, and review processes must be calibrated to verify that AI-generated code meets human standards without creating bottlenecks.

The most mature solutions integrate these layers: GitButler's virtual branches handle organizational structure, conventional commits enable automation, pre-commit hooks enforce discipline, and interactive review creates checkpoints before changes propagate. GitHub Copilot's draft PRs achieve similar goals through GitHub's native concepts. Cursor's agent mode provides interactive approval workflows. Aider's immediate commits prevent accumulation by design.

Emerging best practice patterns include planning before generation, using edit-test loops, committing granularly, maintaining fresh context, and treating AI output with the same review rigor applied to junior developers. Teams implementing these patterns report dramatically improved workflow satisfaction and code quality compared to working with AI without structure.

As AI coding assistants become more sophisticated and more teams adopt agentic workflows, the tools and practices discussed here represent the current frontier of keeping development organized. The field is evolving rapidly, with tools adding new capabilities and teams discovering new patterns regularly. The fundamental principle, however, remains constant: code organization is a prerequisite for sustainable development, whether that code is written by humans or AI agents. Version control discipline, meaningful commits, and human oversight remain as essential as ever, just applied in different ways to accommodate the new capabilities and challenges that AI brings to software development.

---

## Citations

1. https://blog.gitbutler.com/gitbutler-agent-assist
2. https://www.conventionalcommits.org/en/about/
3. https://forgecode.dev/blog/ai-agent-best-practices/
4. https://www.tensorzero.com/blog/automatically-evaluating-ai-coding-assistants-with-each-git-commit/
5. https://github.com/semantic-release/semantic-release
6. https://www.harness.io/harness-devops-academy/version-control-system-best-practices
7. https://pypi.org/project/git-autocommit-hook/
8. https://dev.to/zhangzewei/pre-commit-with-husky-lint-staged-2kcm
9. https://docs.qodo.ai/qodo-documentation/qodo-gen/code-review/review-uncommitted-changes
10. https://pre-commit.com
11. https://github.com/lint-staged/lint-staged
12. https://www.jetbrains.com/help/idea/managing-changelists.html
13. https://cursor.com/docs/integrations/git
14. https://github.blog/changelog/2025-11-13-manage-copilot-coding-agent-tasks-in-visual-studio-code/
15. https://github.com/opencode-ai/opencode
16. https://cursor.com/docs/integrations/github
17. https://github.com/fork-dev/TrackerWin/issues/2100
18. https://refact.ai
19. https://www.datacamp.com/tutorial/git-reset-soft-complete-guide
20. https://github.com/di-sukharev/opencommit
21. https://dev.to/alfreedom/automate-your-changelog-with-git-cliff-and-keep-a-changelog-2go8
22. https://git-scm.com/docs/git-reset
23. https://dev.to/disukharev/opencommit-gpt-cli-to-auto-generate-impressive-commits-in-1-second-46dh
24. https://git-cliff.org
25. https://github.com/newsroom/press-releases/coding-agent-for-github-copilot
26. https://code.claude.com/docs/en/checkpointing
27. https://www.datacamp.com/tutorial/windsurf-ai-agentic-code-editor
28. https://github.blog/changelog/2025-11-13-manage-copilot-coding-agent-tasks-in-visual-studio-code/
29. https://github.com/p32929/ccheckpoints
30. https://windsurf.com
31. https://github.com/renatogalera/ai-commit
32. https://github.com/JetBrains-Research/PyNose
33. https://monorepo.tools/ai
34. https://www.ksred.com/automating-git-commits-using-ai/
35. https://www.jit.io/resources/appsec-tools/top-python-code-analysis-tools-to-improve-code-quality
36. https://graphite.com/guides/strategies-managing-dependencies-monorepo
37. https://aider.chat
38. https://dev.to/iredox10/mastering-git-stash-a-handy-tool-for-managing-uncommitted-changes-4ba3
39. https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-mode?view=visualstudio
40. https://www.youtube.com/watch?v=3skLPyFL8xU
41. https://www.atlassian.com/git/tutorials/saving-changes/git-stash
42. https://davidmelamed.com/2025/08/08/overview-of-advanced-ai-coding-agents-august-2025/
43. https://blog.itdepends.be/parallel-workflows-git-worktrees-agents/
44. https://commitizen-tools.github.io/commitizen/
45. https://code.visualstudio.com/docs/getstarted/tips-and-tricks
46. https://news.ycombinator.com/item?id=46027947
47. https://github.com/commitizen/cz-cli
48. https://forum.cursor.com/t/smarter-diff-visualization-for-ai-code-edits-like-git-in-visual-studio/92375
49. https://blog.gitbutler.com/automate-your-ai-workflows-with-claude-code-hooks
50. https://graphite.com/guides/how-do-stacked-diffs-work
51. https://www.ranger.net/post/version-control-best-practices-ai-code
52. https://blog.gitbutler.com/stacked-branches-with-gitbutler
53. https://newsletter.pragmaticengineer.com/p/stacked-diffs
54. https://github.com/f/git-rewrite-commits
55. https://www.kernel.org/pub/software/scm/git/docs/git-diff-index.html
56. https://nx.dev/docs/features/enhance-ai
57. https://www.lyzr.ai/blog/agent-orchestration/
58. https://git-scm.com/docs/git-diff-index
59. https://github.com/nrwl/nx/issues/5570
60. https://www.epam.com/insights/ai/blogs/single-responsibility-agents-and-multi-agent-workflows

---

## Usage Stats

- Prompt tokens: 175
- Completion tokens: 5131
- Total tokens: 5306
