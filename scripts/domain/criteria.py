"""Search criteria and filter value objects for Vale Invest rental search."""

from dataclasses import dataclass
from scripts.domain.exceptions import InvalidFilterException
from scripts.domain.value_objects import ListingPrice


@dataclass(frozen=True)
class PriceRange:
    """Represents a validated monetary budget interval."""

    minimum_price: ListingPrice
    maximum_price: ListingPrice

    def __post_init__(self) -> None:
        """Validate that minimum price does not exceed maximum price."""
        has_positive_maximum = self.maximum_price.value() > 0.0
        is_inverted = self.minimum_price.value() > self.maximum_price.value()
        if has_positive_maximum and is_inverted:
            raise InvalidFilterException("Minimum price cannot exceed maximum price.")

    @classmethod
    def create_unbounded(cls) -> "PriceRange":
        """Create an open price range."""
        zero_min = ListingPrice(0.0)
        zero_max = ListingPrice(0.0)
        return cls(minimum_price=zero_min, maximum_price=zero_max)


@dataclass(frozen=True)
class LocationCriteria:
    """Represents location filters."""

    city: str = ""
    neighborhood: str = ""


@dataclass(frozen=True)
class SpecificationCriteria:
    """Represents physical property type and dimension constraints."""

    property_type: str = ""
    minimum_bedrooms: int = 0


@dataclass(frozen=True)
class SearchPagination:
    """Represents pagination parameters."""

    page_number: int = 1
    page_size: int = 12

    def __post_init__(self) -> None:
        """Validate page number is at least 1."""
        if self.page_number < 1:
            raise InvalidFilterException("Page number must be at least 1.")
        if self.page_size < 1:
            raise InvalidFilterException("Page size must be at least 1.")


@dataclass(frozen=True)
class SortCriteria:
    """Represents listing order and direction."""

    field: str = "valor"
    direction: str = "crescente"


@dataclass(frozen=True)
class RentalSearchCriteria:
    """Combines location and specification criteria."""

    location: LocationCriteria = LocationCriteria()
    specifications: SpecificationCriteria = SpecificationCriteria()


@dataclass(frozen=True)
class SearchConstraints:
    """Combines price range, pagination, and sorting constraints."""

    price_range: PriceRange = PriceRange.create_unbounded()
    pagination: SearchPagination = SearchPagination()
    sorting: SortCriteria = SortCriteria()


@dataclass(frozen=True)
class RentalFilter:
    """Comprehensive rental search query filter."""

    criteria: RentalSearchCriteria = RentalSearchCriteria()
    constraints: SearchConstraints = SearchConstraints()

    def with_city(self, city_name: str) -> "RentalFilter":
        """Return a copy with specified city."""
        current_nb = self.criteria.location.neighborhood
        new_loc = LocationCriteria(city=city_name, neighborhood=current_nb)
        new_crit = RentalSearchCriteria(location=new_loc, specifications=self.criteria.specifications)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_neighborhood(self, neighborhood_name: str) -> "RentalFilter":
        """Return a copy with specified neighborhood."""
        current_city = self.criteria.location.city
        new_loc = LocationCriteria(city=current_city, neighborhood=neighborhood_name)
        new_crit = RentalSearchCriteria(location=new_loc, specifications=self.criteria.specifications)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_property_type(self, property_type: str) -> "RentalFilter":
        """Return a copy with specified property type."""
        curr_beds = self.criteria.specifications.minimum_bedrooms
        new_specs = SpecificationCriteria(property_type=property_type, minimum_bedrooms=curr_beds)
        new_crit = RentalSearchCriteria(location=self.criteria.location, specifications=new_specs)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_bedrooms(self, count: int) -> "RentalFilter":
        """Return a copy with minimum bedroom count."""
        curr_type = self.criteria.specifications.property_type
        new_specs = SpecificationCriteria(property_type=curr_type, minimum_bedrooms=count)
        new_crit = RentalSearchCriteria(location=self.criteria.location, specifications=new_specs)
        return RentalFilter(criteria=new_crit, constraints=self.constraints)

    def with_price_ceiling(self, ceiling_price: ListingPrice) -> "RentalFilter":
        """Return a copy with maximum price ceiling."""
        curr_min = self.constraints.price_range.minimum_price
        new_range = PriceRange(minimum_price=curr_min, maximum_price=ceiling_price)
        new_constraints = SearchConstraints(
            price_range=new_range,
            pagination=self.constraints.pagination,
            sorting=self.constraints.sorting,
        )
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)

    def with_price_range(self, min_price: float, max_price: float) -> "RentalFilter":
        """Return a copy with both min and max price."""
        new_range = PriceRange(
            minimum_price=ListingPrice(min_price),
            maximum_price=ListingPrice(max_price),
        )
        new_constraints = SearchConstraints(
            price_range=new_range,
            pagination=self.constraints.pagination,
            sorting=self.constraints.sorting,
        )
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)

    def with_page(self, page_index: int) -> "RentalFilter":
        """Return a copy with target page index."""
        curr_size = self.constraints.pagination.page_size
        new_pag = SearchPagination(page_number=page_index, page_size=curr_size)
        new_constraints = SearchConstraints(
            price_range=self.constraints.price_range,
            pagination=new_pag,
            sorting=self.constraints.sorting,
        )
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)

    def with_page_size(self, size: int) -> "RentalFilter":
        """Return a copy with target page size."""
        curr_page = self.constraints.pagination.page_number
        new_pag = SearchPagination(page_number=curr_page, page_size=size)
        new_constraints = SearchConstraints(
            price_range=self.constraints.price_range,
            pagination=new_pag,
            sorting=self.constraints.sorting,
        )
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)

    def with_sorting(self, field: str, direction: str) -> "RentalFilter":
        """Return a copy with sorting criteria."""
        new_sort = SortCriteria(field=field, direction=direction)
        new_constraints = SearchConstraints(
            price_range=self.constraints.price_range,
            pagination=self.constraints.pagination,
            sorting=new_sort,
        )
        return RentalFilter(criteria=self.criteria, constraints=new_constraints)
