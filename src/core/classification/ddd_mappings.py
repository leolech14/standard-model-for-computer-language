"""
DDD Type Mappings for Inheritance-based Classification
Separated to avoid circular imports and clean up classifiers.
"""

DDD_BASE_CLASS_MAPPINGS = {
    # Entities & Aggregates
    "Entity": "Entity",
    "BaseEntity": "Entity",
    "DomainEntity": "Entity",
    "EntityModel": "Entity",
    "AggregateRoot": "AggregateRoot",
    "Aggregate": "AggregateRoot",
    
    # Value Objects
    "ValueObject": "ValueObject",
    "ValueObjectModel": "ValueObject",
    "BaseFrozenModel": "ValueObject",
    
    # Repositories
    "GenericRepository": "Repository",
    "AbstractRepository": "Repository",
    "BaseRepository": "Repository",
    
    # Events
    "DomainEvent": "DomainEvent",
    "Event": "DomainEvent",
    "IntegrationEvent": "DomainEvent",
    
    # Commands/Queries (CQRS)
    "Command": "Command",
    "BaseCommand": "Command",
    "Query": "Query",
    "BaseQuery": "Query",
    
    # Services
    "DomainService": "DomainService",
    "ApplicationService": "Service",
    
    # Configuration
    "BaseSettings": "Configuration",
}
