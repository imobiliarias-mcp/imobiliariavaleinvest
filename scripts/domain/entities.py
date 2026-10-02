"""Domain entities for rental property listings."""

from dataclasses import dataclass
from urllib.parse import urlsplit

from scripts.domain.value_objects import ListingPrice, PropertyCode


def _validated_public_url(property_url: str, property_context: str) -> str:
    """Require a serialized public URL to be absolute HTTP(S) without credentials."""
    try:
        parts = urlsplit(property_url)
        hostname = parts.hostname
    except ValueError as error:
        raise ValueError(f"Invalid public property URL for '{property_context}'.") from error
    if (
        property_url != property_url.strip()
        or parts.scheme.lower() not in {"http", "https"}
        or not hostname
        or parts.username
        or parts.password
    ):
        raise ValueError(f"Invalid public property URL for '{property_context}'.")
    return property_url


@dataclass(frozen=True)
class ListingIdentity:
    """Core identification fields for a listing."""

    code: PropertyCode
    title: str


@dataclass(frozen=True)
class ListingValuation:
    """Monetary and typology valuation for a listing."""

    rental_price: ListingPrice
    property_type: str


@dataclass(frozen=True)
class ListingCore:
    """Combines identification and valuation attributes."""

    identity: ListingIdentity
    valuation: ListingValuation


@dataclass(frozen=True)
class ListingResources:
    """Public property page and media resource URLs."""

    media_url: str
    property_url: str = ""

    def to_dictionary(self, property_context: str) -> dict:
        """Serialize legacy media and a validated public property URL."""
        public_url = _validated_public_url(self.property_url, property_context)
        return {"media_url": self.media_url, "url": public_url}


@dataclass(frozen=True, init=False)
class ListingDetails:
    """Supplementary display metadata with legacy media constructor support."""

    location_summary: str
    resources: ListingResources

    def __init__(
        self,
        location_summary: str,
        resources: ListingResources | str | None = None,
        *,
        media_url: str = "",
        property_url: str = "",
    ) -> None:
        """Accept composed resources or the legacy positional/keyword media URL."""
        legacy_media_url = resources if isinstance(resources, str) else media_url
        if resources is None or isinstance(resources, str):
            resources = ListingResources(media_url=legacy_media_url, property_url=property_url)
        object.__setattr__(self, "location_summary", location_summary)
        object.__setattr__(self, "resources", resources)

    @property
    def media_url(self) -> str:
        """Return the legacy media URL through composed resources."""
        return self.resources.media_url


@dataclass(frozen=True)
class RentalListing:
    """Lightweight rental listing model for search results."""

    core: ListingCore
    details: ListingDetails

    def code(self) -> str:
        """Return business listing code."""
        return self.core.identity.code.value()

    def title(self) -> str:
        """Return public display title."""
        return self.core.identity.title

    def format_summary(self) -> str:
        """Format listing into a readable single-line summary."""
        code_str = self.core.identity.code.value()
        price_str = self.core.valuation.rental_price.format_brl()
        type_str = self.core.valuation.property_type
        loc_str = self.details.location_summary
        return f"[{code_str}] {type_str} em {loc_str} - {price_str}/mês"

    def to_dictionary(self) -> dict:
        """Export entity with a valid public property URL."""
        property_code = self.core.identity.code.value()
        resources = self.details.resources.to_dictionary(property_code)
        return {
            "code": property_code,
            "title": self.core.identity.title,
            "property_type": self.core.valuation.property_type,
            "rental_price": self.core.valuation.rental_price.value(),
            "rental_price_formatted": self.core.valuation.rental_price.format_brl(),
            "location": self.details.location_summary,
            **resources,
        }


@dataclass(frozen=True)
class DetailedProfile:
    """Extended description and attributes for a listing."""

    description: str
    amenities_summary: str


@dataclass(frozen=True)
class RentalPropertyDetail:
    """Detailed rental property view."""

    listing: RentalListing
    profile: DetailedProfile

    def format_detailed_view(self) -> str:
        """Format full property information into structured text."""
        summary = self.listing.format_summary()
        amenities = self.profile.amenities_summary
        description = self.profile.description
        return f"{summary}\nComodidades: {amenities}\n\nDescrição:\n{description}"

    def to_dictionary(self) -> dict:
        """Export detailed property into dictionary representation."""
        base_dict = self.listing.to_dictionary()
        base_dict["amenities"] = self.profile.amenities_summary
        base_dict["description"] = self.profile.description
        return base_dict
