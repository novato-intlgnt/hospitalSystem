"""Value objects related to a person's name"""

import unicodedata
from dataclasses import dataclass

from src.dev.domain.enum.user import UserRole
from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class Name(BaseValueObject):
    """Represents a single word name (no spaces, no hyphens)."""

    value: str

    def __post_init__(self) -> None:
        normalized = self._normalize(self.value)

        if not normalized:
            raise ValueError("A name cannot be empty")

        if not self._is_valid(normalized):
            raise ValueError(
                "A name must contain only alphabetic characters (including accents) without spaces"
            )

        object.__setattr__(self, "value", normalized)

    @staticmethod
    def _normalize(value: str) -> str:
        # Delete leading & trailing whitespace
        value = value.strip()
        value = unicodedata.normalize("NFC", value)
        return value.title()

    @staticmethod
    def _is_valid(value: str) -> bool:
        # Only allow unicode letters
        return all(char.isalpha() for char in value)


@dataclass(frozen=True)
class PersonName(BaseValueObject):
    """Represents a person's full name"""

    first_name: Name
    paternal_last_name: Name
    maternal_last_name: Name
    second_name: Name | None = None

    def __post_init__(self):
        if not isinstance(self.first_name, Name):
            raise ValueError("First name required")

        if not isinstance(self.paternal_last_name, Name):
            raise ValueError("Paternal last name required")

        if not isinstance(self.maternal_last_name, Name):
            raise ValueError("Maternal last name required")

        if self.second_name and not isinstance(self.second_name, Name):
            raise ValueError("Second name must be a Name object")

    @property
    def full_name(self) -> str:
        """Returns the person's full name"""
        parts = [
            self.first_name.value,
            self.second_name.value if self.second_name else None,
            self.paternal_last_name.value,
            self.maternal_last_name.value,
        ]
        return " ".join(filter(None, parts))

    @property
    def short_name(self) -> str:
        """Return the person's short name"""
        return f"{self.first_name.value} {self.paternal_last_name.value}"

    @property
    def clinical_format(self) -> str:
        """Return the person's name in clinical format"""
        names = " ".join(
            filter(
                None,
                [
                    self.first_name.value,
                    self.second_name.value if self.second_name else None,
                ],
            )
        )
        return (
            f"{self.paternal_last_name.value} "
            f"{self.maternal_last_name.value}, "
            f"{names}"
        )


@dataclass(frozen=True)
class PersonData(BaseValueObject):
    """Value object representing a person's data"""

    name: PersonName
    role: UserRole
