"""Domain models and value objects for rental research."""

from scripts.domain.collections import (
    FacetCollection,
    RentalListingCollection,
    RentalSearchResult,
)
from scripts.domain.criteria import (
    LocationCriteria,
    PriceRange,
    RentalFilter,
    RentalSearchCriteria,
    SearchConstraints,
    SearchPagination,
    SortCriteria,
    SpecificationCriteria,
)
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingResources,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import (
    InvalidFilterException,
    InvalidPriceException,
    InvalidPropertyCodeException,
    NetworkTransportException,
    PropertyNotFoundException,
    RentalSearchException,
)
from scripts.domain.value_objects import (
    AreaMeasure,
    ListingPrice,
    PropertyCode,
    RoomCount,
)

__all__ = [
    "AreaMeasure",
    "DetailedProfile",
    "FacetCollection",
    "InvalidFilterException",
    "InvalidPriceException",
    "InvalidPropertyCodeException",
    "ListingCore",
    "ListingDetails",
    "ListingIdentity",
    "ListingPrice",
    "ListingResources",
    "ListingValuation",
    "LocationCriteria",
    "NetworkTransportException",
    "PriceRange",
    "PropertyCode",
    "PropertyNotFoundException",
    "RentalFilter",
    "RentalListing",
    "RentalListingCollection",
    "RentalPropertyDetail",
    "RentalSearchCriteria",
    "RentalSearchException",
    "RentalSearchResult",
    "RoomCount",
    "SearchConstraints",
    "SearchPagination",
    "SortCriteria",
    "SpecificationCriteria",
]
