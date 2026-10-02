"""HTML and JSON parsers for Imobiliária Vale Invest portal data."""

import json
import re
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup, Tag

from scripts.client.property_detail_parser import ValeInvestPropertyDetailParser
from scripts.client.public_urls import PublicPropertyUrlError, PublicPropertyUrlResolver
from scripts.domain.collections import (
    FacetCollection,
    RentalListingCollection,
    RentalSearchResult,
)
from scripts.domain.entities import (
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingResources,
    ListingValuation,
    RentalListing,
)
from scripts.domain.value_objects import ListingPrice, PropertyCode

__all__ = [
    "CardFieldExtractor",
    "ValeInvestFacetParser",
    "ValeInvestPropertyDetailParser",
    "ValeInvestSearchResultParser",
]


class CardFieldExtractor:
    """Helper extracting structured fields from single listing HTML card."""

    @staticmethod
    def extract_identifier(card_tag: Tag, href: str) -> str:
        """Extract property unique identifier from card href or favorites action."""
        try:
            parsed_href = urlsplit(href)
        except ValueError as error:
            context = CardFieldExtractor.extract_public_reference(card_tag) or "unknown"
            raise PublicPropertyUrlError(f"Invalid public property URL for '{context}'.") from error
        query_identifier = parse_qs(parsed_href.query).get("id", [""])[0]
        if query_identifier.isdigit():
            return query_identifier
        id_match = re.search(r"/(\d+)/?$", parsed_href.path)
        if id_match:
            return id_match.group(1)
        return CardFieldExtractor._extract_favorite_identifier(card_tag)

    @staticmethod
    def _extract_favorite_identifier(card_tag: Tag) -> str:
        """Read fallback listing ID from the favorites action."""
        favorite_element = card_tag.find(class_="botao_favoritos_fundo")
        if not favorite_element or not favorite_element.has_attr("onclick"):
            return "0"
        match = re.search(r"favoritos\('(\d+)'\)", str(favorite_element["onclick"]))
        if not match:
            return "0"
        return match.group(1)

    @staticmethod
    def extract_price(card_tag: Tag) -> ListingPrice:
        """Extract monetary price from card element."""
        price_elem = card_tag.find("h5")
        if not price_elem:
            return ListingPrice(0.0)
        raw_text = price_elem.get_text(strip=True)
        numeric_str = re.sub(r"[^\d,]", "", raw_text).replace(",", ".")
        if not numeric_str:
            return ListingPrice(0.0)
        return ListingPrice(float(numeric_str))

    @staticmethod
    def extract_public_reference(card_tag: Tag) -> str:
        """Extract an explicit public reference code from the card."""
        ref_elem = card_tag.find(class_="flag_ref")
        if not ref_elem:
            return ""
        text = ref_elem.get_text(strip=True)
        return text.replace("Ref.", "").replace("Ref", "").strip()

    @staticmethod
    def extract_reference(card_tag: Tag, fallback_id: str) -> str:
        """Return explicit public reference or the stable card identifier."""
        public_reference = CardFieldExtractor.extract_public_reference(card_tag)
        return public_reference or fallback_id


class ValeInvestSearchResultParser:
    """Parses search results HTML page into domain collections."""

    DEFAULT_PUBLIC_BASE_URL = "https://imobiliariavaleinvest.com.br"

    def __init__(self, public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> None:
        """Initialize URL resolution with the configured public origin."""
        self._url_resolver = PublicPropertyUrlResolver(public_base_url)

    def _parse_card(self, card_tag: Tag) -> RentalListing:
        """Parse individual card HTML tag into domain RentalListing."""
        href = str(card_tag.get("href", ""))
        property_id = CardFieldExtractor.extract_identifier(card_tag, href)
        reference = CardFieldExtractor.extract_public_reference(card_tag)
        identity = self._build_identity(card_tag, property_id, reference)
        valuation = self._build_valuation(card_tag)
        details = self._build_details(card_tag, href, property_id, reference)
        return RentalListing(core=ListingCore(identity=identity, valuation=valuation), details=details)

    def _build_identity(self, card_tag: Tag, property_id: str, reference: str) -> ListingIdentity:
        """Build listing identity from explicit reference and card identifier."""
        code = reference or property_id
        title_elem = card_tag.find(class_="titulo_novo")
        property_type = title_elem.get_text(strip=True) if title_elem else "Imóvel"
        return ListingIdentity(code=PropertyCode(code), title=f"{property_type} - {code}")

    def _build_valuation(self, card_tag: Tag) -> ListingValuation:
        """Build listing valuation from card price and type fields."""
        title_elem = card_tag.find(class_="titulo_novo")
        property_type = title_elem.get_text(strip=True) if title_elem else "Imóvel"
        price = CardFieldExtractor.extract_price(card_tag)
        return ListingValuation(rental_price=price, property_type=property_type)

    def _build_details(
        self, card_tag: Tag, href: str, property_id: str, reference: str
    ) -> ListingDetails:
        """Build location and normalized property/media resources."""
        location_elem = card_tag.find(class_="final_card")
        location = location_elem.get_text(strip=True) if location_elem else ""
        image_elem = card_tag.find("img")
        media_url = self._extract_media_url(image_elem)
        context = reference or property_id or "unknown"
        fallback_url = self._url_resolver.reference_fallback_url(reference)
        property_url = self._url_resolver.resolve(href, context, fallback_url)
        resources = ListingResources(media_url=media_url, property_url=property_url)
        return ListingDetails(location_summary=location, resources=resources)

    def _extract_media_url(self, image_elem: Tag | None) -> str:
        """Return primary card image URL when present."""
        if not image_elem:
            return ""
        return str(image_elem.get("data-src") or image_elem.get("src", ""))

    def _extract_total_count(self, soup: BeautifulSoup, parsed_cards_count: int) -> int:
        """Extract total listings count from hidden input or card count."""
        count_input = soup.find(id="countResultado")
        if count_input and count_input.has_attr("value"):
            raw_val = str(count_input["value"]).strip()
            if raw_val.isdigit():
                return int(raw_val)
        return parsed_cards_count

    def parse_search_response(self, html_content: str) -> RentalSearchResult:
        """Parse full search page HTML into RentalSearchResult."""
        soup = BeautifulSoup(html_content, "html.parser")
        card_tags = soup.find_all("a", class_="link_resultado")
        listings = []
        for card_tag in card_tags:
            listing = self._parse_card(card_tag)
            listings.append(listing)
        collection = RentalListingCollection(listings=tuple(listings))
        total_count = self._extract_total_count(soup, len(listings))
        return RentalSearchResult(collection=collection, total_listings_count=total_count)


class ValeInvestFacetParser:
    """Parses /data/localizacoes.json into FacetCollection."""

    def parse_facets(self, json_payload) -> FacetCollection:
        """Parse JSON localizacoes catalog into search facets."""
        data = json_payload
        if isinstance(json_payload, str):
            data = json.loads(json_payload)
        if isinstance(data, list) and data:
            data = data[0]
        imoveis = data.get("imoveis", []) if isinstance(data, dict) else []
        cities = set()
        neighborhoods = set()
        types = set()
        for item in imoveis:
            if not isinstance(item, dict):
                continue
            city = item.get("cidade")
            if city:
                cities.add(city.strip().title())
            bairro = item.get("bairro")
            if bairro:
                neighborhoods.add(bairro.strip().title())
            ptype = item.get("tipo")
            if ptype:
                types.add(ptype.strip().upper())
        facet_map = {
            "cities": tuple(sorted(cities)),
            "neighborhoods": tuple(sorted(neighborhoods)),
            "types": tuple(sorted(types)),
        }
        return FacetCollection(facet_map=facet_map)
