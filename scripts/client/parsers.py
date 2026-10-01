"""HTML and JSON parsers for Imobiliária Vale Invest portal data."""

import json
import re
from bs4 import BeautifulSoup, Tag
from scripts.domain.collections import (
    FacetCollection,
    RentalListingCollection,
    RentalSearchResult,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import PropertyNotFoundException
from scripts.domain.value_objects import ListingPrice, PropertyCode


class CardFieldExtractor:
    """Helper extracting structured fields from single listing HTML card."""

    @staticmethod
    def extract_identifier(card_tag: Tag, href: str) -> str:
        """Extract property unique identifier from card href or favorites action."""
        id_match = re.search(r"/(\d+)/?$", href)
        if id_match:
            return id_match.group(1)
        fav_elem = card_tag.find(class_="botao_favoritos_fundo")
        if fav_elem and fav_elem.has_attr("onclick"):
            onclick = str(fav_elem["onclick"])
            match = re.search(r"favoritos\('(\d+)'\)", onclick)
            if match:
                return match.group(1)
        return "0"

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
    def extract_reference(card_tag: Tag, fallback_id: str) -> str:
        """Extract business reference code from flag tag."""
        ref_elem = card_tag.find(class_="flag_ref")
        if not ref_elem:
            return fallback_id
        text = ref_elem.get_text(strip=True)
        cleaned = text.replace("Ref.", "").replace("Ref", "").strip()
        if not cleaned:
            return fallback_id
        return cleaned


class ValeInvestSearchResultParser:
    """Parses search results HTML page into domain collections."""

    def _parse_card(self, card_tag: Tag) -> RentalListing:
        """Parse individual card HTML tag into domain RentalListing."""
        href = str(card_tag.get("href", ""))
        prop_id = CardFieldExtractor.extract_identifier(card_tag, href)
        ref_code = CardFieldExtractor.extract_reference(card_tag, prop_id)
        title_elem = card_tag.find(class_="titulo_novo")
        prop_type = title_elem.get_text(strip=True) if title_elem else "Imóvel"
        price_vo = CardFieldExtractor.extract_price(card_tag)
        loc_elem = card_tag.find(class_="final_card")
        location_str = loc_elem.get_text(strip=True) if loc_elem else ""
        img_elem = card_tag.find("img")
        media_url = ""
        if img_elem:
            media_url = img_elem.get("data-src") or img_elem.get("src", "")
        code_vo = PropertyCode(ref_code)
        identity = ListingIdentity(code=code_vo, title=f"{prop_type} - {ref_code}")
        valuation = ListingValuation(rental_price=price_vo, property_type=prop_type)
        core = ListingCore(identity=identity, valuation=valuation)
        details = ListingDetails(location_summary=location_str, media_url=media_url)
        return RentalListing(core=core, details=details)

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


class ValeInvestPropertyDetailParser:
    """Parses property detail page HTML into RentalPropertyDetail entity."""

    def _extract_detail_price(self, soup: BeautifulSoup) -> ListingPrice:
        """Extract rental price from detail page."""
        h4_elem = soup.find("h4")
        if not h4_elem:
            return ListingPrice(0.0)
        raw_text = h4_elem.get_text(strip=True)
        numeric_str = re.sub(r"[^\d,]", "", raw_text).replace(",", ".")
        if not numeric_str:
            return ListingPrice(0.0)
        return ListingPrice(float(numeric_str))

    def _extract_photos(self, soup: BeautifulSoup) -> list[str]:
        """Extract photo URLs from detail gallery."""
        photos = []
        for img in soup.find_all("img", class_="swiper_slide_img"):
            src = img.get("data-src") or img.get("src")
            if src and "cdn.uso.com.br" in src:
                photos.append(str(src))
        return photos

    def parse_property_detail(self, html_content: str) -> RentalPropertyDetail:
        """Parse property detail HTML into domain entity."""
        soup = BeautifulSoup(html_content, "html.parser")
        pk_input = soup.find(id="pkimovel_ficha")
        if not pk_input:
            raise PropertyNotFoundException("Property detail inputs not found on page.")
        ref_input = soup.find(id="referencia_imovel_ficha")
        code_str = str(ref_input["value"]).strip() if ref_input else str(pk_input["value"]).strip()
        code_vo = PropertyCode(code_str)
        title_elem = soup.find("h1", class_="titulo")
        title_str = title_elem.get_text(strip=True) if title_elem else f"Imóvel {code_str}"
        loc_elem = soup.find("h2", class_="localizacao")
        loc_str = loc_elem.get_text(strip=True) if loc_elem else ""
        price_vo = self._extract_detail_price(soup)
        desc_elem = soup.find(id="descricao_imovel")
        desc_str = desc_elem.get_text(separator=" ", strip=True) if desc_elem else ""
        features = [d.get_text(separator=" ", strip=True) for d in soup.find_all(class_="detalhe_novo")]
        amenities_str = ", ".join(features)
        photos = self._extract_photos(soup)
        main_photo = photos[0] if photos else ""
        identity = ListingIdentity(code=code_vo, title=title_str)
        valuation = ListingValuation(rental_price=price_vo, property_type="Imóvel")
        core = ListingCore(identity=identity, valuation=valuation)
        details = ListingDetails(location_summary=loc_str, media_url=main_photo)
        listing = RentalListing(core=core, details=details)
        profile = DetailedProfile(description=desc_str, amenities_summary=amenities_str)
        return RentalPropertyDetail(listing=listing, profile=profile)


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
