"""Provider interfaces and capabilities for central rental research MCP."""

from typing import Protocol, runtime_checkable
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.value_objects import PropertyCode


@runtime_checkable
class RentalSearchCapability(Protocol):
    """Capability protocol for searching rental properties."""

    def search_rentals(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Search rental listings matching filter criteria."""
        ...


@runtime_checkable
class RentalDetailCapability(Protocol):
    """Capability protocol for retrieving single property details."""

    def get_property_detail(self, code: PropertyCode) -> RentalPropertyDetail:
        """Retrieve full details of a specific property listing."""
        ...


@runtime_checkable
class RentalFacetsCapability(Protocol):
    """Capability protocol for retrieving search aggregations."""

    def get_facets(self) -> FacetCollection:
        """Retrieve available cities, neighborhoods, and filter facets."""
        ...


@runtime_checkable
class RentalProviderProtocol(
    RentalSearchCapability,
    RentalDetailCapability,
    RentalFacetsCapability,
    Protocol,
):
    """Complete provider interface for Central Rental Research MCP integration."""

    def provider_name(self) -> str:
        """Return unique provider name identifier."""
        ...
