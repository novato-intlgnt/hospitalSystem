"""Base classes for domain types and errors."""

from typing import Any


class DomainTypeError(Exception):
    """Invalid construction of domain types (Value Objects)."""


class DomainError(Exception):
    """Domain rule violation not tied to domain type construction."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class EntityNotFoundError(DomainError):
    """Raised when an entity with a specific identity does not exist."""

    def __init__(self, entity_name: str, entity_id: Any) -> None:
        super().__init__(f"{entity_name} with ID {entity_id} not found")
