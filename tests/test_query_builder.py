"""Unit tests for ValeInvestQueryBuilder."""

from scripts.client.query_builder import UrlSlugHelper, ValeInvestQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import ListingPrice


def test_slug_helper() -> None:
    """Verify UrlSlugHelper handles accents, uppercase, and special chars."""
    assert UrlSlugHelper.slugify("Timóteo") == "timoteo"
    assert UrlSlugHelper.slugify("Coronel Fabriciano") == "coronel-fabriciano"
    assert UrlSlugHelper.slugify("São Geraldo") == "sao-geraldo"
    assert UrlSlugHelper.slugify("APARTAMENTO") == "apartamento"
    assert UrlSlugHelper.slugify("") == ""


def test_default_rental_url() -> None:
    """Verify default filter builds /alugar/ordem-valor/resultado-crescente/quantidade-12/."""
    builder = ValeInvestQueryBuilder()
    f = RentalFilter()
    url = builder.build_search_url(f)
    assert url == "https://imobiliariavaleinvest.com.br/alugar/ordem-valor/resultado-crescente/quantidade-12/"


def test_target_url_exact_match() -> None:
    """Verify query builder matches user target URL character-for-character."""
    builder = ValeInvestQueryBuilder()
    f = (
        RentalFilter()
        .with_city("Timoteo")
        .with_bedrooms(2)
        .with_sorting("valor", "crescente")
        .with_page_size(12)
    )
    url = builder.build_search_url(f)
    expected = (
        "https://imobiliariavaleinvest.com.br/alugar/mg/timoteo/"
        "dormitorios-2/ordem-valor/resultado-crescente/quantidade-12/"
    )
    assert url == expected


def test_price_range_url() -> None:
    """Verify price range segments."""
    builder = ValeInvestQueryBuilder()
    f_range = RentalFilter().with_city("Coronel Fabriciano").with_price_range(600, 1500)
    url = builder.build_search_url(f_range)
    assert "/valor-600_1500/" in url

    f_max = RentalFilter().with_city("Coronel Fabriciano").with_price_ceiling(ListingPrice(2000.0))
    url_max = builder.build_search_url(f_max)
    assert "/valor-max_2000/" in url_max


def test_pagination_and_size_url() -> None:
    """Verify page number and page size segments."""
    builder = ValeInvestQueryBuilder()
    f = RentalFilter().with_page(3).with_page_size(24)
    url = builder.build_search_url(f)
    assert "/quantidade-24/" in url
    assert "/pagina-3/" in url


def test_detail_and_reference_urls() -> None:
    """Verify property detail and reference search URLs."""
    builder = ValeInvestQueryBuilder()
    detail_url = builder.build_detail_url("78933085")
    assert detail_url.endswith("/78933085")

    ref_url = builder.build_reference_search_url("PT00028")
    assert "/imoveis/referencia-PT00028/" in ref_url

    facets_url = builder.build_facets_url()
    assert facets_url.endswith("/data/localizacoes.json")
