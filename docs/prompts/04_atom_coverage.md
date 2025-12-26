# MEGAPROMPT 04: ATOM COVERAGE & AST MAPPING

## Context
Standard Code defines 167 "Atoms" organized into 4 Phases × 4 Families = 16 Families.
The claim is that these 167 atoms **completely cover** all AST node types across all programming languages.

## Your Task
Design and execute a coverage test.

## Instructions

1. **Select Target Languages**: Python, TypeScript, Java, Go, Rust

2. **For Each Language**:
   - Extract the official AST node type list (e.g., Tree-sitter grammar)
   - Create a **crosswalk table**: `AST Node Kind → Atom ID`
   - Mark each mapping as: **Direct** (1:1), **Merged** (N:1), **Split** (1:N), **Missing**

3. **Coverage Metrics**:
   - **Coverage %**: AST nodes mapped / Total AST nodes
   - **Atom Utilization %**: Atoms used / 167
   - **Unmapped Nodes**: List with proposed fix (new atom or merge)

4. **Stability Test**:
   - If language X adds a new AST node in version Y, how do we handle it?
   - Propose a versionless atom schema OR versioned atom registry

5. **Evolution Protocol**:
   - If we must add atom #168, what's the process?
   - How do we migrate existing analysis data?

## Expected Output
- Crosswalk tables for 5 languages
- Coverage summary (should be >95%)
- Unmapped node list with proposals
- Evolution protocol document
