"""Patient filter query parameters for the application layer."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.dev.domain.enum.gender import Gender


@dataclass(frozen=True, slots=True, kw_only=True)
class PatientQueryParams:
    """Immutable filter parameters for patient list queries.

    Passed from use-cases to ``PatientQueryGateway.read_all`` to narrow
    down the result set.  All fields are optional; when ``None`` the
    corresponding filter is not applied.

    Args:
        search_term: Free-text search applied against the patient's full name
                     and DNI.  Case-insensitive; ``None`` disables text search.
        gender: Restrict results to patients of a specific gender.
        birth_date_from: Lower bound (inclusive) of the patient's birth date
                         range.  ``None`` means no lower bound.
        birth_date_to: Upper bound (inclusive) of the patient's birth date
                       range.  ``None`` means no upper bound.

    Raises:
        ValueError: If ``birth_date_from`` is later than ``birth_date_to``
                    when both are provided.

    Example::

        filters = PatientQueryParams(
            search_term="García",
            gender=Gender.FEMALE,
            birth_date_from=date(1980, 1, 1),
            birth_date_to=date(2000, 12, 31),
        )
    """

    search_term: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date_from: Optional[date] = None
    birth_date_to: Optional[date] = None

    def __post_init__(self) -> None:
        if (
            self.birth_date_from is not None
            and self.birth_date_to is not None
            and self.birth_date_from > self.birth_date_to
        ):
            raise ValueError(
                f"'birth_date_from' ({self.birth_date_from}) cannot be later "
                f"than 'birth_date_to' ({self.birth_date_to})."
            )

    @property
    def has_filters(self) -> bool:
        """Return ``True`` if at least one filter field is set."""
        return any(
            [
                self.search_term is not None,
                self.gender is not None,
                self.birth_date_from is not None,
                self.birth_date_to is not None,
            ]
        )
