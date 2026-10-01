"""URL query builder for Imobiliária Vale Invest rental search engine."""

import re
import unicodedata
from scripts.client.configuration import ValeInvestConfiguration
from scripts.domain.criteria import RentalFilter


class UrlSlugHelper:
    """Helper utility for normalizing and slugifying URL segments."""

    @staticmethod
    def slugify(raw_text: str) -> str:
        """Convert arbitrary Portuguese text into clean SEO URL slug."""
        if not raw_text:
            return ""
        normalized = unicodedata.normalize("NFKD", raw_text)
        ascii_chars = "".join(char for char in normalized if not unicodedata.combining(char))
        lowered = ascii_chars.lower().strip()
        cleaned = re.sub(r"[^\w\s-]", "", lowered)
        return re.sub(r"[\s_]+", "-", cleaned)


class ValeInvestQueryBuilder:
    """Builds canonical search URLs conforming to the Vale Invest Express router."""

    def __init__(self, configuration: ValeInvestConfiguration | None = None) -> None:
        """Initialize query builder with base configuration."""
        self._config = configuration or ValeInvestConfiguration()

    def _append_location_segments(self, segments: list[str], search_filter: RentalFilter) -> None:
        """Append state, city, and neighborhood segments if configured."""
        loc = search_filter.criteria.location
        if not loc.city:
            return
        segments.append("mg")
        city_slug = UrlSlugHelper.slugify(loc.city)
        segments.append(city_slug)
        if loc.neighborhood:
            neighborhood_slug = UrlSlugHelper.slugify(loc.neighborhood)
            segments.append(neighborhood_slug)

    def _append_specification_segments(self, segments: list[str], search_filter: RentalFilter) -> None:
        """Append property type and bedroom constraint segments."""
        specs = search_filter.criteria.specifications
        if specs.property_type:
            type_slug = UrlSlugHelper.slugify(specs.property_type)
            segments.append(type_slug)
        if specs.minimum_bedrooms > 0:
            segments.append(f"dormitorios-{specs.minimum_bedrooms}")

    def _append_price_segments(self, segments: list[str], search_filter: RentalFilter) -> None:
        """Append monetary pricing filter segments."""
        pr = search_filter.constraints.price_range
        min_val = int(pr.minimum_price.value())
        max_val = int(pr.maximum_price.value())
        if min_val > 0 and max_val > 0:
            segments.append(f"valor-{min_val}_{max_val}")
            return
        if min_val > 0:
            segments.append(f"valor-min_{min_val}")
            return
        if max_val > 0:
            segments.append(f"valor-max_{max_val}")

    def _append_order_segments(self, segments: list[str], search_filter: RentalFilter) -> None:
        """Append sorting and ordering segments."""
        sort = search_filter.constraints.sorting
        if not sort.field:
            return
        field_slug = UrlSlugHelper.slugify(sort.field)
        dir_slug = UrlSlugHelper.slugify(sort.direction)
        segments.append(f"ordem-{field_slug}")
        segments.append(f"resultado-{dir_slug}")

    def _append_pagination_segments(self, segments: list[str], search_filter: RentalFilter) -> None:
        """Append quantity and page number segments."""
        pag = search_filter.constraints.pagination
        if pag.page_size > 0:
            segments.append(f"quantidade-{pag.page_size}")
        if pag.page_number > 1:
            segments.append(f"pagina-{pag.page_number}")

    def build_search_path(self, search_filter: RentalFilter) -> str:
        """Construct relative URL path for rental search criteria."""
        segments = ["alugar"]
        self._append_location_segments(segments, search_filter)
        self._append_specification_segments(segments, search_filter)
        self._append_price_segments(segments, search_filter)
        self._append_order_segments(segments, search_filter)
        self._append_pagination_segments(segments, search_filter)
        joined_path = "/".join(segments)
        return f"/{joined_path}/"

    def build_search_url(self, search_filter: RentalFilter) -> str:
        """Construct complete canonical URL for rental search criteria."""
        relative_path = self.build_search_path(search_filter)
        return f"{self._config.base_url}{relative_path}"

    def build_detail_url(self, property_id: str) -> str:
        """Construct canonical property detail URL."""
        cleaned_id = property_id.strip()
        return f"{self._config.base_url}/alugar/mg/coronel-fabriciano/centro/imovel/{cleaned_id}"

    def build_reference_search_url(self, reference_code: str) -> str:
        """Construct URL to search listing by exact reference code."""
        cleaned_ref = reference_code.strip()
        return f"{self._config.base_url}/imoveis/referencia-{cleaned_ref}/"

    def build_facets_url(self) -> str:
        """Construct URL for taxonomy and inventory facet catalog."""
        return f"{self._config.base_url}/data/localizacoes.json"
