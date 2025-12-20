#!/usr/bin/env python3
"""
🧪 LLM Classification Test — End-to-End Pipeline Test

Tests the smart extraction → LLM classification → validation pipeline
on a sample of Unknown nodes.
"""

import json
import sys
import requests
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent))

from smart_extractor import SmartExtractor, format_card_for_llm, ComponentCard
from llm_classifier import (
    ALLOWED_ROLES, format_system_prompt, EvidenceValidator,
    ClassificationResult
)


def call_ollama(system_prompt: str, user_prompt: str, model: str = "qwen2.5:7b-instruct") -> dict:
    """Call Ollama via CLI for classification."""
    import subprocess
    
    # Combine prompts
    full_prompt = f"""{system_prompt}

{user_prompt}

IMPORTANT: Respond with valid JSON only, no markdown, no explanation outside JSON."""
    
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        response = result.stdout.strip()
        
        # Try to parse JSON from response
        # Sometimes LLM wraps in markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        return json.loads(response)
        
    except subprocess.TimeoutExpired:
        print("⚠️ LLM call timed out")
        return {"error": "timeout", "role": "Unknown", "confidence": 0}
    except json.JSONDecodeError as e:
        print(f"⚠️ LLM returned invalid JSON")
        # Try to extract role from raw response
        raw = result.stdout if 'result' in dir() else ""
        for role in ["Test", "Factory", "Service", "Entity", "Repository", "UseCase", "Configuration"]:
            if role in raw:
                return {"role": role, "confidence": 0.5, "evidence": [], "reasoning": f"Fallback extraction: found '{role}' in response"}
        return {"error": "invalid_json", "role": "Unknown", "confidence": 0}
    except Exception as e:
        print(f"⚠️ LLM call failed: {e}")
        return {"error": str(e), "role": "Unknown", "confidence": 0}


def classify_component(card: ComponentCard, validator: EvidenceValidator) -> ClassificationResult:
    """Classify a single component using LLM."""
    # Format prompts
    system_prompt = format_system_prompt()
    user_prompt = format_card_for_llm(card)
    
    # Call LLM
    raw_result = call_ollama(system_prompt, user_prompt)
    
    # Validate result
    result = validator.validate(raw_result, card)
    
    return result


def test_pipeline(graph_path: str, repo_path: str, limit: int = 5):
    """Test the full classification pipeline."""
    print("=" * 60)
    print("🧪 LLM CLASSIFICATION PIPELINE TEST")
    print("=" * 60)
    print()
    
    # Load graph
    with open(graph_path) as f:
        graph_data = json.load(f)
    
    print(f"📂 Repo: {repo_path}")
    print(f"📊 Graph: {graph_path}")
    
    # Count unknowns
    components = graph_data.get("components", {})
    unknowns = [c for c in components.values() if c.get("type") == "Unknown"]
    print(f"❓ Unknown nodes: {len(unknowns)}")
    print(f"🎯 Testing on: {min(limit, len(unknowns))} samples")
    print()
    
    # Extract ComponentCards
    print("📦 Extracting ComponentCards...")
    extractor = SmartExtractor(repo_path)
    cards = extractor.extract_unknowns(graph_data, limit=limit)
    print(f"   Extracted: {len(cards)} cards")
    print()
    
    # Classify each
    validator = EvidenceValidator(strict=True)
    results = []
    
    print("🤖 Classifying with LLM...")
    for i, card in enumerate(cards, 1):
        print(f"   [{i}/{len(cards)}] {card.name[:40]}...", end=" ", flush=True)
        result = classify_component(card, validator)
        results.append(result)
        print(f"→ {result.role} ({result.confidence:.0%})")
    
    # Summary
    print()
    print("=" * 60)
    print("📊 RESULTS SUMMARY")
    print("=" * 60)
    print()
    
    classified = [r for r in results if r.role != "Unknown"]
    unknown_still = [r for r in results if r.role == "Unknown"]
    
    print(f"✅ Classified: {len(classified)}/{len(results)} ({len(classified)/len(results)*100:.0f}%)")
    print(f"❓ Still Unknown: {len(unknown_still)}/{len(results)}")
    print()
    
    print("📋 Classifications:")
    for r in results:
        evidence_count = len(r.evidence)
        print(f"   {r.node_id[:60]}...")
        print(f"      → {r.role} ({r.confidence:.0%}, {evidence_count} evidence)")
        if r.reasoning:
            print(f"      💬 {r.reasoning[:80]}...")
    
    # Return aggregated stats
    return {
        "total": len(results),
        "classified": len(classified),
        "unknown": len(unknown_still),
        "results": [
            {
                "node_id": r.node_id,
                "role": r.role,
                "confidence": r.confidence,
                "evidence_count": len(r.evidence),
            }
            for r in results
        ]
    }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python llm_test.py <graph.json> <repo_path> [limit]")
        print()
        print("Example:")
        print("  python llm_test.py validation/100_repo_results/pgorecki__python-ddd/graph.json \\")
        print("      validation/benchmarks/repos/pgorecki__python-ddd 5")
        sys.exit(1)
    
    graph_path = sys.argv[1]
    repo_path = sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    stats = test_pipeline(graph_path, repo_path, limit)
    
    # Save results
    output_path = Path(graph_path).parent / "llm_test_results.json"
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"\n💾 Results saved to: {output_path}")
