# 384/42 Consistency Report

- Generated: 2025-12-14T05:41:15
- Canvas snapshot CSV: `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`
- Canonical impossible skeleton: `spectrometer_v12_minimal/IMPOSSIBLE_42_CANONICAL.csv`
- Canonical laws: `spectrometer_v12_minimal/LAW_11_CANONICAL.json`

## Expected vs Observed
| metric | expected | observed |
|---|---:|---:|
| total subhadrons | 384 | 384 |
| impossible (theory target) | 42 | 239 |
| possible (theory target) | 342 | 145 |

## Canvas Antimatter Distribution
| type | total | antimatter |
|---|---:|---:|
| `LambdaEntry` | 18 | 8 |
| `Service` | 12 | 8 |
| `CommandHandler` | 11 | 7 |
| `APIHandler` | 10 | 8 |
| `Actor` | 10 | 6 |
| `Entity` | 9 | 6 |
| `EventHandler` | 9 | 6 |
| `CircuitBreakerInit` | 9 | 6 |
| `ValueObject` | 8 | 6 |
| `HealthCheck` | 8 | 4 |
| `RateLimiter` | 8 | 3 |
| `FeatureFlagCheck` | 8 | 4 |
| `AggregateRoot` | 7 | 5 |
| `QueryHandler` | 7 | 4 |
| `DomainEvent` | 7 | 5 |
| `ContextMap` | 7 | 5 |
| `TracerProvider` | 7 | 4 |
| `MessageConsumer` | 7 | 5 |
| `QueueWorker` | 7 | 5 |
| `Cache` | 7 | 4 |
| `ChaosMonkey` | 6 | 4 |
| `GracefulShutdown` | 6 | 3 |
| `CanaryDeployTrigger` | 6 | 4 |
| `BoundedContext` | 6 | 3 |
| `MetricsExporter` | 6 | 4 |
| `Module` | 6 | 6 |
| `ContainerEntry` | 6 | 4 |
| `KubernetesJob` | 6 | 4 |
| `CronJob` | 6 | 4 |
| `WebWorker` | 6 | 3 |

## Top Antimatter Reasons (Canvas)
| reason | count |
|---|---:|
| Defeats purpose | 4 |
| Policy must be pure | 3 |
| Controller must not contain domain | 3 |
| DTO must be anemic | 2 |
| Saga must have compensation | 2 |
| Port must be interface only | 2 |
| Not a flag | 2 |
| Query cannot mutate | 2 |
| Repository must not contain business | 2 |
| Service must not touch storage | 2 |
| Domain service must be pure | 2 |
| Must be non-blocking | 2 |
| Must be async | 2 |
| Security risk | 2 |
| Breaks isolation | 2 |
| Risk of DoS | 2 |
| Not reproducible | 2 |
| No backpressure | 2 |
| Silent failures | 2 |
| Death spiral | 2 |
| Entity must have state | 1 |
| ValueObject cannot have identity | 1 |
| ValueObject must be immutable | 1 |
| CommandHandler cannot return data | 1 |
| QueryHandler cannot mutate state | 1 |
| EventHandler is fire-and-forget | 1 |
| Repository has I/O | 1 |
| Service must be stateless | 1 |
| API crosses boundary | 1 |
| Validator must reject | 1 |

## Canonical 42 Skeleton Coverage (Confirmed Items)
- Confirmed in skeleton: 16
- Placeholders in skeleton: 26
- Matched in canvas snapshot (heuristic): 13/16

| canonical | base_hadron | matched canvas subhadron | canvas type | canvas antimatter |
|---|---|---|---|---|
| `CommandHandler::FindById` | `CommandHandler` | `CommandHandler_FindById` | `CommandHandler` | True |
| `QueryHandler::Save` | `QueryHandler` | `QueryHandler_Save` | `QueryHandler` | True |
| `Entity::Stateless` | `Entity` | `Entity_Stateless` | `Entity` | True |
| `ValueObject::HasIdentity` | `ValueObject` | `ValueObject_WithIdentity` | `ValueObject` | True |
| `RepositoryImpl::PureFunction` | `RepositoryImpl` | `Repository_PureFunction` | `RepositoryImpl` | True |
| `PureFunction::ExternalIO` | `PureFunction` | — | — | — |
| `EventHandler::ReturnsValue` | `EventHandler` | `EventHandler_ReturnsValue` | `EventHandler` | True |
| `TestFunction::ModifiesProductionData` | `TestFunction` | `TestFunction_TouchesProduction` | `TestFunction` | True |
| `APIHandler::InternalOnly` | `APIHandler` | `APIHandler_InternalOnly` | `APIHandler` | True |
| `Service::GlobalState` | `Service` | `Service_GlobalState` | `Service` | True |
| `AggregateRoot::NoInvariants` | `AggregateRoot` | — | — | — |
| `Validator::AcceptsInvalid` | `Validator` | `Validator_AcceptsInvalid` | `Validator` | True |
| `Middleware::SkipsNext` | `Middleware` | — | — | — |
| `HealthCheck::Returns500WhenHealthy` | `HealthCheck` | `HealthCheck_Returns500WhenHealthy` | `HealthCheck` | True |
| `GracefulShutdown::HardKill` | `GracefulShutdown` | `GracefulShutdown_HardKill` | `GracefulShutdown` | True |
| `ChaosMonkey::ImprovesStability` | `ChaosMonkey` | `ChaosMonkey_ImprovesStability` | `ChaosMonkey` | True |

### Missing (Likely Taxonomy Drift)
- `AggregateRoot::NoInvariants` (base: `AggregateRoot`)
- `Middleware::SkipsNext` (base: `Middleware`)
- `PureFunction::ExternalIO` (base: `PureFunction`)

## Law Scope Coverage (L1–L11)
- Antimatter inside L1–L11 scopes: 51
- Antimatter outside L1–L11 scopes: 188

| law | antimatter count |
|---|---:|
| `L1` | 7 |
| `L10` | 1 |
| `L11` | 1 |
| `L2` | 4 |
| `L4` | 6 |
| `L5` | 6 |
| `L6` | 4 |
| `L7` | 6 |
| `L8` | 8 |
| `L9` | 8 |

## Interpretation
- The canvas contains a full 384-node subhadron set, but the current antimatter marking (239) does not match the theory target of 42; this implies the canvas is encoding additional “bad smells” as antimatter, or the 42 definition is being applied differently.
- The canonical 11-law list (L1–L11) only scopes a subset of types; a large portion of canvas antimatter is outside those scopes, which prevents deriving a stable 42 without deciding what is a hard-impossible law vs a soft smell.

## Next Steps (To Canonicalize 42)
- Decide the semantics of `impossible`: strict logical impossibility (42) vs strong architecture smell (additional canvas antimatter).
- If the target is strict-42: extend the extraction to map each antimatter pattern to a single law (or add new laws), then reclassify the remaining antimatter patterns as smells with severity (not impossible).
- Once canonicalized: generate `subhadrons_384.csv` and `impossible_42.csv` from a single ruleset and keep them machine-readable next to the detector.

