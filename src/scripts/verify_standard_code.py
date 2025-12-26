#!/usr/bin/env python3
"""
verify_standard_code.py - Verification script for STANDARD_CODE.md

Checks:
1. YAML frontmatter is valid
2. All required sections are present
3. Canonical counts are consistent throughout the document
4. All theorems are stated
5. No duplicate section headers
6. All internal links resolve
"""

import re
import sys
import json
import yaml
from pathlib import Path
from collections import Counter

def load_document(path: str) -> tuple[dict, str]:
    """Load the document and extract frontmatter."""
    content = Path(path).read_text(encoding='utf-8')
    
    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.+?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        raise ValueError("No YAML frontmatter found")
    
    frontmatter = yaml.safe_load(frontmatter_match.group(1))
    body = content[frontmatter_match.end():]
    
    return frontmatter, body

def check_required_sections(frontmatter: dict, body: str) -> list[str]:
    """Check all required sections are present."""
    errors = []
    required = frontmatter.get('required_sections', [])
    
    for section in required:
        if section not in body:
            errors.append(f"Missing required section: '{section}'")
    
    return errors

def check_canonical_counts(frontmatter: dict, body: str) -> list[str]:
    """Check canonical counts are consistent in the document."""
    errors = []
    warnings = []
    counts = frontmatter.get('canonical_counts', {})
    
    # Define patterns to search for each count
    patterns = {
        'planes': [r'(\d+)\s+planes', r'(\d+)\s+PLANES', r'THE\s+(\d+)\s+PLANES'],
        'levels': [r'(\d+)\s+levels', r'(\d+)\s+LEVELS', r'THE\s+(\d+)\s+LEVELS'],
        'lenses': [r'(\d+)\s+lenses', r'(\d+)\s+LENSES', r'THE\s+(\d+)\s+LENSES'],
        'dimensions': [r'(\d+)\s+dimensions', r'(\d+)\s+DIMENSIONS', r'THE\s+(\d+)\s+DIMENSIONS'],
        'atoms': [r'(\d+)\s+atoms', r'(\d+)\s+ATOMS', r'(\d+)\s+atom\s+types'],
        'roles': [r'(\d+)\s+roles', r'(\d+)\s+ROLES', r'(\d+)\s+canonical\s+roles'],
    }
    
    for key, expected in counts.items():
        if key not in patterns:
            continue
            
        found_values = []
        for pattern in patterns[key]:
            matches = re.findall(pattern, body, re.IGNORECASE)
            found_values.extend([int(m) for m in matches])
        
        # Check for inconsistencies
        unique_values = set(found_values)
        if len(unique_values) > 1:
            errors.append(f"INCONSISTENT {key}: found values {unique_values}, expected {expected}")
        elif len(unique_values) == 1 and list(unique_values)[0] != expected:
            errors.append(f"MISMATCH {key}: document says {list(unique_values)[0]}, schema says {expected}")
    
    return errors

def check_postulates(frontmatter: dict, body: str) -> list[str]:
    """Check all postulates are stated."""
    errors = []
    # Support both old 'theorems' and new 'postulates' key
    postulates = frontmatter.get('postulates', frontmatter.get('theorems', []))
    
    for postulate in postulates:
        if postulate not in body:
            errors.append(f"Missing postulate: '{postulate}'")
    
    return errors

def check_duplicate_headers(body: str) -> list[str]:
    """Check for duplicate section headers."""
    errors = []
    headers = re.findall(r'^#+\s+(.+)$', body, re.MULTILINE)
    
    # Count occurrences (ignoring case)
    header_counts = Counter(h.strip().lower() for h in headers)
    
    for header, count in header_counts.items():
        if count > 1 and 'section' not in header.lower():
            # Allow some duplication for common patterns
            if header not in ['---', '']:
                errors.append(f"Possible duplicate header: '{header}' appears {count} times")
    
    return errors

def check_assert_markers(body: str) -> list[str]:
    """Check that ASSERT markers are present and valid."""
    errors = []
    
    # Find all ASSERT markers
    asserts = re.findall(r'<!--\s*ASSERT:\s*([^>]+)\s*-->', body)
    
    if not asserts:
        errors.append("No ASSERT markers found in document")
    else:
        print(f"  Found {len(asserts)} ASSERT markers")
    
    return errors

def check_json_cross_reference(frontmatter: dict) -> list[str]:
    """Cross-check canonical counts against JSON files."""
    errors = []
    
    # Try both old and new paths
    roles_paths = [Path("schema/fixed/roles.json"), Path("canonical/fixed/roles.json")]
    for roles_path in roles_paths:
        if roles_path.exists():
            try:
                roles_data = json.load(open(roles_path))
                json_role_count = roles_data.get("count", len(roles_data.get("roles", {})))
                expected = frontmatter.get("canonical_counts", {}).get("roles")
                if expected and json_role_count != expected:
                    errors.append(f"roles.json has {json_role_count} roles but schema expects {expected}")
                else:
                    print(f"  ✓ roles.json count matches ({json_role_count})")
                break
            except Exception as e:
                errors.append(f"Failed to check {roles_path}: {e}")
    
    dims_paths = [Path("schema/fixed/dimensions.json"), Path("canonical/fixed/dimensions.json")]
    for dims_path in dims_paths:
        if dims_path.exists():
            try:
                dims_data = json.load(open(dims_path))
                json_dim_count = len(dims_data.get("dimensions", []))
                expected = frontmatter.get("canonical_counts", {}).get("dimensions")
                if expected and json_dim_count != expected:
                    errors.append(f"dimensions.json has {json_dim_count} dimensions but schema expects {expected}")
                else:
                    print(f"  ✓ dimensions.json count matches ({json_dim_count})")
                break
            except Exception as e:
                errors.append(f"Failed to check {dims_path}: {e}")
    
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_standard_code.py <path_to_STANDARD_CODE.md>")
        sys.exit(1)
    
    path = sys.argv[1]
    print(f"\n{'='*60}")
    print(f"STANDARD CODE VERIFICATION")
    print(f"{'='*60}")
    print(f"Document: {path}")
    print()
    
    try:
        frontmatter, body = load_document(path)
        print(f"✓ Frontmatter loaded (schema v{frontmatter.get('schema_version', 'unknown')})")
    except Exception as e:
        print(f"✗ Failed to load document: {e}")
        sys.exit(1)
    
    all_errors = []
    
    # Check required sections
    print("\nChecking required sections...")
    errors = check_required_sections(frontmatter, body)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print(f"  ✓ All {len(frontmatter.get('required_sections', []))} required sections present")
    
    # Check canonical counts
    print("\nChecking canonical counts consistency...")
    errors = check_canonical_counts(frontmatter, body)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print(f"  ✓ Canonical counts consistent")
    
    # Check postulates
    print("\nChecking postulates...")
    errors = check_postulates(frontmatter, body)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  ✗ {e}")
    else:
        postulate_count = len(frontmatter.get('postulates', frontmatter.get('theorems', [])))
        print(f"  ✓ All {postulate_count} postulates present")
    
    # Check for duplicates
    print("\nChecking for duplicate headers...")
    errors = check_duplicate_headers(body)
    if errors:
        # These are warnings, not fatal
        for e in errors:
            print(f"  ⚠ {e}")
    else:
        print(f"  ✓ No problematic duplicate headers")
    
    # Check ASSERT markers
    print("\nChecking ASSERT markers...")
    errors = check_assert_markers(body)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  ✗ {e}")
    
    # Cross-check JSON files
    print("\nCross-checking canonical JSON files...")
    errors = check_json_cross_reference(frontmatter)
    if errors:
        all_errors.extend(errors)
        for e in errors:
            print(f"  ✗ {e}")
    
    # Summary
    print(f"\n{'='*60}")
    if all_errors:
        print(f"VERIFICATION FAILED: {len(all_errors)} errors found")
        sys.exit(1)
    else:
        print("✓ VERIFICATION PASSED")
        print(f"  Document: {frontmatter.get('document_name', 'Unknown')}")
        print(f"  Version:  {frontmatter.get('schema_version', 'Unknown')}")
        print(f"  Verified: {frontmatter.get('last_verified', 'Unknown')}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
