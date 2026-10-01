"""Imobiliária Vale Invest rental research package."""

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
from scripts.domain.entities import RentalListing, RentalPropertyDetail
from scripts.domain.value_objects import ListingPrice, PropertyCode
from scripts.mcp.tools import ValeInvestMcpAdapter
from scripts.providers.vale_invest import ValeInvestRentalProvider
from valei_research.client import ValeInvestRentalClient

__all__ = [
    "FacetCollection",
    "ListingPrice",
    "PropertyCode",
    "RentalFilter",
    "RentalListing",
    "RentalPropertyDetail",
    "RentalSearchResult",
    "ValeInvestConfiguration",
    "ValeInvestFacetParser",
    "ValeInvestHttpTransport",
    "ValeInvestMcpAdapter",
    "ValeInvestPropertyDetailParser",
    "ValeInvestQueryBuilder",
    "ValeInvestRentalClient",
    "ValeInvestRentalProvider",
    "ValeInvestSearchResultParser",
]
