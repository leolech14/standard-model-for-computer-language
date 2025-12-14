# Subhadrons 384 — Extracted From Canvas

- Generated: 2025-12-14T05:38:30
- Source: `THEORY_COMPLETE.canvas`
- CSV: `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`

## Snapshot
- Total subhadrons found: 384
- Marked antimatter in canvas: 239
- Marked non-antimatter in canvas: 145
- Unique `Type:` values: 66

## Top Types
| type | count | antimatter |
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

## Antimatter Reasons (Top)
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

## Note
This is a faithful snapshot of what the canvas currently marks as antimatter; it is not asserting that the true canonical impossible set is 42.

