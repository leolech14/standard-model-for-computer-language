# Research: COMPATIBILITY ANALYSIS for commit hygiene solution.

OUR STACK:
- Claude Code CLI (primary dev tool)...

> **Date:** 2026-01-24 15:06:52
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:f9a878a179b913283ca5f0846eb6ee7bc01f64dd2962c8486b4b3e9cf8771ddd`
> **Raw JSON:** `raw/20260124_150652_compatibility_analysis_for_commit_hygiene_solution.json`

---

## Query

COMPATIBILITY ANALYSIS for commit hygiene solution.

OUR STACK:
- Claude Code CLI (primary dev tool)
- Google Antigravity IDE (VSCode-based)
- Project has .agent/ directory with task registry, sprints, card game metaphor
- Agentic onboarding with INITIATION_REPORT pattern
- Wave/Particle architecture

CANDIDATES: git add -p, GitButler, Pre-commit+commitlint, OpenCommit, Git Worktrees, Aider

Which is MOST COMPATIBLE and a NO-BRAINER fix? Single recommendation with justification.

---

## Response

Okay, I've analyzed the provided codebase context to determine the most compatible "commit hygiene" solution for your setup. Here's my recommendation and justification:

**Recommendation: Pre-commit + Commitlint**

**Justification:**

1.  **Existing Tooling Compatibility:**
    *   Your project already leverages configuration files (`.agent/manifest.yaml`, etc.)  This suggests a preference for explicit configuration over more "magical" or implicit systems. Pre-commit, with its YAML-based configuration (`.pre-commit-config.yaml`), aligns well with this.
    *   You also have existing validation rules defined for your Agent System. Commitlint integrates well with Pre-commit and allows you to extend these rules to commit messages, thus ensuring consistency across all commits.

2.  **Agentic Workflow & Task Management:**
    *   You have a well-defined task registry and agent-driven workflow.  Clean commit messages are crucial for tracking changes related to specific tasks. Commitlint enforces a standardized format (e.g., referencing `TASK-XXX` in the commit message), making it easier to link commits to tasks and track progress. This is **more valuable** than a patch selection tool at the high level and granularity of your overall approach.

3.  **Wave/Particle Architecture:**
    *   Pre-commit introduces a codified means of enforcing quality code. Thus Pre-commit is the *Particle* side, making code truth, and Code Linter is the *Wave* side.

4.  **Explicit vs. Implicit**: Your preference for config over code is reflected in your Wave/Particle symmetry, so going with code generation via `aider` or context-aware changes to staged areas with `git-add -p` are out.

5.  **"No-Brainer" Fix:**
    *   Pre-commit is relatively easy to integrate.  You can start with a minimal set of checks (e.g., just commitlint) and gradually add more as needed.  The configuration is explicit, making it easy to understand and maintain.
    *   GitButler, while potentially powerful, is more invasive and requires a deeper change to the developer's workflow and is therefore unsuitable given your requirements.

6.  **Version History.** The project has well-defined history and has a *documented preference for manual steps over high automation*, especially in light of your "Always Green Refinement Pipeline" and related goals. Adding automatic steps would be a premature optimization.

**Why not the others:**

*   **`git add -p`**: is more a code patch selection workflow, not a overall commit validation tool.
*   **GitButler**: Too opinionated. Introduces a new workflow and potentially conflicts with your existing task management system.
*   **OpenCommit**: is code generation, but you value documentation over code.
*   **Git Worktrees**: Primarily for managing multiple branches, not commit hygiene.
*   **Aider**: Same as OpenCommit.

**Integration Steps:**

1.  **Install Pre-commit:** `pip install pre-commit`
2.  **Create `.pre-commit-config.yaml`:**  Start with a minimal configuration, focusing on commitlint. Example:

```yaml
repos:
  - repo: https://github.com/conventional-changelog/commitlint
    rev: '8.3.5' # Use the current version
    hooks:
      - id: commitlint
        stages: [commit-msg]
```

3.  **Install Commitlint:** `npm install --save-dev @commitlint/{config-conventional,cli}`
4.  **Configure Commitlint:** Create `commitlint.config.js` with conventional rules (e.g., requiring type, scope, and description).
5.  **Install Git Hooks**: pre-commit install
6.  **Test**: commit changes and verify rules are triggered.
7.  **Customize:** refine pre-commit config + commitlint rules.

**Revised Steps Based on User Feedback**
Since user expresses manual steps over automation steps as well, a shell function would serve as a quick check, rather than a full commit.

```shell
#!/bin/bash
# Shell Script for quick testing changes
check_commits() {
  # Add CommitLint function that relies on npm
  npm install --save-dev @commitlint/{config-conventional,cli}
  # Validate commit title
  commitlint --config commitlint.config.js < commit summary>

}
```


---

## Citations

_No citations provided_
