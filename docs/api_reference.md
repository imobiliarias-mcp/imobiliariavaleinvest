# API Reference & Usage Guide: Imobiliária Vale Invest Research

## Python Module Usage

### 1. Execute Rental Searches
```python
from scripts.providers.vale_invest import ValeInvestRentalProvider
from scripts.domain.criteria import RentalFilter

provider = ValeInvestRentalProvider.create_default()

# Basic search
search_filter = (
    RentalFilter()
    .with_city("Coronel Fabriciano")
    .with_property_type("Apartamento")
    .with_bedrooms(2)
    .with_page_size(12)
)

result = provider.search_rentals(search_filter)
print(f"Total matching: {result.total_count()}")

for listing in result.listings():
    print(listing.format_summary())
    print("Public property URL:", listing.to_dictionary()["url"])
```

### 2. Retrieve Property Details
```python
from scripts.providers.vale_invest import ValeInvestRentalProvider
from scripts.domain.value_objects import PropertyCode

provider = ValeInvestRentalProvider.create_default()

# Retrieve by ID or Reference
property_detail = provider.get_property_detail(PropertyCode("78933085"))
print(property_detail.format_detailed_view())
print("Public property URL:", property_detail.to_dictionary()["url"])
```

### 3. Retrieve Search Facets & Taxonomy
```python
from scripts.providers.vale_invest import ValeInvestRentalProvider

provider = ValeInvestRentalProvider.create_default()
facets = provider.get_facets()

print("Available Cities:", facets.city_names())
print("Available Types:", facets.property_types())
```

### 4. Use MCP Tool Adapter
```python
from scripts.mcp.tools import ValeInvestMcpAdapter

adapter = ValeInvestMcpAdapter.create_default()

# Tool invocation for LLM agent
search_data = adapter.search_rentals(city="Coronel Fabriciano", bedrooms=2)
print(search_data["total_count"], len(search_data["listings"]))

property_data = adapter.get_property_detail("PT00028")
print(property_data["title"], property_data["rental_price_formatted"])
```
