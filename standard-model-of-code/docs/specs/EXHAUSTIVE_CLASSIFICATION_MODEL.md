# Exhaustive Classification Model (ECM)

> **Status:** DRAFT
> **Date:** 2026-01-23
> **Insight:** If SIGNAL + NOISE = 100%, completeness is provable.

---

## The Core Theorem

```
For any source file F:

  |F| = Σ(SIGNAL) + Σ(NOISE)

Where:
  |F|          = Total tokens/bytes in file
  Σ(SIGNAL)    = Sum of tokens classified as particles
  Σ(NOISE)     = Sum of tokens classified as non-particles

If Σ(SIGNAL) + Σ(NOISE) = |F|, then classification is EXHAUSTIVE.
If exhaustive, then completeness is PROVABLE.
```

---

## Token Classification Taxonomy

Every token in a source file belongs to exactly ONE category:

### SIGNAL (Particles — What We Extract)

| Category | Symbol | Examples |
|----------|--------|----------|
| **Function Definition** | S.FN | `function foo()`, `const bar = () =>` |
| **Class Definition** | S.CL | `class MyClass`, `class extends Base` |
| **Variable Declaration** | S.VR | `const x`, `let y`, `var z` |
| **Method Definition** | S.MT | `myMethod()` inside class |
| **Module Export** | S.EX | `export function`, `module.exports` |
| **Interface/Type** | S.TY | `interface IFoo`, `type Bar =` |

### NOISE (Non-Particles — What We Explicitly Exclude)

| Category | Symbol | Examples | Confidence |
|----------|--------|----------|------------|
| **Whitespace** | N.WS | spaces, tabs, newlines | 100% |
| **Comments** | N.CM | `//`, `/* */`, `#` | 100% |
| **String Literals** | N.ST | `"hello"`, `'world'`, `` `template` `` | 100% |
| **Number Literals** | N.NM | `42`, `3.14`, `0xFF` | 100% |
| **Punctuation** | N.PN | `{}`, `[]`, `()`, `;`, `,` | 100% |
| **Operators** | N.OP | `+`, `-`, `=`, `===`, `=>` | 100% |
| **Keywords** | N.KW | `if`, `else`, `return`, `for` | 100% |
| **Import Statements** | N.IM | `import x from`, `require()` | 99% |
| **Built-in References** | N.BI | `console`, `window`, `Math` | 99% |
| **Function Calls** | N.FC | `foo()`, `bar.baz()` | 98% |
| **Property Access** | N.PA | `obj.prop`, `arr[0]` | 98% |
| **Control Flow** | N.CF | `if (cond)`, `for (;;)` | 100% |
| **Type Annotations** | N.TA | `: string`, `: number[]` | 100% |

### UNKNOWN (Gap — What We Can't Classify)

| Category | Symbol | Examples | Action |
|----------|--------|----------|--------|
| **Unrecognized Syntax** | U.SY | Novel language features | Research |
| **Dynamic Code** | U.DY | `eval()`, `new Function()` | Mark as blind spot |
| **Metaprogramming** | U.MP | Decorators, proxies | Enhance parser |

---

## The Completeness Equation

```
For each file F:

  Coverage(F) = (Σ SIGNAL + Σ NOISE) / |F|

  If Coverage(F) = 1.0:
    → EXHAUSTIVELY CLASSIFIED
    → Completeness is PROVEN for this file

  If Coverage(F) < 1.0:
    → GAP EXISTS
    → Gap size = |F| - (Σ SIGNAL + Σ NOISE)
    → Investigate the gap
```

---

## Implementation: Token-Level Classifier

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple
import tree_sitter

class TokenClass(Enum):
    # SIGNAL
    SIGNAL_FUNCTION = "S.FN"
    SIGNAL_CLASS = "S.CL"
    SIGNAL_VARIABLE = "S.VR"
    SIGNAL_METHOD = "S.MT"
    SIGNAL_EXPORT = "S.EX"
    SIGNAL_TYPE = "S.TY"

    # NOISE
    NOISE_WHITESPACE = "N.WS"
    NOISE_COMMENT = "N.CM"
    NOISE_STRING = "N.ST"
    NOISE_NUMBER = "N.NM"
    NOISE_PUNCTUATION = "N.PN"
    NOISE_OPERATOR = "N.OP"
    NOISE_KEYWORD = "N.KW"
    NOISE_IMPORT = "N.IM"
    NOISE_BUILTIN = "N.BI"
    NOISE_CALL = "N.FC"
    NOISE_PROPERTY = "N.PA"
    NOISE_CONTROL = "N.CF"
    NOISE_TYPE_ANN = "N.TA"

    # UNKNOWN
    UNKNOWN_SYNTAX = "U.SY"
    UNKNOWN_DYNAMIC = "U.DY"
    UNKNOWN_META = "U.MP"

@dataclass
class ClassifiedToken:
    start_byte: int
    end_byte: int
    text: str
    classification: TokenClass
    confidence: float

@dataclass
class ExhaustiveClassification:
    file_path: str
    total_bytes: int
    signal_bytes: int
    noise_bytes: int
    unknown_bytes: int
    coverage: float  # (signal + noise) / total
    is_exhaustive: bool  # coverage == 1.0
    tokens: List[ClassifiedToken]
    gaps: List[Tuple[int, int, str]]  # (start, end, unclassified_text)

def exhaustively_classify(file_path: str) -> ExhaustiveClassification:
    """
    Classify EVERY byte of a source file as either SIGNAL or NOISE.
    Any unclassified bytes are GAPS that need investigation.
    """
    with open(file_path, 'rb') as f:
        content = f.read()

    total_bytes = len(content)
    classified = [False] * total_bytes  # Track which bytes are classified
    tokens = []

    # Step 1: Parse with Tree-sitter to get AST
    tree = parse_file(file_path)

    # Step 2: Walk every node and classify
    def classify_node(node):
        start = node.start_byte
        end = node.end_byte
        node_type = node.type

        # SIGNAL: Definition nodes
        if node_type in SIGNAL_NODE_TYPES:
            classification = get_signal_class(node_type)
            tokens.append(ClassifiedToken(
                start_byte=start,
                end_byte=end,
                text=content[start:end].decode('utf-8', errors='replace'),
                classification=classification,
                confidence=0.99
            ))
            for i in range(start, end):
                if i < total_bytes:
                    classified[i] = True

        # NOISE: Non-definition nodes
        elif node_type in NOISE_NODE_TYPES:
            classification = get_noise_class(node_type)
            tokens.append(ClassifiedToken(
                start_byte=start,
                end_byte=end,
                text=content[start:end].decode('utf-8', errors='replace')[:50],
                classification=classification,
                confidence=0.99
            ))
            for i in range(start, end):
                if i < total_bytes:
                    classified[i] = True

        # Recurse into children
        for child in node.children:
            classify_node(child)

    classify_node(tree.root_node)

    # Step 3: Classify whitespace (bytes not in any AST node)
    # Tree-sitter AST doesn't include pure whitespace between tokens
    i = 0
    while i < total_bytes:
        if not classified[i]:
            # Check if it's whitespace
            byte = content[i:i+1]
            if byte in (b' ', b'\t', b'\n', b'\r'):
                # Find extent of whitespace
                ws_start = i
                while i < total_bytes and content[i:i+1] in (b' ', b'\t', b'\n', b'\r'):
                    classified[i] = True
                    i += 1
                tokens.append(ClassifiedToken(
                    start_byte=ws_start,
                    end_byte=i,
                    text="<whitespace>",
                    classification=TokenClass.NOISE_WHITESPACE,
                    confidence=1.0
                ))
            else:
                i += 1
        else:
            i += 1

    # Step 4: Identify gaps (unclassified bytes)
    gaps = []
    i = 0
    while i < total_bytes:
        if not classified[i]:
            gap_start = i
            while i < total_bytes and not classified[i]:
                i += 1
            gap_text = content[gap_start:i].decode('utf-8', errors='replace')
            gaps.append((gap_start, i, gap_text))
        else:
            i += 1

    # Step 5: Calculate metrics
    signal_bytes = sum(
        t.end_byte - t.start_byte
        for t in tokens
        if t.classification.value.startswith('S.')
    )
    noise_bytes = sum(
        t.end_byte - t.start_byte
        for t in tokens
        if t.classification.value.startswith('N.')
    )
    unknown_bytes = sum(end - start for start, end, _ in gaps)

    coverage = (signal_bytes + noise_bytes) / total_bytes if total_bytes > 0 else 1.0

    return ExhaustiveClassification(
        file_path=file_path,
        total_bytes=total_bytes,
        signal_bytes=signal_bytes,
        noise_bytes=noise_bytes,
        unknown_bytes=unknown_bytes,
        coverage=coverage,
        is_exhaustive=(coverage >= 0.9999),  # Allow for floating point
        tokens=tokens,
        gaps=gaps
    )

# Node type mappings
SIGNAL_NODE_TYPES = {
    'function_declaration',
    'function_expression',
    'arrow_function',
    'class_declaration',
    'class_expression',
    'method_definition',
    'variable_declarator',  # The name part of const x = ...
    'interface_declaration',
    'type_alias_declaration',
}

NOISE_NODE_TYPES = {
    'comment',
    'string',
    'template_string',
    'number',
    'regex',
    'true',
    'false',
    'null',
    'undefined',
    'import_statement',
    'export_statement',  # Just the keyword, not the definition
    'if_statement',
    'for_statement',
    'while_statement',
    'return_statement',
    'call_expression',
    'member_expression',
    'binary_expression',
    'unary_expression',
    'assignment_expression',
    'identifier',  # When used as reference, not definition
    # ... and many more
}
```

---

## The Completeness Proof

```
Given:
  File F with |F| = 1000 bytes

After exhaustive classification:
  SIGNAL bytes: 450 (function/class/variable definitions)
  NOISE bytes:  550 (whitespace, comments, keywords, calls, etc.)
  UNKNOWN:        0

  Coverage = (450 + 550) / 1000 = 1.0

Proof:
  Since Coverage = 1.0:
    Every byte is accounted for.
    No byte is left unclassified.
    Therefore, we have found ALL particles.

  If we missed a particle:
    Its bytes would be unclassified (UNKNOWN > 0).
    But UNKNOWN = 0.
    Therefore, we did not miss any particle.

  QED: Completeness is PROVEN for file F.
```

---

## The Signal-to-Noise Ratio

```
SNR = SIGNAL / NOISE

For typical source files:
  SNR ~= 0.3 to 0.5 (30-50% is definitions, rest is glue)

For minified files:
  SNR ~= 0.8+ (minimal whitespace/comments)

For test files:
  SNR ~= 0.2 (lots of setup, assertions, mocking)

SNR is a health metric:
  Very high SNR (>0.7) → Suspiciously dense, might be minified
  Very low SNR (<0.1) → Mostly boilerplate, might be generated
```

---

## Completeness Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│            EXHAUSTIVE CLASSIFICATION REPORT                 │
│                     viz/assets                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Files: 55/55 exhaustively classified (100%)                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SIGNAL    ████████████░░░░░░░░░░░░░░░  35%  (450KB) │   │
│  │ NOISE     ████████████████████████████  65%  (845KB) │   │
│  │ UNKNOWN   ░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%    (0KB) │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Coverage: 100.0%  ← COMPLETENESS PROVEN                    │
│                                                             │
│  SIGNAL breakdown:                                          │
│    Functions:  612 (76%)                                    │
│    Classes:     45 (6%)                                     │
│    Variables:  145 (18%)                                    │
│                                                             │
│  NOISE breakdown:                                           │
│    Whitespace: 312KB (37%)                                  │
│    Comments:    89KB (11%)                                  │
│    Strings:    156KB (18%)                                  │
│    Keywords:    78KB (9%)                                   │
│    Calls:      134KB (16%)                                  │
│    Other:       76KB (9%)                                   │
│                                                             │
│  ATTESTATION: L4 (PROVEN) ✓                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Edge Cases and Their Classification

| Pattern | Classification | Rationale |
|---------|---------------|-----------|
| `function foo() {}` | SIGNAL (S.FN) | Named function definition |
| `foo()` | NOISE (N.FC) | Function call, not definition |
| `const x = 1` | SIGNAL (S.VR) for `x`, NOISE for `= 1` | Declaration vs assignment |
| `// function fake()` | NOISE (N.CM) | It's a comment |
| `"function string()"` | NOISE (N.ST) | It's a string literal |
| `eval("code")` | NOISE (N.FC) | Call to eval; content is U.DY |
| `class A { m() {} }` | SIGNAL (S.CL) for class, (S.MT) for method | Nested signals |

---

## The Philosophical Implication

If SIGNAL + NOISE = 100%, then:

1. **Completeness becomes provable** — No byte is unaccounted for
2. **Gaps become visible** — UNKNOWN > 0 means we have a blind spot
3. **False negatives become impossible** — Either it's SIGNAL (found) or NOISE (explicitly not a particle)
4. **The CCI becomes exact** — Not an estimate, but a measurement

```
Traditional approach:
  "We found 802 particles. Did we miss any? Unknown."

Exhaustive classification:
  "We classified 100% of bytes. 802 are SIGNAL. 0 are UNKNOWN.
   Therefore, 802 is the COMPLETE set of particles."
```

---

## Implementation Status

| Task | Status | Notes |
|------|--------|-------|
| Define token taxonomy | ✅ DONE | 19 categories |
| Map Tree-sitter nodes to taxonomy | TODO | ~100 node types |
| Implement exhaustive classifier | TODO | Core algorithm |
| Handle whitespace gaps | TODO | Between AST nodes |
| Generate coverage report | TODO | Dashboard |
| Integrate with survey | TODO | Add to Stage 0 |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-01-23 | Initial draft |
