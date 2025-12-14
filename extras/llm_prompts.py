#!/usr/bin/env python3
"""
🤖 LLM PROMPT GENERATOR — Context-Rich Prompts for AI Coding Assistants

Generates optimized prompts that include:
1. System architecture diagrams
2. Component relationships
3. Semantic IDs for precise code references
4. Context-aware instructions

Usage:
    python3 llm_prompts.py ~/project --template understand
    python3 llm_prompts.py ~/project --template feature --description "Add user auth"
    python3 llm_prompts.py ~/project --template refactor --target "payment module"
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "core"))


class LLMPromptGenerator:
    """Generates context-rich prompts for LLM coding assistants."""
    
    TEMPLATES = {
        "understand": "Understand and explain the codebase architecture",
        "feature": "Add a new feature to the codebase",
        "refactor": "Refactor a specific module or component",
        "debug": "Debug and fix an issue",
        "test": "Add comprehensive tests",
        "document": "Generate documentation",
    }
    
    def __init__(self):
        self.diagram_generator = None
        self.learning_engine = None
    
    def _init_engines(self):
        """Initialize analysis engines."""
        if self.learning_engine is None:
            from learning_engine import LearningEngine
            from diagram_generator import SystemDiagramGenerator
            self.learning_engine = LearningEngine(auto_learn=False)
            self.diagram_generator = SystemDiagramGenerator()
    
    def generate_context(self, repo_path: str) -> Dict:
        """Generate full context for a repository."""
        self._init_engines()
        
        # Analyze repo
        analysis = self.learning_engine.analyze_repo(repo_path)
        
        # Generate diagrams
        diagram = self.diagram_generator.generate(repo_path)
        
        return {
            "repo_name": analysis.name,
            "files": analysis.files,
            "lines": analysis.lines,
            "coverage": analysis.coverage_pct,
            "classes": analysis.classes,
            "functions": analysis.functions,
            "semantic_ids": analysis.semantic_ids,
            "layers": diagram.layers,
            "components": diagram.components,
            "relationships": diagram.relationships,
            "architecture_diagram": diagram.layer_diagram,
            "component_diagram": diagram.component_diagram,
            "class_hierarchy": diagram.class_hierarchy,
            "class_hierarchy": diagram.class_hierarchy,
            "call_flow": diagram.call_flow,
            "package_map": diagram.package_map,
        }
    
    def generate_prompt(self, repo_path: str, template: str, 
                        description: str = "", target: str = "") -> str:
        """Generate a complete LLM prompt."""
        context = self.generate_context(repo_path)
        
        if template == "understand":
            return self._generate_understand_prompt(context)
        elif template == "feature":
            return self._generate_feature_prompt(context, description)
        elif template == "refactor":
            return self._generate_refactor_prompt(context, target)
        elif template == "debug":
            return self._generate_debug_prompt(context, description)
        elif template == "test":
            return self._generate_test_prompt(context, target)
        elif template == "document":
            return self._generate_document_prompt(context)
        else:
            return self._generate_understand_prompt(context)
    
    def _generate_understand_prompt(self, ctx: Dict) -> str:
        """Generate prompt for understanding codebase."""
        return f"""# 🎯 CODEBASE UNDERSTANDING REQUEST

## Repository: {ctx['repo_name']}

### Quick Stats
- Files: {ctx['files']:,}
- Lines: {ctx['lines']:,}
- Classes: {ctx['classes']}
- Functions: {ctx['functions']}
- Coverage: {ctx['coverage']:.1f}%

### Architecture Layers
{', '.join(ctx['layers']) if ctx['layers'] else 'Not detected'}

### System Architecture
{ctx['architecture_diagram']}

### Component Overview
{ctx['component_diagram']}

### Class Hierarchy
{ctx['class_hierarchy']}

### Call Flow
### Call Flow
{ctx['call_flow']}

### Package Heterogeneity Map
{ctx['package_map']}

---

## YOUR TASK

Please analyze this codebase and provide:

1. **Architecture Summary**: What architectural pattern does this codebase follow? (DDD, Clean Architecture, Hexagonal, MVC, etc.)

2. **Key Components**: List the main components/modules and their responsibilities.

3. **Data Flow**: How does data flow through the system?

4. **Entry Points**: Where are the main entry points for the application?

5. **Dependencies**: What are the key external dependencies?

6. **Improvement Opportunities**: What could be improved in this architecture?

Be specific and reference the diagrams above in your analysis.
"""
    
    def _generate_feature_prompt(self, ctx: Dict, description: str) -> str:
        """Generate prompt for adding a feature."""
        return f"""# 🚀 FEATURE IMPLEMENTATION REQUEST

## Repository: {ctx['repo_name']}

### Feature to Add
{description}

---

### Current Architecture
{ctx['architecture_diagram']}

### Existing Components
{ctx['component_diagram']}

### Class Hierarchy
{ctx['class_hierarchy']}

---

## YOUR TASK

Implement the requested feature following these steps:

1. **Identify Impact**: Which existing components need modification?

2. **Design New Components**: What new classes/functions are needed?

3. **Define Interfaces**: What interfaces should the new code implement?

4. **Layer Placement**: Where in the architecture should each piece go?
   - Domain layer: Core business logic
   - Application layer: Use cases, orchestration
   - Infrastructure layer: External integrations
   - Presentation layer: API/UI handlers

5. **Implementation**: Write the actual code, following existing patterns.

6. **Tests**: Add comprehensive tests for the new feature.

Important: Follow the existing coding style and architectural patterns found in this codebase.
"""
    
    def _generate_refactor_prompt(self, ctx: Dict, target: str) -> str:
        """Generate prompt for refactoring."""
        return f"""# 🔧 REFACTORING REQUEST

## Repository: {ctx['repo_name']}

### Target for Refactoring
{target}

---

### Current Architecture
{ctx['architecture_diagram']}

### Component Dependencies
{ctx['component_diagram']}

### Class Hierarchy (look for violations)
{ctx['class_hierarchy']}

### Call Flow (identify complexity)
{ctx['call_flow']}

---

## YOUR TASK

Refactor the specified target following these steps:

1. **Analyze Current State**: What problems exist with the current implementation?
   - Too many responsibilities?
   - Hidden dependencies?
   - Violation of SOLID principles?
   - Complex call chains?

2. **Design Improvements**: How can we improve the code?
   - Extract classes/functions?
   - Introduce abstractions?
   - Simplify dependencies?

3. **Plan the Refactoring**: What steps should we take?
   - List changes in order
   - Identify risks
   - Plan for backwards compatibility

4. **Implement Changes**: Provide the refactored code.

5. **Verify**: Ensure all existing tests pass and behavior is preserved.

Important: Refactoring should NOT change external behavior, only improve internal structure.
"""
    
    def _generate_debug_prompt(self, ctx: Dict, issue: str) -> str:
        """Generate prompt for debugging."""
        return f"""# 🐛 DEBUG REQUEST

## Repository: {ctx['repo_name']}

### Issue Description
{issue}

---

### System Architecture
{ctx['architecture_diagram']}

### Call Flow (trace the issue path)
{ctx['call_flow']}

### Class Hierarchy
{ctx['class_hierarchy']}

---

## YOUR TASK

Debug and fix this issue:

1. **Reproduce**: Understand how to reproduce the issue.

2. **Trace**: Follow the call flow to identify where the bug might occur.

3. **Identify Root Cause**: What is actually causing the problem?

4. **Propose Fix**: What changes will fix the issue?

5. **Verify**: How can we verify the fix works?

6. **Prevent**: How can we prevent similar bugs in the future?

Be thorough - bugs often hide in edge cases and unexpected interactions.
"""
    
    def _generate_test_prompt(self, ctx: Dict, target: str) -> str:
        """Generate prompt for adding tests."""
        return f"""# 🧪 TEST GENERATION REQUEST

## Repository: {ctx['repo_name']}

### Target for Testing
{target if target else 'Generate comprehensive tests for the entire codebase'}

---

### Architecture (identify test boundaries)
{ctx['architecture_diagram']}

### Components (unit test targets)
{ctx['component_diagram']}

### Class Hierarchy (mock candidates)
{ctx['class_hierarchy']}

### Call Flow (integration test paths)
{ctx['call_flow']}

---

## YOUR TASK

Generate comprehensive tests:

1. **Unit Tests**: Test individual components in isolation.
   - Mock external dependencies
   - Test edge cases
   - Test error handling

2. **Integration Tests**: Test component interactions.
   - Test call flows
   - Test data transformations
   - Test database operations

3. **Test Structure**: Follow existing test patterns in the codebase.

4. **Coverage Goals**: Aim for meaningful coverage, not just line coverage.

5. **Test Data**: Include realistic test data and fixtures.

Generate tests that will catch bugs and prevent regressions.
"""
    
    def _generate_document_prompt(self, ctx: Dict) -> str:
        """Generate prompt for documentation."""
        return f"""# 📚 DOCUMENTATION REQUEST

## Repository: {ctx['repo_name']}

### Current Stats
- Files: {ctx['files']:,}
- Lines: {ctx['lines']:,}
- Components: {ctx['components']}
- Relationships: {ctx['relationships']}

---

### Architecture
{ctx['architecture_diagram']}

### Components
{ctx['component_diagram']}

### Class Hierarchy
{ctx['class_hierarchy']}

### Call Flow
{ctx['call_flow']}

---

## YOUR TASK

Generate comprehensive documentation:

1. **README.md**: Project overview, setup instructions, quick start.

2. **ARCHITECTURE.md**: Detailed architecture documentation.
   - Layer descriptions
   - Component responsibilities
   - Key patterns used

3. **API Documentation**: Document public interfaces.
   - Endpoints (if web API)
   - Public functions/methods
   - Data models

4. **Developer Guide**: How to contribute.
   - Code style
   - Testing requirements
   - PR process

5. **Diagrams**: Include the Mermaid diagrams above.

Make documentation clear, concise, and actionable.
"""
    
    def export(self, prompt: str, output_path: str) -> str:
        """Export prompt to file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prompt)
        return str(path)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="🤖 LLM Prompt Generator - Create context-rich prompts for AI coding"
    )
    parser.add_argument(
        "repo_path",
        help="Path to repository to analyze"
    )
    parser.add_argument(
        "--template", "-t",
        choices=["understand", "feature", "refactor", "debug", "test", "document"],
        default="understand",
        help="Prompt template to use"
    )
    parser.add_argument(
        "--description", "-d",
        default="",
        help="Description for feature/debug templates"
    )
    parser.add_argument(
        "--target",
        default="",
        help="Target module/component for refactor/test templates"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🤖 LLM PROMPT GENERATOR")
    print("=" * 70)
    
    generator = LLMPromptGenerator()
    
    print(f"\n📁 Analyzing: {args.repo_path}")
    print(f"📝 Template: {args.template}")
    
    prompt = generator.generate_prompt(
        args.repo_path,
        args.template,
        args.description,
        args.target
    )
    
    if args.output:
        out = generator.export(prompt, args.output)
        print(f"\n💾 Exported to: {out}")
    else:
        print("\n" + "=" * 70)
        print(prompt)
