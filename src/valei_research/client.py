"""High-level client module for Imobiliária Vale Invest research operations."""

from scripts.client.configuration import ValeInvestConfiguration
from scripts.client.http_transport import ValeInvestHttpTransport
from scripts.client.parsers import (
    ValeInvestFacetParser,
    ValeInvestPropertyDetailParser,
    ValeInvestSearchResultParser,
)
from scripts.client.query_builder import ValeInvestQueryBuilder
from scripts.domain.collections import FacetCollection, RentalSearchResult
from scripts.domain.criteria import RentalFilter
from scripts.domain.entities import RentalPropertyDetail
from scripts.domain.value_objects import ListingPrice, PropertyCode
from scripts.providers.vale_invest import ValeInvestRentalProvider


class ValeInvestRentalClient:
    """Convenience facade for rental search, detail retrieval, and facet queries."""

    def __init__(self, provider: ValeInvestRentalProvider | None = None) -> None:
        """Initialize client with a provider or create default."""
        self._provider = provider or ValeInvestRentalProvider.create_default()

    @classmethod
    def create_default(cls) -> "ValeInvestRentalClient":
        """Factory constructor instantiating default client configuration."""
        provider = ValeInvestRentalProvider.create_default()
        return cls(provider=provider)

    def search(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Execute rental search with domain filter."""
        return self._provider.search_rentals(search_filter)

    def search_by_parameters(
        self,
        city: str = "",
        neighborhood: str = "",
        bedrooms: int = 0,
        property_type: str = "",
        max_price: float = 0.0,
        page: int = 1,
        page_size: int = 12,
        sort_field: str = "valor",
        sort_direction: str = "crescente",
    ) -> RentalSearchResult:
        """Execute rental search using parameter primitives."""
        rf = (
            RentalFilter()
            .with_page(page)
            .with_page_size(page_size)
            .with_sorting(sort_field, sort_direction)
        )
        if city:
            rf = rf.with_city(city)
        if neighborhood:
            rf = rf.with_neighborhood(neighborhood)
        if bedrooms > 0:
            rf = rf.with_bedrooms(bedrooms)
        if property_type:
            rf = rf.with_property_type(property_type)
        if max_price > 0.0:
            rf = rf.with_price_ceiling(ListingPrice(max_price))
        return self._provider.search_rentals(rf)

    def get_property(self, code_or_id: str) -> RentalPropertyDetail:
        """Retrieve single property details by reference or numeric ID."""
        code_vo = PropertyCode(code_or_id)
        return self._provider.get_property_detail(code_vo)

    def get_facets(self) -> FacetCollection:
        """Retrieve available taxonomy and inventory facets."""
        return self._provider.get_facets()
