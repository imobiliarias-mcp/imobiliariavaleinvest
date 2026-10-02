"""Public property URL validation and documented reference fallback."""

from urllib.parse import parse_qs, quote, urljoin, urlsplit


class PublicPropertyUrlError(ValueError):
    """Raised when a listing has no recoverable public property URL."""


class PublicPropertyUrlResolver:
    """Resolve card links against the configured public site base URL."""

    def __init__(self, public_base_url: str) -> None:
        """Validate and retain the configured public site base URL."""
        self._base_url = self._validate_base_url(public_base_url)

    def resolve(self, raw_url: object, property_context: str, fallback_url: str = "") -> str:
        """Resolve a card link, using only a supplied documented fallback."""
        candidate = self._clean_candidate(raw_url)
        if candidate:
            return self._resolve_candidate(candidate, property_context)
        if not fallback_url:
            raise PublicPropertyUrlError(f"Missing public property URL for '{property_context}'.")
        return self._resolve_candidate(fallback_url, property_context)

    def reference_fallback_url(self, reference_code: str) -> str:
        """Build the documented reference lookup URL for an explicit code."""
        cleaned_reference = reference_code.strip()
        if not cleaned_reference:
            return ""
        encoded_reference = quote(cleaned_reference, safe="")
        return urljoin(self._base_url, f"/imoveis/referencia-{encoded_reference}/")

    def _clean_candidate(self, raw_url: object) -> str:
        """Trim string URL input and reject values of other types."""
        if not isinstance(raw_url, str):
            return ""
        return raw_url.strip()

    def _validate_base_url(self, public_base_url: str) -> str:
        """Require an HTTP(S) base URL with a hostname."""
        try:
            parts = urlsplit(public_base_url.strip())
            hostname = parts.hostname
        except ValueError as error:
            raise PublicPropertyUrlError("Invalid configured public base URL.") from error
        if parts.scheme.lower() not in {"http", "https"} or not hostname:
            raise PublicPropertyUrlError("Invalid configured public base URL.")
        return f"{public_base_url.rstrip('/')}/"

    def _resolve_candidate(self, candidate: str, property_context: str) -> str:
        """Join a candidate link and validate its final scheme and host."""
        try:
            absolute_url = urljoin(self._base_url, candidate)
            parts = urlsplit(absolute_url)
            hostname = parts.hostname
        except ValueError as error:
            raise PublicPropertyUrlError(
                f"Invalid public property URL for '{property_context}'."
            ) from error
        if parts.scheme.lower() not in {"http", "https"} or not hostname or parts.username or parts.password:
            raise PublicPropertyUrlError(f"Invalid public property URL for '{property_context}'.")
        if not self._is_property_page(parts):
            raise PublicPropertyUrlError(f"Invalid public property URL for '{property_context}'.")
        return absolute_url

    def _is_property_page(self, parts) -> bool:
        """Accept documented property routes, not facets, media, or searches."""
        path = parts.path.lower().rstrip("/")
        if self._is_media_path(path) or path.endswith(".json"):
            return False
        if path == "/imovel" and parse_qs(parts.query).get("id"):
            return True
        if path.startswith("/imoveis/referencia-"):
            return True
        return self._is_detail_route(path)

    def _is_detail_route(self, path: str) -> bool:
        """Require a public listing identifier at the end of known detail routes."""
        route_prefixes = ("/alugar/", "/comprar/", "/comprar-ou-alugar/")
        if not path.startswith(route_prefixes):
            return False
        identifier = path.rsplit("/", 1)[-1]
        return identifier.isdigit() or self._is_reference_identifier(identifier)

    def _is_reference_identifier(self, identifier: str) -> bool:
        """Recognize alphanumeric reference identifiers ending in digits."""
        prefix = identifier.rstrip("0123456789")
        suffix = identifier[len(prefix):]
        return bool(prefix) and prefix.isalpha() and bool(suffix) and suffix.isdigit()

    @staticmethod
    def _is_media_path(path: str) -> bool:
        """Recognize common public media asset suffixes."""
        return path.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"))
