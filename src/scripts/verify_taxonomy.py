import json
import sys

try:
    with open('patterns/taxonomy.json', 'r') as f:
        data = json.load(f)
    
    atoms = data.get('atoms', [])
    total_atoms = len(atoms)
    unique_ids = set(a['unique_id'] for a in atoms)
    
    print(f"Total atoms found: {total_atoms}")
    print(f"Unique IDs count: {len(unique_ids)}")
    
    if total_atoms == 167 and len(unique_ids) == 167:
        print("SUCCESS: Taxonomy has exactly 167 unique atoms.")
        sys.exit(0)
    else:
        print("FAILURE: Counts do not match.")
        if total_atoms != 167:
            print(f"Expected 167 atoms, got {total_atoms}")
        if len(unique_ids) != total_atoms:
            print("Duplicate IDs detected!")
        sys.exit(1)
        
except Exception as e:
    print(f"Error reading taxonomy: {e}")
    sys.exit(1)
