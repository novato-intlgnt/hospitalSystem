"""Pagination query parameters for the application layer."""

from dataclasses import dataclass

from src.dev.application.common.exceptions import ApplicationError


class PaginationError(ApplicationError):
    """Raised when pagination parameters are out of the allowed range.

    This is a lightweight validation guard for ``PaginationParams``; it is
    raised inside ``__post_init__`` before any use-case logic runs.
    """


@dataclass(frozen=True, slots=True, kw_only=True)
class PaginationParams:
    """Immutable offset-based pagination parameters.

    Encapsulates ``limit`` and ``offset`` for any paginated query use-case.
    Validation is enforced on construction so callers cannot pass invalid
    values to gateways.

    Args:
        limit: Maximum number of records to return.  Must be ≥ 1 and ≤ 200.
        offset: Zero-based starting position in the result set.  Must be ≥ 0.

    Raises:
        PaginationError: If ``limit`` or ``offset`` violate the constraints above.

    Example::

        params = PaginationParams(limit=20, offset=0)
        results = await gateway.read_all(params.limit, params.offset)
    """

    limit: int
    offset: int

    _MAX_LIMIT: int = 200

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise PaginationError(f"'limit' must be ≥ 1, got {self.limit}.")
        if self.limit > self._MAX_LIMIT:
            raise PaginationError(
                f"'limit' must be ≤ {self._MAX_LIMIT}, got {self.limit}."
            )
        if self.offset < 0:
            raise PaginationError(f"'offset' must be ≥ 0, got {self.offset}.")

    @property
    def page(self) -> int:
        """Return the 1-based logical page number derived from limit/offset."""
        return (self.offset // self.limit) + 1
