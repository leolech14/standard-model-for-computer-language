#!/usr/bin/env python3
"""
🦙 OLLAMA CLIENT — Local LLM Integration for Spectrometer

This module provides the Ollama adapter for the LLM Classifier.
It enables evidence-anchored component classification using local models.
"""

import json
import re
import subprocess
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OllamaConfig:
    """Configuration for Ollama client."""
    model: str = "qwen2.5:7b-instruct"  # Best for structured JSON output
    base_url: str = "http://localhost:11434"
    timeout: int = 120  # seconds
    temperature: float = 0.1  # Low temp for deterministic classification
    max_tokens: int = 2048


class OllamaClient:
    """
    Ollama client for LLM classification.
    
    Designed to work with the LLMClassifier's evidence-anchored prompts.
    Returns structured JSON that the EvidenceValidator can check.
    """
    
    def __init__(self, config: Optional[OllamaConfig] = None):
        self.config = config or OllamaConfig()
        self._check_ollama_available()
    
    def _check_ollama_available(self):
        """Check if Ollama is running."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.config.base_url}/api/tags"],
                capture_output=True,
                timeout=5,
            )
            if result.returncode != 0:
                raise RuntimeError("Ollama is not running. Start it with: ollama serve")
        except subprocess.TimeoutExpired:
            raise RuntimeError("Ollama connection timed out")
        except FileNotFoundError:
            # curl not available, try with requests
            pass
    
    def classify(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call Ollama to classify a component.
        
        Uses subprocess to call ollama CLI directly, which is more reliable
        than the HTTP API when multiple instances may be running.
        
        Returns the raw JSON string response.
        """
        # Combine prompts for the CLI
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nRespond with valid JSON only."
        
        try:
            result = subprocess.run(
                ["ollama", "run", self.config.model, full_prompt],
                capture_output=True,
                text=True,
                timeout=self.config.timeout,
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Ollama failed: {result.stderr}")
            
            content = result.stdout.strip()
            
            # Extract JSON from response (sometimes wrapped in markdown)
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                return json_match.group(1)
            
            # Try to find raw JSON object (possibly nested)
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json_match.group(0)
            
            return content
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Ollama timed out after {self.config.timeout}s")
        except FileNotFoundError:
            raise RuntimeError("ollama CLI not found. Install from https://ollama.ai")
    
    def is_available(self) -> bool:
        """Check if Ollama service is available."""
        try:
            import urllib.request
            # Just check if Ollama is responding, not specific models
            req = urllib.request.Request(f"{self.config.base_url}/api/version")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False


def classify_component_with_ollama(
    component_card: Dict[str, Any],
    config: Optional[OllamaConfig] = None,
) -> Dict[str, Any]:
    """
    Convenience function to classify a single component using Ollama.
    
    This is a standalone function that can be used without the full
    LLMClassifier infrastructure.
    """
    from llm_classifier import (
        ComponentCard,
        format_system_prompt,
        format_user_prompt,
        EvidenceValidator,
    )
    
    # Create client
    client = OllamaClient(config)
    
    # Build component card if dict
    if isinstance(component_card, dict):
        card = ComponentCard(**component_card)
    else:
        card = component_card
    
    # Generate prompts
    system_prompt = format_system_prompt()
    user_prompt = format_user_prompt(card)
    
    # Call Ollama
    response = client.classify(system_prompt, user_prompt)
    
    # Parse and validate
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        return {
            "node_id": card.node_id,
            "role": "Unknown",
            "confidence": 0.1,
            "evidence": [],
            "reasoning": f"Failed to parse LLM response: {response[:200]}",
        }
    
    # Validate evidence
    validator = EvidenceValidator(strict=True)
    validated = validator.validate(result, card)
    
    return {
        "node_id": validated.node_id,
        "role": validated.role,
        "confidence": validated.confidence,
        "evidence": [
            {
                "type": e.evidence_type,
                "quote": e.quote,
                "file": e.file,
                "line_start": e.line_start,
            }
            for e in validated.evidence
        ],
        "reasoning": validated.reasoning,
        "validation_errors": validator.validation_errors,
    }


# =============================================================================
# CLI DEMO
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🦙 OLLAMA CLIENT — Local LLM Integration")
    print("=" * 70)
    print()
    
    # Check if Ollama is available
    client = OllamaClient()
    
    if client.is_available():
        print(f"✅ Ollama is available with model: {client.config.model}")
        
        # Test a simple classification
        print("\n📝 Testing classification prompt...")
        
        system_prompt = """You are a code classifier. Respond with valid JSON only.
Format: {"role": "<role>", "confidence": <0.0-1.0>, "reasoning": "<explanation>"}
Allowed roles: Repository, Service, Controller, Entity, UseCase, Unknown"""
        
        user_prompt = """Classify this code:

```python
class UserRepository:
    def __init__(self, session):
        self.session = session
    
    def get_by_id(self, user_id):
        return self.session.query(User).filter_by(id=user_id).first()
    
    def save(self, user):
        self.session.add(user)
        self.session.commit()
```"""
        
        print("Calling Ollama...")
        response = client.classify(system_prompt, user_prompt)
        print(f"\n📤 Response:\n{response}")
        
        try:
            result = json.loads(response)
            print(f"\n✅ Parsed successfully: role={result.get('role')}, confidence={result.get('confidence')}")
        except json.JSONDecodeError:
            print(f"\n⚠️ Could not parse as JSON")
    else:
        print(f"❌ Ollama not available or model {client.config.model} not found")
        print("   Run: ollama pull qwen2.5:7b-instruct")
