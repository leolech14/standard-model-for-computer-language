"""
Purpose Registry

Defines the INTRINSIC PURPOSE of every known code sub-unit in the Standard Model.

Each atom and role has a PURPOSE - the reason it exists.
"""

# =============================================================================
# ROLE PURPOSES (27 roles - the WHY dimension)
# =============================================================================

ROLE_PURPOSE = {
    # Data Access (3 roles)
    "Query": "Retrieve data without modification",
    "Command": "Execute an action that changes state",
    "Repository": "Abstract data persistence operations",
    
    # Domain Modeling (2 roles)
    "Entity": "Represent a domain object with identity",
    "Service": "Coordinate business operations across entities",
    
    # Creation (2 roles)
    "Factory": "Create and configure new instances",
    "Builder": "Construct complex objects step by step",
    
    # Validation & Transformation (2 roles)
    "Validator": "Verify data meets constraints",
    "Transformer": "Convert data from one representation to another",
    
    # Structural Patterns (3 roles)
    "Adapter": "Convert between incompatible interfaces",
    "Decorator": "Add behavior dynamically to objects",
    "Strategy": "Encapsulate interchangeable algorithms",
    
    # Interface & Presentation (3 roles)
    "Controller": "Handle external requests and delegate to application",
    "Presenter": "Format data for display",
    "View": "Render user interface components",
    
    # Configuration & Constants (2 roles)
    "Configuration": "Define system parameters and settings",
    "Constant": "Store immutable values used across codebase",
    
    # Testing (3 roles)
    "Test": "Verify behavior meets expectations",
    "Mock": "Simulate dependencies for testing",
    "Fixture": "Provide test data and setup",
    
    # Lifecycle & Events (3 roles)
    "EventHandler": "React to domain events",
    "Observer": "Watch for changes and respond",
    "Migration": "Manage schema and data evolution",
    
    # Infrastructure (2 roles)
    "Singleton": "Ensure single instance exists globally",
    "Guard": "Control access and enforce authorization",
    
    # Cross-cutting (2 roles)
    "Utility": "Provide stateless helper operations",
    "Middleware": "Intercept and process requests/responses",
}

# =============================================================================
# ATOM PURPOSES (167 atoms organized by phase)
# =============================================================================

ATOM_PURPOSE = {
    # =========================================================================
    # DATA PHASE (26 atoms) - "What data exists"
    # =========================================================================
    
    # Primitives
    "Integer": "Store whole numbers",
    "Float": "Store decimal numbers",
    "String": "Store text sequences",
    "Boolean": "Store true/false values",
    "Null": "Represent absence of value",
    "Byte": "Store raw binary data",
    
    # Structured Data
    "Array": "Store ordered collection of same-type elements",
    "List": "Store dynamic ordered collection",
    "Set": "Store unique unordered elements",
    "Dict": "Store key-value mappings",
    "Tuple": "Store fixed immutable sequence",
    "Struct": "Group related data fields",
    "Record": "Represent immutable data with named fields",
    
    # Domain Data
    "Entity": "Represent object with unique identity",
    "ValueObject": "Represent immutable domain concept",
    "Aggregate": "Group entities with consistency boundary",
    "DTO": "Transfer data across boundaries",
    "Enum": "Define fixed set of named values",
    
    # References
    "Reference": "Point to another object",
    "WeakReference": "Point without preventing cleanup",
    "ForeignKey": "Reference entity in another aggregate",
    
    # Specialized Data
    "DateTime": "Store date and time",
    "Money": "Store monetary values with precision",
    "UUID": "Store universally unique identifier",
    "Email": "Store validated email address",
    "URL": "Store validated web address",
    
    # =========================================================================
    # LOGIC PHASE (61 atoms) - "What computations happen"
    # =========================================================================
    
    # Control Flow
    "IfBranch": "Choose between execution paths",
    "Switch": "Select from multiple options",
    "ForLoop": "Repeat over sequence",
    "WhileLoop": "Repeat while condition holds",
    "Break": "Exit loop early",
    "Continue": "Skip to next iteration",
    "Return": "Exit function with value",
    
    # Exception Handling
    "TryCatch": "Handle errors gracefully",
    "Throw": "Signal error condition",
    "Finally": "Execute cleanup unconditionally",
    
    # Functions
    "Function": "Encapsulate reusable computation",
    "Lambda": "Define inline anonymous function",
    "Closure": "Capture surrounding context",
    "Generator": "Produce values lazily on demand",
    "Coroutine": "Pause and resume execution",
    "Async": "Execute without blocking",
    "Await": "Wait for async completion",
    
    # Operations
    "Assignment": "Bind value to name",
    "Comparison": "Compare two values",
    "Arithmetic": "Perform mathematical operation",
    "Logical": "Combine boolean conditions",
    "Bitwise": "Manipulate individual bits",
    
    # Queries
    "Query": "Retrieve data without modification",
    "Filter": "Select subset matching criteria",
    "Map": "Transform each element",
    "Reduce": "Combine elements into single result",
    "Sort": "Order elements by criteria",
    "Group": "Partition elements by key",
    "Join": "Combine data from multiple sources",
    
    # Commands
    "Create": "Bring new entity into existence",
    "Update": "Modify existing entity",
    "Delete": "Remove entity from existence",
    "Upsert": "Create or update based on existence",
    
    # Validation
    "Validate": "Check data meets constraints",
    "Sanitize": "Clean data for safe use",
    "Normalize": "Transform to standard form",
    "Parse": "Extract structured data from text",
    
    # Transformation
    "Serialize": "Convert object to bytes/string",
    "Deserialize": "Reconstruct object from bytes/string",
    "Encode": "Transform to target format",
    "Decode": "Transform from source format",
    "Hash": "Compute fixed-size digest",
    "Encrypt": "Transform to unreadable form",
    "Decrypt": "Restore from encrypted form",
    
    # =========================================================================
    # ORGANIZATION PHASE (45 atoms) - "How code is structured"
    # =========================================================================
    
    # Classes
    "Class": "Define blueprint for objects",
    "AbstractClass": "Define partial blueprint requiring completion",
    "Interface": "Define contract without implementation",
    "Trait": "Define reusable behavior mixin",
    "Mixin": "Add functionality to classes",
    
    # Patterns
    "Repository": "Abstract data persistence",
    "Service": "Coordinate domain operations",
    "Factory": "Encapsulate object creation",
    "Builder": "Construct complex objects step-by-step",
    "Singleton": "Ensure single instance exists",
    "Adapter": "Convert between interfaces",
    "Decorator": "Add behavior dynamically",
    "Facade": "Simplify complex subsystem",
    "Proxy": "Control access to object",
    "Observer": "Notify dependents of changes",
    "Strategy": "Encapsulate interchangeable algorithms",
    "Command": "Encapsulate action as object",
    "State": "Change behavior based on state",
    "Template": "Define algorithm skeleton",
    "Visitor": "Add operations without modifying",
    
    # Modules
    "Module": "Group related code units",
    "Package": "Group related modules",
    "Namespace": "Prevent name collisions",
    "Import": "Bring external code into scope",
    "Export": "Make code available externally",
    
    # Architecture
    "Controller": "Handle external requests",
    "Gateway": "Adapt external systems",
    "Port": "Define interface to outside world",
    "UseCase": "Implement single user intention",
    "Aggregate": "Maintain consistency boundary",
    "DomainEvent": "Capture significant occurrence",
    "Saga": "Coordinate distributed transactions",
    
    # =========================================================================
    # EXECUTION PHASE (35 atoms) - "How code runs"
    # =========================================================================
    
    # Lifecycle
    "Constructor": "Initialize new instance",
    "Destructor": "Clean up before removal",
    "Initializer": "Set up after construction",
    "Finalizer": "Execute before garbage collection",
    
    # Invocation
    "Call": "Invoke function or method",
    "Callback": "Function passed for later invocation",
    "Hook": "Extension point for customization",
    "Middleware": "Intercept and process requests",
    "Interceptor": "Modify behavior transparently",
    
    # Concurrency
    "Thread": "Independent execution context",
    "Process": "Isolated execution environment",
    "Task": "Unit of concurrent work",
    "Future": "Placeholder for eventual result",
    "Promise": "Commitment to provide value",
    "Lock": "Ensure exclusive access",
    "Semaphore": "Control concurrent access count",
    "Channel": "Communicate between concurrent units",
    
    # Scheduling
    "CronJob": "Execute on time schedule",
    "Worker": "Process background tasks",
    "Queue": "Order tasks for processing",
    "Scheduler": "Determine when to execute",
    
    # Events
    "Event": "Signal that something happened",
    "EventEmitter": "Publish events to listeners",
    "EventListener": "Subscribe to events",
    "MessageBus": "Route messages between components",
    
    # Resources
    "Connection": "Link to external system",
    "Pool": "Manage reusable resources",
    "Cache": "Store frequently accessed data",
    "Transaction": "Group operations atomically",
    "Session": "Maintain state across requests",
    
    # Testing
    "Test": "Verify behavior",
    "Mock": "Simulate dependency",
    "Stub": "Provide canned responses",
    "Fixture": "Set up test environment",
}

# =============================================================================
# LAYER PURPOSES
# =============================================================================

LAYER_PURPOSE = {
    "presentation": "Display data and capture user intent",
    "application": "Orchestrate use cases and coordinate flow",
    "domain": "Express and enforce business rules",
    "infrastructure": "Handle technical concerns and external systems",
}

# =============================================================================
# RELATIONSHIP PURPOSES
# =============================================================================

RELATIONSHIP_PURPOSE = {
    "calls": "Invoke behavior of another component",
    "imports": "Depend on definitions from another module",
    "extends": "Inherit and specialize behavior",
    "implements": "Fulfill contract defined by interface",
    "contains": "Own and manage lifecycle of child",
    "references": "Know about without owning",
    "creates": "Bring instances into existence",
    "observes": "React to changes in another component",
    "validates": "Check correctness of data",
    "transforms": "Convert from one form to another",
}


def get_purpose(element_type: str) -> str:
    """
    Get the purpose of any code element type.
    
    Args:
        element_type: Role name, atom name, or layer name
    
    Returns:
        Purpose string describing why this element exists
    """
    # Check roles first
    if element_type in ROLE_PURPOSE:
        return ROLE_PURPOSE[element_type]
    
    # Check atoms
    if element_type in ATOM_PURPOSE:
        return ATOM_PURPOSE[element_type]
    
    # Check layers
    if element_type.lower() in LAYER_PURPOSE:
        return LAYER_PURPOSE[element_type.lower()]
    
    return f"Purpose not defined for '{element_type}'"


def list_all_purposes() -> dict:
    """Return all purposes organized by category"""
    return {
        "roles": ROLE_PURPOSE,
        "atoms": ATOM_PURPOSE,
        "layers": LAYER_PURPOSE,
        "relationships": RELATIONSHIP_PURPOSE,
        "total_defined": len(ROLE_PURPOSE) + len(ATOM_PURPOSE) + len(LAYER_PURPOSE) + len(RELATIONSHIP_PURPOSE)
    }


if __name__ == "__main__":
    import json
    
    print("="*70)
    print("PURPOSE REGISTRY - All Code Units Have Purpose")
    print("="*70)
    print()
    
    summary = list_all_purposes()
    
    print(f"Roles with purpose:         {len(ROLE_PURPOSE)}")
    print(f"Atoms with purpose:         {len(ATOM_PURPOSE)}")
    print(f"Layers with purpose:        {len(LAYER_PURPOSE)}")
    print(f"Relationships with purpose: {len(RELATIONSHIP_PURPOSE)}")
    print(f"TOTAL:                      {summary['total_defined']}")
    print()
    
    print("Sample purposes:")
    print(f"  Query:      {get_purpose('Query')}")
    print(f"  Repository: {get_purpose('Repository')}")
    print(f"  Entity:     {get_purpose('Entity')}")
    print(f"  ForLoop:    {get_purpose('ForLoop')}")
    print(f"  TryCatch:   {get_purpose('TryCatch')}")
