"""Unit tests for Vale Invest client facade and MCP adapter."""

from unittest.mock import MagicMock
from scripts.client.configuration import ValeInvestConfiguration
from scripts.client.http_transport import ValeInvestHttpTransport
from scripts.client.query_builder import ValeInvestQueryBuilder
from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import PropertyCode
from scripts.mcp.tools import ValeInvestMcpAdapter
from scripts.providers.vale_invest import ValeInvestRentalProvider
from valei_research.client import ValeInvestRentalClient


def test_configuration_defaults() -> None:
    """Verify configuration defaults and headers."""
    cfg = ValeInvestConfiguration()
    assert cfg.base_hostname == "imobiliariavaleinvest.com.br"
    assert cfg.origin_header_value() == "https://imobiliariavaleinvest.com.br"
    assert cfg.referer_header_value() == "https://imobiliariavaleinvest.com.br/"


def test_provider_with_mock_transport() -> None:
    """Verify provider coordinates transport, builder, and parser."""
    mock_transport = MagicMock(spec=ValeInvestHttpTransport)
    mock_transport.get_text.return_value = """
    <html>
      <body>
        <input id="countResultado" value="1" />
        <a class="link_resultado" href="/alugar/mg/coronel-fabriciano/centro/ponto/78933085">
          <h3 class="titulo_novo">Ponto</h3>
          <h5>R$ 620,00</h5>
          <span class="flag_ref">Ref.PT00028</span>
          <div class="final_card"><span>Centro - Coronel Fabriciano/MG</span></div>
        </a>
      </body>
    </html>
    """
    builder = ValeInvestQueryBuilder()
    provider = ValeInvestRentalProvider(transport=mock_transport, query_builder=builder)

    search_filter = RentalFilter().with_city("Coronel Fabriciano")
    result = provider.search_rentals(search_filter)

    assert result.total_count() == 1
    assert result.returned_count() == 1
    first = list(result.listings())[0]
    assert first.code() == "PT00028"


def test_mcp_adapter_serialization() -> None:
    """Verify MCP adapter returns valid dictionary structures."""
    adapter = ValeInvestMcpAdapter.create_default()
    mock_provider = MagicMock(spec=ValeInvestRentalProvider)

    mock_result = MagicMock()
    mock_result.to_dictionary.return_value = {"total_count": 0, "returned_count": 0, "listings": []}
    mock_provider.search_rentals.return_value = mock_result

    adapter_with_mock = ValeInvestMcpAdapter(provider=mock_provider)
    payload = adapter_with_mock.search_rentals(city="Timoteo", bedrooms=2, page=1)

    assert "total_count" in payload
    assert "listings" in payload
    mock_provider.search_rentals.assert_called_once()


def test_rental_client_facade() -> None:
    """Verify ValeInvestRentalClient delegates to provider."""
    mock_provider = MagicMock(spec=ValeInvestRentalProvider)
    mock_provider.search_rentals.return_value = MagicMock()
    client = ValeInvestRentalClient(provider=mock_provider)

    client.search_by_parameters(city="Fabriciano", max_price=1500.0)
    mock_provider.search_rentals.assert_called_once()
