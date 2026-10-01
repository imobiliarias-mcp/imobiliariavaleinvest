"""Model Context Protocol (MCP) tool adapters for Central Rental Research."""

from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import ListingPrice, PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol
from scripts.providers.vale_invest import ValeInvestRentalProvider


class ValeInvestMcpAdapter:
    """Adapts domain rental provider for consumption by MCP servers and tool registries."""

    def __init__(self, provider: RentalProviderProtocol) -> None:
        """Initialize adapter with an abstract rental provider."""
        self._provider = provider

    @classmethod
    def create_default(cls) -> "ValeInvestMcpAdapter":
        """Factory constructor instantiating the default Vale Invest provider."""
        default_provider = ValeInvestRentalProvider.create_default()
        return cls(provider=default_provider)

    def _apply_constraints(self, target_filter: RentalFilter, max_price: float, bedrooms: int) -> RentalFilter:
        """Apply numerical constraints to search filter."""
        working = target_filter
        if bedrooms > 0:
            working = working.with_bedrooms(bedrooms)
        if max_price > 0.0:
            ceiling = ListingPrice(max_price)
            working = working.with_price_ceiling(ceiling)
        return working

    def _assemble_filter(self, city: str, max_price: float, bedrooms: int, page: int) -> RentalFilter:
        """Construct a validated RentalFilter from tool arguments."""
        working = RentalFilter().with_page(page)
        if city:
            working = working.with_city(city)
        return self._apply_constraints(working, max_price, bedrooms)

    def search_rentals(
        self,
        city: str = "",
        min_price: float = 0.0,
        max_price: float = 0.0,
        bedrooms: int = 0,
        property_type: str = "",
        page: int = 1,
    ) -> dict:
        """Execute a rental property search for an MCP tool call."""
        search_filter = self._assemble_filter(city, max_price, bedrooms, page)
        if property_type:
            search_filter = search_filter.with_property_type(property_type)
        if min_price > 0.0 and max_price > 0.0:
            search_filter = search_filter.with_price_range(min_price, max_price)
        search_result = self._provider.search_rentals(search_filter)
        return search_result.to_dictionary()

    def get_property_detail(self, property_code: str) -> dict:
        """Retrieve complete property detail for an MCP tool call."""
        code_vo = PropertyCode(property_code)
        property_detail = self._provider.get_property_detail(code_vo)
        return property_detail.to_dictionary()

    def get_facets(self) -> dict:
        """Retrieve available search facets for an MCP tool call."""
        facet_collection = self._provider.get_facets()
        return facet_collection.to_dictionary()
