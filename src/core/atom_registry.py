#!/usr/bin/env python3
"""
Atom Registry — Canonical list of all known atoms in the taxonomy.

This is the SINGLE SOURCE OF TRUTH for:
- All known atoms (currently categorized)
- Their classification (category, fundamental, tier, composition)
- Discovery history (when added, from which repo)

The registry grows as we discover new patterns!

TERMINOLOGY (see docs/GLOSSARY.md):
- Tier: T0/T1/T2 - How UNIVERSAL is this atom (T0=all languages, T1=architectural, T2=ecosystem)
- Composition: atom/molecule/organelle - How COMPLEX is this pattern
- Category: Data/Logic/Organization/Execution - Which "continent" it belongs to
- Ring: Domain/App/Interface/Infra - Architectural position (Clean Architecture)
- Layer: Physical/Virtual/Semantic - The THREE PARALLEL PERSPECTIVES on Information
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class AtomDefinition:
    """A canonical atom in the taxonomy."""
    id: int                          # Unique ID (1-96 from original, 97+ are discoveries)
    name: str                        # PascalCase name (e.g., "PureFunction")
    ast_types: List[str]             # Tree-sitter node types that map to this
    category: str                    # Data Foundations, Logic & Flow, Organization, Execution
    fundamental: str                 # Bits, Variables, Functions, etc.
    tier: str                        # T0 (core), T1 (architectural), T2 (ecosystem)
    composition: str                 # atom, molecule, organelle (complexity level)
    description: str                 # What this atom represents
    detection_rule: str              # How to detect it

    # Discovery metadata
    source: str = "original"         # "original" or repo name where discovered
    discovered_at: str = ""          # ISO timestamp
    occurrence_count: int = 0        # Total times seen across all repos


class AtomRegistry:
    """
    The canonical registry of all known atoms.

    This grows over time as we discover new patterns.
    """

    def __init__(self):
        self.atoms: Dict[int, AtomDefinition] = {}
        self.ast_type_map: Dict[str, int] = {}  # node_type -> atom_id
        self.t2_atoms: Dict[str, Dict] = {}  # T2 string IDs (EXT.REACT.001) -> atom data
        self.ecosystem_patterns: Dict[str, Dict] = {}  # ecosystem -> detection patterns
        self.next_id: int = 118  # 117 canonical atoms + new discoveries start at 118
        self._init_canonical_atoms()
        self._load_t2_extensions()
    
    def _init_canonical_atoms(self):
        """Initialize with the original 96 + refined atoms."""
        
        # ═══════════════════════════════════════════════════════════════════
        # DATA FOUNDATIONS (Cyan) — IDs 1-20
        # ═══════════════════════════════════════════════════════════════════
        
        # Bits (1-4)
        self._add(1, "BitFlag", ["binary_expression"], "Data Foundations", "Bits", "atom",
                  "Bit operation with mask", "bit operation + constant mask")
        self._add(2, "BitMask", ["binary_literal"], "Data Foundations", "Bits", "atom",
                  "Binary literal value", "binary literal 0b...")
        
        # Primitives (5-12)
        self._add(5, "Boolean", ["true", "false"], "Data Foundations", "Primitives", "atom",
                  "Boolean true/false value", "type bool")
        self._add(6, "Integer", ["integer"], "Data Foundations", "Primitives", "atom",
                  "Integer numeric value", "integer type")
        self._add(7, "Float", ["float"], "Data Foundations", "Primitives", "atom",
                  "Floating point value", "float type")
        self._add(8, "StringLiteral", ["string", "concatenated_string"], "Data Foundations", "Primitives", "atom",
                  "String literal value", "string literal")
        self._add(9, "NoneLiteral", ["none"], "Data Foundations", "Primitives", "atom",
                  "None/null value", "None/null literal")
        self._add(10, "ListLiteral", ["list"], "Data Foundations", "Primitives", "atom",
                   "List literal []", "list brackets")
        self._add(11, "DictLiteral", ["dictionary"], "Data Foundations", "Primitives", "atom",
                   "Dictionary literal {}", "dict braces")
        self._add(12, "TupleLiteral", ["tuple"], "Data Foundations", "Primitives", "atom",
                   "Tuple literal ()", "tuple parens")
        
        # Variables (13-17)
        self._add(13, "LocalVar", ["identifier"], "Data Foundations", "Variables", "atom",
                  "Local variable reference", "local declaration")
        self._add(14, "Parameter", ["typed_parameter", "default_parameter"], "Data Foundations", "Variables", "atom",
                  "Function parameter", "function parameter")
        self._add(15, "InstanceField", ["attribute"], "Data Foundations", "Variables", "atom",
                  "Instance field access", "this/self field access")
        self._add(16, "IndexAccess", ["subscript"], "Data Foundations", "Variables", "atom",
                  "Array/dict index access", "bracket access")
        self._add(17, "SliceAccess", ["slice"], "Data Foundations", "Variables", "atom",
                  "Slice access [a:b]", "slice notation")
        
        # ═══════════════════════════════════════════════════════════════════
        # LOGIC & FLOW (Magenta) — IDs 18-50
        # ═══════════════════════════════════════════════════════════════════
        
        # Expressions (18-25)
        self._add(18, "BinaryExpr", ["binary_operator"], "Logic & Flow", "Expressions", "atom",
                  "Binary operation a + b", "arithmetic/bitwise ops")
        self._add(19, "UnaryExpr", ["unary_operator", "not_operator"], "Logic & Flow", "Expressions", "atom",
                  "Unary operation -x, !x", "unary prefix")
        self._add(20, "ComparisonExpr", ["comparison_operator"], "Logic & Flow", "Expressions", "atom",
                  "Comparison a == b", "comparison ops")
        self._add(21, "LogicalExpr", ["boolean_operator"], "Logic & Flow", "Expressions", "atom",
                  "Logical and/or", "boolean ops")
        self._add(22, "CallExpr", ["call"], "Logic & Flow", "Expressions", "atom",
                  "Function call f(x)", "function call")
        self._add(23, "TernaryExpr", ["conditional_expression"], "Logic & Flow", "Expressions", "atom",
                  "Ternary a ? b : c", "conditional expression")
        self._add(24, "Closure", ["lambda"], "Logic & Flow", "Expressions", "atom",
                  "Lambda/closure", "lambda keyword")
        self._add(25, "AwaitExpr", ["await"], "Logic & Flow", "Expressions", "atom",
                  "Await expression", "await keyword")
        
        # Statements (26-35)
        self._add(26, "Assignment", ["assignment"], "Logic & Flow", "Statements", "atom",
                  "Variable assignment", "= operator")
        self._add(27, "AugmentedAssignment", ["augmented_assignment"], "Logic & Flow", "Statements", "atom",
                  "Augmented assignment +=", "+= operator")
        self._add(28, "ExpressionStmt", ["expression_statement"], "Logic & Flow", "Statements", "atom",
                  "Standalone expression", "expression as statement")
        self._add(29, "ReturnStmt", ["return_statement"], "Logic & Flow", "Statements", "atom",
                  "Return statement", "return keyword")
        self._add(30, "RaiseStmt", ["raise_statement"], "Logic & Flow", "Statements", "atom",
                  "Raise/throw exception", "raise keyword")
        self._add(31, "AssertStmt", ["assert_statement"], "Logic & Flow", "Statements", "atom",
                  "Assert statement", "assert keyword")
        self._add(32, "PassStmt", ["pass_statement"], "Logic & Flow", "Statements", "atom",
                  "Pass/no-op statement", "pass keyword")
        self._add(33, "BreakStmt", ["break_statement"], "Logic & Flow", "Statements", "atom",
                  "Break loop", "break keyword")
        self._add(34, "ContinueStmt", ["continue_statement"], "Logic & Flow", "Statements", "atom",
                  "Continue loop", "continue keyword")
        self._add(35, "DeleteStmt", ["delete_statement"], "Logic & Flow", "Statements", "atom",
                  "Delete statement", "del keyword")
        
        # Control Structures (36-45)
        self._add(36, "IfBranch", ["if_statement"], "Logic & Flow", "Control Structures", "atom",
                  "If conditional", "if/else")
        self._add(37, "ElifBranch", ["elif_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Elif branch", "elif keyword")
        self._add(38, "ElseBranch", ["else_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Else branch", "else keyword")
        self._add(39, "LoopFor", ["for_statement"], "Logic & Flow", "Control Structures", "atom",
                  "For loop", "for loop")
        self._add(40, "LoopWhile", ["while_statement"], "Logic & Flow", "Control Structures", "atom",
                  "While loop", "while loop")
        self._add(41, "TryCatch", ["try_statement"], "Logic & Flow", "Control Structures", "atom",
                  "Try/catch block", "try/except")
        self._add(42, "ExceptHandler", ["except_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Exception handler", "except clause")
        self._add(43, "FinallyBlock", ["finally_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Finally block", "finally clause")
        self._add(44, "ContextManager", ["with_statement"], "Logic & Flow", "Control Structures", "atom",
                  "With context manager", "with statement")
        self._add(45, "PatternMatch", ["match_statement", "case_clause"], "Logic & Flow", "Control Structures", "atom",
                  "Pattern matching", "match/case")
        
        # Functions (46-55)
        self._add(46, "Function", ["function_definition"], "Logic & Flow", "Functions", "molecule",
                  "Function definition", "def keyword")
        self._add(47, "AsyncFunction", ["async_function_definition"], "Logic & Flow", "Functions", "molecule",
                  "Async function", "async def")
        self._add(48, "DecoratedFunction", ["decorated_definition"], "Logic & Flow", "Functions", "molecule",
                  "Decorated function", "@decorator")
        self._add(49, "Generator", ["generator_expression"], "Logic & Flow", "Functions", "molecule",
                  "Generator expression", "yield keyword")
        self._add(50, "ListComprehension", ["list_comprehension"], "Logic & Flow", "Functions", "atom",
                  "List comprehension", "[x for x in]")
        self._add(51, "DictComprehension", ["dictionary_comprehension"], "Logic & Flow", "Functions", "atom",
                  "Dict comprehension", "{k:v for}")
        self._add(52, "SetComprehension", ["set_comprehension"], "Logic & Flow", "Functions", "atom",
                  "Set comprehension", "{x for x}")
        self._add(53, "Decorator", ["decorator"], "Logic & Flow", "Functions", "atom",
                  "Decorator", "@symbol")
        self._add(54, "ParameterList", ["parameters"], "Logic & Flow", "Functions", "atom",
                  "Parameter list", "(params)")
        self._add(55, "ArgumentList", ["argument_list"], "Logic & Flow", "Functions", "atom",
                  "Argument list", "(args)")
        
        # ═══════════════════════════════════════════════════════════════════
        # ORGANIZATION (Green) — IDs 56-75
        # ═══════════════════════════════════════════════════════════════════
        
        # Aggregates (56-65)
        self._add(56, "Class", ["class_definition"], "Organization", "Aggregates", "molecule",
                  "Class definition", "class keyword")
        self._add(57, "ValueObject", [], "Organization", "Aggregates", "molecule",
                  "Immutable value type", "class immutable + no id")
        self._add(58, "Entity", [], "Organization", "Aggregates", "molecule",
                  "Entity with identity", "class with id field")
        self._add(59, "AggregateRoot", [], "Organization", "Aggregates", "organelle",
                  "Aggregate root", "raises domain events")
        self._add(60, "DTO", [], "Organization", "Aggregates", "molecule",
                  "Data transfer object", "data-only class")
        self._add(61, "Factory", [], "Organization", "Aggregates", "molecule",
                  "Factory class/method", "static create method")
        
        # Modules (66-75)
        self._add(66, "Import", ["import_statement"], "Organization", "Modules", "atom",
                  "Import statement", "import keyword")
        self._add(67, "ImportFrom", ["import_from_statement"], "Organization", "Modules", "atom",
                  "From import", "from x import y")
        self._add(68, "ImportAlias", ["aliased_import"], "Organization", "Modules", "atom",
                  "Import alias", "import as")
        self._add(69, "DottedName", ["dotted_name"], "Organization", "Modules", "atom",
                  "Dotted module path", "a.b.c")
        self._add(70, "Comment", ["comment"], "Organization", "Files", "atom",
                  "Code comment", "# or //")
        
        # Types (71-75)
        self._add(71, "TypeAnnotation", ["type"], "Organization", "Types", "atom",
                  "Type annotation", ": Type")
        self._add(72, "GenericType", ["generic_type"], "Organization", "Types", "atom",
                  "Generic type", "List[T]")
        self._add(73, "UnionType", ["union_type"], "Organization", "Types", "atom",
                  "Union type", "A | B")
        self._add(74, "KeywordArg", ["keyword_argument"], "Organization", "Types", "atom",
                  "Keyword argument", "key=value")
        
        # ═══════════════════════════════════════════════════════════════════
        # EXECUTION (Amber) — IDs 76-96  [T1 Architectural Patterns]
        # ═══════════════════════════════════════════════════════════════════

        # (These are T1 architectural patterns - appear across many codebases but not universal)
        self._add(76, "MainEntry", [], "Execution", "Executables", "organelle",
                  "Main entry point", "if __name__", tier="T1")
        self._add(77, "APIHandler", [], "Execution", "Executables", "organelle",
                  "API route handler", "@app.get/post", tier="T1")
        self._add(78, "CommandHandler", [], "Execution", "Executables", "organelle",
                  "Command handler (CQRS)", "handles *Command", tier="T1")
        self._add(79, "QueryHandler", [], "Execution", "Executables", "organelle",
                  "Query handler (CQRS)", "handles *Query", tier="T1")
        self._add(80, "EventHandler", [], "Execution", "Executables", "organelle",
                  "Event handler", "@Subscribe", tier="T1")
        self._add(81, "Middleware", [], "Execution", "Executables", "organelle",
                  "Middleware function", "calls next()", tier="T1")
        self._add(82, "Validator", [], "Execution", "Executables", "organelle",
                  "Validation function", "validate* + throws", tier="T1")
        self._add(83, "Repository", [], "Execution", "Executables", "organelle",
                  "Repository pattern", "save/find methods", tier="T1")
        self._add(84, "UseCase", [], "Execution", "Executables", "organelle",
                  "Use case handler", "single execute method", tier="T1")

        # ═══════════════════════════════════════════════════════════════════
        # NEW ATOMS (v3.0.0) — IDs 85-99  [Mixed T0/T1/T2]
        # ═══════════════════════════════════════════════════════════════════

        # Data - New Primitives (85-88) - T0 (universal types)
        self._add(85, "UUID", ["uuid"], "Data Foundations", "Primitives", "atom",
                  "Unique identifier value", "uuid type or import")  # T0 default
        self._add(86, "Timestamp", ["datetime"], "Data Foundations", "Primitives", "atom",
                  "Date/time value", "datetime type")  # T0 default
        self._add(87, "Duration", ["timedelta"], "Data Foundations", "Primitives", "atom",
                  "Time duration/interval", "timedelta type")  # T0 default
        self._add(88, "SecretVar", [], "Data Foundations", "Variables", "atom",
                  "Sensitive credential/secret", "secret/password/key pattern", tier="T1")

        # Logic - New Functions (89-92) - T1 (architectural patterns)
        self._add(89, "RetryFunction", [], "Logic & Flow", "Functions", "molecule",
                  "Function with retry/backoff logic", "retry decorator or loop", tier="T1")
        self._add(90, "CachedFunction", [], "Logic & Flow", "Functions", "molecule",
                  "Memoized/cached function", "@cache/@lru_cache", tier="T1")
        self._add(91, "Saga", [], "Logic & Flow", "Functions", "organelle",
                  "Distributed transaction coordinator", "compensating actions", tier="T1")
        self._add(92, "Pipeline", [], "Logic & Flow", "Functions", "molecule",
                  "Composable transformation chain", "pipe pattern", tier="T1")

        # Organization - New Services (93-95) - T1 (architectural patterns)
        self._add(93, "Cache", [], "Organization", "Services", "molecule",
                  "Caching abstraction", "cache get/set methods", tier="T1")
        self._add(94, "EventBus", [], "Organization", "Services", "organelle",
                  "Event publishing/subscription", "publish/subscribe pattern", tier="T1")
        self._add(95, "MessageBroker", [], "Organization", "Services", "organelle",
                  "Message queue abstraction", "queue/topic pattern", tier="T1")

        # Execution - New Handlers/Probes (96-99) - T1/T2 (some ecosystem-specific)
        self._add(96, "SSEHandler", [], "Execution", "Executables", "organelle",
                  "Server-sent events stream", "event stream pattern", tier="T1")
        self._add(97, "gRPCHandler", [], "Execution", "Executables", "organelle",
                  "gRPC service method", "grpc stub/service", tier="T2")  # gRPC ecosystem
        self._add(98, "ChaosProbe", [], "Execution", "Executables", "organelle",
                  "Chaos engineering fault injection", "chaos/fault injection", tier="T2")  # DevOps ecosystem
        self._add(99, "CanaryCheck", [], "Execution", "Executables", "organelle",
                  "Canary deployment validator", "canary/gradual rollout", tier="T2")  # DevOps ecosystem

        # ═══════════════════════════════════════════════════════════════════
        # FINAL 18 ATOMS (v3.0.0 Completeness) — IDs 100-117  [Mixed T0/T1/T2]
        # ═══════════════════════════════════════════════════════════════════

        # Data - New Structures (100-102)
        self._add(100, "Blob", ["blob"], "Data Foundations", "Bytes", "atom",
                  "Binary large object", "blob/binary type")  # T0 default
        self._add(101, "Tensor", ["tensor"], "Data Foundations", "Primitives", "atom",
                  "Multi-dimensional array", "tensor type", tier="T2")  # ML ecosystem
        self._add(102, "Coordinate", ["coordinate"], "Data Foundations", "Primitives", "atom",
                  "Geo/spatial coordinate", "lat/long pair", tier="T2")  # GIS ecosystem

        # Organization - Aggregates (103-108) - T1 (data structures are architectural)
        self._add(103, "GraphNode", [], "Organization", "Aggregates", "molecule",
                  "Graph vertex", "node/vertex class", tier="T1")
        self._add(104, "GraphEdge", [], "Organization", "Aggregates", "molecule",
                  "Graph connection", "edge/link class", tier="T1")
        self._add(105, "Tree", [], "Organization", "Aggregates", "molecule",
                  "Hierarchical structure", "tree class", tier="T1")
        self._add(106, "Stack", [], "Organization", "Aggregates", "molecule",
                  "LIFO collection", "stack class", tier="T1")
        self._add(107, "Queue", [], "Organization", "Aggregates", "molecule",
                  "FIFO collection", "queue class", tier="T1")
        self._add(108, "LinkedList", [], "Organization", "Aggregates", "molecule",
                  "Linked node sequence", "linked list class", tier="T1")

        # Logic - Functions & Control (109-114) - T1 (functional patterns)
        self._add(109, "ThrottledFunction", [], "Logic & Flow", "Functions", "molecule",
                  "Rate-limited execution", "throttle wrapper", tier="T1")
        self._add(110, "DebouncedFunction", [], "Logic & Flow", "Functions", "molecule",
                  "Delayed execution", "debounce wrapper", tier="T1")
        self._add(111, "CurriedFunction", [], "Logic & Flow", "Functions", "molecule",
                  "Partial application", "curry wrapper", tier="T1")
        self._add(112, "LazyFunction", [], "Logic & Flow", "Functions", "molecule",
                  "Evaluation on demand", "lazy wrapper", tier="T1")
        self._add(113, "DeferStmt", [], "Logic & Flow", "Statements", "atom",
                  "Deferred execution", "defer keyword")  # T0 (Go has this)
        self._add(114, "GotoStmt", [], "Logic & Flow", "Statements", "atom",
                  "Unconditional jump", "goto keyword")  # T0 (many languages have this)

        # Logic/Execution - New Patterns (115-117)
        self._add(115, "PipelineStep", [], "Logic & Flow", "Functions", "atom",
                  "Step in a pipeline", "pipeline stage", tier="T1")
        self._add(116, "Sidecar", [], "Execution", "Workers", "organelle",
                  "Auxiliary container process", "sidecar pattern", tier="T2")  # K8s ecosystem
        self._add(117, "ReplicaSet", [], "Execution", "Workers", "organelle",
                  "Redundant process set", "replica set configuration", tier="T2")  # K8s ecosystem

    def _load_t2_extensions(self):
        """Load T2 ecosystem-specific atoms from schema/atoms/extensions/*.json"""
        extensions_dir = Path(__file__).parent.parent.parent / "schema" / "atoms" / "extensions"

        if not extensions_dir.exists():
            return

        # Detection patterns for each ecosystem
        self.ecosystem_patterns = {
            "react": {
                "imports": ["react", "react-dom", "react-native"],
                "file_patterns": [".js", ".jsx", ".ts", ".tsx"],
                "code_patterns": {
                    # Functional Component - any function returning JSX
                    "EXT.REACT.001": ["function", "return", "<", "/>"],  
                    # Class Component
                    "EXT.REACT.002": ["class", "extends", "React.Component"],  
                    # Hooks - require parentheses to avoid substring false positives
                    "EXT.REACT.005": ["useState("],
                    "EXT.REACT.006": ["useEffect("],
                    "EXT.REACT.007": ["useContext("],
                    "EXT.REACT.008": ["useMemo("],
                    "EXT.REACT.009": ["useCallback("],
                    "EXT.REACT.010": ["useRef("],
                    "EXT.REACT.011": ["useReducer("],
                    # Context
                    "EXT.REACT.015": ["createContext", "Context.Provider"],
                    # Portal
                    "EXT.REACT.016": ["createPortal"],
                    # Suspense
                    "EXT.REACT.017": ["Suspense"],
                    # Error Boundary
                    "EXT.REACT.018": ["componentDidCatch", "getDerivedStateFromError"],
                    # Fragment
                    "EXT.REACT.019": ["Fragment", "<>"],
                }
            },
            "ml": {
                "imports": ["tensorflow", "torch", "pytorch", "keras", "sklearn", "numpy", "pandas"],
                "file_patterns": [".py"],
                "code_patterns": {
                    # EXT.ML.001: Model/Forward Pass - neural network model definition
                    "EXT.ML.001": [
                        "torch.nn.Module", "tf.keras.Model", "nn.Module",  # Model class
                        "def forward(", "(Module)",  # Forward pass method (with paren to avoid false matches)
                        "F.relu(", "F.softmax(", "F.log_softmax(",  # Functional activations
                        "F.max_pool2d(", "F.avg_pool2d(", "F.dropout(",  # Functional layers (with paren)
                    ],
                    # EXT.ML.002: Layer Definition - neural network layers
                    "EXT.ML.002": [
                        "nn.Linear", "nn.Conv2d", "nn.Conv1d", "nn.LSTM", "nn.GRU",
                        "nn.Dropout", "nn.BatchNorm", "nn.LayerNorm",
                        "Dense", "torch.nn.Linear",  # Keras/verbose
                    ],
                    # EXT.ML.003: Backpropagation - gradient computation
                    "EXT.ML.003": [
                        "backward", "loss.backward", ".backward()",
                        "zero_grad", "optimizer.step",
                    ],
                    # EXT.ML.004: Data Pipeline - dataset and loading
                    "EXT.ML.004": [
                        "Dataset", "DataLoader", "torch.utils.data",
                        ".dataset", "train_loader", "test_loader",
                    ],
                    # EXT.ML.005: Training/Eval Loop - training workflow
                    "EXT.ML.005": [
                        "model.train()", ".train()", "model.eval()", ".eval()",
                        "train_test_split", "fit", "epochs",
                    ],
                    # EXT.ML.006: Optimizer - optimization algorithms
                    "EXT.ML.006": [
                        "optim.SGD", "optim.Adam", "optim.AdamW", "optim.Adadelta",
                        "optimizer", "learning_rate", "lr=",
                    ],
                    # EXT.ML.007: Loss Function - loss computation
                    "EXT.ML.007": [
                        "nn.CrossEntropy", "nn.MSELoss", "nn.BCELoss",
                        "F.nll_loss", "F.cross_entropy", "F.mse_loss",
                        "loss =", "criterion",
                    ],
                    # EXT.ML.008: Tensor Operations - tensor manipulation
                    "EXT.ML.008": [
                        "torch.tensor", "torch.zeros", "torch.ones", "torch.randn",
                        "torch.flatten", "torch.cat", "torch.stack",
                        ".to(device)", ".cuda()", ".cpu()",
                    ],
                }
            },
            "kubernetes": {
                "imports": ["kubernetes", "k8s"],
                "file_patterns": [".yaml", ".yml"],
                "code_patterns": {
                    "EXT.K8S.001": ["kind: Pod", "apiVersion:"],  # Pod
                    "EXT.K8S.002": ["kind: Deployment"],  # Deployment
                    "EXT.K8S.003": ["kind: Service"],  # Service
                    "EXT.K8S.004": ["kind: ConfigMap"],  # ConfigMap
                }
            },
            "functional": {
                "imports": ["functools", "itertools", "toolz", "funcy"],
                "file_patterns": [".py", ".hs", ".ml", ".scala"],
                "code_patterns": {
                    # Patterns use ANY match (at least one keyword present)
                    "EXT.FP.001": ["reduce"],  # Reduce (single keyword)
                    "EXT.FP.002": ["partial"],  # Partial application
                    "EXT.FP.003": ["compose"],  # Compose
                    "EXT.FP.004": ["Maybe"],  # Maybe monad
                    "EXT.FP.005": ["Either"],  # Either monad
                    "EXT.FP.006": ["pipe"],  # Pipe
                }
            },
            "rust": {
                "imports": ["std", "tokio", "serde", "actix", "async-std"],  # Common crates
                "file_patterns": [".rs"],
                "code_patterns": {
                    # Struct - data aggregate (detected by symbol_kind or code)
                    "EXT.RUST.001": ["struct"],
                    # Trait - interface definition
                    "EXT.RUST.002": ["trait"],
                    # Impl - implementation block
                    "EXT.RUST.003": ["impl"],
                    # Async - async functions/blocks
                    "EXT.RUST.004": ["async fn", ".await"],
                    # Result handling - error handling pattern
                    "EXT.RUST.005": ["Result<", "Ok(", "Err("],
                    # Option handling - optional values
                    "EXT.RUST.006": ["Option<", "Some(", "None"],
                    # Unsafe block
                    "EXT.RUST.007": ["unsafe"],
                    # Lifetime annotations
                    "EXT.RUST.008": ["'a", "'static", "lifetime"],
                    # Ownership - smart pointers
                    "EXT.RUST.009": ["Box<", "Rc<", "Arc<", "RefCell<"],
                    # Enum - algebraic data type
                    "EXT.RUST.010": ["enum"],
                }
            }
        }

        # Load T2 atom definitions from JSON files
        for json_file in extensions_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)

                pack_id = data.get("pack_id", json_file.stem)
                atoms = data.get("atoms", [])

                for atom in atoms:
                    atom_id = atom.get("id", "")
                    self.t2_atoms[atom_id] = {
                        "id": atom_id,
                        "name": atom.get("name", ""),
                        "description": atom.get("description", ""),
                        "pack": pack_id,
                        "tier": "T2"
                    }
            except Exception:
                pass  # Skip malformed files

    def detect_ecosystem(self, file_path: str, imports: List[str] = None, content: str = "") -> Optional[str]:
        """Detect which ecosystem a file belongs to based on imports and patterns."""
        imports = imports or []
        file_path_lower = file_path.lower()
        content_lower = content.lower()

        for ecosystem, patterns in self.ecosystem_patterns.items():
            # print(f"DEBUG: Checking {ecosystem} against {file_path}")
            # Check file extension (React: .jsx, .tsx)
            file_exts = patterns.get("file_patterns", [])
            if any(file_path_lower.endswith(ext) for ext in file_exts):
                # Only return for non-Python ecosystems by extension
                if ecosystem in ["react", "rust", "kubernetes"]:
                    return ecosystem

            # Check explicit imports list
            if any(imp in imports for imp in patterns.get("imports", [])):
                return ecosystem

            # Check content for import statements (flexible matching)
            for imp in patterns.get("imports", []):
                imp_lower = imp.lower()
                if f"import {imp_lower}" in content_lower or f"from {imp_lower}" in content_lower:
                    # print(f"DEBUG: Detected ecosystem {ecosystem} for {file_path}")
                    return ecosystem
            
            # Special check for React without imports (JSX presence)
            if ecosystem == "react" and ("<div" in content_lower or "/>" in content_lower):
                 return ecosystem

        return None

    def detect_t2_atom(self, ecosystem: str, body_source: str, name: str = "") -> Optional[str]:
        """Detect specific T2 atom based on code patterns.

        Returns the first matching T2 atom ID, or None if no match.
        Checks both body_source and function name for pattern matches.
        """
        if ecosystem not in self.ecosystem_patterns:
            return None

        patterns = self.ecosystem_patterns[ecosystem].get("code_patterns", {})
        combined = f"{name} {body_source}"  # Check both name and body

        for atom_id, keywords in patterns.items():
            # Match if ALL keywords are found (precise)
            if all(kw.lower() in combined.lower() for kw in keywords):
                # print(f"DEBUG: Detected T2 atom {atom_id} for ecosystem {ecosystem}.")
                return atom_id

        # print(f"DEBUG: No T2 atom detected for ecosystem {ecosystem} with provided source.")
        return None

    def get_t2_atom(self, atom_id: str) -> Optional[Dict]:
        """Get T2 atom definition by string ID."""
        return self.t2_atoms.get(atom_id)

    def _add(self, id: int, name: str, ast_types: List[str], category: str,
             fundamental: str, composition: str, description: str, detection_rule: str,
             tier: str = "T0"):
        """Add an atom to the registry.

        Args:
            tier: T0 (universal/core), T1 (architectural), T2 (ecosystem-specific)
            composition: atom (simple), molecule (composite), organelle (complex)
        """
        atom = AtomDefinition(
            id=id, name=name, ast_types=ast_types, category=category,
            fundamental=fundamental, tier=tier, composition=composition,
            description=description, detection_rule=detection_rule, source="original"
        )
        self.atoms[id] = atom

        # Map AST types to this atom
        for ast_type in ast_types:
            self.ast_type_map[ast_type] = id
    
    def add_discovery(self, name: str, ast_types: List[str], category: str,
                      fundamental: str, composition: str, description: str,
                      detection_rule: str, source_repo: str, tier: str = "T2") -> int:
        """Add a newly discovered atom to the registry.

        Discovered atoms default to T2 (ecosystem-specific) until validated
        for broader applicability.
        """
        atom = AtomDefinition(
            id=self.next_id,
            name=name,
            ast_types=ast_types,
            category=category,
            fundamental=fundamental,
            tier=tier,
            composition=composition,
            description=description,
            detection_rule=detection_rule,
            source=source_repo,
            discovered_at=datetime.now().isoformat()
        )
        self.atoms[self.next_id] = atom

        for ast_type in ast_types:
            self.ast_type_map[ast_type] = self.next_id

        self.next_id += 1
        return atom.id
    
    def get_by_ast_type(self, ast_type: str) -> Optional[AtomDefinition]:
        """Get atom definition by AST node type."""
        if ast_type in self.ast_type_map:
            return self.atoms[self.ast_type_map[ast_type]]
        return None
    
    def get_stats(self) -> Dict:
        """Get registry statistics."""
        by_category = {}
        by_fundamental = {}
        by_tier = {}
        by_composition = {}
        by_source = {"original": 0, "discovered": 0}

        for atom in self.atoms.values():
            by_category[atom.category] = by_category.get(atom.category, 0) + 1
            by_fundamental[atom.fundamental] = by_fundamental.get(atom.fundamental, 0) + 1
            by_tier[atom.tier] = by_tier.get(atom.tier, 0) + 1
            by_composition[atom.composition] = by_composition.get(atom.composition, 0) + 1
            if atom.source == "original":
                by_source["original"] += 1
            else:
                by_source["discovered"] += 1

        return {
            "total_atoms": len(self.atoms),
            "ast_types_mapped": len(self.ast_type_map),
            "by_category": by_category,
            "by_fundamental": by_fundamental,
            "by_tier": by_tier,
            "by_composition": by_composition,
            "by_source": by_source,
            "next_id": self.next_id,
        }
    
    def export_canon(self, path: str):
        """Export the canonical registry to JSON."""
        data = {
            "version": "2.0",  # Version bump for new terminology
            "timestamp": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "atoms": {
                str(id): {
                    "id": atom.id,
                    "name": atom.name,
                    "ast_types": atom.ast_types,
                    "category": atom.category,
                    "fundamental": atom.fundamental,
                    "tier": atom.tier,
                    "composition": atom.composition,
                    "description": atom.description,
                    "detection_rule": atom.detection_rule,
                    "source": atom.source,
                    "discovered_at": atom.discovered_at,
                } for id, atom in self.atoms.items()
            }
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_summary(self):
        """Print a summary of the registry."""
        stats = self.get_stats()

        print("=" * 70)
        print("ATOM REGISTRY - Canonical Taxonomy v2.0")
        print("=" * 70)
        print()
        print(f"Total Atoms: {stats['total_atoms']}")
        print(f"AST Types Mapped: {stats['ast_types_mapped']}")
        print(f"Original (96 base): {stats['by_source']['original']}")
        print(f"Discovered: {stats['by_source']['discovered']}")
        print()

        print("By Tier (Universality):")
        tier_order = ["T0", "T1", "T2"]
        for tier in tier_order:
            count = stats['by_tier'].get(tier, 0)
            bar = "=" * min(count // 2, 30)
            label = {"T0": "Core (universal)", "T1": "Architectural", "T2": "Ecosystem"}.get(tier, tier)
            print(f"  {tier} {label:20} {count:3} {bar}")
        print()

        print("By Category:")
        for category, count in sorted(stats['by_category'].items(), key=lambda x: -x[1]):
            bar = "=" * min(count // 2, 30)
            print(f"  {category:20} {count:3} {bar}")
        print()

        print("By Composition (Complexity):")
        for comp, count in sorted(stats['by_composition'].items(), key=lambda x: -x[1]):
            bar = "=" * min(count, 30)
            print(f"  {comp:12} {count:3} {bar}")
        print()

        print("By Fundamental:")
        for fund, count in sorted(stats['by_fundamental'].items(), key=lambda x: -x[1])[:10]:
            bar = "=" * min(count, 30)
            print(f"  {fund:20} {count:3} {bar}")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    registry = AtomRegistry()
    registry.print_summary()
    
    # Export canonical registry
    output_path = Path(__file__).parent.parent / "output" / "atom_registry_canon.json"
    output_path.parent.mkdir(exist_ok=True)
    registry.export_canon(str(output_path))
    print()
    print(f"💾 Exported to: {output_path}")
