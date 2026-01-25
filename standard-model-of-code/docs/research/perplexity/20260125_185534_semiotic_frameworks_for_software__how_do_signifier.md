# Perplexity Research: Semiotic frameworks for software: how do signifier-signified relationships apply to code? Specifical...

> **Date:** 2026-01-25 18:55:34
> **Model:** sonar-pro
> **Query Length:** 454 chars

---

## Query

Semiotic frameworks for software: how do signifier-signified relationships apply to code? Specifically: 1) Code as signifier, behavior as signified 2) The role of documentation/context as 'interpretant' (Peirce's triadic model) 3) How meaning emerges from code+context together 4) Frame semantics (Fillmore) applied to software understanding 5) Knowledge graphs that separate 'what is' from 'what it means'. Looking for formal models, not just analogies.

---

## Response

Semiotic frameworks for software, particularly those adapting models like Saussure's dyadic signifier-signified and Peirce's triadic sign-interpretant, treat **code as a sign system** where syntactic and semantic quality is evaluated against formal language metamodels (e.g., UML or SQL:2003).[1][2] These frameworks, such as the SEQUAL-based semiotic quality framework, provide formal models for assessing software entities like measures, specifications, and models by measuring syntactic validity/completeness (form vs. language rules) and semantic validity/completeness (content vs. domain).[1][2]

### 1) Code as Signifier, Behavior as Signified
In these frameworks, **code acts as the signifier** (syntactic form specified via metamodels of languages like UML), while **runtime behavior or measured quality is the signified** (semantic content mapped to domain models).[1][2] Validity is assessed by a bijective mapping between the structure model of a specification \( m \) (set \( X \)) and its possible representation model (set \( Y \)), where discrepancies indicate syntactic issues; semantic quality checks if \( m \)'s concepts align with language \( L \)'s metamodel (e.g., identifying L-specific concepts and verifying coverage).[1][2]

### 2) Documentation/Context as Interpretant (Peirce's Triadic Model)
SEQUAL and its adaptations imply documentation/context as the **interpretant**, resolving ambiguities in sign interpretation by evaluating **feasible validity** (agreement on meaning) and **feasible completeness** (coverage of domain interpretations).[1][2] For a measure set \( M \) evaluating entities in language \( L \), completeness \( EC(M) \) is computed from metamodel coverage (e.g., class mappings), with interpretants like multiple developer agreements resolving conflicts in informal specs (e.g., English+OCL).[1][2]

### 3) Meaning Emergence from Code+Context
**Meaning emerges triadicly** from code (sign vehicle), domain metamodel (object), and quality goals/interpretants (e.g., physical, empirical, syntactic, semantic levels).[1][2] For software measures, this is formalized as multilevel quality evaluation: syntactic quality via abstract syntax metamodels, semantic via domain metamodels, ensuring bijective mappings and concept coverage; incomplete/ambiguous specs fail this, as seen in database design measures.[1][2]

### 4) Frame Semantics (Fillmore) Applied to Software Understanding
Search results lack direct formal applications of **Fillmore's frame semantics** to software, though semiotic frameworks parallel frame-like structures via metamodels defining "frames" of language elements (classes/properties/relationships as semantic roles).[1][2] A related semiotic approach to UML models clarifies analysis (domain frames) vs. design (implementation frames), treating models as sign systems with contextual interpretation.[4]

### 5) Knowledge Graphs Separating 'What Is' from 'What It Means'
**Metamodels function as knowledge graphs** in these frameworks, separating **'what is'** (physical/empirical entities, e.g., UML classes) from **'what it means'** (semantic/pragmatic levels via validity measures against domain metamodels).[1][2] For example, UML class models graph language syntax (nodes: elements; edges: relationships), enabling syntactic discrepancy quantification and semantic evaluation procedures (e.g., concept identification from specs).[1][2]

These models, primarily from Eessaar (2008), emphasize formal evaluation over analogies, but coverage of points 4-5 is limited; broader literature (e.g., on UML semiotics) suggests extensions via metamodel mappings.[1][2][4]

---

## Citations

1. http://staff.ttu.ee/~erki.eessaar/files/Eessaar_ICEIS_2008.pdf
2. https://www.scitepress.org/Papers/2008/17034/17034.pdf
3. https://books.openbookpublishers.com/10.11647/obp.0369.03.pdf
4. https://www.semanticscholar.org/paper/A-Semiotic-Approach-to-UML-models-G%C3%A9nova-Valiente/bc24cc33ecdea2f7f35b826ab6169e1f30715d66

---

## Usage Stats

- Input tokens: 104
- Output tokens: 796
