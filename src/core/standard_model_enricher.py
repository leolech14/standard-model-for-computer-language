"""
Standard Model Enricher
Applies the full Standard Model theory to particles:
- 58 Canonical Types from canonical_types.json
- RPBL Scores (Responsibility, Purity, Boundary, Lifecycle)
- Atom Mapping (DAT.BYT.A, LOG.FNC.M, etc.)
- Type Alias Resolution (Helper→Utility, Schema→DTO)
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from classification.universal_classifier import UniversalClassifier


class StandardModelEnricher:
    """Enriches particles with full Standard Model theory."""
    
    def __init__(self):
        self.canonical_types = {}       # type_id -> {description, rpbl, ring, aliases}
        self.type_aliases = {}          # alias -> canonical_type
        self.rpbl_scores = {}           # type_id -> {R, P, B, L}
        self.type_to_ring = {}         # type_id -> ring
        self.atoms = {}                 # atom_id -> {name, layer, description}
        self.atom_mappings = {}         # language -> {symbol_kind -> atom_id}
        
        self.classifier = UniversalClassifier()
        
        self._load_canonical_types()
        self._load_atoms()
    
    def _load_canonical_types(self):
        """Load all 58 canonical types from canonical_types.json"""
        patterns_dir = Path(__file__).parent.parent / "patterns"
        types_file = patterns_dir / "canonical_types.json"
        
        if not types_file.exists():
            print(f"⚠️  canonical_types.json not found at {types_file}")
            return
        
        with open(types_file) as f:
            data = json.load(f)
        
        # Parse rings and types
        for ring_name, ring_data in data.get('rings', {}).items():
            for type_def in ring_data.get('types', []):
                type_id = type_def.get('id')
                if not type_id:
                    continue
                
                self.canonical_types[type_id] = {
                    'description': type_def.get('description', ''),
                    'ring': ring_name,
                    'aliases': type_def.get('aliases', []),
                    'rpbl': type_def.get('rpbl', {})
                }
                
                # Store RPBL scores
                self.rpbl_scores[type_id] = type_def.get('rpbl', {})
                
                # Store ring mapping
                self.type_to_ring[type_id] = ring_name
                
                # Register aliases
                for alias in type_def.get('aliases', []):
                    self.type_aliases[alias] = type_id
                    self.type_aliases[alias.lower()] = type_id
                
                # Also register lowercase
                self.type_aliases[type_id.lower()] = type_id
        
        print(f"   ✓ Loaded {len(self.canonical_types)} canonical types")
    
    def _load_atoms(self):
        """Load atoms from atoms.json"""
        patterns_dir = Path(__file__).parent.parent / "patterns"
        atoms_file = patterns_dir / "atoms.json"
        
        if not atoms_file.exists():
            print(f"⚠️  atoms.json not found at {atoms_file}")
            return
        
        with open(atoms_file) as f:
            data = json.load(f)
        
        self.atoms = data.get('atoms', {})
        self.atom_mappings = data.get('mappings', {})
        print(f"   ✓ Loaded {len(self.atoms)} atoms")
    
    def resolve_canonical_type(self, type_name: str) -> str:
        """Resolve a type name to its canonical form."""
        if not type_name:
            return "Unknown"
        
        # Direct match
        if type_name in self.canonical_types:
            return type_name
        
        # Alias match
        if type_name in self.type_aliases:
            return self.type_aliases[type_name]
        
        # Case-insensitive match
        lower = type_name.lower()
        if lower in self.type_aliases:
            return self.type_aliases[lower]
        
        # Suffix matching for common patterns
        suffix_map = {
            'helper': 'Utility',
            'utils': 'Utility',
            'util': 'Utility',
            'schema': 'DTO',
            'request': 'DTO',
            'response': 'DTO',
            'model': 'Entity',
            'aggregate': 'Entity',
            'vo': 'ValueObject',
            'config': 'Configuration',
            'settings': 'Configuration',
            'handler': 'CommandHandler',
            'spec': 'Specification',
            'rule': 'Specification',
        }
        
        for suffix, canonical in suffix_map.items():
            if lower.endswith(suffix) or lower == suffix:
                return canonical
        
        return type_name  # Return as-is if no match
    
    def get_rpbl_scores(self, type_name: str) -> Dict[str, int]:
        """Get RPBL scores for a type."""
        canonical = self.resolve_canonical_type(type_name)
        return self.rpbl_scores.get(canonical, {
            'responsibility': 5,
            'purity': 5,
            'boundary': 5,
            'lifecycle': 5
        })
    
    def get_ring(self, type_name: str) -> Optional[str]:
        """Get the architectural ring for a type."""
        canonical = self.resolve_canonical_type(type_name)
        return self.type_to_ring.get(canonical)
    
    def get_atom(self, symbol_kind: str, role: str = None, language: str = 'python') -> str:
        """Get the Atom ID for a symbol kind and optional semantic role."""
        lang_map = self.atom_mappings.get(language, self.atom_mappings.get('python', {}))
        
        # 1. Direct mapping from language specific kinds
        atom_id = lang_map.get(symbol_kind)
        if atom_id:
            return atom_id
            
        # 2. Semantic Role Mapping (The "Smart" Layer)
        # Maps discovered roles (e.g. "Repository") to specific Atom IDs
        role_map = {
            # Organization - Services
            'Repository': 'ORG.SVC.M',
            'Service': 'ORG.SVC.M',
            'Gateway': 'ORG.SVC.M',
            'Cache': 'ORG.SVC.M',
            'EventBus': 'ORG.SVC.M',
            'MessageBroker': 'ORG.SVC.M',
            'InfrastructureService': 'ORG.SVC.M',
            
            # Organization - Aggregates
            'Entity': 'ORG.AGG.M',
            'ValueObject': 'ORG.AGG.M',
            'DTO': 'ORG.AGG.M',
            'Command': 'ORG.AGG.M',
            'Query': 'ORG.AGG.M',
            'Event': 'ORG.AGG.M',
            'Union': 'ORG.AGG.M',
            'GraphNode': 'ORG.AGG.M',
            'Tree': 'ORG.AGG.M',
            
            # Logic - Functions
            'Factory': 'LOG.FNC.M',
            'Builder': 'LOG.FNC.M',
            'Validator': 'LOG.FNC.M',
            'Mapper': 'LOG.FNC.M',
            'Hook': 'LOG.FNC.M',
            'Predicate': 'LOG.FNC.M',
            'RetryFunction': 'LOG.FNC.M',
            'CachedFunction': 'LOG.FNC.M',
            'Saga': 'LOG.FNC.M',
            'Pipeline': 'LOG.FNC.M',
            'Constructor': 'LOG.FNC.M',
            
            # Execution - Handlers
            'APIHandler': 'EXE.HDL.O',
            'EventHandler': 'EXE.HDL.O',
            'CommandHandler': 'EXE.HDL.O',
            'QueryHandler': 'EXE.HDL.O',
            'MessageConsumer': 'EXE.HDL.O',
            'SSEHandler': 'EXE.HDL.O',
            'gRPCHandler': 'EXE.HDL.O',
            
            # Execution - Probes/Workers
            'ChaosProbe': 'EXE.PRB.O',
            'CanaryCheck': 'EXE.PRB.O',
            'HealthCheck': 'EXE.PRB.O',
            'Sidecar': 'EXE.WRK.O',
            'ReplicaSet': 'EXE.WRK.O',
        }
        
        if role and role in role_map:
            return role_map[role]
        
        # 3. Fallback mappings based on symbol kind
        fallbacks = {
            'class': 'ORG.AGG.M',
            'function': 'LOG.FNC.M',
            'method': 'LOG.FNC.M',
            'module': 'ORG.MOD.O',
            'variable': 'DAT.VAR.A',
            'constant': 'DAT.PRM.A',
            'interface': 'ORG.AGG.M',
            'enum': 'DAT.PRM.A',
        }
        return fallbacks.get(symbol_kind, 'ORG.AGG.M')
    
    def enrich_particle(self, particle: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single particle with full Standard Model data."""
        
        # Resolve canonical type
        current_type = particle.get('type') or particle.get('role') or 'Unknown'
        canonical_type = self.resolve_canonical_type(current_type)
        
        # Update type/role to canonical
        particle['type'] = canonical_type
        particle['role'] = canonical_type
        
        # Add RPBL scores
        rpbl = self.get_rpbl_scores(canonical_type)
        particle['rpbl'] = rpbl
        # 2. Dimensions (T2 Atoms)
        # The classifier usually does this during extraction, but if not...
        if 'dimensions' not in particle:
             # print(f"DEBUG: Deriving dimensions for {particle.get('name')}")
             particle['dimensions'] = self.classifier._derive_dimensions(particle)
        
        # Add to dimensions if dimensions dict exists
        if 'dimensions' in particle:
            particle['dimensions']['responsibility'] = rpbl.get('responsibility', 5)
            particle['dimensions']['purity'] = rpbl.get('purity', 5)
            particle['dimensions']['boundary'] = rpbl.get('boundary', 5)
            particle['dimensions']['lifecycle'] = rpbl.get('lifecycle', 5)
        
        # Add ring from type definition
        ring = self.get_ring(canonical_type)
        if ring and not particle.get('ring'):
            particle['ring'] = ring
        
        # Add Atom mapping
        symbol_kind = particle.get('symbol_kind') or particle.get('kind') or 'unknown'
        
        # Check for T2 atom from UniversalClassifier (stored in dimensions)
        t2_atom = None
        if 'dimensions' in particle and 'D1_WHAT' in particle['dimensions']:
            d1 = particle['dimensions']['D1_WHAT']
            if d1 and d1.startswith('EXT.'):
                t2_atom = d1
        
        if t2_atom:
            particle['atom'] = t2_atom
        else:
            # Pass the resolved canonical role to get_atom to enable semantic detection
            particle['atom'] = self.get_atom(symbol_kind, role=canonical_type)
        
        return particle
    
    def enrich_all(self, particles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich all particles with Standard Model data."""
        for particle in particles:
            self.enrich_particle(particle)
        return particles


# Singleton instance
_enricher = None

def get_standard_model_enricher() -> StandardModelEnricher:
    """Get or create the singleton enricher instance."""
    global _enricher
    if _enricher is None:
        _enricher = StandardModelEnricher()
    return _enricher


def enrich_with_standard_model(particles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convenience function to enrich particles with Standard Model."""
    enricher = get_standard_model_enricher()
    return enricher.enrich_all(particles)


if __name__ == "__main__":
    # Test the enricher
    enricher = StandardModelEnricher()
    
    test_particles = [
        {'name': 'UserRepository', 'type': 'Internal', 'symbol_kind': 'class'},
        {'name': 'CreateUserCommand', 'type': 'Command', 'symbol_kind': 'class'},
        {'name': 'helper_function', 'type': 'Utility', 'symbol_kind': 'function'},
        {'name': 'UserSchema', 'type': 'DTO', 'symbol_kind': 'class'},
    ]
    
    print("\nTest enrichment:")
    for p in test_particles:
        enricher.enrich_particle(p)
        print(f"  {p['name']}: type={p['type']}, rpbl={p.get('rpbl')}, atom={p.get('atom')}")
