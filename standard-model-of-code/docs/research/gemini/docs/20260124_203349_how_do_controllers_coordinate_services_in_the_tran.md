# Research: How do controllers coordinate services in the transport layer?

> **Date:** 2026-01-24 20:33:49
> **Source:** gemini
> **Model:** gemini-3-pro-preview
> **Checksum:** `sha256:2d33e0166d5b6fbe692d71e69bb560433747eed4ef159522a32435809790e1a0`
> **Raw JSON:** `raw/20260124_203349_how_do_controllers_coordinate_services_in_the_tran.json`

---

## Query

How do controllers coordinate services in the transport layer?

---

## Response

Based on the **Standard Model of Code** architecture defined in your provided context (specifically `TOOL.md` and `AGENTKNOWLEDGEDUMP.md`), Controllers and Services coordinate through a strict **Orchestration vs. Behavior** hierarchy governed by **Antimatter Laws**.

Here is the analysis of how they coordinate within the Transport/API layer:

### 1. The Architectural Hierarchy
In the Standard Model, the coordination flows vertically across layers. Controllers exist at the **Boundary**, while Services exist in the **Core Domain**.

*   **Controllers (Orchestration)**:
    *   **Atom Role**: `D3_ROLE: Controller` / `D3_ROLE: Router`
    *   **Layer**: `D2_LAYER: API` or `Application`
    *   **Responsibility**: They handle the "Transport" concerns—HTTP requests, CLI arguments, or event payloads. They deserialize input and delegate work. They **must not** contain business logic.
*   **Services (Behavior)**:
    *   **Atom Role**: `D3_ROLE: Service`
    *   **Layer**: `D2_LAYER: Domain`
    *   **Responsibility**: They contain the actual business rules and logic. They are unaware of the transport mechanism (HTTP/CLI).

### 2. The Coordination Rules (Antimatter Laws)
The interaction is strictly governed by the architectural rules defined in `TOOL.md` (Part V). The coordination **must** follow these paths to pass the **Holographic-Socratic Layer (HSL)** audit:

*   **Rule 1: Downward Flow Only (AM002 Violation Prevention)**
    *   Controllers call Services.
    *   Services **never** import or call Controllers.
    *   *Violation:* If a Service imports a Controller, it triggers `AM002: Reverse Layer Dependency`.

*   **Rule 2: No Layer Skipping (AM001 Violation Prevention)**
    *   Controllers should coordinate via Services, not by jumping directly to the Database.
    *   *Violation:* `TOOL.md` explicitly cites: *"Controller calling Repository directly (skipping Service)"* as an `AM001` violation.

### 3. Concrete Example: ACI Tier Router
Looking at the codebase context provided (specifically `context-management/docs/ACI_DATASET_MANAGEMENT.md`), we can see this pattern in action within the **Adaptive Context Intelligence (ACI)** system:

1.  **Transport/Controller**: The `Tier Router` (acting as the controller) receives the raw query.
2.  **Coordination**: It does not answer the query itself. Instead, it calculates the "Routing Matrix" (Intent × Complexity × Scope).
3.  **Service Delegation**: Based on the calculation, it delegates to a specific underlying service:
    *   `Tier 0 Service`: `answer_from_truths()` (Cached lookup)
    *   `Tier 1 Service`: `RAG`
    *   `Tier 3 Service`: `Perplexity`

### 4. Semantic Definitions (Tau Notation)
According to the `TOOL.md` specification, a healthy Controller-to-Service relationship would look like this in Tau notation:

**The Controller (Transport):**
```
τ(Class:Controller:API:In:Stateless:Read:Use:95)
```
*   **Boundary**: `In` (Input handling)
*   **Effect**: `Read` (Reads request, delegates)

**The Service (Business Logic):**
```
τ(Class:Service:Domain:Internal:Stateless:Pure:Use:95)
```
*   **Boundary**: `Internal` (No knowledge of HTTP/Transport)
*   **Effect**: `Pure` (Deterministic business logic)

### Summary
Controllers coordinate services by acting as **stateless orchestrators**. They strip away the "Transport" context (HTTP headers, CLI flags) and pass clean data objects to Services, strictly adhering to the rule that **Orchestration (Layer N) calls Behavior (Layer N-1)**, never the reverse.

---

## Citations

_No citations provided_
