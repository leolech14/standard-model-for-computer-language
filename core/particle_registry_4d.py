#!/usr/bin/env python3
# ⚠️ DEPRECATED: This 4D registry groups dimensions for convenience.
# The canonical model is 8D (particle_registry_8d.py).
# See STANDARD_MODEL_PAPER.md Section 2.3 for authoritative spec.
"""
4D Particle Registry — Canonical Storage for Multi-Dimensional Code Physics

This module provides:
1. Schema definition for 4D particles (WHAT + HOW + WHERE + WHY)
2. Registry management (add, update, query)
3. Export to JSON for persistence and LLM consumption

The 4D Particle format:
{
    "id": "P001",
    "name": "UserRepository",
    "file": "domain/user/repository.py",
    "line": 45,
    
    # WHAT (Material Composition)
    "what": {
        "continent": "Organization",
        "fundamental": "Aggregates",
        "level": "molecule",
        "atom_type": "class_definition"
    },
    
    # HOW (Behavior)
    "how": {
        "is_pure": false,
        "is_async": true,
        "is_mutating": true,
        "has_side_effects": true
    },
    
    # WHERE (Context)
    "where": {
        "architectural_layer": "domain",
        "crosses_boundary": false,
        "module_path": "domain.user.repository"
    },
    
    # WHY (Intent)
    "why": {
        "pattern": "Repository",
        "pattern_confidence": 0.9,
        "role": "Repository",
        "smells": [],
        "smell_severity": 0.0
    }
}
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict


@dataclass
class ParticleWHAT:
    """Material composition (Dimension 1)."""
    continent: str = "unknown"           # DATA/LOGIC/ORG/EXEC
    fundamental: str = "unknown"         # Primitives/Aggregates/etc.
    level: str = "atom"                  # atom/molecule/organelle
    atom_type: str = ""                  # AST type


@dataclass
class ParticleHOW:
    """Behavior properties (Dimension 2)."""
    is_pure: Optional[bool] = None
    is_async: Optional[bool] = None
    is_mutating: Optional[bool] = None
    has_side_effects: Optional[bool] = None


@dataclass
class ParticleWHERE:
    """Contextual location (Dimension 3)."""
    architectural_layer: str = "unknown"  # domain/application/infrastructure/presentation
    crosses_boundary: bool = False
    module_path: str = ""


@dataclass
class ParticleWHY:
    """Intent and meaning (Dimension 4)."""
    pattern: Optional[str] = None         # Factory, Repository, Singleton...
    pattern_confidence: float = 0.0
    role: Optional[str] = None            # Entity, UseCase, Service...
    smells: List[str] = field(default_factory=list)
    smell_severity: float = 0.0


@dataclass
class Particle4D:
    """
    A complete 4-dimensional code particle.
    
    This is the atomic unit of our code physics system.
    Every component in your codebase can be described by this structure.
    """
    id: str
    name: str
    file: str
    line: int
    
    # The 4 Dimensions
    what: ParticleWHAT = field(default_factory=ParticleWHAT)
    how: ParticleHOW = field(default_factory=ParticleHOW)
    where: ParticleWHERE = field(default_factory=ParticleWHERE)
    why: ParticleWHY = field(default_factory=ParticleWHY)
    
    # Metadata
    semantic_id: str = ""       # The full semantic ID string
    confidence: float = 0.0     # Overall classification confidence
    discovered_at: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "file": self.file,
            "line": self.line,
            "what": asdict(self.what),
            "how": asdict(self.how),
            "where": asdict(self.where),
            "why": asdict(self.why),
            "semantic_id": self.semantic_id,
            "confidence": self.confidence,
            "discovered_at": self.discovered_at,
        }
    
    @classmethod
    def from_semantic_id(cls, sid) -> 'Particle4D':
        """Create a Particle4D from a SemanticID object."""
        props = sid.properties
        
        return cls(
            id=sid.content_hash,
            name=sid.name,
            file=sid.module_path.replace(".", "/") + ".py",
            line=props.get("line", 0),
            
            what=ParticleWHAT(
                continent=sid.continent.value if hasattr(sid.continent, 'value') else str(sid.continent),
                fundamental=sid.fundamental.value if hasattr(sid.fundamental, 'value') else str(sid.fundamental),
                level=sid.level.value if hasattr(sid.level, 'value') else str(sid.level),
                atom_type=props.get("type", ""),
            ),
            
            how=ParticleHOW(
                is_pure=getattr(sid, 'is_pure', None),
                is_async=getattr(sid, 'is_async', None) or props.get("async", False),
                is_mutating=getattr(sid, 'is_mutating', None),
                has_side_effects=getattr(sid, 'has_side_effects', None),
            ),
            
            where=ParticleWHERE(
                architectural_layer=getattr(sid, 'architectural_layer', "unknown") or "unknown",
                crosses_boundary=getattr(sid, 'crosses_boundary', False) or False,
                module_path=sid.module_path,
            ),
            
            why=ParticleWHY(
                pattern=props.get("pattern"),
                pattern_confidence=props.get("pattern_confidence", 0.0),
                role=props.get("type"),
                smells=props.get("smells", "").split(",") if props.get("smells") else [],
                smell_severity=props.get("smell_severity", 0.0),
            ),
            
            semantic_id=sid.to_string(),
            confidence=props.get("confidence", 50) / 100.0,
            discovered_at=datetime.now().isoformat(),
        )


class ParticleRegistry4D:
    """
    The 4D Particle Registry — Canonical storage for multi-dimensional code knowledge.
    
    Usage:
        registry = ParticleRegistry4D()
        registry.add_from_semantic_ids(semantic_ids)
        registry.save("output/particle_registry_4d.json")
    """
    
    def __init__(self, path: Optional[str] = None):
        self.particles: Dict[str, Particle4D] = {}
        self.path = Path(path) if path else None
        
        if self.path and self.path.exists():
            self.load()
    
    def add(self, particle: Particle4D):
        """Add a particle to the registry."""
        self.particles[particle.id] = particle
    
    def add_from_semantic_ids(self, semantic_ids: List) -> int:
        """
        Bulk add particles from SemanticID objects.
        
        Returns: Number of particles added.
        """
        count = 0
        for sid in semantic_ids:
            try:
                particle = Particle4D.from_semantic_id(sid)
                self.add(particle)
                count += 1
            except Exception as e:
                print(f"⚠️  Could not convert SID {sid.name}: {e}")
        return count
    
    def get_stats(self) -> Dict:
        """Get registry statistics across all dimensions."""
        by_continent = {}
        by_layer = {}
        by_pattern = {}
        by_smell = {}
        
        pure_count = 0
        impure_count = 0
        async_count = 0
        boundary_violations = 0
        
        for p in self.particles.values():
            # WHAT
            c = p.what.continent
            by_continent[c] = by_continent.get(c, 0) + 1
            
            # WHERE
            l = p.where.architectural_layer
            by_layer[l] = by_layer.get(l, 0) + 1
            
            if p.where.crosses_boundary:
                boundary_violations += 1
            
            # HOW
            if p.how.is_pure is True:
                pure_count += 1
            elif p.how.is_pure is False:
                impure_count += 1
            
            if p.how.is_async:
                async_count += 1
            
            # WHY
            if p.why.pattern:
                by_pattern[p.why.pattern] = by_pattern.get(p.why.pattern, 0) + 1
            
            for smell in p.why.smells:
                if smell:
                    by_smell[smell] = by_smell.get(smell, 0) + 1
        
        return {
            "total_particles": len(self.particles),
            "by_continent": by_continent,
            "by_layer": by_layer,
            "by_pattern": by_pattern,
            "by_smell": by_smell,
            "pure_count": pure_count,
            "impure_count": impure_count,
            "async_count": async_count,
            "boundary_violations": boundary_violations,
        }
    
    def to_dict(self) -> Dict:
        """Export registry to dictionary."""
        return {
            "version": "4D-1.0",
            "timestamp": datetime.now().isoformat(),
            "stats": self.get_stats(),
            "particles": {pid: p.to_dict() for pid, p in self.particles.items()},
        }
    
    def save(self, path: Optional[str] = None):
        """Save registry to JSON file."""
        save_path = Path(path) if path else self.path
        if not save_path:
            save_path = Path("output/particle_registry_4d.json")
        
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(json.dumps(self.to_dict(), indent=2))
        
        print(f"💾 Saved 4D Registry: {save_path}")
        print(f"   Particles: {len(self.particles)}")
        return save_path
    
    def load(self):
        """Load registry from JSON file."""
        if not self.path or not self.path.exists():
            return
        
        try:
            data = json.loads(self.path.read_text())
            for pid, pdata in data.get("particles", {}).items():
                self.particles[pid] = Particle4D(
                    id=pdata["id"],
                    name=pdata["name"],
                    file=pdata["file"],
                    line=pdata["line"],
                    what=ParticleWHAT(**pdata.get("what", {})),
                    how=ParticleHOW(**pdata.get("how", {})),
                    where=ParticleWHERE(**pdata.get("where", {})),
                    why=ParticleWHY(**pdata.get("why", {})),
                    semantic_id=pdata.get("semantic_id", ""),
                    confidence=pdata.get("confidence", 0.0),
                    discovered_at=pdata.get("discovered_at", ""),
                )
            print(f"📂 Loaded 4D Registry: {len(self.particles)} particles")
        except Exception as e:
            print(f"⚠️  Could not load registry: {e}")
    
    def query(self, 
              continent: Optional[str] = None,
              layer: Optional[str] = None,
              pattern: Optional[str] = None,
              is_pure: Optional[bool] = None,
              has_smells: Optional[bool] = None) -> List[Particle4D]:
        """
        Query particles by dimension filters.
        
        Example:
            # Find all impure domain entities
            registry.query(layer="domain", is_pure=False)
            
            # Find all Repository patterns
            registry.query(pattern="Repository")
            
            # Find all code smells
            registry.query(has_smells=True)
        """
        results = []
        
        for p in self.particles.values():
            if continent and p.what.continent != continent:
                continue
            if layer and p.where.architectural_layer != layer:
                continue
            if pattern and p.why.pattern != pattern:
                continue
            if is_pure is not None and p.how.is_pure != is_pure:
                continue
            if has_smells is True and not p.why.smells:
                continue
            if has_smells is False and p.why.smells:
                continue
            
            results.append(p)
        
        return results


# CLI for testing
if __name__ == "__main__":
    print("=== 4D Particle Registry Test ===\n")
    
    registry = ParticleRegistry4D()
    
    # Create sample particles
    p1 = Particle4D(
        id="p001",
        name="UserRepository",
        file="domain/user/repository.py",
        line=10,
        what=ParticleWHAT(continent="Organization", fundamental="Aggregates", level="molecule"),
        how=ParticleHOW(is_pure=False, is_async=True, has_side_effects=True),
        where=ParticleWHERE(architectural_layer="domain", crosses_boundary=False),
        why=ParticleWHY(pattern="Repository", pattern_confidence=0.9),
    )
    
    p2 = Particle4D(
        id="p002",
        name="GodService",
        file="application/god_service.py",
        line=1,
        what=ParticleWHAT(continent="Logic & Flow", fundamental="Functions", level="organelle"),
        how=ParticleHOW(is_pure=False, is_mutating=True),
        where=ParticleWHERE(architectural_layer="application", crosses_boundary=True),
        why=ParticleWHY(pattern="Service", smells=["GodClass", "FeatureEnvy"], smell_severity=0.8),
    )
    
    registry.add(p1)
    registry.add(p2)
    
    # Print stats
    stats = registry.get_stats()
    print(f"📊 Registry Stats:")
    print(f"   Total Particles: {stats['total_particles']}")
    print(f"   By Continent: {stats['by_continent']}")
    print(f"   By Layer: {stats['by_layer']}")
    print(f"   By Pattern: {stats['by_pattern']}")
    print(f"   By Smell: {stats['by_smell']}")
    print(f"   Pure/Impure: {stats['pure_count']}/{stats['impure_count']}")
    print(f"   Boundary Violations: {stats['boundary_violations']}")
    
    # Query examples
    print(f"\n🔍 Query: All Repositories")
    repos = registry.query(pattern="Repository")
    for r in repos:
        print(f"   - {r.name} @ {r.file}")
    
    print(f"\n🔍 Query: Code with smells")
    smelly = registry.query(has_smells=True)
    for s in smelly:
        print(f"   - {s.name}: {s.why.smells}")
    
    # Save
    registry.save("/tmp/test_4d_registry.json")
