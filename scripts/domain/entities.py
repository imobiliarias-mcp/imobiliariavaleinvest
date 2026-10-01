"""Domain entities for rental property listings."""

from dataclasses import dataclass
from scripts.domain.value_objects import ListingPrice, PropertyCode


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
class ListingDetails:
    """Supplementary display metadata for a listing."""

    location_summary: str
    media_url: str


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
        """Export entity into a plain dictionary representation."""
        return {
            "code": self.core.identity.code.value(),
            "title": self.core.identity.title,
            "property_type": self.core.valuation.property_type,
            "rental_price": self.core.valuation.rental_price.value(),
            "rental_price_formatted": self.core.valuation.rental_price.format_brl(),
            "location": self.details.location_summary,
            "media_url": self.details.media_url,
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
