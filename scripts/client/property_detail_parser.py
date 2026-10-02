"""Parser for individual Vale Invest property detail pages."""

import re

from bs4 import BeautifulSoup

from scripts.client.public_urls import PublicPropertyUrlResolver
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingResources,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import PropertyNotFoundException
from scripts.domain.value_objects import ListingPrice, PropertyCode


class ValeInvestPropertyDetailParser:
    """Parse detail page HTML into a public property detail entity."""

    DEFAULT_PUBLIC_BASE_URL = "https://imobiliariavaleinvest.com.br"

    def __init__(self, public_base_url: str = DEFAULT_PUBLIC_BASE_URL) -> None:
        """Initialize property URL resolution with the configured public origin."""
        self._url_resolver = PublicPropertyUrlResolver(public_base_url)

    def _extract_detail_price(self, soup: BeautifulSoup) -> ListingPrice:
        """Extract rental price from detail page."""
        price_element = soup.find("h4")
        if not price_element:
            return ListingPrice(0.0)
        raw_text = price_element.get_text(strip=True)
        numeric_text = re.sub(r"[^\d,]", "", raw_text).replace(",", ".")
        if not numeric_text:
            return ListingPrice(0.0)
        return ListingPrice(float(numeric_text))

    def _extract_photos(self, soup: BeautifulSoup) -> list[str]:
        """Extract media CDN URLs from detail gallery."""
        photos = []
        for image in soup.find_all("img", class_="swiper_slide_img"):
            source = image.get("data-src") or image.get("src")
            if source and "cdn.uso.com.br" in source:
                photos.append(str(source))
        return photos

    def _extract_input_value(self, soup: BeautifulSoup, element_id: str) -> str:
        """Read one hidden property identity field from detail markup."""
        element = soup.find(id=element_id)
        if not element:
            return ""
        return str(element.get("value", "")).strip()

    def _extract_public_url(self, soup: BeautifulSoup, context: str, reference: str) -> str:
        """Resolve canonical detail URL or documented explicit-reference fallback."""
        canonical_link = soup.find("link", rel="canonical")
        raw_url = str(canonical_link.get("href", "")) if canonical_link else ""
        fallback_url = self._url_resolver.reference_fallback_url(reference)
        return self._url_resolver.resolve(raw_url, context, fallback_url)

    def _build_listing(self, soup: BeautifulSoup, code: str, public_url: str) -> RentalListing:
        """Build listing identity, valuation, and resources from detail markup."""
        title = self._extract_text(soup, "h1", "titulo") or f"Imóvel {code}"
        location = self._extract_text(soup, "h2", "localizacao")
        photo_list = self._extract_photos(soup)
        media_url = photo_list[0] if photo_list else ""
        identity = ListingIdentity(code=PropertyCode(code), title=title)
        valuation = ListingValuation(rental_price=self._extract_detail_price(soup), property_type="Imóvel")
        resources = ListingResources(media_url=media_url, property_url=public_url)
        details = ListingDetails(location_summary=location, resources=resources)
        return RentalListing(core=ListingCore(identity=identity, valuation=valuation), details=details)

    def _extract_text(self, soup: BeautifulSoup, tag_name: str, class_name: str) -> str:
        """Extract visible text from one tag and class pair."""
        element = soup.find(tag_name, class_=class_name)
        return element.get_text(strip=True) if element else ""

    def _build_profile(self, soup: BeautifulSoup) -> DetailedProfile:
        """Build description and amenities from detail page markup."""
        description_element = soup.find(id="descricao_imovel")
        description = description_element.get_text(separator=" ", strip=True) if description_element else ""
        features = [item.get_text(separator=" ", strip=True) for item in soup.find_all(class_="detalhe_novo")]
        return DetailedProfile(description=description, amenities_summary=", ".join(features))

    def parse_property_detail(self, html_content: str) -> RentalPropertyDetail:
        """Parse a detail page and require a resolved public property link."""
        soup = BeautifulSoup(html_content, "html.parser")
        property_id = self._extract_input_value(soup, "pkimovel_ficha")
        if not property_id:
            raise PropertyNotFoundException("Property detail inputs not found on page.")
        reference = self._extract_input_value(soup, "referencia_imovel_ficha")
        code = reference or property_id
        public_url = self._extract_public_url(soup, code, reference)
        listing = self._build_listing(soup, code, public_url)
        return RentalPropertyDetail(listing=listing, profile=self._build_profile(soup))
