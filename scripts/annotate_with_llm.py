#!/usr/bin/env python3
"""
LLM Annotator - Automated Ground Truth Generation

Uses GPT-4 or Ollama to annotate code samples with roles.
This creates "ground truth" labels to validate Collider's accuracy.
"""

import csv
import json
import os
from pathlib import Path
from typing import Dict, Optional
import time

# Try to import OpenAI (optional)
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

def get_role_options() -> str:
    """Return the 27-role taxonomy for the LLM."""
    return """
Available Roles (choose ONE):
1. Query - Retrieves data without modification
2. Command - Modifies state (create, update, delete)
3. Entity - Domain model/data structure
4. Repository - Data access layer
5. Service - Business logic orchestration
6. Factory - Creates/instantiates objects
7. Builder - Constructs complex objects step-by-step
8. Validator - Checks constraints/rules
9. Transformer - Converts between formats
10. Adapter - Bridges different interfaces
11. Controller - Handles requests/routes
12. Presenter - Formats data for display
13. View - UI component
14. Configuration - Settings/parameters
15. Constant - Immutable values
16. Utility - Helper functions
17. Test - Test code
18. Mock - Test double
19. Fixture - Test data
20. Migration - Schema/data migration
21. EventHandler - Responds to events
22. Observer - Watches for changes
23. Strategy - Encapsulates algorithm
24. Decorator - Adds behavior dynamically
25. Singleton - Single instance
26. Guard - Authorization/permission check
27. Middleware - Request/response processing
"""

def annotate_with_openai(sample: Dict, api_key: str) -> str:
    """Use GPT-4 to classify the role."""
    client = OpenAI(api_key=api_key)
    
    prompt = f"""You are a software architecture expert. Classify the following code element by its SEMANTIC ROLE.

Code Element:
- Name: {sample['name']}
- Kind: {sample['kind']}
- Signature: {sample['signature'][:150]}
- Docstring: {sample['docstring'][:150]}

{get_role_options()}

Respond with ONLY the role name (e.g., "Query", "Command", "Entity"). No explanation."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=10
    )
    
    return response.choices[0].message.content.strip()

def annotate_with_ollama(sample: Dict, model: str = "llama3.2") -> str:
    """Use local Ollama to classify the role."""
    import requests
    
    prompt = f"""You are a software architecture expert. Classify the following code element by its SEMANTIC ROLE.

Code Element:
- Name: {sample['name']}
- Kind: {sample['kind']}
- Signature: {sample['signature'][:150]}
- Docstring: {sample['docstring'][:150]}

{get_role_options()}

Respond with ONLY the role name (e.g., "Query", "Command", "Entity"). No explanation."""

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0}
        }
    )
    
    if response.status_code == 200:
        return response.json()['response'].strip()
    else:
        raise Exception(f"Ollama request failed: {response.status_code}")

def annotate_samples(
    input_csv: Path,
    output_csv: Path,
    method: str = "ollama",
    api_key: Optional[str] = None,
    limit: Optional[int] = None
) -> None:
    """Annotate all samples using LLM."""
    
    # Load samples
    with open(input_csv, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        samples = list(reader)
    
    if limit:
        samples = samples[:limit]
    
    print(f"Annotating {len(samples)} samples using {method}...")
    
    # Annotate
    annotated = []
    for i, sample in enumerate(samples, 1):
        try:
            if method == "openai":
                if not HAS_OPENAI or not api_key:
                    raise Exception("OpenAI not available. Install: pip install openai")
                role = annotate_with_openai(sample, api_key)
            else:  # ollama
                role = annotate_with_ollama(sample)
            
            sample['annotated_role'] = role
            sample['annotation_method'] = method
            annotated.append(sample)
            
            print(f"[{i}/{len(samples)}] {sample['name']}: {role}")
            
            # Rate limiting
            if method == "openai":
                time.sleep(0.5)  # Avoid rate limits
                
        except Exception as e:
            print(f"Error annotating {sample['name']}: {e}")
            sample['annotated_role'] = 'ERROR'
            sample['annotation_method'] = method
            sample['error'] = str(e)
            annotated.append(sample)
    
    # Save
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        if annotated:
            writer = csv.DictWriter(f, fieldnames=annotated[0].keys())
            writer.writeheader()
            writer.writerows(annotated)
    
    print(f"\n✅ Annotated {len(annotated)} samples")
    print(f"📄 Output: {output_csv}")
    
    # Summary
    success = sum(1 for s in annotated if s['annotated_role'] != 'ERROR')
    print(f"\n✓ Success: {success}/{len(annotated)}")
    print(f"\nNext: Run python scripts/validate_annotations.py")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Annotate samples using LLM')
    parser.add_argument('--input', type=Path,
                       default=Path('data/mini_validation_samples.csv'),
                       help='Input CSV with samples')
    parser.add_argument('--output', type=Path,
                       default=Path('data/mini_validation_annotated.csv'),
                       help='Output CSV with annotations')
    parser.add_argument('--method', choices=['ollama', 'openai'],
                       default='ollama',
                       help='LLM to use (ollama=local, openai=GPT-4)')
    parser.add_argument('--api-key', type=str,
                       help='OpenAI API key (if using openai method)')
    parser.add_argument('--limit', type=int,
                       help='Limit number of samples (for testing)')
    
    args = parser.parse_args()
    
    # Check API key for OpenAI
    if args.method == 'openai' and not args.api_key:
        args.api_key = os.getenv('OPENAI_API_KEY')
        if not args.api_key:
            print("❌ OpenAI API key required!")
            print("   Set OPENAI_API_KEY env var or use --api-key")
            return
    
    annotate_samples(
        args.input,
        args.output,
        args.method,
        args.api_key,
        args.limit
    )

if __name__ == '__main__':
    main()
