"""User entity"""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True, repr=False)
class EntityID:
    """Value object representing a UUID for an entity"""

    value: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.value, UUID):
            raise ValueError("Invalid UserID format")
