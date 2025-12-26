
import json
import shutil
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_DIR = REPO_ROOT / "output"
CANON_PATH = BASE_DIR / "atom_registry_canon.json"
UNKNOWN_PATH = BASE_DIR / "unknown_registry.json"
BACKUP_PATH = BASE_DIR / "atom_registry_canon.v13.bak"

def categorize_atom(name, ast_type):
    """
    Apply the 2-Tier Taxonomy Strategy (Heuristics).
    Returns (Continent, Fundamental).
    """
    name = name.lower()
    ast_type = ast_type.lower()
    
    # 1. ORGANIZATION (Green)
    if any(x in ast_type for x in ['import', 'module', 'package', 'dot', 'alias', 'from']):
        return "Organization", "Modules"
    if any(x in ast_type for x in ['class', 'def', 'type', 'interface', 'generic']):
        if 'def' in ast_type or 'function' in ast_type:
            return "Logic & Flow", "Functions" # 'Def' keyword is part of function def
        if 'class' in ast_type:
             return "Organization", "Aggregates"
        return "Organization", "Types"
        
    # 2. DATA (Cyan)
    if any(x in ast_type for x in ['string', 'float', 'integer', 'bool', 'true', 'false', 'none', 'literal', 'constant', 'number']):
        return "Data Foundations", "Primitives"
    if any(x in ast_type for x in ['list', 'dict', 'tuple', 'set', 'array', 'pair']):
        return "Data Foundations", "Primitives" # Structural primitives
    if any(x in ast_type for x in ['assign', 'field', 'var', 'identifier', 'pattern']):
        return "Data Foundations", "Variables"

    # 3. LOGIC (Magenta)
    if any(x in ast_type for x in ['if', 'else', 'for', 'while', 'try', 'catch', 'match', 'case', 'with']):
        return "Logic & Flow", "Control Structures"
    if any(x in ast_type for x in ['return', 'yield', 'break', 'continue', 'raise', 'throw', 'assert', 'await']):
        return "Logic & Flow", "Statements"
    if any(x in ast_type for x in ['expr', 'op', 'lambda', 'call', 'arg', 'param', 'compare', 'binary', 'unary']):
        return "Logic & Flow", "Expressions"
    if any(x in ast_type for x in ['stmt', 'statement']):
        return "Logic & Flow", "Statements"
    
    # 4. EXECUTION (Amber)
    if any(x in ast_type for x in ['main', 'print', 'exec', 'eval', 'async']):
        return "Execution", "Runtime"
    
    # Fallback / Specific Tokens
    if ast_type in ['.', ',', ':', ';']:
        return "Organization", "Syntax" # Connectors
    if ast_type in ['=', '+=', '-=']:
        return "Logic & Flow", "Statements" # Assignment is an action
    if ast_type in ['(', ')', '[', ']', '{', '}']:
        return "Organization", "Syntax"
    
    # Final Fallback
    return "Logic & Flow", "Expressions"

def main():
    print("🚀 Starting Canonization Protocol (v13 -> v14)...")
    
    # 1. Backup
    shutil.copy(CANON_PATH, BACKUP_PATH)
    print(f"📦 Backup created: {BACKUP_PATH}")
    
    # 2. Load Data
    canon = json.loads(CANON_PATH.read_text())
    unknowns = json.loads(UNKNOWN_PATH.read_text())
    
    print(f"📊 Current Canon: {len(canon['atoms'])} atoms")
    print(f"📊 Unknown Candidates: {len(unknowns)}")
    
    # 3. Process Unknowns
    next_id = canon['stats'].get('next_id', 150)
    new_atoms = []
    
    # Get unique AST types to avoid duplicates if registry has multiple entries for same type
    # (Though unknown registry is keyed by hash, multiple hashes might share AST type? 
    #  Let's trust the unknown registry distinctness for now, but dedupe by ast_type against canon)
    
    existing_ast_types = set()
    for atom in canon['atoms'].values():
        existing_ast_types.update(atom.get('ast_types', []))
    
    # Sort unknowns by frequency
    sorted_unknowns = sorted(unknowns.values(), key=lambda x: x['occurrence_count'], reverse=True)
    
    count_added = 0
    
    for ua in sorted_unknowns:
        ast_type = ua['ast_type']
        
        # SKIP if already known
        if ast_type in existing_ast_types:
            continue
            
        # CLASSIFY
        continent, fundamental = categorize_atom(ua.get('proposed_name', ast_type), ast_type)
        
        # CREATE ATOM
        new_atom = {
            "id": next_id,
            "name": ua.get('proposed_name') or ast_type.capitalize(),
            "ast_types": [ast_type],
            "continent": continent,
            "fundamental": fundamental,
            "level": ua.get('proposed_level', 'atom'),
            "description": f"Canonized from observations. {ua.get('occurrence_count', 0)} occurrences.",
            "detection_rule": f"ast_type == {ast_type}",
            "source": "discovered_v14",
            "discovered_at": datetime.now().isoformat()
        }
        
        canon['atoms'][str(next_id)] = new_atom
        new_atoms.append(new_atom)
        existing_ast_types.add(ast_type)
        next_id += 1
        count_added += 1

    # 4. Update Stats
    canon['version'] = "14.0" # UPGRADE
    canon['timestamp'] = datetime.now().isoformat()
    canon['stats']['total_atoms'] = len(canon['atoms'])
    canon['stats']['next_id'] = next_id
    
    # Recalculate deep stats
    stats_cont = {"Data Foundations": 0, "Logic & Flow": 0, "Organization": 0, "Execution": 0}
    stats_src = {"original": 0, "discovered": 0, "discovered_v14": 0}
    
    for a in canon['atoms'].values():
        c = a.get('continent', 'Logic & Flow')
        if c in stats_cont: stats_cont[c] += 1
        else: stats_cont['Logic & Flow'] += 1
        
        s = a.get('source', 'discovered')
        if s == 'original': stats_src['original'] += 1
        elif s == 'discovered_v14': stats_src['discovered_v14'] += 1
        else: stats_src['discovered'] += 1
        
    canon['stats']['by_continent'] = stats_cont
    canon['stats']['by_source'] = stats_src
    
    # 5. Save
    CANON_PATH.write_text(json.dumps(canon, indent=2))
    
    print("-" * 50)
    print(f"✅ Canonization Complete.")
    print(f"🆕 Atoms Added: {count_added}")
    print(f"⚛️  Total Atoms (v14): {canon['stats']['total_atoms']}")
    print(f"📜 Version: {canon['version']}")
    
    # Dump Summary
    for a in new_atoms[:10]:
        print(f"   + {a['name']} ({a['continent']} / {a['fundamental']})")
    if len(new_atoms) > 10:
        print(f"   ... and {len(new_atoms)-10} more.")

if __name__ == "__main__":
    main()
