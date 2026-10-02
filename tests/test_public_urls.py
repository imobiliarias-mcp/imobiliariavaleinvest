"""Offline public property URL contract tests for Vale Invest."""

import html

import pytest

from scripts.client.configuration import ValeInvestConfiguration
from scripts.client.parsers import ValeInvestSearchResultParser
from scripts.client.public_urls import PublicPropertyUrlError
from scripts.domain.criteria import RentalFilter
from scripts.mcp.tools import ValeInvestMcpAdapter
from scripts.providers.vale_invest import ValeInvestRentalProvider
from scripts.run_search import display_results
from valei_research.client import ValeInvestRentalClient

PUBLIC_BASE = "https://imobiliariavaleinvest.com.br"
CUSTOM_BASE = "https://listings.example.test"


def listing_card(href: str, reference: str = "PT00028") -> str:
    """Build one documented search-card shape with an optional public reference."""
    escaped_href = html.escape(href, quote=True)
    reference_html = f'<div class="flag_ref"><span>Ref.{reference}</span></div>' if reference else ""
    return (
        f'<a class="link_resultado" href="{escaped_href}">'
        '<h3 class="titulo_novo">PONTO</h3><h5>R$ 620,00</h5>'
        '<div class="final_card">CENTRO - CORONEL FABRICIANO/MG</div>'
        '<img src="https://cdn.uso.com.br/cover.jpg">'
        f'{reference_html}<div class="botao_favoritos_fundo" onclick="favoritos(\'78933085\');"></div>'
        '</a><input id="countResultado" value="1">'
    )


@pytest.mark.parametrize(
    ("href", "expected_url"),
    [
        (
            "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
            "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
        ),
        (
            "/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
            "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
        ),
        (
            "alugar/mg/coronel-fabriciano/centro/ponto/78933085",
            "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
        ),
        (
            "//imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
            "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/78933085",
        ),
        (
            "/imovel?id=608",
            "https://imobiliariavaleinvest.com.br/imovel?id=608",
        ),
    ],
)
def test_search_parser_serializes_normalized_card_url(href: str, expected_url: str) -> None:
    """Resolve card links and preserve query identifiers, media, and prices."""
    result = ValeInvestSearchResultParser().parse_search_response(listing_card(href))
    serialized = result.to_dictionary()
    listing = serialized["listings"][0]

    assert listing["url"] == expected_url
    assert listing["code"] == "PT00028"
    assert listing["rental_price"] == 620.0
    assert listing["media_url"] == "https://cdn.uso.com.br/cover.jpg"
    assert serialized["returned_count"] == 1


def test_query_identifier_is_used_for_card_identity() -> None:
    """Read the public id query parameter when a card URL has no path id."""
    result = ValeInvestSearchResultParser().parse_search_response(listing_card("/imovel?id=608", ""))

    assert result.to_dictionary()["listings"][0]["code"] == "608"


def test_missing_card_link_uses_only_documented_reference_lookup_route() -> None:
    """Build the documented reference lookup only from a public reference code."""
    result = ValeInvestSearchResultParser().parse_search_response(listing_card("", "PT00028"))

    assert result.to_dictionary()["listings"][0]["url"] == f"{PUBLIC_BASE}/imoveis/referencia-PT00028/"


def test_invalid_or_unrecoverable_card_link_raises_with_property_context() -> None:
    """Reject invalid links when no documented public-reference fallback exists."""
    parser = ValeInvestSearchResultParser()

    invalid_urls = (
        "javascript:alert(1)",
        "https://imobiliariavaleinvest.com.br/data/localizacoes.json",
        "https://cdn.uso.com.br/property.jpg",
        "https://imobiliariavaleinvest.com.br/alugar/mg/coronel-fabriciano/centro/ponto/quantidade-12/",
    )
    for invalid_url in invalid_urls:
        with pytest.raises(ValueError, match="78933085"):
            parser.parse_search_response(listing_card(invalid_url, ""))
    with pytest.raises(ValueError, match="78933085"):
        parser.parse_search_response(listing_card("", ""))


def test_invalid_card_url_is_not_replaced_by_reference_fallback() -> None:
    """Use the documented fallback only when the card link is absent."""
    parser = ValeInvestSearchResultParser()

    with pytest.raises(ValueError, match="PT00028"):
        parser.parse_search_response(listing_card("javascript:alert(1)", "PT00028"))


def test_malformed_card_href_raises_contextual_public_url_error() -> None:
    """Retain available public reference when href parsing fails."""
    parser = ValeInvestSearchResultParser()

    with pytest.raises(PublicPropertyUrlError, match="PT00028"):
        parser.parse_search_response(listing_card("http://[broken", "PT00028"))


def test_provider_config_flows_to_parser_and_client_without_extra_requests() -> None:
    """Use configured site origin through the facade and retain one search call."""
    configuration = ValeInvestConfiguration(base_url=CUSTOM_BASE)
    transport = StubValeInvestTransport(listing_card("/alugar/mg/timoteo/ponto/78933085"))
    provider = ValeInvestRentalProvider(transport, ConfiguredQueryBuilder(configuration))
    client = ValeInvestRentalClient(provider=provider)

    result = client.search(RentalFilter())

    assert result.to_dictionary()["listings"][0]["url"] == f"{CUSTOM_BASE}/alugar/mg/timoteo/ponto/78933085"
    assert transport.call_count == 1


def test_existing_mcp_adapter_and_cli_expose_public_url(capsys: pytest.CaptureFixture[str]) -> None:
    """Return the same resolved URL through MCP and command-line output."""
    result = ValeInvestSearchResultParser().parse_search_response(
        listing_card("/alugar/mg/coronel-fabriciano/centro/ponto/78933085")
    )
    adapter = ValeInvestMcpAdapter(FixedSearchProvider(result))

    mcp_result = adapter.search_rentals(city="Timóteo")
    display_results(result)

    expected_url = f"{PUBLIC_BASE}/alugar/mg/coronel-fabriciano/centro/ponto/78933085"
    assert mcp_result["listings"][0]["url"] == expected_url
    assert f"Link: {expected_url}" in capsys.readouterr().out


class StubValeInvestTransport:
    """Serve one HTML search response and count transport calls."""

    def __init__(self, html_content: str) -> None:
        self._html_content = html_content
        self.call_count = 0

    def get_text(self, url: str) -> str:
        self.call_count += 1
        return self._html_content


class ConfiguredQueryBuilder:
    """Construct the regular query builder with a configured public origin."""

    def __new__(cls, configuration):
        from scripts.client.query_builder import ValeInvestQueryBuilder

        return ValeInvestQueryBuilder(configuration=configuration)


class FixedSearchProvider:
    """Return an injected search result without live requests."""

    def __init__(self, result) -> None:
        self._result = result

    def search_rentals(self, _search_filter):
        return self._result
