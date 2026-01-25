# Research: In software architecture and programming language theory, I'm researching ENTITY STRATIFICATION acro...

> **Date:** 2026-01-23 13:37:07
> **Source:** perplexity-mcp
> **Model:** sonar-deep-research
> **Checksum:** `sha256:abc04079117bdedd2aadd29bc0fc3ba8ed026b139703a1bc37b2f8a734320840`
> **Raw JSON:** `raw/20260123_133707_in_software_architecture_and_programming_language.json`

---

## Query

In software architecture and programming language theory, I'm researching ENTITY STRATIFICATION across abstraction levels.

CONTEXT:
We have established that code exists in a space that is:
- BOUNDED BELOW: Physical substrate (bits, gates, electrons)
- UNBOUNDED ABOVE: Infinite possible abstraction levels

A typical hierarchy might be:
- L0: Bit
- L1: Byte
- L2: Primitive (int, float, char)
- L3: Variable
- L4: Expression
- L5: Statement
- L6: Function/Method
- L7: Class/Module
- L8: Package/Namespace
- L9: Service/Component
- L10: System
- L11: Domain
- L12+: Enterprise, Industry, Universe...

QUESTIONS:

1. Do software entities LIVE AT a single level, or can they SPAN multiple levels?
   - Is a function strictly L6, or does it span L4-L6 because it contains statements and expressions?
   - Is a class L7, or does it span L6-L7 because it contains methods?

2. Are abstraction levels DEFINED BY entity types, or do entities INHABIT pre-existing levels?
   - Chicken-egg: Do levels exist because entities exist, or vice versa?

3. Is there academic work on "entity stratification" or "level residency" in software?
   - Particularly interested in: Can an entity be BORN at one level but OPERATE at another?

4. How do cross-cutting concerns (logging, security, transactions) relate to levels?
   - These seem to span ALL levels - how is this modeled?

5. What is the relationship between CONTAINMENT (class contains method) and LEVEL (class is higher than method)?
   - Is containment the MECHANISM that creates levels?

6. In category theory or type theory, how are abstraction levels formalized?
   - Are there functors between levels?

Provide academic references where possible. This is for a theoretical framework called 'Standard Model of Code' that treats software entities like particles in physics.

---

## Response

# Entity Stratification Across Abstraction Levels in Software Architecture and Programming Language Theory

This comprehensive research report examines the theoretical foundations and practical implications of how software entities exist, move, and interact across multiple abstraction levels. Drawing from contemporary research in software architecture, programming language theory, category theory, and multi-level modeling, we present evidence that entities in software systems do not simply "live at" a single abstraction level, but rather participate in complex stratification patterns that demand sophisticated theoretical frameworks to understand and formalize.

## Understanding Abstraction as Hierarchical Organization

The concept of abstraction levels in software represents a fundamental organizing principle that structures how we understand, design, and implement computational systems. An abstraction level exists as a distinct organizational stratum characterized by a specific perspective, vocabulary, and set of concerns that define what information is relevant and what details can be safely hidden or deferred[2][9][19]. When we refer to a "level" of abstraction, we are not merely describing a vertical position in some arbitrary hierarchy, but rather identifying a coherent model of the system expressed in terms that make sense for the problems being solved at that particular level[21].

The relationship between abstraction levels can be understood through the principle that moving from one level to another represents a transition from describing **what** a system does to describing **how** it does it[2][9]. At a higher level of abstraction, we concern ourselves with behavior and capability; at a lower level, we concern ourselves with implementation and mechanism. A sorting algorithm at the high level of abstraction is simply "arrange these elements in order," but at lower levels, this becomes a sequence of comparisons, swaps, and memory operations[9]. This what-how relationship establishes a directional structure to abstraction hierarchies: we can decompose higher-level concepts into lower-level mechanisms, and we can compose lower-level mechanisms into higher-level abstractions[2].

In contemporary software systems, these abstraction levels form a spectrum bounded below by the physical substrate of computation (bits, transistors, electrical signals) and extending upward through successive layers of linguistic and conceptual organization[1][9][19][21]. The typical hierarchy begins with primitive operations at the machine level, rises through assembly language, compiled code, high-level language constructs, and continues upward through functions, classes, modules, services, and eventually reaches architectural patterns and enterprise-level system design[1][4][9].

## The Question of Entity Residency: Single-Level vs. Multi-Level Existence

One of the most fundamental questions in understanding software entities is whether an entity genuinely exists at a single, determinate abstraction level, or whether the very nature of software entities is to span multiple levels simultaneously. The traditional object-oriented perspective, which treats classes, methods, and functions as discrete, level-specific constructs, suggests that entities are fundamentally associated with particular levels—methods exist at level L6, classes at level L7, modules at level L8. However, examination of modern architectural and semantic frameworks reveals this view to be considerably oversimplified.

Consider a method defined within a class[8][11]. Traditional analysis would place this method at the functional level (L6) and the containing class at the class level (L7). Yet this classification obscures crucial structural relationships: the method structurally contains statements and expressions (L5 and L4 in our hierarchy), while simultaneously serving as a component of the class structure. The method is not simply "at" level L6; rather, it participates in multiple levels simultaneously, acting as a structural container for lower-level constructs while serving as a structural component of higher-level constructs. This multi-level participation is not accidental or an artifact of representation; it is fundamental to how software is actually organized.

This phenomenon becomes even clearer when examining containerization relationships. A class that contains methods, which contain statements, which contain expressions, which contain variables and literals—this entire structure demonstrates what we might call **level spanning**: the class is not merely a higher-level abstraction that happens to reference lower levels; it is a composite entity whose definition necessarily encompasses multiple levels of internal structure[8][11][44]. The containment relationship itself creates these level-spanning characteristics. When we say a class "contains" a method, we are describing a relationship that has consequences for level residency: the class cannot be fully understood without reference to its internal methods, just as methods cannot be understood without reference to their internal statements[8][11].

Research in multi-level modeling provides crucial evidence that entities routinely inhabit multiple levels with varying roles and responsibilities. The clabject model, which combines aspects of class and object into a single modeling primitive, demonstrates that an entity can simultaneously serve as both a type definition (class facet) at one level and an instance (object facet) at another level[37][38][40][41]. A "Car" clabject, for example, is itself an instance of "Product" while simultaneously serving as a class for specific car instances. This is not a violation of the single-level principle; rather, it reveals that the single-level principle was never adequate for describing actual software structures[37][38][40][41]. The potency-based deep instantiation approach formalizes this multi-level existence by assigning each property or attribute a potency value indicating at how many levels below it remains active in the instantiation hierarchy[37][38][40][41].

## Defining Levels: The Chicken-and-Egg Problem

An essential but frequently overlooked question concerns the generative relationship between abstraction levels and software entities: which comes first? Are abstraction levels emergent properties of how we organize entities, or do pre-existing level structures determine where entities can exist?

The evidence suggests that this relationship is fundamentally **bidirectional and co-constitutive** rather than unidirectional. Abstraction levels are not imposed from outside onto a neutral collection of entities; rather, levels emerge from the structural relationships that entities maintain with one another. Specifically, the dependency relationship and the composition relationship define level structure[1][4]. The foundational principle of stratified architecture states that dependencies should only point inward toward more stable, lower-level abstractions—never upward toward higher levels[1]. This dependency rule is not arbitrary; it expresses a structural constraint that defines what we mean by "levels" in the first place. When we say one layer is "higher" than another, we mean that the higher layer depends on the lower layer for its implementation, not vice versa[1][4].

Composition relationships similarly contribute to level definition. When a class is defined as containing methods, or a method as containing statements, these containment relationships establish a compositional hierarchy that becomes coextensive with our notion of abstraction levels[8][11]. An entity's level is partly determined by what it contains and partly by what contains it. A method that contains only primitive operations and built-in language constructs would normally be considered mid-to-high-level code, but the same syntactic structure embedded within a framework template that contains numerous methods might be reconceived as lower-level infrastructure within a higher-level architectural pattern[1][4].

However, levels also exhibit significant independence from individual entity arrangements. We can recognize that "expression," "statement," and "function" represent coherent levels in programming language hierarchies regardless of how any particular program organizes its entities[5][9][19][21]. These level definitions emerge from the fundamental operations available at each level, the vocabulary through which problems are expressed, and the scope of concerns that become relevant. The lexical/syntactic level is distinguished by concerns about tokens and grammar; the semantic level by concerns about meaning and type correctness; the execution level by concerns about runtime behavior and resource consumption[5][9][19][21]. These are not arbitrary divisions but reflect genuine discontinuities in the structure of computation[5][9][19][21].

A productive way to understand this apparent paradox is through the concept of **level instantiation**: pre-existing logical level structures get instantiated differently in different systems and contexts, while specific entity arrangements create new micro-hierarchies and local levels that operate within the broader macro-level framework. The levels of programming language construction (lexical, syntactic, semantic, intermediate, assembly, machine) represent relatively stable, pre-existing logical levels that organize all software systems. Within these, specific architectural and organizational choices create domain-specific and application-specific level structures that have genuine reality within those systems even though they depend on the underlying logical levels[1][4][9][19].

## Multi-Level Modeling: Formalization of Entity Stratification

Contemporary research in multi-level modeling provides the most sophisticated available formalization of how entities exist across multiple abstraction levels. Unlike traditional two-level metamodeling approaches—which strictly separate classes (meta-level) from instances (object-level)—multi-level modeling recognizes that the class-instance distinction is itself relative and that entities regularly participate in both roles simultaneously at different levels of the instantiation hierarchy[34][37][38][40][41].

The core insight of multi-level modeling is captured in the concept of **clabjects** (portmanteau of "class" and "object"): modeling primitives that embody characteristics of both classes and objects, with the distinction between these roles becoming relative rather than absolute[37][38][40][41]. A clabject can simultaneously be an instance of a higher-order clabject (object facet) and a class for lower-order clabjects (class facet). This simultaneity is not merely a representational trick; it reflects the actual structure of many software and domain concepts.

For example, in a product catalog domain, we might have a Product clabject at level 0 (the highest level of abstraction), which classifies product categories like "Car" as its instances. The Car clabject simultaneously serves as an object (instance of Product) and a class (defining the structure that product models like Porsche911GT3 must conform to). Porsche911GT3 in turn is an instance of Car and simultaneously a class whose instances are specific product individuals like MarysCar[37][38][40][41]. Each of these entities lives at a specific level in the hierarchy but simultaneously serves dual roles depending on perspective.

Multi-level modeling formalizes this through the concept of **potency**, a numeric property attached to each modeling element indicating how many levels below it remains active in the instantiation hierarchy[37][38][40][41]. An attribute with potency 3 defined on the Product clabject actively structures the schema for three levels of instances below it. Deep characterization extends this further, allowing a clabject to define schema elements not only for its direct instances but for instances of instances, instances of instances of instances, and so on, at arbitrary depths[37][38][40][41]. This formal framework directly addresses the theoretical problem of entity stratification by providing mathematical machinery for describing precisely how entities inhabit multiple levels.

The dual deep modeling extension of multi-level modeling introduces **source potency** and **target potency** for properties connecting clabjects in different hierarchies, allowing properties to be instantiated selectively across different numbers of levels in different hierarchies[56]. This addresses the practical reality that different entity types often have different instantiation depths. Person entities might exist at a single instantiation level, while Product entities span three levels; a property connecting persons and products needs to be flexible about these different instantiation depths[56]. The formal specification of these relationships through dual potency provides a mathematical framework for describing exactly how entities at different levels can meaningfully interact.

## Cross-Cutting Concerns and Vertical Consistency

One of the most theoretically challenging aspects of entity stratification is understanding how cross-cutting concerns operate across multiple abstraction levels. Cross-cutting concerns are aspects of a system that affect multiple components, layers, and modules without being neatly encapsulated within any single level—logging, security, transaction management, performance monitoring, and error handling all exemplify this phenomenon[3][6][26].

The traditional problem with cross-cutting concerns is that they resist encapsulation at any single level. Logging, for instance, may need to be applied at the statement execution level, the function call level, the service invocation level, and the external transaction level—creating scattered, tangled code that violates modularity principles[3][26]. Aspect-oriented programming emerged as an approach to address this problem by allowing the specification of behaviors that cut across multiple modules without modifying the core logic of those modules[26][29]. An aspect specifies pointcuts (locations where the aspect applies) and advice (behavior to be injected at those locations), enabling cross-cutting behavior to be expressed as a first-class concern rather than scattered throughout the system[26][29].

However, aspect-oriented programming itself reveals something profound about entity stratification: concerns that genuinely cross-cut multiple levels cannot be adequately modeled by treating levels as independent. Instead, they demand that we recognize a **vertical consistency requirement**: certain properties and behaviors must be consistently maintained across all levels of a system, creating vertical constraints that unify what would otherwise be independent horizontal layers[3][6][26].

Security provides a concrete example. A security concern cannot be adequately addressed by implementing authentication at the service boundary and assuming security is thereby ensured. Security requirements must be consistently maintained from the lowest levels of memory access control, through statement-level operations that might leak information through timing channels, through method-level access controls, through class-level encapsulation, through module-level export restrictions, through service-level authorization, and up through architectural access policies[3][6]. Each level has its own specific security mechanisms and vulnerabilities, and failing at any level compromises security at all levels. The cross-cutting nature of security stems from its vertical consistency requirement, not from any weakness in level structure[3][6].

Research in distributed systems has developed sophisticated frameworks for understanding cross-cutting concerns in multi-tier architectures, identifying logging, data validation, error handling, performance monitoring, and security as fundamental concerns that must be consistently addressed across all system levels[6]. The fact that these concerns are "cross-cutting" does not mean they violate stratification principles; rather, it reveals that genuine stratification requires more than horizontal independence—it requires vertical consistency along certain critical dimensions[3][6][26].

## Containment, Composition, and the Generation of Level Structure

The relationship between containment (the "is part of" relationship) and abstraction levels deserves particular attention, as containment appears to be a primary mechanism through which level structure is created and maintained. When a class contains methods, or a method contains statements, or a statement contains expressions, these containment relationships generate a compositional hierarchy that directly corresponds to our intuitive understanding of abstraction levels[8][11][44].

The distinction between aggregation and composition, as formalized in object-oriented theory, proves relevant here[8][11]. Aggregation represents a looser whole-part relationship where components maintain relatively independent lifecycles and meaning; composition represents a tighter relationship where components derive their meaning and existence from their role within the whole[8][11]. This distinction maps onto differences in level participation: aggregated components participate less deeply in the level structure of their containing entity, while composed components are more thoroughly integrated into higher-level abstractions[8][11][44].

A method is composed into its containing class (the method has no meaning independent of the class context), whereas a component might be aggregated into a system (the component potentially has meaning independent of its current system context). This compositional depth correlates with how thoroughly the contained entity participates in the level structure of the containing entity. A composed method takes on properties of its class level while retaining its own method-level properties, resulting in multi-level participation[8][11]. An aggregated component might maintain more independence, more clearly occupying its own single level[8][11][44].

The entity-component-system model that has emerged in game development and systems design offers an alternative perspective on level generation through composition[44]. Rather than strictly hierarchical containment where entities are composed into classes into modules into services, the entity-component system separates entity identity from entity attributes, with entities understood as collections of independent components that can be queried and manipulated without strict hierarchical containment[44]. Even in this model, however, levels still emerge—but they emerge from component interaction patterns and query relationships rather than from containment alone[44]. The vertical consistency requirements differ from traditional hierarchical systems, but level structure still emerges and remains essential for understanding the system[44].

## Formal Approaches: Category Theory and Type Theory

The most sophisticated available mathematical frameworks for understanding abstraction levels draw from category theory, type theory, and formal semantics. These frameworks provide abstraction beyond any particular programming language or architectural pattern, revealing deep structural principles that govern how levels organize computational systems.

In category theory, abstraction levels can be understood as organizing principles within or across categories, with functors serving as structure-preserving mappings between levels of abstraction[13][16][51][54]. A functor from one category to another preserves the essential structural relationships of the source category while potentially mapping them to different representations in the target category, analogous to how higher-level abstractions preserve the logical structure of lower-level implementations while changing representation[13][51][54]. The concept of adjoint functors—functors that stand in an optimal relationship to one another—provides a formal model for how different levels of abstraction can be related; the left adjoint functor represents going from a more concrete level to a more abstract level, while the right adjoint represents going from abstract back to concrete[13][51][54].

Denotational semantics provides another framework through which abstraction levels can be formalized[27][32]. In denotational semantics, the meaning of a program phrase is given by its denotation—a mathematical object in some abstract domain that represents what the phrase means[27]. Different levels of abstraction in denotational semantics correspond to different domains of interpretation: high-level program phrases denote mathematical objects representing program behavior, mid-level intermediate representations denote lower-level semantic structures, and low-level assembly instructions denote operations on memory and processors[27]. The compositional principle in denotational semantics—the requirement that the denotation of a complex phrase be computable from the denotations of its subphrases—directly encodes the level-spanning nature of software entities: complex entities at higher levels have denotations built compositionally from denotations of constituent lower-level entities[27][32].

The notion of **full abstraction** in semantic theory provides a criterion for when an abstraction truly captures the essential properties we care about[32]. An abstraction is fully abstract when two program phrases have the same denotation if and only if they behave identically in all possible computational contexts[32]. This provides a principled way to distinguish between true abstraction levels (those that correspond to genuinely distinguishable semantic properties) and false or artificial level distinctions[32]. Not all partitions of code into different organizational levels are genuine abstraction levels; genuine levels carve the universe of code at genuine semantic joints[32].

Type systems and type theory provide frameworks for understanding how entities of different abstraction levels can safely interact. The concept of **type variance**—which governs when substitution is safe between complex types and their components—reveals deep structural principles about safe interaction across abstraction levels[33][36]. When a function expects a list of Mammals, can we safely pass it a list of Cats? The answer depends on whether the function only reads from the list (covariance, yes) or also modifies it (contravariance, no)[33][36]. This principle generalizes: safe interaction across abstraction levels requires careful attention to what each level can depend on regarding lower levels, which connects directly to the dependency rule of stratified architecture[1][33][36].

Polymorphism, understood through universal quantification and existential quantification in type theory, provides mechanisms for abstractions that apply uniformly across multiple instantiations without knowing the specific types of those instances[22][33][36]. A generic function that works with any type, or a container class that can hold any object, represents abstraction that genuinely spans levels—the polymorphic abstraction exists at a level above type-specific code, yet permits type-specific behavior when instantiated[22][33][36].

## Intermediate Representations and the Stratification of Compilation

The compilation process in modern compilers provides concrete evidence for the stratification principle and reveals how compilers themselves function as systems that navigate multiple abstraction levels. A compiler does not translate source code directly into machine code; instead, it passes code through multiple intermediate representations, each at a different abstraction level[50][53].

A typical compilation pipeline processes source code first into an abstract syntax tree (AST), which abstracts away syntactic details (parentheses, semicolons, whitespace) while preserving semantic structure[49][52]. The AST is then transformed into intermediate representations at varying abstraction levels: high-level intermediate representations (HIRs) that remain close to the source language, mid-level intermediate representations (MIRs) that support program analysis and optimization, and low-level intermediate representations (LIRs) that approach assembly-level semantics[50][53].

Crucially, each intermediate representation preserves the meaning of the program (or at least an approximation sufficient for compilation purposes) while changing what aspects are visible or manipulable at that level[50][53]. A MIR might expose control flow structure for analysis and optimization but hide the original source syntax. A LIR might expose memory operations and register allocation but hide higher-level language constructs. An entity like a function or a loop exists at multiple intermediate representation levels, but its manifestation differs: at the HIR level, a function includes all its source-level syntax; at the LIR level, it becomes a sequence of basic blocks with jump instructions; at the machine code level, it becomes processor instructions with registers and memory addresses[50][53].

The intermediate representation design process itself reveals implicit principles about abstraction levels. Good intermediate representations are designed with specific goals in mind: simplicity (making analysis easier), machine-independence (allowing multiple targets), language-independence (allowing multiple sources), and support for transformation (making optimization possible)[50][53]. These design goals reflect the fact that intermediate representations must serve as meaningful levels within a larger multi-level structure. A representation that fails to be meaningfully intermediate—too high-level to generate efficient code from, or too low-level to support optimizations—fails as an abstraction level[50][53].

## The Scope Hierarchy and Entity-Level Allocation

Software systems exhibit multiple nested scope hierarchies that interact with abstraction levels in complex ways. A variable exists within the scope of a function, which exists within the scope of a module, which exists within the scope of a package, which exists within the scope of a system[1][4][21][46]. These nested scopes create an organizational hierarchy related to but distinct from abstraction levels.

An entity's scope defines the region of code in which it is accessible; its abstraction level defines its position within the hierarchy of what-versus-how abstraction. These are related but not identical concepts. A low-level helper function might have file scope (accessible throughout a single file) but operate at a low abstraction level (close to the machine); a high-level policy function might have global scope (accessible throughout the system) and operate at a high abstraction level (close to domain concerns)[1][4][21]. The relationship between scope hierarchy and abstraction level hierarchy is important but not one-to-one.

Module boundaries and dependency rules exploit this distinction. Nx, a modern monorepo management framework, explicitly enforces rules about which modules can depend on which other modules through a tag-based system that allows multiple dimensions of categorization[43]. Tags like "scope:users" versus "scope:shared" establish a horizontal partitioning, while tags like "type:feature" versus "type:util" establish a functional distinction orthogonal to scope[43]. The dependency rules then enforce that certain combinations of these tags are prohibited: code tagged as "feature" can depend on code tagged as "util," but not vice versa[43]. This reveals that genuine stratification often requires multi-dimensional organization rather than simple linear hierarchies[43].

## Hierarchical Decomposition and Analysis

The hierarchical decomposition methodology, developed for analyzing complex cyber-physical systems, provides insights into how entity stratification supports system understanding and analysis[25]. The methodology partitions a system into multiple hierarchical levels of abstraction, with each level providing a different view of system health and behavior. Lower-level models capture detailed component behavior; higher-level models aggregate information from lower levels while abstracting away details. By linking separate models at different levels through hierarchical relationships, the methodology enables analysis that would be intractable if attempted at a single level of detail[25].

This multi-level analysis approach reveals several benefits of proper stratification: false alarms can be reduced by recognizing when multiple low-level problems have a common cause recognizable only at a higher level; true root causes become identifiable by tracing high-level symptoms to specific low-level components; and system understanding becomes manageable through progressive refinement rather than requiring comprehensive understanding at all levels simultaneously[25]. These benefits derive directly from the fact that entities at different levels capture genuinely different information, and that proper stratification maintains relationships between levels that enable productive cross-level reasoning[25].

## Hierarchies in Knowledge Organization Systems

The theory of hierarchies in taxonomies, thesauri, and ontologies reveals that different knowledge organization systems permit different types of hierarchical relationships, each capturing different semantic structures[10][14][17]. A taxonomy might use generic-specific hierarchies (IS-A relationships), part-whole hierarchies (IS-PART-OF relationships), and sometimes instance hierarchies (IS-INSTANCE-OF relationships)[10][14][17]. Ontologies, in their pure form, restrict to generic-specific hierarchies (one entity being a subclass of another), with part-whole relationships requiring different representational machinery[10][14][17].

This diversity of hierarchical types in knowledge organization reveals that "levels" in different organizational contexts might represent different semantic structures. Not all hierarchies are abstraction-level hierarchies; some capture domain decomposition, others capture taxonomic classification, others capture temporal sequences or importance rankings[10][17]. Confusing these different types of hierarchies leads to conceptual incoherence[10][17]. A meaningful theory of entity stratification must carefully distinguish between these different types of hierarchical relationships and recognize that abstraction-level hierarchies represent a specific type of hierarchy with particular formal properties.

## Reflection, Meta-Level Programming, and Level Crossing

Reflective programming enables code to examine and modify other code, creating explicit mechanisms for crossing between abstraction levels and the meta-levels above them[39][42]. In reflective architectures following the mirror pattern, meta-level facilities are encapsulated into separate intermediary objects that provide a distinct interface for meta-level operations, rather than embedding meta-level capabilities within base-level objects[42]. This design principle of stratification in reflection—keeping base-level and meta-level concerns separated—directly reflects the stratification principle in architecture more broadly[42].

However, reflection also reveals that the distinction between a level and a meta-level to that level is not absolute but depends on perspective and purpose. Code that operates as base-level when examined from one perspective becomes meta-level when examined from another. A type system operates at the meta-level relative to programs typed by that system, but the type system itself is a program operating in a type system at a higher meta-level. The layers of reflection and meta-level programming create potentially infinite regressive chains of meta-levels, revealing that "level" and "meta-level" are relative rather than absolute concepts[39][42].

Well-designed reflective systems maintain clear separation between levels while enabling necessary communication, using principled interfaces that prevent the confusion and complexity that arises from unconstrained access between levels[42]. This again reflects the broader principle that stratification does not prohibit interaction across levels; rather, it structures such interaction through explicit interfaces and dependency rules[1][42].

## Conclusion: A Framework for Understanding Entity Stratification

The evidence from contemporary software architecture, programming language theory, multi-level modeling, category theory, and formal semantics converges on several conclusions about entity stratification in software:

**First, entities routinely span multiple abstraction levels rather than residing at single, determinate levels.** This is not a failure of our abstractions but a fundamental characteristic of how software is actually structured. A function contains statements and expressions (spanning multiple levels downward), serves as a component of classes and modules (spanning multiple levels upward), and often exhibits dual roles as both definition and instance in reflective or meta-level contexts. Multi-level modeling provides the most sophisticated formalization of this phenomenon through clabjects and potency-based deep characterization.

**Second, abstraction levels are both discovered and created.** Pre-existing logical levels organize all computational systems—the distinction between expression, statement, function, class, module, service, and system represents genuine discontinuities in the structure of software. Yet within these logical levels, specific systems create domain-specific and architectural levels through organizational choices. Level structure emerges from both the intrinsic mathematical properties of computation and the design decisions reflected in particular systems.

**Third, stratification creates genuine constraints that support system properties including modularity, understandability, maintainability, and evolution.** These constraints are not artificial restrictions imposed from above but enable real benefits by capturing information about which parts of a system can be understood or modified independently. Violation of stratification (allowing higher layers to depend on lower layers, or mixing levels inappropriately) leads to the tangling and scattering that make systems difficult to maintain.

**Fourth, cross-cutting concerns do not violate stratification; rather, they reveal the vertical consistency requirements that stratification must support.** Security, logging, transaction management, and other cross-cutting concerns must be consistently maintained across all levels because they represent genuinely system-wide properties, not because stratification failed.

**Fifth, formal approaches including category theory, type theory, denotational semantics, and multi-level modeling provide rigorous frameworks for understanding and reasoning about entity stratification.** These frameworks reveal deep structural principles about how different levels relate, how entities can safely interact across levels, and what properties characterize genuine abstraction levels versus artificial organizational distinctions.

For the "Standard Model of Code" theoretical framework the user is developing, these findings suggest that software entities should be modeled as multi-dimensional objects with multiple aspects of their nature: an abstraction level, a scope, contained lower-level entities, containing higher-level entities, dependency relationships to other entities at various levels, and participation in multiple vertical consistency dimensions. The model should recognize potency-like properties that indicate how many levels below an entity its properties remain active. Most importantly, the model should treat level participation not as a flat categorization but as a complex multi-faceted relationship with significant mathematical structure that can be studied formally using category-theoretic and type-theoretic tools.

Entities in such a model are not particles existing at fixed points in an abstract space, but rather fields or wave functions that extend across multiple abstraction levels, with different aspects of their nature becoming salient at different levels of observation. This perspective acknowledges the fundamental multi-level nature of software entities while preserving the genuine insights that stratification provides about system structure and properties.

---

## Citations

1. https://buildsimple.substack.com/p/stratification-in-application-architecture
2. https://dev.to/miguelmj/high-level-programming-explaining-abstraction-4ko
3. https://en.wikipedia.org/wiki/Cross-cutting_concern
4. https://vfunction.com/blog/enterprise-software-architecture-patterns/
5. https://en.wikipedia.org/wiki/Abstraction_(computer_science)
6. https://www.geeksforgeeks.org/system-design/cross-cutting-concerns-in-distributed-system/
7. https://www.i2b2.org/software/files/PDF/current/Ontology_Architecture.pdf
8. https://programminggems.wordpress.com/2019/04/22/aggregation-composition-and-containment-in-grady-boochs-object-oriented-analysis-and-design-with-applications/
9. https://www.fluentcpp.com/2016/12/15/respect-levels-of-abstraction/
10. https://www.hedden-information.com/2305-2/
11. https://isaaccomputerscience.org/concepts/prog_oop_aggregation_composition
12. https://atomicobject.com/oo-programming/object-oriented-polymorphism
13. https://plato.stanford.edu/archives/fall2012/entries/category-theory/
14. https://fib-dm.com/ontology-class-and-data-model-entity-hierarchy/
15. https://ceur-ws.org/Vol-3241/paper22.pdf
16. https://golem.ph.utexas.edu/category/2010/07/what_is_a_theory.html
17. http://lambda-the-ultimate.org/node/1386
18. https://en.wikipedia.org/wiki/Mereology
19. https://cacm.acm.org/research/abstractions-their-algorithms-and-their-compilers/
20. https://www.jsoftware.us/vol3/jsw0301-01.pdf
21. https://tgdwyer.github.io/levelsofabstraction/
22. https://www.classes.cs.uchicago.edu/archive/2012/spring/22300-1/papers/Cardelli-Wegner.pdf
23. https://users.soe.ucsc.edu/~ejw/papers/medvidovic_css96.pdf
24. https://en.wikipedia.org/wiki/Formal_semantics_(natural_language)
25. https://pmc.ncbi.nlm.nih.gov/articles/PMC6508658/
26. https://en.wikipedia.org/wiki/Aspect-oriented_programming
27. https://en.wikipedia.org/wiki/Denotational_semantics
28. https://www.gogravity.com/product/insights/reporting/dimensional-reporting-software
29. https://www.cs.drexel.edu/~yc349/CS575/Week8/KiczalesAOP_Ecoop97.pdf
30. https://www.cl.cam.ac.uk/teaching/1112/DenotSem/dens-notes-bw.pdf
31. https://realpython.com/python-metaclasses/
32. https://plato.stanford.edu/entries/games-abstraction/
33. https://en.wikipedia.org/wiki/Type_variance
34. https://emisa-journal.org/emisa/article/view/281/194
35. https://en.wikipedia.org/wiki/Abstract_interpretation
36. https://eli.thegreenplace.net/2018/covariance-and-contravariance-in-subtyping/
37. https://homepages.ecs.vuw.ac.nz/~tk/publications/papers/essence.pdf
38. https://www.dke.uni-linz.ac.at/rest/dke_web_res/publications/papers/Neum17d/Neum17d_copy.pdf
39. http://cshub.bc.edu/stumpaa/papers/archon.pdf
40. https://nemo.inf.ufes.br/wp-content/papercite-data/pdf/multi_level_conceptual_modeling_theory_language_and_application_2021.pdf
41. https://dl.acm.org/doi/pdf/10.1109/MODELS-C59198.2023.00104
42. https://bracha.org/mirrors.pdf
43. https://www.stefanos-lignos.dev/posts/nx-module-boundaries
44. https://datavirke.dk/posts/contemplating-entity-component-architecture/
45. https://www2.cs.sfu.ca/CourseCentral/354/zaiane/material/postscript/Chapter2.pdf
46. http://dmtopolog.com/modularity-1-boundaries
47. https://vfunction.com/blog/architecture-diagram-guide/
48. https://www.geeksforgeeks.org/dbms/entity-in-dbms/
49. https://dev.to/balapriya/abstract-syntax-tree-ast-explained-in-plain-english-1h38
50. https://www.cs.cornell.edu/courses/cs4120/2023sp/notes/ir/
51. https://www.cs.man.ac.uk/~david/categories/book/book.pdf
52. https://en.wikipedia.org/wiki/Abstract_syntax_tree
53. https://en.wikipedia.org/wiki/Intermediate_representation
54. https://www.math.mcgill.ca/triples/Barr-Wells-ctcs.pdf
55. https://en.wikipedia.org/wiki/Chomsky_hierarchy
56. https://pmc.ncbi.nlm.nih.gov/articles/PMC5807479/
57. https://www.di.fc.ul.pt/~mal/papers/amast02.pdf
58. https://timhunter.humspace.ucla.edu/papers/blackwell-chomsky-hierarchy.pdf
59. https://www.dke.uni-linz.ac.at/rest/dke_web_res/publications/papers/Neum17d/Neum17d_copy.pdf
60. https://fredriknf.com/papers/universaluniversal_mscs2017.pdf

---

## Usage Stats

- Prompt tokens: 435
- Completion tokens: 6327
- Total tokens: 6762
