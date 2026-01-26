"""
Projectome Omniscience Module (POM)
Complete Visibility Across the Entire Project Universe

This module provides:
1. Complete inventory of PROJECTOME (CODOME ⊔ CONTEXTOME)
2. Purpose Field analysis across both universes
3. Symmetry detection (SYMMETRIC, ORPHAN, PHANTOM, DRIFT)
4. Self-referential manifest generation (Lawvere fixed point)

Mathematical Grounding:
- P = C ⊔ X is NECESSARY (Lawvere's Fixed-Point Theorem)
- See: docs/theory/FOUNDATIONS_INTEGRATION.md

Usage:
    pom = ProjectomeOmniscience(project_root="/path/to/project")
    manifest = pom.scan()
    pom.save_manifest("projectome_manifest.yaml")
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
import json
import yaml
import re
from collections import Counter


# =============================================================================
# ENUMS
# =============================================================================

class Universe(Enum):
    """The two universes of PROJECTOME"""
    CODOME = "codome"          # Executable code
    CONTEXTOME = "contextome"  # Non-executable content


class SymmetryState(Enum):
    """Symmetry states between code and documentation"""
    SYMMETRIC = "symmetric"    # Paired and aligned
    ORPHAN = "orphan"          # Code without docs
    PHANTOM = "phantom"        # Docs without code
    DRIFT = "drift"            # Paired but misaligned


class EntityType(Enum):
    """Types of entities in PROJECTOME"""
    # Codome types
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    VARIABLE = "variable"

    # Contextome types
    DOCUMENT = "document"
    SECTION = "section"
    DEFINITION = "definition"
    CONFIG = "config"
    TASK = "task"
    SCHEMA = "schema"
    RESEARCH = "research"

    # Meta types
    MANIFEST = "manifest"
    SPECIFICATION = "specification"


class Layer(Enum):
    """Architectural layers"""
    PRESENTATION = "presentation"
    APPLICATION = "application"
    DOMAIN = "domain"
    INFRASTRUCTURE = "infrastructure"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    UNKNOWN = "unknown"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Location:
    """Position within a file"""
    start_line: int = 0
    end_line: int = 0
    section: Optional[str] = None


@dataclass
class Purpose:
    """Purpose annotation for an entity"""
    role: str = "unknown"
    intent: str = ""
    confidence: float = 0.0
    layer: Layer = Layer.UNKNOWN


@dataclass
class Edge:
    """Relationship between entities"""
    target: str
    type: str  # calls, imports, describes, references
    universe_crossing: bool = False


@dataclass
class Entity:
    """Universal entity in PROJECTOME"""
    id: str
    universe: Universe
    type: EntityType
    name: str
    path: str
    location: Location = field(default_factory=Location)
    purpose: Purpose = field(default_factory=Purpose)
    edges: List[Edge] = field(default_factory=list)

    # Symmetry tracking
    symmetry_state: SymmetryState = SymmetryState.ORPHAN
    pair_id: Optional[str] = None
    drift_score: float = 0.0


@dataclass
class SymmetryReport:
    """Report on code-documentation symmetry"""
    symmetric_count: int = 0
    orphan_count: int = 0
    phantom_count: int = 0
    drift_count: int = 0

    pairs: List[Tuple[str, str]] = field(default_factory=list)
    orphans: List[str] = field(default_factory=list)
    phantoms: List[str] = field(default_factory=list)
    drifted: List[Tuple[str, str, float]] = field(default_factory=list)


@dataclass
class PurposeFieldResult:
    """Purpose Field analysis results"""
    coverage: float = 0.0
    coherence: float = 0.0
    entropy: float = 0.0
    layer_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class ProjectomeManifest:
    """Complete manifest of PROJECTOME"""
    generated: str
    generator: str = "POM v1.0"
    self_reference: bool = True

    # Universe counts
    codome_files: int = 0
    codome_entities: int = 0
    contextome_files: int = 0
    contextome_entities: int = 0

    # Totals
    total_entities: int = 0
    total_edges: int = 0
    cross_universe_edges: int = 0

    # Symmetry
    symmetry: SymmetryReport = field(default_factory=SymmetryReport)

    # Purpose
    purpose_field: PurposeFieldResult = field(default_factory=PurposeFieldResult)

    # Entities
    entities: List[Entity] = field(default_factory=list)


# =============================================================================
# CODOME SCANNER
# =============================================================================

class CodomeScanner:
    """Scans CODOME using Collider output"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def scan(self, unified_analysis_path: Optional[Path] = None) -> List[Entity]:
        """
        Extract entities from Collider's unified_analysis.json
        """
        # Find unified_analysis.json
        if unified_analysis_path is None:
            unified_analysis_path = self._find_unified_analysis()

        if unified_analysis_path is None or not unified_analysis_path.exists():
            print("Warning: No unified_analysis.json found. Run Collider first.")
            return []

        with open(unified_analysis_path) as f:
            data = json.load(f)

        entities = []

        for node in data.get('nodes', []):
            entity = Entity(
                id=f"code::{node.get('id', '')}",
                universe=Universe.CODOME,
                type=self._map_kind_to_type(node.get('kind', '')),
                name=node.get('name', node.get('id', '')),
                path=node.get('file_path', ''),
                location=Location(
                    start_line=node.get('start_line', 0),
                    end_line=node.get('end_line', 0)
                ),
                purpose=Purpose(
                    role=node.get('semantic_role', 'unknown'),
                    intent=node.get('docstring', ''),
                    # Use coherence_score from Stage 3.7 as confidence
                    confidence=node.get('coherence_score', node.get('purpose_confidence', 0.0)),
                    layer=self._map_layer(node.get('layer', ''))
                ),
                edges=self._extract_edges(node)
            )
            entities.append(entity)

        return entities

    def _find_unified_analysis(self) -> Optional[Path]:
        """Find unified_analysis.json in common locations"""
        candidates = [
            self.project_root / '.collider' / 'unified_analysis.json',
            self.project_root / 'collider_output' / 'unified_analysis.json',
            self.project_root / 'unified_analysis.json',
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _map_kind_to_type(self, kind: str) -> EntityType:
        """Map Collider kind to EntityType"""
        mapping = {
            'function': EntityType.FUNCTION,
            'method': EntityType.FUNCTION,
            'class': EntityType.CLASS,
            'module': EntityType.MODULE,
            'variable': EntityType.VARIABLE,
        }
        return mapping.get(kind.lower(), EntityType.FUNCTION)

    def _map_layer(self, layer: str) -> Layer:
        """Map layer string to Layer enum"""
        try:
            return Layer(layer.lower())
        except ValueError:
            return Layer.UNKNOWN

    def _extract_edges(self, node: dict) -> List[Edge]:
        """Extract edges from node data"""
        edges = []
        for edge in node.get('edges', []):
            edges.append(Edge(
                target=f"code::{edge.get('target', '')}",
                type=edge.get('type', 'unknown'),
                universe_crossing=False
            ))
        return edges


# =============================================================================
# CONTEXTOME SCANNER
# =============================================================================

class ContextomeScanner:
    """Scans CONTEXTOME (docs, configs, etc.)"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def scan(self) -> List[Entity]:
        """Scan all contextome files"""
        entities = []

        # Documentation
        entities.extend(self._scan_markdown())

        # Configuration
        entities.extend(self._scan_yaml())
        entities.extend(self._scan_json_config())

        # Agent artifacts
        entities.extend(self._scan_agent())

        return entities

    def _scan_markdown(self) -> List[Entity]:
        """Scan Markdown documentation"""
        entities = []

        for md_file in self.project_root.rglob('*.md'):
            # Skip node_modules, .git, etc.
            if self._should_skip(md_file):
                continue

            try:
                content = md_file.read_text(encoding='utf-8')
                rel_path = str(md_file.relative_to(self.project_root))

                # Document entity
                doc_id = f"doc::{rel_path}"
                doc_entity = Entity(
                    id=doc_id,
                    universe=Universe.CONTEXTOME,
                    type=EntityType.DOCUMENT,
                    name=md_file.stem,
                    path=rel_path,
                    purpose=Purpose(
                        role='documentation',
                        intent=self._extract_title(content),
                        layer=Layer.DOCUMENTATION
                    ),
                    edges=[]
                )

                # Extract code references
                for ref in self._extract_code_refs(content):
                    doc_entity.edges.append(Edge(
                        target=f"code::{ref}",
                        type='describes',
                        universe_crossing=True
                    ))

                entities.append(doc_entity)

                # Section entities
                for heading in self._extract_headings(content):
                    section_id = f"section::{rel_path}::{heading['slug']}"
                    entities.append(Entity(
                        id=section_id,
                        universe=Universe.CONTEXTOME,
                        type=EntityType.SECTION,
                        name=heading['text'],
                        path=rel_path,
                        location=Location(
                            start_line=heading['line'],
                            section=heading['text']
                        ),
                        purpose=Purpose(
                            role='section',
                            intent=heading['text'],
                            layer=Layer.DOCUMENTATION
                        )
                    ))

            except Exception as e:
                print(f"Warning: Could not parse {md_file}: {e}")

        return entities

    def _scan_yaml(self) -> List[Entity]:
        """Scan YAML configuration files"""
        entities = []

        for yaml_file in self.project_root.rglob('*.yaml'):
            if self._should_skip(yaml_file):
                continue

            try:
                rel_path = str(yaml_file.relative_to(self.project_root))
                entities.append(Entity(
                    id=f"config::{rel_path}",
                    universe=Universe.CONTEXTOME,
                    type=EntityType.CONFIG,
                    name=yaml_file.stem,
                    path=rel_path,
                    purpose=Purpose(
                        role='configuration',
                        intent=f"Configuration: {yaml_file.stem}",
                        layer=Layer.CONFIGURATION
                    )
                ))
            except Exception as e:
                print(f"Warning: Could not process {yaml_file}: {e}")

        return entities

    def _scan_json_config(self) -> List[Entity]:
        """Scan JSON schema and config files"""
        entities = []

        for json_file in self.project_root.rglob('*.json'):
            if self._should_skip(json_file):
                continue

            # Only include config/schema, not analysis outputs
            if 'schema' in str(json_file) or 'config' in str(json_file):
                try:
                    rel_path = str(json_file.relative_to(self.project_root))
                    entity_type = EntityType.SCHEMA if 'schema' in str(json_file) else EntityType.CONFIG

                    entities.append(Entity(
                        id=f"{entity_type.value}::{rel_path}",
                        universe=Universe.CONTEXTOME,
                        type=entity_type,
                        name=json_file.stem,
                        path=rel_path,
                        purpose=Purpose(
                            role=entity_type.value,
                            intent=f"{entity_type.value.title()}: {json_file.stem}",
                            layer=Layer.CONFIGURATION
                        )
                    ))
                except Exception as e:
                    print(f"Warning: Could not process {json_file}: {e}")

        return entities

    def _scan_agent(self) -> List[Entity]:
        """Scan .agent directory artifacts"""
        entities = []
        agent_dir = self.project_root / '.agent'

        if not agent_dir.exists():
            return entities

        for agent_file in agent_dir.rglob('*'):
            if agent_file.is_file() and not self._should_skip(agent_file):
                try:
                    rel_path = str(agent_file.relative_to(self.project_root))
                    entities.append(Entity(
                        id=f"agent::{rel_path}",
                        universe=Universe.CONTEXTOME,
                        type=EntityType.TASK if 'registry' in str(agent_file) else EntityType.CONFIG,
                        name=agent_file.stem,
                        path=rel_path,
                        purpose=Purpose(
                            role='agent-artifact',
                            intent=f"Agent artifact: {agent_file.stem}",
                            layer=Layer.CONFIGURATION
                        )
                    ))
                except Exception as e:
                    print(f"Warning: Could not process {agent_file}: {e}")

        return entities

    def _should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        skip_patterns = [
            'node_modules', '.git', '__pycache__', '.venv',
            'venv', 'dist', 'build', '.cache', '.collider'
        ]
        return any(pattern in str(path) for pattern in skip_patterns)

    def _extract_title(self, content: str) -> str:
        """Extract first heading or first line as title"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        lines = content.strip().split('\n')
        return lines[0][:100] if lines else "Unknown"

    def _extract_headings(self, content: str) -> List[dict]:
        """Extract all headings from Markdown"""
        headings = []
        for i, line in enumerate(content.split('\n'), 1):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                text = match.group(2).strip()
                slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
                headings.append({
                    'level': len(match.group(1)),
                    'text': text,
                    'slug': slug,
                    'line': i
                })
        return headings

    def _extract_code_refs(self, content: str) -> List[str]:
        """Extract code references from Markdown"""
        refs = []
        # Match patterns like `function_name`, `ClassName`, file paths with .py
        patterns = [
            r'`([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)`',
            r'`([^`]+\.py[^`]*)`',
        ]
        for pattern in patterns:
            refs.extend(re.findall(pattern, content))
        return refs


# =============================================================================
# SYMMETRY DETECTOR
# =============================================================================

class SymmetryDetector:
    """Detects symmetry states between CODOME and CONTEXTOME"""

    DRIFT_THRESHOLD = 0.3

    def detect(self, codome: List[Entity], contextome: List[Entity]) -> SymmetryReport:
        """
        Analyze symmetry between code and documentation
        """
        report = SymmetryReport()

        # Build lookup maps
        code_by_name = {e.name: e for e in codome}
        code_by_id = {e.id: e for e in codome}

        # Track which code entities have docs
        documented_code = set()

        # Find cross-universe edges in contextome
        for ctx_entity in contextome:
            for edge in ctx_entity.edges:
                if edge.universe_crossing:
                    # This doc references code
                    target_id = edge.target
                    target_name = target_id.replace('code::', '')

                    if target_id in code_by_id or target_name in code_by_name:
                        # Found a pair
                        code_entity = code_by_id.get(target_id) or code_by_name.get(target_name)
                        if code_entity:
                            documented_code.add(code_entity.id)

                            # Check for drift
                            drift = self._compute_drift(code_entity, ctx_entity)

                            if drift > self.DRIFT_THRESHOLD:
                                report.drift_count += 1
                                report.drifted.append((code_entity.id, ctx_entity.id, drift))
                                code_entity.symmetry_state = SymmetryState.DRIFT
                                code_entity.drift_score = drift
                            else:
                                report.symmetric_count += 1
                                report.pairs.append((code_entity.id, ctx_entity.id))
                                code_entity.symmetry_state = SymmetryState.SYMMETRIC
                                code_entity.pair_id = ctx_entity.id
                    else:
                        # Phantom: doc references non-existent code
                        report.phantom_count += 1
                        report.phantoms.append(ctx_entity.id)
                        ctx_entity.symmetry_state = SymmetryState.PHANTOM

        # Find orphans: code without docs
        for code_entity in codome:
            if code_entity.id not in documented_code:
                report.orphan_count += 1
                report.orphans.append(code_entity.id)
                code_entity.symmetry_state = SymmetryState.ORPHAN

        return report

    def _compute_drift(self, code: Entity, doc: Entity) -> float:
        """Compute semantic drift between code and doc"""
        # Simple heuristic: compare purpose intents
        if not code.purpose.intent or not doc.purpose.intent:
            return 0.0

        # Basic word overlap measure
        code_words = set(code.purpose.intent.lower().split())
        doc_words = set(doc.purpose.intent.lower().split())

        if not code_words or not doc_words:
            return 0.0

        overlap = len(code_words & doc_words)
        union = len(code_words | doc_words)

        jaccard = overlap / union if union > 0 else 0
        drift = 1.0 - jaccard

        return drift


# =============================================================================
# PURPOSE FIELD ANALYZER
# =============================================================================

class PurposeFieldAnalyzer:
    """Applies Purpose Field analysis across PROJECTOME"""

    def analyze(self, entities: List[Entity]) -> PurposeFieldResult:
        """Analyze purpose field across all entities"""
        result = PurposeFieldResult()

        # Coverage: % with non-empty purpose
        with_purpose = sum(1 for e in entities if e.purpose.intent)
        result.coverage = with_purpose / len(entities) if entities else 0.0

        # Layer distribution
        layer_counts = Counter(e.purpose.layer.value for e in entities)
        result.layer_distribution = dict(layer_counts)

        # Coherence: average confidence
        confidences = [e.purpose.confidence for e in entities if e.purpose.confidence > 0]
        result.coherence = sum(confidences) / len(confidences) if confidences else 0.0

        # Entropy: diversity of roles
        role_counts = Counter(e.purpose.role for e in entities)
        total = sum(role_counts.values())
        if total > 0:
            probs = [c / total for c in role_counts.values()]
            result.entropy = -sum(p * (p and __import__('math').log2(p)) for p in probs if p > 0)

        return result


# =============================================================================
# MAIN CLASS: PROJECTOME OMNISCIENCE
# =============================================================================

class ProjectomeOmniscience:
    """
    Complete visibility across PROJECTOME

    The Omniscience Module provides:
    - Full inventory of CODOME ⊔ CONTEXTOME
    - Purpose Field analysis
    - Symmetry detection
    - Self-referential manifest (Lawvere fixed point)
    """

    VERSION = "1.0.0"

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.codome_scanner = CodomeScanner(self.project_root)
        self.contextome_scanner = ContextomeScanner(self.project_root)
        self.symmetry_detector = SymmetryDetector()
        self.purpose_analyzer = PurposeFieldAnalyzer()

        self.codome_entities: List[Entity] = []
        self.contextome_entities: List[Entity] = []
        self.manifest: Optional[ProjectomeManifest] = None

    def scan(self, unified_analysis_path: Optional[str] = None) -> ProjectomeManifest:
        """
        Perform complete scan of PROJECTOME

        Returns manifest including itself (fixed point)
        """
        print(f"Scanning PROJECTOME at: {self.project_root}")

        # 1. Scan CODOME
        print("  Scanning CODOME...")
        ua_path = Path(unified_analysis_path) if unified_analysis_path else None
        self.codome_entities = self.codome_scanner.scan(ua_path)
        print(f"    Found {len(self.codome_entities)} code entities")

        # 2. Scan CONTEXTOME
        print("  Scanning CONTEXTOME...")
        self.contextome_entities = self.contextome_scanner.scan()
        print(f"    Found {len(self.contextome_entities)} context entities")

        # 3. Detect symmetry
        print("  Detecting symmetry...")
        symmetry = self.symmetry_detector.detect(
            self.codome_entities,
            self.contextome_entities
        )
        print(f"    Symmetric: {symmetry.symmetric_count}")
        print(f"    Orphan: {symmetry.orphan_count}")
        print(f"    Phantom: {symmetry.phantom_count}")
        print(f"    Drift: {symmetry.drift_count}")

        # 4. Analyze purpose field
        print("  Analyzing purpose field...")
        all_entities = self.codome_entities + self.contextome_entities
        purpose_result = self.purpose_analyzer.analyze(all_entities)
        print(f"    Coverage: {purpose_result.coverage:.1%}")
        print(f"    Coherence: {purpose_result.coherence:.2f}")

        # 5. Add self-reference (FIXED POINT!)
        print("  Adding self-reference (Lawvere fixed point)...")
        self._add_self_reference()

        # 6. Build manifest
        all_entities = self.codome_entities + self.contextome_entities

        # Count cross-universe edges
        cross_edges = sum(
            1 for e in all_entities
            for edge in e.edges
            if edge.universe_crossing
        )

        self.manifest = ProjectomeManifest(
            generated=datetime.now().isoformat(),
            generator=f"POM v{self.VERSION}",
            self_reference=True,
            codome_files=len(set(e.path for e in self.codome_entities)),
            codome_entities=len(self.codome_entities),
            contextome_files=len(set(e.path for e in self.contextome_entities)),
            contextome_entities=len(self.contextome_entities),
            total_entities=len(all_entities),
            total_edges=sum(len(e.edges) for e in all_entities),
            cross_universe_edges=cross_edges,
            symmetry=symmetry,
            purpose_field=purpose_result,
            entities=all_entities
        )

        print(f"\nPROJECTOME SCANNED:")
        print(f"  Total entities: {self.manifest.total_entities}")
        print(f"  |CODOME|: {self.manifest.codome_entities}")
        print(f"  |CONTEXTOME|: {self.manifest.contextome_entities}")
        print(f"  Cross-universe edges: {self.manifest.cross_universe_edges}")

        return self.manifest

    def _add_self_reference(self):
        """
        Add POM itself to the inventory (Lawvere fixed point)

        By Lawvere's theorem, a complete inventory must include itself.
        """
        # Add this module
        self.contextome_entities.append(Entity(
            id="pom::projectome_omniscience.py",
            universe=Universe.CONTEXTOME,
            type=EntityType.SPECIFICATION,
            name="ProjectomeOmniscience",
            path="context-management/tools/pom/projectome_omniscience.py",
            purpose=Purpose(
                role='omniscience',
                intent='Complete visibility across PROJECTOME (self-referential)',
                confidence=1.0,
                layer=Layer.INFRASTRUCTURE
            )
        ))

        # Add the spec document
        self.contextome_entities.append(Entity(
            id="pom::PROJECTOME_OMNISCIENCE_MODULE.md",
            universe=Universe.CONTEXTOME,
            type=EntityType.SPECIFICATION,
            name="PROJECTOME_OMNISCIENCE_MODULE",
            path="context-management/docs/specs/PROJECTOME_OMNISCIENCE_MODULE.md",
            purpose=Purpose(
                role='specification',
                intent='Specification of Projectome Omniscience Module',
                confidence=1.0,
                layer=Layer.DOCUMENTATION
            )
        ))

    def save_manifest(self, output_path: str):
        """Save manifest to YAML file"""
        if not self.manifest:
            raise ValueError("No manifest to save. Run scan() first.")

        # Convert to serializable format
        manifest_dict = {
            'manifest': {
                'generated': self.manifest.generated,
                'generator': self.manifest.generator,
                'self_reference': self.manifest.self_reference,
                'fixed_point_proof': 'Lawvere 1969',

                'universes': {
                    'codome': {
                        'files': self.manifest.codome_files,
                        'entities': self.manifest.codome_entities,
                    },
                    'contextome': {
                        'files': self.manifest.contextome_files,
                        'entities': self.manifest.contextome_entities,
                    }
                },

                'totals': {
                    'entities': self.manifest.total_entities,
                    'edges': self.manifest.total_edges,
                    'cross_universe_edges': self.manifest.cross_universe_edges,
                },

                'symmetry': {
                    'symmetric': self.manifest.symmetry.symmetric_count,
                    'orphan': self.manifest.symmetry.orphan_count,
                    'phantom': self.manifest.symmetry.phantom_count,
                    'drift': self.manifest.symmetry.drift_count,
                },

                'purpose_field': {
                    'coverage': round(self.manifest.purpose_field.coverage, 3),
                    'coherence': round(self.manifest.purpose_field.coherence, 3),
                    'entropy': round(self.manifest.purpose_field.entropy, 3),
                    'layer_distribution': self.manifest.purpose_field.layer_distribution,
                },

                'orphan_list': self.manifest.symmetry.orphans[:20],  # Top 20
                'phantom_list': self.manifest.symmetry.phantoms[:20],
            }
        }

        with open(output_path, 'w') as f:
            yaml.dump(manifest_dict, f, default_flow_style=False, sort_keys=False)

        print(f"\nManifest saved to: {output_path}")

    def save_full_manifest(self, output_path: str):
        """Save full manifest including all entities"""
        if not self.manifest:
            raise ValueError("No manifest to save. Run scan() first.")

        # Convert entities to dicts
        entities_list = []
        for entity in self.manifest.entities:
            entities_list.append({
                'id': entity.id,
                'universe': entity.universe.value,
                'type': entity.type.value,
                'name': entity.name,
                'path': entity.path,
                'purpose': {
                    'role': entity.purpose.role,
                    'intent': entity.purpose.intent[:200] if entity.purpose.intent else '',
                    'layer': entity.purpose.layer.value,
                },
                'symmetry_state': entity.symmetry_state.value,
                'edge_count': len(entity.edges),
            })

        full_manifest = {
            'manifest': {
                'generated': self.manifest.generated,
                'generator': self.manifest.generator,
                'entity_count': len(entities_list),
            },
            'entities': entities_list
        }

        with open(output_path, 'w') as f:
            yaml.dump(full_manifest, f, default_flow_style=False, sort_keys=False)

        print(f"Full manifest saved to: {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Projectome Omniscience Module - Complete PROJECTOME visibility'
    )
    parser.add_argument(
        'project_root',
        nargs='?',
        default='.',
        help='Project root directory (default: current directory)'
    )
    parser.add_argument(
        '--output', '-o',
        default='projectome_manifest.yaml',
        help='Output manifest path'
    )
    parser.add_argument(
        '--unified-analysis', '-u',
        help='Path to unified_analysis.json from Collider'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Include all entities in manifest (larger file)'
    )

    args = parser.parse_args()

    pom = ProjectomeOmniscience(args.project_root)
    pom.scan(args.unified_analysis)

    if args.full:
        pom.save_full_manifest(args.output)
    else:
        pom.save_manifest(args.output)


if __name__ == '__main__':
    main()
