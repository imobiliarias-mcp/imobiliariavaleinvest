"""Unit tests for search, detail, and facet HTML/JSON parsers."""

from pathlib import Path
import pytest
from scripts.client.parsers import (
    ValeInvestFacetParser,
    ValeInvestPropertyDetailParser,
    ValeInvestSearchResultParser,
)
from scripts.domain.exceptions import PropertyNotFoundException

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "tmp"


def test_parse_search_results_with_listings() -> None:
    """Verify parsing search page with active listings."""
    html_path = FIXTURE_DIR / "alugar_fabriciano.html"
    if not html_path.exists():
        pytest.skip("Fixture alugar_fabriciano.html not found.")
    html_content = html_path.read_text(encoding="utf-8")
    parser = ValeInvestSearchResultParser()
    result = parser.parse_search_response(html_content)

    assert result.total_count() == 32
    assert result.returned_count() == 12
    first_listing = list(result.listings())[0]
    assert first_listing.code() == "PT00028"
    assert first_listing.core.valuation.rental_price.value() == 620.0
    assert "CORONEL FABRICIANO" in first_listing.details.location_summary.upper()


def test_parse_search_results_target_page_empty() -> None:
    """Verify parsing target search page returning 0 results."""
    html_path = FIXTURE_DIR / "target_page.html"
    if not html_path.exists():
        pytest.skip("Fixture target_page.html not found.")
    html_content = html_path.read_text(encoding="utf-8")
    parser = ValeInvestSearchResultParser()
    result = parser.parse_search_response(html_content)

    assert result.total_count() == 0
    assert result.returned_count() == 0


def test_parse_property_detail_commercial() -> None:
    """Verify parsing commercial property detail page."""
    html_path = FIXTURE_DIR / "property_detail.html"
    if not html_path.exists():
        pytest.skip("Fixture property_detail.html not found.")
    html_content = html_path.read_text(encoding="utf-8")
    parser = ValeInvestPropertyDetailParser()
    detail = parser.parse_property_detail(html_content)

    assert detail.listing.code() == "PT00028"
    assert detail.listing.core.valuation.rental_price.value() == 620.0
    assert "FABRICIANO" in detail.listing.details.location_summary.upper()
    assert "ponto comercial" in detail.profile.description.lower()


def test_parse_property_detail_apartment() -> None:
    """Verify parsing apartment property detail page."""
    html_path = FIXTURE_DIR / "property_apartment.html"
    if not html_path.exists():
        pytest.skip("Fixture property_apartment.html not found.")
    html_content = html_path.read_text(encoding="utf-8")
    parser = ValeInvestPropertyDetailParser()
    detail = parser.parse_property_detail(html_content)

    assert detail.listing.code() == "AP00163"
    assert detail.listing.core.valuation.rental_price.value() == 800.0
    assert "FLORESTA" in detail.listing.details.location_summary.upper()
    assert "quartos" in detail.profile.amenities_summary.lower()


def test_parse_property_detail_missing_raises() -> None:
    """Verify parser raises PropertyNotFoundException for non-property page."""
    parser = ValeInvestPropertyDetailParser()
    with pytest.raises(PropertyNotFoundException):
        parser.parse_property_detail("<html><body><h1>Not Found</h1></body></html>")


def test_parse_facets_from_json() -> None:
    """Verify parsing facets catalog JSON."""
    json_path = FIXTURE_DIR / "localizacoes.json"
    if not json_path.exists():
        pytest.skip("Fixture localizacoes.json not found.")
    json_content = json_path.read_text(encoding="utf-8")
    parser = ValeInvestFacetParser()
    facets = parser.parse_facets(json_content)

    cities = facets.city_names()
    neighborhoods = facets.neighborhood_names()
    types = facets.property_types()

    assert len(cities) > 0
    assert any("Timóteo" in c or "Fabriciano" in c for c in cities)
    assert len(neighborhoods) > 0
    assert len(types) > 0
    assert "APARTAMENTO" in types
