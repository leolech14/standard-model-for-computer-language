# Canonical Mermaids (v1 catalogs)

Mermaid diagrams for the key v1 canonical lists: constraints (11), forbidden archetypes (legacy 42 skeleton), and the RPBL purpose-map snapshot (1440 grid).

## 11 Fundamental Constraints (v1)
```mermaid
graph TD
    L1["L1 CQRS – Commands<br/>CommandHandler never returns data"]:::law
    L2["L2 CQRS – Queries<br/>QueryHandler never mutates state"]:::law
    L3["L3 Referential Purity<br/>PureFunction has no side effects"]:::law
    L4["L4 Entity Identity<br/>Entity always has ID"]:::law
    L5["L5 ValueObject Immutability<br/>VO has no identity"]:::law
    L6["L6 Repository Impurity<br/>RepositoryImpl is never pure"]:::law
    L7["L7 Fire-and-Forget Events<br/>EventHandler never returns value"]:::law
    L8["L8 External APIs<br/>APIHandler always crosses boundary"]:::law
    L9["L9 Stateless Services<br/>Service does not keep state"]:::law
    L10["L10 Test Isolation<br/>TestFunction never touches prod data"]:::law
    L11["L11 Validator Rejection<br/>Validator never accepts invalid"]:::law

    subgraph "11 Constraints (v1)"
      L1 --> L2 --> L3 --> L4 --> L5 --> L6 --> L7 --> L8 --> L9 --> L10 --> L11
    end

    classDef law fill:#111,color:#fff,stroke:#999,stroke-width:1.2px;
```

## Forbidden Archetypes (legacy “42 impossible”, skeleton)
```mermaid
graph TD
    subgraph "Confirmed (16)"
      I1["CommandHandler::FindById<br/>L1"]:::imp
      I2["QueryHandler::Save<br/>L2"]:::imp
      I3["Entity::Stateless<br/>L4"]:::imp
      I4["ValueObject::HasIdentity<br/>L5"]:::imp
      I5["RepositoryImpl::PureFunction<br/>L6"]:::imp
      I6["PureFunction::ExternalIO<br/>L3"]:::imp
      I7["EventHandler::ReturnsValue<br/>L7"]:::imp
      I8["TestFunction::ModifiesProductionData<br/>L10"]:::imp
      I9["APIHandler::InternalOnly<br/>L8"]:::imp
      I10["Service::GlobalState<br/>L9"]:::imp
      I11["AggregateRoot::NoInvariants<br/>pending"]:::imp
      I12["Validator::AcceptsInvalid<br/>L11"]:::imp
      I13["Middleware::SkipsNext<br/>pending"]:::imp
      I14["HealthCheck::Returns500WhenHealthy<br/>pending"]:::imp
      I15["GracefulShutdown::HardKill<br/>pending"]:::imp
      I16["ChaosMonkey::ImprovesStability<br/>pending"]:::imp
    end

    subgraph "Placeholders (26)"
      P17["TBD_17"]:::placeholder
      P18["TBD_18"]:::placeholder
      P19["TBD_19"]:::placeholder
      P20["TBD_20"]:::placeholder
      P21["TBD_21"]:::placeholder
      P22["TBD_22"]:::placeholder
      P23["TBD_23"]:::placeholder
      P24["TBD_24"]:::placeholder
      P25["TBD_25"]:::placeholder
      P26["TBD_26"]:::placeholder
      P27["TBD_27"]:::placeholder
      P28["TBD_28"]:::placeholder
      P29["TBD_29"]:::placeholder
      P30["TBD_30"]:::placeholder
      P31["TBD_31"]:::placeholder
      P32["TBD_32"]:::placeholder
      P33["TBD_33"]:::placeholder
      P34["TBD_34"]:::placeholder
      P35["TBD_35"]:::placeholder
      P36["TBD_36"]:::placeholder
      P37["TBD_37"]:::placeholder
      P38["TBD_38"]:::placeholder
      P39["TBD_39"]:::placeholder
      P40["TBD_40"]:::placeholder
      P41["TBD_41"]:::placeholder
      P42["TBD_42"]:::placeholder
    end

    classDef imp fill:#220000,color:#ff6666,stroke:#ff3333,stroke-width:1.4px;
    classDef placeholder fill:#111111,color:#777,stroke:#444,stroke-width:1px,stroke-dasharray:3 3;
```

## RPBL Purpose Map Snapshot (1440 grid)
```mermaid
flowchart TD
    A["1,440 Grid<br/>source: 1440_csv.csv"]:::root --> C["Continents<br/>5 present"]:::cont
    A --> H["Hadrons<br/>79 subtypes present"]:::had
    A --> I["Impossible rows<br/>81 rows / 56 hadron subtypes"]:::imp

    C --> C1["Counts:<br/>Execution 530<br/>Logic & Flow 400<br/>Organization 275<br/>Data Foundations 144<br/>Foundations 91"]
    H --> H1["Top occurrences (19 each):<br/>TestFile, Actor, TryCatch,<br/>MainEntry, QueryHandler,<br/>GraphQLResolver, LocalVar,<br/>SourceFile, ContainerEntry, DTO"]
    I --> I1["Continent spread:<br/>Exec 25, Org 24, L&F 22,<br/>DataF 8, Foundations 2"]
    I --> I2["Top impossible hadrons:<br/>Entity 5, CommandHandler 4,<br/>ValueObject 3, QueryHandler 2, DTO 2…"]

    classDef root fill:#0b1b2b,color:#fff,stroke:#4fc3f7,stroke-width:1.5px;
    classDef cont fill:#1c2f3f,color:#9be7ff,stroke:#4fc3f7,stroke-width:1px;
    classDef had fill:#1f2933,color:#c3e88d,stroke:#8bc34a,stroke-width:1px;
    classDef imp fill:#2b1b1b,color:#ff8a80,stroke:#ef5350,stroke-width:1px;
```
