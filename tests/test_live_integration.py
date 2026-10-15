"""Integration tests connecting to live Imobiliária Vale Invest endpoints."""

import pytest
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.providers.vale_invest import ValeInvestRentalProvider


@pytest.fixture
def provider() -> ValeInvestRentalProvider:
    """Fixture returning default configured rental provider."""
    return ValeInvestRentalProvider.create_default()


def test_live_search_rentals(provider: ValeInvestRentalProvider) -> None:
    """Ensure live rental search returns valid listings from portal."""
    search_filter = RentalFilter().with_city("Coronel Fabriciano")
    result = provider.search_rentals(search_filter)

    assert result.total_count() > 0
    assert result.returned_count() > 0
    listings_list = list(result.listings())
    assert len(listings_list) > 0
    assert len(listings_list[0].code()) > 0


def test_live_target_url_reproduction(provider: ValeInvestRentalProvider) -> None:
    """Verify live search behavior on the user-specified target URL.

    URL: https://imobiliariavaleinvest.com.br/alugar/mg/timoteo/dormitorios-2/ordem-valor/resultado-crescente/quantidade-12/
    Note: As verified via localizacoes.json, Timóteo currently hosts only commercial
    rentals (PONTO), so 2-bedroom filter correctly returns 0 matching properties.
    """
    target_filter = (
        RentalFilter()
        .with_city("Timoteo")
        .with_bedrooms(2)
        .with_sorting("valor", "crescente")
        .with_page_size(12)
    )
    result = provider.search_rentals(target_filter)

    assert result.total_count() == 0
    assert result.returned_count() == 0


def test_live_property_detail_retrieval(provider: ValeInvestRentalProvider) -> None:
    """Ensure live property detail retrieval fetches complete info."""
    search_result = provider.search_rentals(RentalFilter().with_city("Coronel Fabriciano"))
    listed_code = next(iter(search_result.listings())).code()
    detail = provider.get_property_detail(PropertyCode(listed_code))

    assert detail.listing.code() == listed_code
    assert detail.listing.core.valuation.rental_price.value() > 0.0
    assert "FABRICIANO" in detail.listing.details.location_summary.upper()


def test_live_facets_retrieval(provider: ValeInvestRentalProvider) -> None:
    """Ensure live facets fetch taxonomy and locations catalog."""
    facets = provider.get_facets()
    cities = facets.city_names()

    assert len(cities) > 0
    assert any("Timóteo" in c or "Fabriciano" in c for c in cities)
