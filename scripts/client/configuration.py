"""Configuration settings for Imobiliária Vale Invest API client."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ValeInvestConfiguration:
    """Holds configuration parameters for portal communication."""

    base_hostname: str = "imobiliariavaleinvest.com.br"
    base_url: str = "https://imobiliariavaleinvest.com.br"

    def origin_header_value(self) -> str:
        """Return canonical portal origin."""
        return f"https://{self.base_hostname}"

    def referer_header_value(self) -> str:
        """Return canonical portal referer."""
        return f"https://{self.base_hostname}/"
