#!/usr/bin/env python3
"""
Discovery Engine — Self-Learning Atom Taxonomy

The core insight: We don't just classify what we KNOW.
We DISCOVER and DOCUMENT what we DON'T know.

For every unknown pattern, we:
1. Extract its structural signature (AST shape)
2. Analyze its behavioral context (what it does)
3. Document it scientifically with a reproducible definition
4. Propose it as a candidate for the taxonomy

This is how the 96 Hadrons become 97, 98, 99... based on EVIDENCE, not engineering.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any, Set, Tuple
import json
import hashlib
from collections import defaultdict
from pathlib import Path

from core.graph_extractor import GraphExtractor
from core.complete_extractor import CompleteExtractor, CompleteCodebase


@dataclass
class UnknownAtom:
    """
    A pattern we couldn't categorize — candidate for taxonomy expansion.
    
    Scientific documentation requires:
    - Reproducible definition (AST signature)
    - Observable behavior (what it does)
    - Frequency evidence (how often it appears)
    - Context (where it appears)
    """
    # Identity
    signature_hash: str              # Unique hash of AST structure
    ast_type: str                    # Tree-sitter node type
    ast_signature: str               # Structural pattern (parent→child relationship)
    
    # Observable behavior
    behavior_indicators: List[str]   # What does it DO? (calls, returns, mutates)
    context_indicators: List[str]    # WHERE does it appear? (class, function, module)
    
    # Frequency evidence
    occurrence_count: int = 0
    files_seen_in: Set[str] = field(default_factory=set)
    repos_seen_in: Set[str] = field(default_factory=set)
    
    # Sample evidence
    code_samples: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)  # file:line
    
    # Proposed classification
    proposed_name: str = ""          # AI/human suggested name
    proposed_continent: str = ""     # Data/Logic/Organization/Execution
    proposed_fundamental: str = ""   # Which particle family
    proposed_level: str = ""         # atom/molecule/organelle
    
    # Scientific metadata
    first_seen: str = ""
    last_seen: str = ""
    confidence_score: float = 0.0    # How confident are we in the pattern?
    
    def to_scientific_report(self) -> str:
        """Generate a scientific documentation entry."""
        return f"""
## Unknown Pattern: {self.signature_hash[:8]}

### AST Signature
- **Node Type:** `{self.ast_type}`
- **Structural Pattern:** `{self.ast_signature}`

### Observable Behavior
- **Behavior Indicators:** {', '.join(self.behavior_indicators) or 'None detected'}
- **Context:** {', '.join(self.context_indicators) or 'Unknown'}

### Frequency Evidence
- **Occurrences:** {self.occurrence_count}
- **Files:** {len(self.files_seen_in)}
- **Repos:** {len(self.repos_seen_in)}

### Code Samples
```python
{self.code_samples[0] if self.code_samples else 'No samples collected'}
```

### Proposed Classification
- **Name:** {self.proposed_name or 'UNCLASSIFIED'}
- **Continent:** {self.proposed_continent or 'Unknown'}
- **Fundamental:** {self.proposed_fundamental or 'Unknown'}
- **Level:** {self.proposed_level or 'Unknown'}

### Confidence: {self.confidence_score:.2f}
---
"""


@dataclass 
class DiscoveryReport:
    """Summary of a discovery run."""
    repo_name: str
    timestamp: str
    files_analyzed: int
    total_nodes: int
    known_atoms: int
    unknown_atoms: int
    unknown_patterns: List[UnknownAtom]
    
    # Coverage metrics
    coverage_ratio: float = 0.0      # known / total
    discovery_rate: float = 0.0      # new unknowns this run
    

class DiscoveryEngine:
    """
    Self-learning taxonomy engine.
    
    Phase 1: Extract ALL AST nodes
    Phase 2: Classify KNOWN atoms
    Phase 3: DISCOVER and document UNKNOWN patterns
    Phase 4: Propose taxonomy expansions
    """
    
    def __init__(self, known_atoms_path: Optional[str] = None):
        self.known_atoms: Dict[str, Dict] = {}
        self.unknown_registry: Dict[str, UnknownAtom] = {}
        self.discovery_history: List[DiscoveryReport] = []
        
        # Load known atoms
        self._load_known_atoms(known_atoms_path)
        
        # Initialize parsers
        self.parsers = {}
        self._init_parsers()
        
        # Initialize graph extractor for internal use
        self.graph_extractor = GraphExtractor()
    
    
    def _init_parsers(self):
        """Initialize tree-sitter parsers using dynamic loader."""
        from core.language_loader import LanguageLoader
        self.parsers, self.languages, self.extensions = LanguageLoader.load_all()
    
    def _load_known_atoms(self, path: Optional[str]):
        """Load the known atom taxonomy."""
        # Syntax tokens to IGNORE (not meaningful atoms)
        self.syntax_tokens = {
            ".", ",", ":", ";", "(", ")", "[", "]", "{", "}", 
            "=", "==", "!=", "<", ">", "<=", ">=", "->", "=>",
            "+", "-", "*", "/", "%", "**", "//", "@", "|", "&", "^", "~",
            "+=", "-=", "*=", "/=", "//=", "%=", "**=", "&=", "|=", "^=",
            "and", "or", "not", "in", "is", "if", "else", "elif",
            "for", "while", "def", "class", "return", "yield", "raise",
            "try", "except", "finally", "with", "as", "from", "import",
            "pass", "break", "continue", "assert", "global", "nonlocal",
            "lambda", "async", "await", "True", "False", "None",
            "module", "block", "ERROR", "NEWLINE", "INDENT", "DEDENT",
            "string_start", "string_end", "string_content",
        }
        
        # Default known atoms from the 96 Hadrons - COMPREHENSIVE
        self.known_atoms = {
            # Primitives
            "true": {"name": "Boolean", "continent": "Data Foundations", "fundamental": "Primitives"},
            "false": {"name": "Boolean", "continent": "Data Foundations", "fundamental": "Primitives"},
            "integer": {"name": "Integer", "continent": "Data Foundations", "fundamental": "Primitives"},
            "float": {"name": "Float", "continent": "Data Foundations", "fundamental": "Primitives"},
            "string": {"name": "StringLiteral", "continent": "Data Foundations", "fundamental": "Primitives"},
            "none": {"name": "NoneValue", "continent": "Data Foundations", "fundamental": "Primitives"},
            "concatenated_string": {"name": "ConcatString", "continent": "Data Foundations", "fundamental": "Primitives"},
            "interpolation": {"name": "StringInterpolation", "continent": "Data Foundations", "fundamental": "Primitives"},
            
            # Variables
            "identifier": {"name": "LocalVar", "continent": "Data Foundations", "fundamental": "Variables"},
            "attribute": {"name": "InstanceField", "continent": "Data Foundations", "fundamental": "Variables"},
            "subscript": {"name": "IndexAccess", "continent": "Data Foundations", "fundamental": "Variables"},
            "slice": {"name": "SliceAccess", "continent": "Data Foundations", "fundamental": "Variables"},
            
            # Comprehensions & Generators
            "list_comprehension": {"name": "ListComprehension", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "dictionary_comprehension": {"name": "DictComprehension", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "set_comprehension": {"name": "SetComprehension", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "generator_expression": {"name": "GeneratorExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            
            # Expressions
            "binary_operator": {"name": "BinaryExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "unary_operator": {"name": "UnaryExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "comparison_operator": {"name": "ComparisonExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "boolean_operator": {"name": "LogicalExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "not_operator": {"name": "NotExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "call": {"name": "CallExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "lambda": {"name": "Closure", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "conditional_expression": {"name": "TernaryExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "named_expression": {"name": "WalrusExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "await": {"name": "AwaitExpr", "continent": "Logic & Flow", "fundamental": "Expressions"},
            
            # Statements
            "expression_statement": {"name": "ExpressionStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "assignment": {"name": "Assignment", "continent": "Logic & Flow", "fundamental": "Statements"},
            "augmented_assignment": {"name": "AugmentedAssignment", "continent": "Logic & Flow", "fundamental": "Statements"},
            "return_statement": {"name": "ReturnStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "pass_statement": {"name": "PassStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "break_statement": {"name": "BreakStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "continue_statement": {"name": "ContinueStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "raise_statement": {"name": "RaiseStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "assert_statement": {"name": "AssertStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "delete_statement": {"name": "DeleteStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "global_statement": {"name": "GlobalStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "nonlocal_statement": {"name": "NonlocalStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            "print_statement": {"name": "PrintStmt", "continent": "Logic & Flow", "fundamental": "Statements"},
            
            # Control Structures
            "if_statement": {"name": "IfBranch", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "elif_clause": {"name": "ElifBranch", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "else_clause": {"name": "ElseBranch", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "for_statement": {"name": "LoopFor", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "while_statement": {"name": "LoopWhile", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "try_statement": {"name": "TryCatch", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "except_clause": {"name": "ExceptHandler", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "finally_clause": {"name": "FinallyBlock", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "with_statement": {"name": "ContextManager", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "match_statement": {"name": "PatternMatch", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            "case_clause": {"name": "MatchCase", "continent": "Logic & Flow", "fundamental": "Control Structures"},
            
            # Functions
            "function_definition": {"name": "Function", "continent": "Logic & Flow", "fundamental": "Functions"},
            "async_function_definition": {"name": "AsyncFunction", "continent": "Logic & Flow", "fundamental": "Functions"},
            "decorated_definition": {"name": "DecoratedFunction", "continent": "Logic & Flow", "fundamental": "Functions"},
            "parameters": {"name": "ParameterList", "continent": "Logic & Flow", "fundamental": "Functions"},
            "default_parameter": {"name": "DefaultParam", "continent": "Logic & Flow", "fundamental": "Functions"},
            "typed_parameter": {"name": "TypedParameter", "continent": "Logic & Flow", "fundamental": "Functions"},
            "typed_default_parameter": {"name": "TypedDefaultParam", "continent": "Logic & Flow", "fundamental": "Functions"},
            "list_splat_pattern": {"name": "ArgsPattern", "continent": "Logic & Flow", "fundamental": "Functions"},
            "dictionary_splat_pattern": {"name": "KwargsPattern", "continent": "Logic & Flow", "fundamental": "Functions"},
            
            # Arguments
            "argument_list": {"name": "ArgumentList", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "keyword_argument": {"name": "KeywordArg", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "list_splat": {"name": "UnpackArgs", "continent": "Logic & Flow", "fundamental": "Expressions"},
            "dictionary_splat": {"name": "UnpackKwargs", "continent": "Logic & Flow", "fundamental": "Expressions"},
            
            # Classes/Organization
            "class_definition": {"name": "Class", "continent": "Organization", "fundamental": "Aggregates"},
            "import_statement": {"name": "Import", "continent": "Organization", "fundamental": "Modules"},
            "import_from_statement": {"name": "ImportFrom", "continent": "Organization", "fundamental": "Modules"},
            "aliased_import": {"name": "ImportAlias", "continent": "Organization", "fundamental": "Modules"},
            "dotted_name": {"name": "DottedName", "continent": "Organization", "fundamental": "Modules"},
            "relative_import": {"name": "RelativeImport", "continent": "Organization", "fundamental": "Modules"},
            
            # Type annotations
            "type": {"name": "TypeAnnotation", "continent": "Organization", "fundamental": "Types"},
            "generic_type": {"name": "GenericType", "continent": "Organization", "fundamental": "Types"},
            "union_type": {"name": "UnionType", "continent": "Organization", "fundamental": "Types"},
            "constrained_type": {"name": "ConstrainedType", "continent": "Organization", "fundamental": "Types"},
            
            # Syntax elements
            "comment": {"name": "Comment", "continent": "Organization", "fundamental": "Files"},
            "decorator": {"name": "Decorator", "continent": "Logic & Flow", "fundamental": "Functions"},
            
            # Collections
            "list": {"name": "ListLiteral", "continent": "Data Foundations", "fundamental": "Primitives"},
            "tuple": {"name": "TupleLiteral", "continent": "Data Foundations", "fundamental": "Primitives"},
            "dictionary": {"name": "DictLiteral", "continent": "Data Foundations", "fundamental": "Primitives"},
            "set": {"name": "SetLiteral", "continent": "Data Foundations", "fundamental": "Primitives"},
            "pair": {"name": "KeyValuePair", "continent": "Data Foundations", "fundamental": "Primitives"},
            
            # ═══ TYPESCRIPT MAPPINGS ═══
            "class_declaration": {"name": "TSClass", "continent": "Organization", "fundamental": "Aggregates"},
            "interface_declaration": {"name": "TSInterface", "continent": "Organization", "fundamental": "Contracts"},
            "function_declaration": {"name": "TSFunction", "continent": "Logic & Flow", "fundamental": "Functions"},
            "method_definition": {"name": "TSMethod", "continent": "Logic & Flow", "fundamental": "Functions"},
            "variable_declarator": {"name": "TSVariable", "continent": "Data Foundations", "fundamental": "Variables"},
            "arrow_function": {"name": "TSArrowFunc", "continent": "Logic & Flow", "fundamental": "Functions"},
            "import_statement": {"name": "TSImport", "continent": "Organization", "fundamental": "Modules"},
            "export_statement": {"name": "TSExport", "continent": "Organization", "fundamental": "Modules"},
            "public_field_definition": {"name": "TSField", "continent": "Data Foundations", "fundamental": "Variables"},
        }
    
    def _compute_signature(self, node) -> str:
        """Compute a structural signature for an AST node."""
        # Include node type and child structure
        child_types = [c.type for c in node.children[:5]]  # First 5 children
        signature = f"{node.type}:[{','.join(child_types)}]"
        return hashlib.md5(signature.encode()).hexdigest()[:12]
    
    def _extract_behavior(self, node) -> List[str]:
        """Analyze what this node DOES."""
        behaviors = []
        text = node.text.decode() if node.text else ""
        
        # Check for common behaviors
        if "return" in text.lower():
            behaviors.append("returns_value")
        if "self." in text or "this." in text:
            behaviors.append("accesses_instance")
        if "=" in text and "==" not in text:
            behaviors.append("assigns")
        if "(" in text:
            behaviors.append("invokes")
        if "await" in text:
            behaviors.append("async_operation")
        if "raise" in text or "throw" in text:
            behaviors.append("raises_exception")
        if any(io in text.lower() for io in ['read', 'write', 'open', 'save', 'fetch', 'request']):
            behaviors.append("performs_io")
        
        return behaviors
    
    def _extract_context(self, node) -> List[str]:
        """Analyze WHERE this node appears."""
        contexts = []
        
        # Walk up the tree to find context
        parent = node.parent
        depth = 0
        while parent and depth < 5:
            if parent.type == "class_definition":
                contexts.append("in_class")
            elif parent.type in ("function_definition", "async_function_definition"):
                contexts.append("in_function")
            elif parent.type == "if_statement":
                contexts.append("in_conditional")
            elif parent.type in ("for_statement", "while_statement"):
                contexts.append("in_loop")
            elif parent.type == "try_statement":
                contexts.append("in_try_block")
            parent = parent.parent
            depth += 1
        
        return list(set(contexts))
    
    def analyze_repo(self, repo_path: str, language: Optional[str] = None) -> DiscoveryReport:
        """
        Analyze a repository and discover atoms across ALL languages (or specific one).
        """
        path = Path(repo_path)
        
        # Determine languages
        if language:
            languages = [language]
        else:
            languages = list(self.parsers.keys())
        
        all_graph_nodes = {}
        combined_stats = {"total_files": 0}
        
        print(f"🔍 Analyzing languages: {', '.join(languages)}")
        
        for lang in languages:
            try:
                # Extract structure
                graph = self.graph_extractor.extract(str(path), language=lang)
                if not graph.nodes:
                    continue
                
                print(f"  ✓ {lang}: {len(graph.nodes)} nodes")
                all_graph_nodes.update(graph.nodes) # Merge nodes
                
            except Exception as e:
                print(f"  ⚠️  {lang} skipped: {e}")
                pass

        # Identify Atoms from Merged Graph
        discovered_atoms = []
        
        for node_id, node in all_graph_nodes.items():
            # Use raw_type (e.g. 'class_declaration') to find atom definition
            atom_def = self.known_atoms.get(node.raw_type)
            
            if atom_def:
                # It's a known atom
                pass
            else:
                # It's unknown - opportunity to learn?
                # For now we just track what we found
                pass
        
        # Calculate stats
        combined_stats["nodes"] = len(all_graph_nodes)
        unique_files = {n.file for n in all_graph_nodes.values() if n.file}
        combined_stats["total_files"] = len(unique_files)

        # Return simplified report
        return DiscoveryReport(
            repo_name=path.name,
            timestamp=datetime.now().isoformat(),
            files_analyzed=combined_stats.get("total_files", 0),
            total_nodes=combined_stats.get("nodes", 0),
            known_atoms=0,
            unknown_atoms=0,
            unknown_patterns=[],
            coverage_ratio=0.0,
            discovery_rate=0.0
        )
        
        files_analyzed = 0
        total_nodes = 0
        known_count = 0
        unknown_count = 0
        run_unknowns: Dict[str, UnknownAtom] = {}
        
        for file_path in repo.rglob(ext):
            path_str = str(file_path)
            if any(x in path_str for x in ["__pycache__", "node_modules", ".git", ".venv", "dddlint_env", "output/"]):
                continue
            
            try:
                code = file_path.read_bytes()
                tree = parser.parse(code)
                files_analyzed += 1
                
                rel_path = str(file_path.relative_to(repo))
                
                # Visit all nodes
                def visit(node, depth=0):
                    nonlocal total_nodes, known_count, unknown_count
                    total_nodes += 1
                    
                    node_type = node.type
                    
                    if node_type in self.known_atoms:
                        # Known atom
                        known_count += 1
                    elif node_type not in self.syntax_tokens:
                        # Unknown pattern - DISCOVER IT
                        unknown_count += 1
                        sig = self._compute_signature(node)
                        
                        if sig not in run_unknowns:
                            run_unknowns[sig] = UnknownAtom(
                                signature_hash=sig,
                                ast_type=node_type,
                                ast_signature=f"{node_type}→[{','.join(c.type for c in node.children[:3])}]",
                                behavior_indicators=self._extract_behavior(node),
                                context_indicators=self._extract_context(node),
                                occurrence_count=1,
                                files_seen_in={rel_path},
                                repos_seen_in={repo_name},
                                code_samples=[node.text.decode()[:200] if node.text else ""],
                                locations=[f"{rel_path}:{node.start_point[0]+1}"],
                                first_seen=datetime.now().isoformat(),
                                last_seen=datetime.now().isoformat(),
                            )
                        else:
                            ua = run_unknowns[sig]
                            ua.occurrence_count += 1
                            ua.files_seen_in.add(rel_path)
                            ua.repos_seen_in.add(repo_name)
                            ua.last_seen = datetime.now().isoformat()
                            if len(ua.code_samples) < 3:
                                sample = node.text.decode()[:200] if node.text else ""
                                if sample and sample not in ua.code_samples:
                                    ua.code_samples.append(sample)
                            if len(ua.locations) < 10:
                                ua.locations.append(f"{rel_path}:{node.start_point[0]+1}")
                    
                    for child in node.children:
                        visit(child, depth + 1)
                
                visit(tree.root_node)
                
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
        
        # Auto-classify unknowns based on patterns
        for sig, ua in run_unknowns.items():
            self._propose_classification(ua)
            ua.confidence_score = self._compute_confidence(ua)
            
            # Merge into global registry
            if sig in self.unknown_registry:
                self._merge_unknown(self.unknown_registry[sig], ua)
            else:
                self.unknown_registry[sig] = ua
        
        # Create report
        coverage = known_count / total_nodes if total_nodes > 0 else 0
        report = DiscoveryReport(
            repo_name=repo_name,
            timestamp=datetime.now().isoformat(),
            files_analyzed=files_analyzed,
            total_nodes=total_nodes,
            known_atoms=known_count,
            unknown_atoms=unknown_count,
            unknown_patterns=list(run_unknowns.values()),
            coverage_ratio=coverage,
            discovery_rate=len(run_unknowns) / total_nodes if total_nodes > 0 else 0,
        )
        
        self.discovery_history.append(report)
        return report
    
    def _propose_classification(self, ua: UnknownAtom):
        """Auto-propose a classification based on patterns."""
        ast_type = ua.ast_type.lower()
        
        # Heuristic classification based on AST type name
        if "statement" in ast_type or "stmt" in ast_type:
            ua.proposed_fundamental = "Statements"
            ua.proposed_continent = "Logic & Flow"
            ua.proposed_level = "atom"
        elif "expression" in ast_type or "expr" in ast_type:
            ua.proposed_fundamental = "Expressions"
            ua.proposed_continent = "Logic & Flow"
            ua.proposed_level = "atom"
        elif "definition" in ast_type or "declaration" in ast_type:
            ua.proposed_fundamental = "Functions" if "function" in ast_type else "Aggregates"
            ua.proposed_continent = "Organization" if "class" in ast_type else "Logic & Flow"
            ua.proposed_level = "molecule"
        elif "literal" in ast_type or "constant" in ast_type:
            ua.proposed_fundamental = "Primitives"
            ua.proposed_continent = "Data Foundations"
            ua.proposed_level = "atom"
        elif "import" in ast_type:
            ua.proposed_fundamental = "Modules"
            ua.proposed_continent = "Organization"
            ua.proposed_level = "atom"
        
        # Propose name based on AST type (convert snake_case to PascalCase)
        parts = ua.ast_type.split("_")
        ua.proposed_name = "".join(p.capitalize() for p in parts)
    
    def _compute_confidence(self, ua: UnknownAtom) -> float:
        """Compute confidence in the pattern classification."""
        score = 0.0
        
        # Frequency bonus
        if ua.occurrence_count > 100:
            score += 0.3
        elif ua.occurrence_count > 10:
            score += 0.2
        elif ua.occurrence_count > 1:
            score += 0.1
        
        # Multi-file bonus
        if len(ua.files_seen_in) > 5:
            score += 0.2
        elif len(ua.files_seen_in) > 1:
            score += 0.1
        
        # Has behavior indicators
        if ua.behavior_indicators:
            score += 0.2
        
        # Has context
        if ua.context_indicators:
            score += 0.1
        
        # Has proposed classification
        if ua.proposed_name:
            score += 0.1
        
        return min(score, 1.0)
    
    def _merge_unknown(self, existing: UnknownAtom, new: UnknownAtom):
        """Merge a new unknown observation into existing."""
        existing.occurrence_count += new.occurrence_count
        existing.files_seen_in.update(new.files_seen_in)
        existing.repos_seen_in.update(new.repos_seen_in)
        existing.last_seen = new.last_seen
        
        # Merge samples
        for sample in new.code_samples:
            if sample not in existing.code_samples and len(existing.code_samples) < 5:
                existing.code_samples.append(sample)
        
        # Recalculate confidence
        existing.confidence_score = self._compute_confidence(existing)
    
    def get_taxonomy_candidates(self, min_occurrences: int = 10, min_confidence: float = 0.5) -> List[UnknownAtom]:
        """
        Get unknown patterns that are strong candidates for taxonomy inclusion.
        
        Criteria:
        - Appears frequently
        - Has high confidence classification
        - Has clear behavioral indicators
        """
        candidates = []
        for ua in self.unknown_registry.values():
            if ua.occurrence_count >= min_occurrences and ua.confidence_score >= min_confidence:
                candidates.append(ua)
        
        # Sort by confidence * frequency
        candidates.sort(key=lambda x: x.confidence_score * x.occurrence_count, reverse=True)
        return candidates
    
    def generate_discovery_report(self) -> str:
        """Generate a scientific report of all discoveries."""
        report = """# 🔬 Atom Discovery Report

## Executive Summary

This report documents patterns discovered during repository analysis that are NOT currently in the known atom taxonomy. These are candidates for taxonomy expansion based on empirical evidence.

## Methodology

1. Parse all source files using tree-sitter
2. Classify nodes against known atom taxonomy
3. Document unknown patterns with:
   - Structural signature (AST shape)
   - Behavioral indicators (what it does)
   - Context indicators (where it appears)
   - Frequency evidence (how often)
4. Propose classifications based on patterns

---

"""
        # Coverage summary
        if self.discovery_history:
            total_files = sum(r.files_analyzed for r in self.discovery_history)
            total_nodes = sum(r.total_nodes for r in self.discovery_history)
            total_known = sum(r.known_atoms for r in self.discovery_history)
            total_unknown = sum(r.unknown_atoms for r in self.discovery_history)
            coverage = total_known / total_nodes if total_nodes > 0 else 0
            
            report += f"""## Coverage Statistics

| Metric | Value |
|--------|-------|
| Repos Analyzed | {len(self.discovery_history)} |
| Files Analyzed | {total_files} |
| Total AST Nodes | {total_nodes:,} |
| Known Atoms | {total_known:,} ({coverage:.1%}) |
| Unknown Patterns | {total_unknown:,} ({1-coverage:.1%}) |
| Unique Unknown Types | {len(self.unknown_registry)} |

---

"""
        
        # Top candidates for taxonomy
        candidates = self.get_taxonomy_candidates(min_occurrences=5, min_confidence=0.3)
        
        if candidates:
            report += "## 🎯 Taxonomy Expansion Candidates\n\n"
            report += "Patterns with high frequency and confidence, recommended for inclusion:\n\n"
            
            for i, ua in enumerate(candidates[:20], 1):
                report += f"""### {i}. {ua.proposed_name or ua.ast_type}

| Property | Value |
|----------|-------|
| **AST Type** | `{ua.ast_type}` |
| **Occurrences** | {ua.occurrence_count:,} |
| **Files** | {len(ua.files_seen_in)} |
| **Confidence** | {ua.confidence_score:.2f} |
| **Proposed Continent** | {ua.proposed_continent or 'Unknown'} |
| **Proposed Fundamental** | {ua.proposed_fundamental or 'Unknown'} |

**Signature:** `{ua.ast_signature}`

**Sample:**
```python
{ua.code_samples[0][:150] if ua.code_samples else 'N/A'}
```

---

"""
        
        return report
    
    def export_unknown_registry(self, path: str):
        """Export the unknown registry to JSON for persistence."""
        data = {}
        for sig, ua in self.unknown_registry.items():
            data[sig] = {
                "signature_hash": ua.signature_hash,
                "ast_type": ua.ast_type,
                "ast_signature": ua.ast_signature,
                "behavior_indicators": ua.behavior_indicators,
                "context_indicators": ua.context_indicators,
                "occurrence_count": ua.occurrence_count,
                "files_seen_in": list(ua.files_seen_in),
                "repos_seen_in": list(ua.repos_seen_in),
                "code_samples": ua.code_samples,
                "locations": ua.locations[:10],
                "proposed_name": ua.proposed_name,
                "proposed_continent": ua.proposed_continent,
                "proposed_fundamental": ua.proposed_fundamental,
                "proposed_level": ua.proposed_level,
                "first_seen": ua.first_seen,
                "last_seen": ua.last_seen,
                "confidence_score": ua.confidence_score,
            }
        
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    print("=" * 70)
    print("🔬 DISCOVERY ENGINE — Self-Learning Atom Taxonomy")
    print("=" * 70)
    print()
    
    engine = DiscoveryEngine()
    
    # Test on dddpy
    dddpy_path = Path(__file__).parent / "validation" / "dddpy_real"
    
    if dddpy_path.exists():
        print(f"Analyzing: {dddpy_path}")
        print()
        
        report = engine.analyze_repo(str(dddpy_path), language="python")
        
        print(f"📊 Files analyzed: {report.files_analyzed}")
        print(f"📊 Total nodes: {report.total_nodes:,}")
        print(f"📊 Known atoms: {report.known_atoms:,} ({report.coverage_ratio:.1%})")
        print(f"📊 Unknown patterns: {report.unknown_atoms:,}")
        print(f"📊 Unique unknown types: {len(report.unknown_patterns)}")
        print()
        
        # Show top discoveries
        candidates = engine.get_taxonomy_candidates(min_occurrences=10, min_confidence=0.3)
        
        if candidates:
            print("🎯 TOP TAXONOMY CANDIDATES:")
            print("-" * 70)
            for i, ua in enumerate(candidates[:15], 1):
                print(f"{i:2}. {ua.proposed_name or ua.ast_type:25} | {ua.occurrence_count:5}x | conf={ua.confidence_score:.2f} | {ua.proposed_continent}")
        
        print()
        
        # Export
        output_path = Path(__file__).parent / "output" / "unknown_registry.json"
        output_path.parent.mkdir(exist_ok=True)
        engine.export_unknown_registry(str(output_path))
        print(f"💾 Unknown registry exported to: {output_path}")
        
        # Generate scientific report
        report_path = Path(__file__).parent / "output" / "discovery_report.md"
        report_content = engine.generate_discovery_report()
        report_path.write_text(report_content)
        print(f"📄 Discovery report generated: {report_path}")
        
    else:
        print(f"ERROR: dddpy fixture not found at {dddpy_path}")
