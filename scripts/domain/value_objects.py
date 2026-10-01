"""Value objects wrapping domain primitives for Vale Invest rental research."""

from dataclasses import dataclass
from scripts.domain.exceptions import (
    InvalidPriceException,
    InvalidPropertyCodeException,
)


@dataclass(frozen=True)
class ListingPrice:
    """Represents a validated monetary price in Brazilian Reais."""

    amount: float

    def __post_init__(self) -> None:
        """Validate non-negative monetary amount."""
        if self.amount < 0.0:
            raise InvalidPriceException(f"Price cannot be negative: {self.amount}")

    def format_brl(self) -> str:
        """Format the monetary amount into Brazilian currency string."""
        formatted_number = f"{self.amount:,.2f}"
        localized = formatted_number.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {localized}"

    def is_zero(self) -> bool:
        """Check if price is zero."""
        return self.amount == 0.0

    def value(self) -> float:
        """Return raw numeric value."""
        return self.amount


@dataclass(frozen=True)
class PropertyCode:
    """Represents a unique real estate listing business code or ID."""

    identifier: str

    def __post_init__(self) -> None:
        """Validate non-empty code identifier."""
        cleaned = self.identifier.strip()
        if not cleaned:
            raise InvalidPropertyCodeException("Property code cannot be empty.")

    def value(self) -> str:
        """Return clean identifier string."""
        return self.identifier.strip()

    def __str__(self) -> str:
        """String representation."""
        return self.value()


@dataclass(frozen=True)
class RoomCount:
    """Represents a validated non-negative room or parking amenity count."""

    count: int

    def __post_init__(self) -> None:
        """Validate non-negative count."""
        if self.count < 0:
            raise ValueError(f"Room count cannot be negative: {self.count}")

    def value(self) -> int:
        """Return integer count."""
        return self.count


@dataclass(frozen=True)
class AreaMeasure:
    """Represents an area measurement in square meters (m²)."""

    square_meters: float

    def __post_init__(self) -> None:
        """Validate non-negative area."""
        if self.square_meters < 0.0:
            raise ValueError(f"Area cannot be negative: {self.square_meters}")

    def value(self) -> float:
        """Return float area."""
        return self.square_meters

    def format_display(self) -> str:
        """Format area display string."""
        formatted = f"{self.square_meters:.2f}".replace(".", ",")
        return f"{formatted} m²"
