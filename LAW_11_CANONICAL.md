# 11 Fundamental Constraints (Canonical v1)

These are the eleven ontological constraints currently used by Spectrometer to derive a “hard impossible” subset (legacy target: 42).

Important:
- This is a **v1 constraint set**. The project is expected to grow beyond 11 as we separate **hard impossibilities** from **soft smells** and add architecture-mode-specific constraints (CQRS/DDD/etc.).

| ID | Name | Canonical statement | Scope (hadrons) | Violation → impossible pattern |
|----|------|---------------------|-----------------|--------------------------------|
| L1 | CQRS – Commands | A `CommandHandler` never returns domain data. | CommandHandler | CommandHandler::FindBy… |
| L2 | CQRS – Queries | A `QueryHandler` never mutates domain state. | QueryHandler | QueryHandler::Save… |
| L3 | Referential Purity | A `PureFunction` has no side effects (I/O, mutation, time). | PureFunction | PureFunction::ExternalIO |
| L4 | Entity Identity | An `Entity` always carries a persistent identifier. | Entity | Entity::Stateless / Entity w/o ID |
| L5 | Value Object Immutability | A `ValueObject` never has identity; equality is by value. | ValueObject | ValueObject::HasIdentity / ::Mutable |
| L6 | Repository Impurity | A `RepositoryImpl` is never pure (it performs I/O). | RepositoryImpl | RepositoryImpl::PureFunction |
| L7 | Fire‑and‑Forget Events | An `EventHandler` never returns a value. | EventHandler | EventHandler::ReturnsValue |
| L8 | External APIs | An `APIHandler` always crosses an external boundary. | APIHandler | APIHandler::InternalOnly |
| L9 | Stateless Services | An Application `Service` does not keep state between calls. | Service (App) | Service::GlobalState |
| L10 | Test Isolation | A `TestFunction` never touches production data. | TestFunction | TestFunction::ModifiesProductionData |
| L11 | Validator Rejection | A `Validator` never accepts invalid input/state. | Validator | Validator::AcceptsInvalid |

Notes
- These laws are exhaustive for the current Standard Model v4/v10. Changing any law changes the set of 42 impossibles.
- Each impossible subhadron in the canonical list is traceable to a single law above.
