"""Domain exceptions for Imobiliária Vale Invest rental research."""


class RentalSearchException(Exception):
    """Base exception for rental search domain errors."""


class InvalidPriceException(RentalSearchException):
    """Raised when price amount violates non-negative validation."""


class InvalidPropertyCodeException(RentalSearchException):
    """Raised when property code is empty or invalid."""


class InvalidFilterException(RentalSearchException):
    """Raised when filter constraints are inconsistent."""


class PropertyNotFoundException(RentalSearchException):
    """Raised when requested property cannot be found or redirects."""


class NetworkTransportException(RentalSearchException):
    """Raised when HTTP request encounters network or connection failures."""
