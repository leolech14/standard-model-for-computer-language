#!/usr/bin/env python3
"""
Role Migration Script

Maps deprecated roles to canonical 27 roles.
Run this before validation to ensure consistency.
"""

# Mapping of old roles to canonical equivalents
ROLE_MIGRATION = {
    # Business Logic roles → Service
    "UseCase": "Service",
    "DomainService": "Service", 
    "ApplicationService": "Service",
    "Lifecycle": "Service",
    "Job": "Service",
    
    # Validation/Rules → Validator
    "Policy": "Validator",
    "Specification": "Validator",
    
    # Data Transformation → Transformer
    "Mapper": "Transformer",
    
    # Data Representations → Entity
    "ValueObject": "Entity",
    "DTO": "Entity",
    
    # Adaptation → Adapter
    "Gateway": "Adapter",
    "Provider": "Factory",
    
    # Observation → Observer
    "Subscriber": "Observer",
    
    # Helpers → Utility
    "Internal": "Utility",
    
    # Events → EventHandler
    "DomainEvent": "EventHandler",
    
    # Other deprecated → closest match
    "Iterator": "Utility",
    "Exception": "Entity",
}

def migrate_role(old_role: str) -> str:
    """Convert deprecated role to canonical equivalent."""
    return ROLE_MIGRATION.get(old_role, old_role)

if __name__ == "__main__":
    print("Role Migration Map:")
    print("=" * 50)
    for old, new in sorted(ROLE_MIGRATION.items()):
        print(f"{old:20s} → {new}")
