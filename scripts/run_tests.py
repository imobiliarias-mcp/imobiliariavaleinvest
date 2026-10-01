"""Standalone test runner for Vale Invest rental research modules."""

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.client.query_builder import ValeInvestQueryBuilder
from scripts.domain.criteria import PriceRange, RentalFilter
from scripts.domain.exceptions import InvalidFilterException, InvalidPriceException
from scripts.domain.value_objects import ListingPrice, PropertyCode
from scripts.mcp.tools import ValeInvestMcpAdapter
from scripts.providers.vale_invest import ValeInvestRentalProvider


def test_listing_price_validation() -> None:
    """Verify ListingPrice rejects negative amounts and formats BRL."""
    price = ListingPrice(1500.50)
    assert price.format_brl() == "R$ 1.500,50"
    assert not price.is_zero()
    try:
        ListingPrice(-10.0)
        assert False, "Should have raised InvalidPriceException"
    except InvalidPriceException:
        pass


def test_price_range_validation() -> None:
    """Verify PriceRange raises error when minimum exceeds maximum."""
    min_price = ListingPrice(3000.0)
    max_price = ListingPrice(1000.0)
    try:
        PriceRange(minimum_price=min_price, maximum_price=max_price)
        assert False, "Should have raised InvalidFilterException"
    except InvalidFilterException:
        pass


def test_target_url_query_builder() -> None:
    """Verify ValeInvestQueryBuilder builds exact user target URL."""
    builder = ValeInvestQueryBuilder()
    filter_obj = (
        RentalFilter()
        .with_city("Timoteo")
        .with_bedrooms(2)
        .with_sorting("valor", "crescente")
        .with_page_size(12)
    )
    url = builder.build_search_url(filter_obj)
    expected = (
        "https://imobiliariavaleinvest.com.br/alugar/mg/timoteo/"
        "dormitorios-2/ordem-valor/resultado-crescente/quantidade-12/"
    )
    assert url == expected, f"Mismatch: {url} != {expected}"


def test_provider_live_search() -> None:
    """Test live search execution against Vale Invest portal."""
    provider = ValeInvestRentalProvider.create_default()
    criteria = RentalFilter().with_city("Coronel Fabriciano")
    result = provider.search_rentals(criteria)
    assert result.total_count() > 0
    assert result.returned_count() > 0
    first_listing = list(result.listings())[0]
    assert len(first_listing.code()) > 0


def test_provider_live_target_url() -> None:
    """Test execution of exact user target URL."""
    provider = ValeInvestRentalProvider.create_default()
    filter_obj = (
        RentalFilter()
        .with_city("Timoteo")
        .with_bedrooms(2)
        .with_sorting("valor", "crescente")
        .with_page_size(12)
    )
    result = provider.search_rentals(filter_obj)
    assert result.total_count() == 0
    assert result.returned_count() == 0


def test_provider_live_detail() -> None:
    """Test live detail retrieval for a known property."""
    provider = ValeInvestRentalProvider.create_default()
    code = PropertyCode("78933085")
    detail = provider.get_property_detail(code)
    assert detail.listing.code() in ["78933085", "PT00028"]
    assert "FABRICIANO" in detail.listing.details.location_summary.upper()


def test_provider_live_facets() -> None:
    """Test live facets retrieval from localizacoes.json."""
    provider = ValeInvestRentalProvider.create_default()
    facets = provider.get_facets()
    cities = facets.city_names()
    assert len(cities) > 0
    assert any("Timóteo" in c or "Fabriciano" in c for c in cities)


def test_mcp_adapter() -> None:
    """Test MCP tool adapter returns serializable dictionaries."""
    adapter = ValeInvestMcpAdapter.create_default()
    search_payload = adapter.search_rentals(city="Coronel Fabriciano", page=1)
    assert "listings" in search_payload
    assert "total_count" in search_payload
    assert search_payload["total_count"] > 0


def _run_unit() -> None:
    """Run pure unit tests."""
    test_listing_price_validation()
    test_price_range_validation()
    test_target_url_query_builder()
    print("✔ Testes unitários de domínio e query builder: OK")


def _run_integration() -> None:
    """Run live API integration tests."""
    test_provider_live_search()
    test_provider_live_target_url()
    test_provider_live_detail()
    test_provider_live_facets()
    print("✔ Testes de integração de API e URL alvo: OK")


def main() -> None:
    """Execute all test suites."""
    print("Executando bateria de testes para Imobiliária Vale Invest...")
    _run_unit()
    _run_integration()
    test_mcp_adapter()
    print("✔ Testes do adaptador MCP: OK")
    print("\n🎉 TODOS OS TESTES PASSARAM COM SUCESSO!\n")


if __name__ == "__main__":
    main()
