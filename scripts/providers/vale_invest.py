"""Imobiliária Vale Invest rental search provider implementation."""

from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

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
from scripts.domain.exceptions import PropertyNotFoundException
from scripts.domain.value_objects import PropertyCode
from scripts.interfaces.provider import RentalProviderProtocol


class ValeInvestRentalProvider(RentalProviderProtocol):
    """Adapter implementing RentalProviderProtocol for Imobiliária Vale Invest."""

    def __init__(
        self,
        transport: ValeInvestHttpTransport,
        query_builder: ValeInvestQueryBuilder,
    ) -> None:
        """Initialize provider with transport and query builder."""
        self._transport = transport
        self._builder = query_builder

    @classmethod
    def create_default(cls) -> "ValeInvestRentalProvider":
        """Factory method constructing provider with default configurations."""
        config = ValeInvestConfiguration()
        client = httpx.Client(timeout=20.0, follow_redirects=True)
        transport = ValeInvestHttpTransport(configuration=config, http_client=client)
        builder = ValeInvestQueryBuilder(configuration=config)
        return cls(transport=transport, query_builder=builder)

    def provider_name(self) -> str:
        """Return unique provider identifier for central MCP registry."""
        return "vale_invest"

    def search_rentals(self, search_filter: RentalFilter) -> RentalSearchResult:
        """Search rental listings using criteria."""
        search_url = self._builder.build_search_url(search_filter)
        html_content = self._transport.get_text(search_url)
        parser = ValeInvestSearchResultParser(public_base_url=self._builder.public_base_url())
        return parser.parse_search_response(html_content)

    def _resolve_detail_url(self, code_str: str) -> str:
        """Resolve property URL from numeric ID or alphanumeric reference code."""
        if code_str.isdigit():
            return self._builder.build_detail_url(code_str)
        ref_search_url = self._builder.build_reference_search_url(code_str)
        html = self._transport.get_text(ref_search_url)
        soup = BeautifulSoup(html, "html.parser")
        card = soup.find("a", class_="link_resultado")
        if not card or not card.has_attr("href"):
            raise PropertyNotFoundException(f"Property with reference '{code_str}' was not found.")
        relative_href = str(card["href"])
        base_url = self._builder.public_base_url()
        return urljoin(f"{base_url}/", relative_href)

    def get_property_detail(self, code: PropertyCode) -> RentalPropertyDetail:
        """Retrieve full details for a single property by code or ID."""
        code_str = code.value()
        target_url = self._resolve_detail_url(code_str)
        html_content = self._transport.get_text(target_url)
        parser = ValeInvestPropertyDetailParser(public_base_url=self._builder.public_base_url())
        return parser.parse_property_detail(html_content)

    def get_facets(self) -> FacetCollection:
        """Retrieve taxonomy and inventory facets from localizacoes.json."""
        facets_url = self._builder.build_facets_url()
        json_data = self._transport.get_json(facets_url)
        parser = ValeInvestFacetParser()
        return parser.parse_facets(json_data)
