#!/usr/bin/env python3
"""
Test the Atom Extractor on the real dddpy fixture.
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.atom_extractor import AtomExtractor, HadronLevel

def test_on_dddpy():
    """Test the atom extractor on the dddpy validation fixture."""
    
    extractor = AtomExtractor()
    
    if "python" not in extractor.parsers:
        print("ERROR: tree-sitter-python not available")
        return
    
    # Find all Python files in dddpy
    dddpy_path = Path(__file__).parent / "validation" / "dddpy_real"
    
    if not dddpy_path.exists():
        print(f"ERROR: dddpy fixture not found at {dddpy_path}")
        return
    
    all_hadrons = []
    files_processed = 0
    
    print("=" * 70)
    print("ATOM EXTRACTOR TEST — dddpy Real Repository")
    print("=" * 70)
    print()
    
    for py_file in dddpy_path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        try:
            code = py_file.read_bytes()
            rel_path = py_file.relative_to(dddpy_path)
            hadrons = extractor.extract(code, language="python", file_path=str(rel_path))
            all_hadrons.extend(hadrons)
            files_processed += 1
            
            # Show interesting findings (molecules and organelles only)
            interesting = [h for h in hadrons if h.level != HadronLevel.ATOM]
            if interesting:
                print(f"📄 {rel_path}")
                for h in interesting:
                    level_icon = "🧬" if h.level == HadronLevel.ORGANELLE else "🔬"
                    print(f"   {level_icon} [{h.id:2}] {h.name:20} | L{h.start_line:3} | {h.detection_rule}")
                print()
                
        except Exception as e:
            print(f"⚠️  Error parsing {py_file}: {e}")
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    summary = extractor.summary(all_hadrons)
    
    print(f"\n📊 Files processed: {files_processed}")
    print(f"📊 Total hadrons extracted: {summary['total']}")
    print()
    
    print("By Level:")
    for level, count in summary['by_level'].items():
        bar = "█" * min(count // 5, 40)
        print(f"  {level:12} {count:5} {bar}")
    print()
    
    print("By Continent:")
    for continent, count in sorted(summary['by_continent'].items(), key=lambda x: -x[1]):
        bar = "█" * min(count // 5, 40)
        print(f"  {continent:20} {count:5} {bar}")
    print()
    
    print("By Fundamental Particle:")
    for fund, count in sorted(summary['by_fundamental'].items(), key=lambda x: -x[1]):
        bar = "█" * min(count // 5, 40)
        print(f"  {fund:20} {count:5} {bar}")
    print()
    
    print("Top 15 Hadron Types:")
    for name, count in summary['top_10_hadrons'][:15]:
        bar = "█" * min(count // 2, 40)
        print(f"  {name:20} {count:5} {bar}")
    print()
    
    # Architecture Role Summary (Organelles only)
    organelles = [h for h in all_hadrons if h.level == HadronLevel.ORGANELLE]
    if organelles:
        print("=" * 70)
        print("DETECTED ARCHITECTURE ROLES (Organelles)")
        print("=" * 70)
        for h in organelles:
            print(f"  [{h.id:2}] {h.name:20} | {h.file_path:40} | L{h.start_line}")
    
    # DDD Pattern Summary
    molecules = [h for h in all_hadrons if h.level == HadronLevel.MOLECULE]
    ddd_patterns = {}
    for h in molecules:
        if h.name in ("Entity", "ValueObject", "Repository", "PureFunction", "ImpureFunction", "AsyncFunction"):
            ddd_patterns[h.name] = ddd_patterns.get(h.name, 0) + 1
    
    if ddd_patterns:
        print()
        print("=" * 70)
        print("DDD PATTERN DISTRIBUTION")
        print("=" * 70)
        for name, count in sorted(ddd_patterns.items(), key=lambda x: -x[1]):
            bar = "█" * min(count, 40)
            print(f"  {name:20} {count:5} {bar}")


if __name__ == "__main__":
    test_on_dddpy()
