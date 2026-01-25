# Research: What is the relationship between atoms and roles in this project?

> **Date:** 2026-01-23 15:07:20
> **Source:** gemini
> **Model:** gemini-2.0-flash-001
> **Checksum:** `sha256:e2848dfdc7379f4c2c946b191b7e47500cea67ab265bb47622783449d8f294f5`
> **Raw JSON:** `raw/20260123_150720_what_is_the_relationship_between_atoms_and_roles_i.json`

---

## Query

What is the relationship between atoms and roles in this project?

---

## Response

```tool_code
from collections import Counter
import json

def analyze_atoms_and_roles(file_path="standard-model-of-code/docs/MODEL.md"):
    """
    Analyzes the relationship between atoms and roles in the project based on the provided context.
    """
    
    try:
        # Load the MODEL.md file to understand the theoretical relationship
        with open(file_path, "r") as f:
            model_md = f.read()
        
        # This is a VERY high-level theoretical relationship
        # The relationship is further defined within the code and schema (see below)
        theoretical_relationship = """
        Atoms and roles are fundamental building blocks of the Standard Model of Code. 
        Atoms represent the 'WHAT' (syntactic element) and roles represent the 'WHY' (semantic purpose).
        They are distinct but linked: every atom is classified with a role.
        """
    except FileNotFoundError:
        theoretical_relationship = "MODEL.md not found"

    # Load relevant schema and code files to understand implemented relationships
    # There are many dimensions and relationships defined in the code so it is
    # important to check the schema and code to see how these are related.
    
    # Enumerate the atoms
    def get_atoms(file_path="standard-model-of-code/schema/fixed/atoms.json"):
        try:
             with open(file_path, "r") as f:
                atoms = json.load(f)
             num_atoms = len(atoms.get("atoms", {})) if atoms else 0
             return num_atoms, file_path
        except:
            return 0, "standard-model-of-code/schema/fixed/atoms.json"

    num_atoms, atoms_file = get_atoms()

    # Enumerate the roles
    def get_roles(file_path="standard-model-of-code/schema/fixed/roles.json"):
        try:
            with open(file_path, "r") as f:
                roles = json.load(f)
            num_roles = len(roles.get("roles", {})) if roles else 0
            return num_roles, file_path
        except:
            return 0, "standard-model-of-code/schema/fixed/roles.json"
    num_roles, roles_file = get_roles()

    # Relationship in code
    classification_code = """
     # Standard Model of Code project - Atoms and Roles
     For each code element (particle), a 'what' (atom) is paired with a 'why' (role).
     A 4 dimensional space is constructed:
       - WHAT: What type of atom is this?
       - LAYER: Architectural layer
       - ROLE: Semantic role (from 33 canonical roles)
       - TRUST: Trust level (0-100)
    """

    ###
    from collections import defaultdict
    import re

    def extract_code_from_file(file_path: str) -> str:
        """Extract code from a file, returning empty string on failure"""
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def extract_dependencies(file_content: str) -> list[str]:
        """Extract import statements from the code"""
        import_list = []
        for line in file_content.splitlines():
            if line.strip().startswith(("import ", "from ")):
                import_list.append(line.strip())
        return import_list

    # ---------------------------------------------------------
    # Extract imports from the specified code (This is for the report)
    # ---------------------------------------------------------

    file_content = extract_code_from_file("standard-model-of-code/src/core/unified_analysis.py")
    imports = extract_dependencies(file_content)

    # ---------------------------------------------------------
    # Extract the most common atom by type
    # ---------------------------------------------------------
    def get_most_common_atom_by_type(file_path="standard-model-of-code/src/core/full_analysis.py"):
      most_common_atom_by_type = ""
      body = extract_code_from_file(file_path)
      atom_matches = re.findall(r"n\['atom'] = '([^']+)'", body)
      if atom_matches:
        atom_counts = Counter(atom_matches)
        top = atom_counts.most_common(1)
        if top:
          most_common_atom_by_type = top[0][0]
      return most_common_atom_by_type

    most_common_atom_by_type = get_most_common_atom_by_type()

    report = f"""
## Relationship between Atoms and Roles

{theoretical_relationship}

The project uses {num_atoms} atoms (defined in {atoms_file}) and {num_roles} roles (defined in {roles_file}).

In the code, a typical particle is classified with a 'what' (atom) and a 'why' (role). This relationship is codified in the _derive_dimensions in the `universal_classifier.py`.  

The most common atom is: {most_common_atom_by_type}

Code Description:
```code
{classification_code}
```

"""

    return report

analysis = analyze_atoms_and_roles()
print(analysis)
```

---

## Citations

_No citations provided_
