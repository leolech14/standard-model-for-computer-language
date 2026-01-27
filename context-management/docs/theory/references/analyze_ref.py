#!/usr/bin/env python3
"""
Analyze a single reference and generate SMoC-specific metadata.

This script takes a reference ID, reads the enhanced TXT file,
and uses an LLM to generate structured SMoC relevance analysis.
"""

import json
import sys
from pathlib import Path

REFS_DIR = Path(__file__).parent.absolute()
TXT_DIR = REFS_DIR / "txt"
METADATA_DIR = REFS_DIR / "metadata"

# SMoC Core Concepts (for analysis guidance)
SMOC_CORE_CONCEPTS = """
Standard Model of Code (SMoC) Core Constructs:

1. CODOME ⊔ CONTEXTOME PARTITION
   - Mathematically necessary separation (Lawvere's Fixed-Point Theorem)
   - Executable code vs non-executable documentation
   - Truth about L₀ (code) can only be defined in L₁ (docs)

2. ATOMS (167+ semantic types)
   - Structural primitives: Function, Class, Variable, Module, etc.
   - Compositional hierarchy with type safety

3. ROLES (33 canonical)
   - Purpose-based classification: Repository, Entity, Service, Utility, etc.
   - WHY vs WHAT distinction

4. LAYERS (architectural strata)
   - Presentation, Application, Domain, Infrastructure, Foundation

5. SCALES (16-level hierarchy)
   - Bit → Byte → Line → Block → Function → File → Package → Module → Library → Framework → Application → Ecosystem → Platform → Paradigm → Discipline → Universe
   - Holon hierarchy: each level is whole AND part

6. DIMENSIONS (8 faceted classification)
   - Purpose, Mutability, Essence, Scope, Temporality, etc.

7. PURPOSE FIELD DYNAMICS
   - d𝒫/dt = -∇Incoherence(𝕮)
   - Code evolves to resolve incoherence
   - Free Energy Principle application

8. CONSTRUCTAL LAW
   - Code structures evolve to optimize flow (data, control, dependencies)
   - From spaghetti → layers

9. RENORMALIZATION GROUP FLOW
   - Properties wash out at higher scales
   - "Focusing Funnel" from details → unified purpose

10. TOPOLOGICAL INVARIANTS
    - Betti numbers: b₀ (components), b₁ (cycles)
    - Euler characteristic, spectral centrality

11. OBSERVABILITY TRIAD (Peircean)
    - Firstness (potential), Secondness (actual), Thirdness (mediation)
    - Three observers for complete observation

12. STONE TOOL PRINCIPLE
    - AI-native tooling (Affordances for AI agents, not humans)
    - Tools shaped for their consumer

13. CATEGORICAL STRUCTURE
    - Code → Graph as forgetful functor
    - Graph → Code as free construction (adjoint)
    - Yoneda embedding

14. GRAPH HEALTH METRICS
    - Dead code detection, cycle analysis
    - Landscape Health Index

15. EXTENDED MIND / DISTRIBUTED COGNITION
    - Documentation as external memory
    - Tools as cognitive prosthesis
"""


def generate_analysis_prompt(ref_id: str, txt_content: str, metadata_stub: dict) -> str:
    """Generate LLM prompt for SMoC relevance analysis."""
    title = metadata_stub.get("title", "Unknown")
    author = metadata_stub["authors"][0] if metadata_stub.get("authors") else "Unknown"
    year = metadata_stub.get("year", "Unknown")

    # Truncate text if too long (keep first 100K chars for analysis)
    text_sample = txt_content[:100000]
    if len(txt_content) > 100000:
        text_sample += f"\n\n[...TRUNCATED: {len(txt_content) - 100000:,} additional characters...]"

    prompt = f"""You are analyzing academic work for the Standard Model of Code (SMoC) reference library.

REFERENCE: {ref_id}
TITLE: {title}
AUTHOR: {author}
YEAR: {year}

{SMOC_CORE_CONCEPTS}

===== FULL TEXT =====
{text_sample}
===== END TEXT =====

Generate structured JSON metadata following this exact format:

{{
  "summary": "300-500 word neutral summary of this work's main contribution",

  "smoc_relevance_summary": "400-600 word analysis of WHY this work matters to SMoC. Be SPECIFIC about which SMoC constructs it informs. Examples:
- How does it relate to CODOME/CONTEXTOME partition?
- Does it inform atoms, roles, layers, or scales?
- How does it connect to purpose field dynamics or constructal flows?
- Does it provide mathematical foundation (category theory, topology)?
- How does it inform observability, tooling, or AI-native design?",

  "key_smoc_concepts": [
    {{
      "smoc_concept": "codome_contextome_partition",
      "paper_concept": "Name as appears in paper",
      "mapping": "150-300 words explaining the connection",
      "quotes_or_pages": ["Direct quote or page reference"],
      "strength": "foundational|strong|moderate|tangential"
    }}
  ],

  "important_figures": [
    {{
      "image_path": "images/{ref_id}/fig_page_XXX_YYY.png",
      "page": 42,
      "description": "What the figure shows",
      "smoc_relevance": "Why this is crucial for SMoC (e.g., visualizes holon hierarchy, shows categorical adjunction)"
    }}
  ],

  "important_equations": [
    {{
      "equation": "LaTeX or plain text",
      "page": 15,
      "description": "What it means",
      "smoc_mapping": "How this maps to SMoC (e.g., 'This is the free energy formulation that becomes d𝒫/dt = -∇Incoherence')"
    }}
  ],

  "cross_references": ["REF-001", "REF-042"],
  "gaps_or_extensions": "What the paper doesn't address that SMoC extends",
  "priority_tier": 1-4 (1=essential, 4=supplementary)
}}

Return ONLY valid JSON. No markdown formatting."""

    return prompt


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_ref.py <REF-ID>")
        print("Example: python analyze_ref.py REF-001")
        sys.exit(1)

    ref_id = sys.argv[1]

    # Load text
    txt_path = TXT_DIR / f"{ref_id}.txt"
    if not txt_path.exists():
        print(f"Error: {txt_path} not found")
        sys.exit(1)

    txt_content = txt_path.read_text(encoding="utf-8")

    # Load metadata stub
    meta_path = METADATA_DIR / f"{ref_id}.json"
    if not meta_path.exists():
        print(f"Error: {meta_path} not found")
        sys.exit(1)

    metadata_stub = json.loads(meta_path.read_text())

    # Generate analysis prompt
    prompt = generate_analysis_prompt(ref_id, txt_content, metadata_stub)

    # Save prompt for LLM processing
    prompt_path = METADATA_DIR / f"{ref_id}_analysis_prompt.txt"
    prompt_path.write_text(prompt, encoding="utf-8")

    print(f"Analysis prompt generated: {prompt_path}")
    print(f"Text length: {len(txt_content):,} chars")
    print(f"Prompt length: {len(prompt):,} chars (~{len(prompt)//4:,} tokens)")
    print("")
    print("Next: Feed this prompt to Gemini/Claude to generate analysis JSON")
    print(f"Then save result to: {meta_path}")


if __name__ == "__main__":
    main()
