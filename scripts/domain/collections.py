"""First-class collections for rental research domain."""

from dataclasses import dataclass
from typing import Iterator
from scripts.domain.entities import RentalListing
from scripts.domain.value_objects import ListingPrice


@dataclass(frozen=True)
class RentalListingCollection:
    """First-class collection wrapping rental listings."""

    listings: tuple[RentalListing, ...]

    def __len__(self) -> int:
        """Return number of listings in collection."""
        return len(self.listings)

    def __iter__(self) -> Iterator[RentalListing]:
        """Iterate over listings."""
        return iter(self.listings)

    def count(self) -> int:
        """Count total items in collection."""
        return len(self.listings)

    def to_dictionary_list(self) -> list[dict]:
        """Convert all listings to list of dictionaries."""
        result_list = []
        for listing in self.listings:
            dictionary = listing.to_dictionary()
            result_list.append(dictionary)
        return result_list

    def filter_under_price(self, ceiling: ListingPrice) -> "RentalListingCollection":
        """Filter collection items under a given price ceiling."""
        filtered_items = []
        for listing in self.listings:
            price_val = listing.core.valuation.rental_price.value()
            if price_val <= ceiling.value():
                filtered_items.append(listing)
        return RentalListingCollection(listings=tuple(filtered_items))


@dataclass(frozen=True)
class FacetCollection:
    """First-class collection wrapping search facets."""

    facet_map: dict[str, tuple[str, ...]]

    def city_names(self) -> tuple[str, ...]:
        """Return available cities."""
        return self.facet_map.get("cities", ())

    def neighborhood_names(self) -> tuple[str, ...]:
        """Return available neighborhoods."""
        return self.facet_map.get("neighborhoods", ())

    def property_types(self) -> tuple[str, ...]:
        """Return available property types."""
        return self.facet_map.get("types", ())

    def to_dictionary(self) -> dict:
        """Return dictionary representation of facets."""
        return dict(self.facet_map)


@dataclass(frozen=True)
class RentalSearchResult:
    """Represents search result with collection and total server count."""

    collection: RentalListingCollection
    total_listings_count: int

    def total_count(self) -> int:
        """Return total matching count on remote portal."""
        return self.total_listings_count

    def returned_count(self) -> int:
        """Return count of items in current page."""
        return len(self.collection)

    def listings(self) -> RentalListingCollection:
        """Return wrapped listings collection."""
        return self.collection

    def to_dictionary(self) -> dict:
        """Export result payload to plain dictionary."""
        return {
            "total_count": self.total_listings_count,
            "returned_count": len(self.collection),
            "listings": self.collection.to_dictionary_list(),
        }
