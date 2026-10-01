# ADR 0001: Architecture & Design of Central Rental Research MCP Modules (Imobiliária Vale Invest)

## Status
Accepted

## Context
The system requires reverse-engineering the rental property search API of **Imobiliária Vale Invest** (`https://imobiliariavaleinvest.com.br/`) and architecting modular Python components intended for integration into a **Central Rental Research MCP (Model Context Protocol)** server.

A central MCP server allows AI assistants and client applications to query multiple real estate platforms through a unified tool contract. To achieve this, the integration must not be a monolithic scraping script, but rather a decoupled, highly cohesive, modular architecture.

Furthermore, the implementation must strictly satisfy:
- **Prioritization Order**: Correctness first, modularity second, style principles third.
- **SOLID Principles**
- **Clean Code**
- **Object Calisthenics** (9 strict rules)
- **Design Patterns** (Adapter, Strategy, Value Object, First-Class Collection, Factory, Builder)
- **Fail-Fast input validation**
- **Defensive error handling**

---

## Decision

We adopt a **Hexagonal / Ports-and-Adapters Architecture** partitioned into four explicit layers:

```
┌────────────────────────────────────────────────────────┐
│               Central Rental Research MCP              │
│               (Model Context Protocol Tools)           │
└──────────────────────────┬─────────────────────────────┘
                           │ uses Port (Protocol)
                           ▼
┌────────────────────────────────────────────────────────┐
│                   Domain Layer                         │
│  - Value Objects (Price, Code, RoomCount, Area)        │
│  - First-Class Collections (Listings, Facets)          │
│  - Domain Exceptions                                   │
│  - Provider Port Interface (RentalProviderProtocol)    │
└──────────────────────────▲─────────────────────────────┘
                           │ implements Port
┌──────────────────────────┴─────────────────────────────┐
│                 Adapter / Provider Layer               │
│  - ValeInvestRentalProvider                            │
│  - ValeInvestMcpAdapter                                │
└──────────────────────────┬─────────────────────────────┘
                           │ coordinates
┌──────────────────────────▼─────────────────────────────┐
│                  Infrastructure Layer                  │
│  - ValeInvestConfiguration (Portal URLs & defaults)    │
│  - ValeInvestHttpTransport (Desktop User-Agent)        │
│  - ValeInvestQueryBuilder (Path & param assembly)      │
│  - Parsers (SearchResultParser, DetailParser, Facets)  │
└────────────────────────────────────────────────────────┘
```

---

## Object Calisthenics Enforcement Matrix

| Calisthenics Rule | Implementation Strategy in Python |
| :--- | :--- |
| **1. One level of indentation per method** | Deep loops and branching are decomposed into named single-purpose private helper methods. |
| **2. Don't use the `else` keyword** | Guard clauses, early returns, polymorphic strategies, or dictionary dispatch tables are used exclusively. Zero `else` keywords across the codebase. |
| **3. Wrap all primitives and strings** | Raw primitives are wrapped in domain value objects: `ListingPrice`, `PropertyCode`, `RoomCount`, `AreaMeasure`, `SearchPagination`. |
| **4. First-class collections** | Any class containing a collection contains no other member fields, exposing only domain collection operations: `RentalListingCollection`, `FacetCollection`, `RentalSearchResult`. |
| **5. One dot per line** | No deep chaining (`a.b().c()`). Every intermediate object is assigned to an explicitly named local variable. |
| **6. Don't abbreviate** | Descriptive domain naming throughout (`response`, `request`, `listing`, `search_filter`, `neighborhood`, `configuration`). |
| **7. Keep all entities small** | Functions ≤ 15 lines, classes ≤ 100 lines, modules < 200 lines. |
| **8. No classes with more than 2 instance variables** | Classes declare at most 2 member attributes. Larger state is factored into value objects or collaborator objects. |
| **9. No getters/setters (Tell, Don't Ask)** | Domain objects encapsulate their state and expose behaviors or representations (`format_brl()`, `format_summary()`, `to_dictionary()`), not mutable getters/setters. |

---

## SOLID Principles Application

### Single Responsibility Principle (SRP)
- `ValeInvestHttpTransport`: Strictly responsible for HTTP network transport and headers.
- `ValeInvestQueryBuilder`: Strictly responsible for converting high-level `RentalFilter` to canonical SEO paths.
- `ValeInvestSearchResultParser`: Strictly responsible for parsing HTML cards into `RentalSearchResult`.
- `ValeInvestPropertyDetailParser`: Strictly responsible for parsing detail HTML.
- `ValeInvestFacetParser`: Strictly responsible for parsing localizacoes JSON catalog.

### Open/Closed Principle (OCP)
- New search criteria or output formats can be extended without modifying existing provider abstractions.
- `RentalProviderProtocol` defines contracts open to extension for new real estate agencies.

### Liskov Substitution Principle (LSP)
- `ValeInvestRentalProvider` fully honors `RentalProviderProtocol` without violating preconditions or postconditions.

### Interface Segregation Principle (ISP)
- Segregated into `RentalSearchCapability`, `RentalDetailCapability`, `RentalFacetsCapability`, united under `RentalProviderProtocol`.

### Dependency Inversion Principle (DIP)
- High-level tools and adapters depend on abstractions (`RentalProviderProtocol`), with concrete implementations injected via constructors or factories.
