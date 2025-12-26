#!/usr/bin/env python3
"""
🧪 DIMENSION MODEL COMPARATOR
Tests 8D Flat vs 6D Grouped on real data.
==========================================
"""
import sys
from pathlib import Path

# Add parent to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.particle_registry_8d import Particle8D, ParticleRegistry8D
from core.particle_registry_6d import (
    Particle6D, ParticleRegistry6D,
    WhatDimension, HowDimension, WhereDimension, 
    WhyDimension, WhenDimension, HowLongDimension
)


def create_sample_particles():
    """Create test particles based on the Periodic Table image."""
    samples = [
        # Interface Layer
        {"name": "RouteHandler", "symbol": "Rh", "layer": "interface", "role": "orchestrator"},
        {"name": "Presenter", "symbol": "Pr", "layer": "interface", "role": "data"},
        {"name": "InputValidator", "symbol": "Iv", "layer": "interface", "role": "worker"},
        {"name": "UIWrapper", "symbol": "Uw", "layer": "interface", "role": "data"},
        # App Layer
        {"name": "UseCase", "symbol": "Uc", "layer": "app", "role": "orchestrator"},
        {"name": "ProcessManager", "symbol": "Pm", "layer": "app", "role": "orchestrator"},
        {"name": "AppPolicy", "symbol": "Ap", "layer": "app", "role": "worker"},
        {"name": "AppMapper", "symbol": "Am", "layer": "app", "role": "data"},
        # Core Layer
        {"name": "BusinessEntity", "symbol": "Be", "layer": "core", "role": "data"},
        {"name": "ValueObject", "symbol": "Vo", "layer": "core", "role": "data"},
        {"name": "CoreService", "symbol": "Bs", "layer": "core", "role": "worker"},
        {"name": "BusinessRule", "symbol": "Br", "layer": "core", "role": "worker"},
        {"name": "DomainEvent", "symbol": "De", "layer": "core", "role": "data"},
        # Infra Layer
        {"name": "Repository", "symbol": "Rp", "layer": "infra", "role": "data", "effect": "read_modify", "boundary": "io"},
        {"name": "QueryObject", "symbol": "Qo", "layer": "infra", "role": "data", "effect": "read"},
        {"name": "APIClient", "symbol": "Ac", "layer": "infra", "role": "worker", "effect": "read_modify", "boundary": "output"},
        {"name": "MsgProducer", "symbol": "Mp", "layer": "infra", "role": "worker", "activation": "event", "boundary": "output"},
        {"name": "MsgConsumer", "symbol": "Mc", "layer": "infra", "role": "worker", "activation": "event", "boundary": "input"},
        {"name": "BackgroundJob", "symbol": "Bj", "layer": "infra", "role": "worker", "activation": "time"},
        {"name": "Cache", "symbol": "Cc", "layer": "infra", "role": "data", "lifetime": "session"},
        {"name": "ConfigLoader", "symbol": "Cf", "layer": "infra", "role": "data", "lifetime": "global"},
        {"name": "FeatureFlag", "symbol": "Ff", "layer": "infra", "role": "data", "state": "stateful"},
        {"name": "Logger", "symbol": "Lg", "layer": "infra", "role": "worker", "effect": "write", "lifetime": "global"},
        {"name": "Metrics", "symbol": "Mt", "layer": "infra", "role": "worker", "effect": "write"},
        {"name": "Serializer", "symbol": "Sz", "layer": "infra", "role": "data", "effect": "pure"},
        # Tests Layer
        {"name": "TestCase", "symbol": "Tc", "layer": "tests", "role": "orchestrator"},
        {"name": "Fixture", "symbol": "Fx", "layer": "tests", "role": "data"},
        {"name": "TestRunner", "symbol": "Tr", "layer": "tests", "role": "orchestrator"},
    ]
    return samples


def test_8d_registry(samples):
    """Test 8D flat model."""
    print("\n" + "="*60)
    print("🔬 8D FLAT MODEL TEST")
    print("="*60)
    
    registry = ParticleRegistry8D()
    
    for i, s in enumerate(samples):
        p = Particle8D(
            id=f"p{i:03d}",
            name=s["name"],
            file=f"src/{s['layer']}/{s['name'].lower()}.py",
            material_continent="Organization",
            material_family="Aggregates",
            material_atom=s["name"],
            layer=s.get("layer", "unknown"),
            role=s.get("role", "unknown"),
            boundary=s.get("boundary", "internal"),
            state=s.get("state", "stateless"),
            effect=s.get("effect", "unknown"),
            activation=s.get("activation", "direct"),
            lifetime=s.get("lifetime", "transient"),
        )
        registry.add(p)
    
    output_path = str(ROOT / "output" / "test_8d_registry.json")
    Path(output_path).parent.mkdir(exist_ok=True)
    data = registry.export(output_path)
    
    print(f"✓ Exported {data['particle_count']} particles")
    print(f"✓ Schema: {data['schema']}")
    print(f"✓ Dimensions: {data['dimensions']}")
    print("\nStats by Layer:")
    for layer, count in data['stats']['by_layer'].items():
        print(f"  {layer}: {count}")
    print("\nStats by Role:")
    for role, count in data['stats']['by_role'].items():
        print(f"  {role}: {count}")
    print("\nStats by Activation:")
    for act, count in data['stats']['by_activation'].items():
        print(f"  {act}: {count}")
    
    return data


def test_6d_registry(samples):
    """Test 6D grouped model."""
    print("\n" + "="*60)
    print("🔬 6D GROUPED MODEL TEST")
    print("="*60)
    
    registry = ParticleRegistry6D()
    
    for i, s in enumerate(samples):
        p = Particle6D(
            id=f"p{i:03d}",
            name=s["name"],
            file=f"src/{s['layer']}/{s['name'].lower()}.py",
            what=WhatDimension(
                continent="Organization",
                family="Aggregates",
                atom=s["name"]
            ),
            how=HowDimension(
                state=s.get("state", "stateless"),
                effect=s.get("effect", "unknown"),
                is_async=False
            ),
            where=WhereDimension(
                layer=s.get("layer", "unknown"),
                boundary=s.get("boundary", "internal")
            ),
            why=WhyDimension(
                role=s.get("role", "unknown"),
                pattern=s["name"],
                smells=[]
            ),
            when=WhenDimension(
                activation=s.get("activation", "direct")
            ),
            how_long=HowLongDimension(
                lifetime=s.get("lifetime", "transient")
            ),
        )
        registry.add(p)
    
    output_path = str(ROOT / "output" / "test_6d_registry.json")
    data = registry.export(output_path)
    
    print(f"✓ Exported {data['particle_count']} particles")
    print(f"✓ Schema: {data['schema']}")
    print(f"✓ Dimensions: {data['dimensions']}")
    print("\nStats - WHERE.layer:")
    for layer, count in data['stats']['where']['by_layer'].items():
        print(f"  {layer}: {count}")
    print("\nStats - WHY.role:")
    for role, count in data['stats']['why']['by_role'].items():
        print(f"  {role}: {count}")
    print("\nStats - WHEN.activation:")
    for act, count in data['stats']['when']['by_activation'].items():
        print(f"  {act}: {count}")
    
    return data


def compare_models(data_8d, data_6d):
    """Compare the two models."""
    print("\n" + "="*60)
    print("📊 COMPARISON: 8D FLAT vs 6D GROUPED")
    print("="*60)
    
    print("\n| Aspect | 8D Flat | 6D Grouped |")
    print("|--------|---------|------------|")
    print(f"| Dimensions | {len(data_8d['dimensions'])} | {len(data_6d['dimensions'])} |")
    print(f"| Particles | {data_8d['particle_count']} | {data_6d['particle_count']} |")
    
    # JSON size comparison
    import json
    size_8d = len(json.dumps(data_8d))
    size_6d = len(json.dumps(data_6d))
    print(f"| JSON Size | {size_8d:,} bytes | {size_6d:,} bytes |")
    
    # Nesting depth
    print(f"| Max Depth | 2 levels | 3 levels |")
    print(f"| Readability | API-friendly | Human-friendly |")
    
    print("\n🎯 VERDICT:")
    if size_8d < size_6d:
        print("  8D is more compact for storage/API")
    else:
        print("  6D is more compact (grouped)")
    print("  6D is better for human understanding (semantic grouping)")
    print("  8D is better for flat queries (no nesting)")


def main():
    print("🧪 DIMENSIONAL MODEL COMPARISON TEST")
    print("Testing the Periodic Table particles from your diagram")
    
    samples = create_sample_particles()
    print(f"\n📦 Loaded {len(samples)} sample particles")
    
    data_8d = test_8d_registry(samples)
    data_6d = test_6d_registry(samples)
    compare_models(data_8d, data_6d)
    
    print("\n✅ TEST COMPLETE")
    print("  → output/test_8d_registry.json")
    print("  → output/test_6d_registry.json")


if __name__ == "__main__":
    main()
