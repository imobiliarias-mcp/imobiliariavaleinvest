"""HTTP transport layer for Imobiliária Vale Invest web queries."""

import httpx
from scripts.client.configuration import ValeInvestConfiguration
from scripts.domain.exceptions import NetworkTransportException


class ValeInvestHttpTransport:
    """Dispatches HTTP network requests to imobiliariavaleinvest.com.br."""

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(
        self,
        configuration: ValeInvestConfiguration | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Initialize transport with configuration and client collaborator."""
        self._config = configuration or ValeInvestConfiguration()
        client = http_client or httpx.Client(timeout=20.0, follow_redirects=True)
        client.headers["User-Agent"] = self.DEFAULT_USER_AGENT
        client.headers["Accept-Language"] = "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
        self._client = client

    def get_text(self, url: str) -> str:
        """Fetch and return text payload from URL."""
        response = self.get_response(url)
        return response.text

    def get_json(self, url: str):
        """Fetch and parse JSON payload from URL."""
        response = self.get_response(url)
        try:
            return response.json()
        except Exception as error:
            raise NetworkTransportException(f"Failed to parse JSON from {url}: {error}") from error

    def get_response(self, url: str) -> httpx.Response:
        """Execute HTTP GET and return raw response."""
        try:
            response = self._client.get(url)
            response.raise_for_status()
            return response
        except httpx.HTTPError as error:
            raise NetworkTransportException(f"Network request to {url} failed: {error}") from error

    def post_form(self, url: str, data: dict) -> httpx.Response:
        """Execute HTTP POST with form payload."""
        try:
            response = self._client.post(url, data=data)
            response.raise_for_status()
            return response
        except httpx.HTTPError as error:
            raise NetworkTransportException(f"Network POST to {url} failed: {error}") from error
