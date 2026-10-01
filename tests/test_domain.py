"""Unit tests for domain models and value objects."""

import pytest
from scripts.domain.collections import RentalListingCollection, RentalSearchResult
from scripts.domain.criteria import PriceRange, RentalFilter, SearchPagination
from scripts.domain.entities import (
    DetailedProfile,
    ListingCore,
    ListingDetails,
    ListingIdentity,
    ListingValuation,
    RentalListing,
    RentalPropertyDetail,
)
from scripts.domain.exceptions import (
    InvalidFilterException,
    InvalidPriceException,
    InvalidPropertyCodeException,
)
from scripts.domain.value_objects import AreaMeasure, ListingPrice, PropertyCode, RoomCount


def test_listing_price_valid() -> None:
    """Ensure ListingPrice holds valid float and formats properly."""
    price = ListingPrice(1250.75)
    assert price.value() == 1250.75
    assert price.format_brl() == "R$ 1.250,75"
    assert not price.is_zero()


def test_listing_price_negative_rejected() -> None:
    """Ensure ListingPrice rejects negative amounts."""
    with pytest.raises(InvalidPriceException):
        ListingPrice(-50.0)


def test_property_code_valid() -> None:
    """Ensure PropertyCode strips whitespace and exposes value."""
    code = PropertyCode("  78933085  ")
    assert code.value() == "78933085"
    assert str(code) == "78933085"


def test_property_code_empty_rejected() -> None:
    """Ensure PropertyCode rejects empty string."""
    with pytest.raises(InvalidPropertyCodeException):
        PropertyCode("   ")


def test_room_count_validation() -> None:
    """Ensure RoomCount rejects negative integer."""
    rc = RoomCount(3)
    assert rc.value() == 3
    with pytest.raises(ValueError):
        RoomCount(-1)


def test_area_measure_formatting() -> None:
    """Ensure AreaMeasure formats m² display."""
    area = AreaMeasure(65.5)
    assert area.value() == 65.5
    assert area.format_display() == "65,50 m²"


def test_price_range_validation() -> None:
    """Ensure PriceRange validates min <= max."""
    valid_range = PriceRange(minimum_price=ListingPrice(500.0), maximum_price=ListingPrice(1500.0))
    assert valid_range.minimum_price.value() == 500.0

    with pytest.raises(InvalidFilterException):
        PriceRange(minimum_price=ListingPrice(2000.0), maximum_price=ListingPrice(1000.0))


def test_pagination_validation() -> None:
    """Ensure SearchPagination rejects page < 1."""
    with pytest.raises(InvalidFilterException):
        SearchPagination(page_number=0)
    with pytest.raises(InvalidFilterException):
        SearchPagination(page_number=1, page_size=0)


def test_rental_filter_fluent_interface() -> None:
    """Ensure RentalFilter copies are correctly constructed."""
    f = (
        RentalFilter()
        .with_city("Timoteo")
        .with_neighborhood("Centro")
        .with_bedrooms(2)
        .with_property_type("Apartamento")
        .with_price_ceiling(ListingPrice(1500.0))
        .with_page(2)
        .with_page_size(24)
        .with_sorting("valor", "crescente")
    )
    assert f.criteria.location.city == "Timoteo"
    assert f.criteria.location.neighborhood == "Centro"
    assert f.criteria.specifications.minimum_bedrooms == 2
    assert f.criteria.specifications.property_type == "Apartamento"
    assert f.constraints.price_range.maximum_price.value() == 1500.0
    assert f.constraints.pagination.page_number == 2
    assert f.constraints.pagination.page_size == 24
    assert f.constraints.sorting.field == "valor"


def test_listing_entities_and_collection() -> None:
    """Ensure RentalListing and collections serialize to dictionary."""
    identity = ListingIdentity(code=PropertyCode("AP001"), title="Apartamento 2Q")
    valuation = ListingValuation(rental_price=ListingPrice(1000.0), property_type="Apartamento")
    core = ListingCore(identity=identity, valuation=valuation)
    details = ListingDetails(location_summary="Centro, Timóteo", media_url="http://img.jpg")
    listing = RentalListing(core=core, details=details)

    collection = RentalListingCollection(listings=(listing,))
    assert len(collection) == 1
    assert collection.count() == 1

    search_result = RentalSearchResult(collection=collection, total_listings_count=1)
    data = search_result.to_dictionary()
    assert data["total_count"] == 1
    assert data["returned_count"] == 1
    assert len(data["listings"]) == 1
    assert data["listings"][0]["code"] == "AP001"
