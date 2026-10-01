# Imobiliária Vale Invest — Rental Search MCP Research & Client

Reverse-engineered rental search integration and client modules for **Imobiliária Vale Invest** (`imobiliariavaleinvest.com.br`), engineered for the central rental research MCP.

## Key Features
- **Stateless Search Engine**: Canonical SEO URL generation matching the Express router conventions.
- **Full Filter Support**: Municipality, neighborhood, property typology, bedrooms, price range, sorting, and pagination.
- **Property Detail Extraction**: Comprehensive extraction of property titles, internal IDs, reference codes, descriptions, amenities, and high-resolution photo URLs.
- **Taxonomy & Inventory Catalog**: Integration with `/data/localizacoes.json` exposing complete facets.
- **Clean Architecture**: Adheres strictly to SOLID, Object Calisthenics (no else, wrapped primitives, small entities, <= 2 attributes), and Hexagonal design.

## Quick Start

### 1. Run Search CLI
```bash
python3 scripts/run_search.py --city "Coronel Fabriciano" --page-size 3
```

### 2. View Property Details CLI
```bash
python3 scripts/run_property_detail.py 78933085
python3 scripts/run_property_detail.py PT00028
```

### 3. Query Facets CLI
```bash
python3 scripts/run_facets.py
```

### 4. Run Test Suite
```bash
# Standalone zero-dependency test runner
python3 scripts/run_tests.py

# Pytest suite
.venv/bin/pytest -v
```

## Documentation
- [API Research & Specification](docs/api-research.md)
- [Research Plan & Report](scripts/research-plan.md)
- [Architecture Decision Record (ADR 0001)](docs/adr/0001-rental-search-mcp-module-design.md)
- [Single Source of Truth Specification](docs/sot/vale_invest_union_api_spec.md)
- [Python API Reference](docs/api_reference.md)
