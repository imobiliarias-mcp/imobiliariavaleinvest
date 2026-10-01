"""Interfaces package for rental search capabilities and providers."""

from scripts.interfaces.provider import (
    RentalDetailCapability,
    RentalFacetsCapability,
    RentalProviderProtocol,
    RentalSearchCapability,
)

__all__ = [
    "RentalDetailCapability",
    "RentalFacetsCapability",
    "RentalProviderProtocol",
    "RentalSearchCapability",
]
