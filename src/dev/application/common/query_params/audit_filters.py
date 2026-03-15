"""Audit log filter query parameters for the application layer.

Business Rule: RN-12
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.dev.domain.enum.user import UserRole


@dataclass(frozen=True, slots=True, kw_only=True)
class AuditLogQueryParams:
    """Immutable filter parameters for audit log queries.

    Business rule **RN-12**: only administrators may query the audit trail,
    and the query must be scoped by at least one filter to prevent unbounded
    full-table scans of the audit log.

    Passed from use-cases to the ``AuditLogQueryGateway`` to narrow the
    audit event result set.  All filter fields are optional, but the
    ``is_bounded`` guard must be respected by the use-case.

    Args:
        user_id: Restrict the audit log to events triggered by a specific user.
        actor_role: Restrict to events performed by actors of a specific role.
        action: Exact action name to filter on
                (e.g. ``"sign_report"``, ``"upload_image"``).
        resource_id: Restrict to events affecting a specific resource ID.
        from_timestamp: Lower bound (inclusive) of the event timestamp window.
        to_timestamp: Upper bound (inclusive) of the event timestamp window.

    Raises:
        ValueError: If ``from_timestamp`` is later than ``to_timestamp``
                    when both are provided.

    Example::

        filters = AuditLogQueryParams(
            actor_role=UserRole.DOCTOR,
            action="sign_report",
            from_timestamp=datetime(2025, 1, 1),
            to_timestamp=datetime(2025, 12, 31, 23, 59, 59),
        )
    """

    user_id: Optional[UUID] = None
    actor_role: Optional[UserRole] = None
    action: Optional[str] = None
    resource_id: Optional[UUID] = None
    from_timestamp: Optional[datetime] = None
    to_timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        if (
            self.from_timestamp is not None
            and self.to_timestamp is not None
            and self.from_timestamp > self.to_timestamp
        ):
            raise ValueError(
                f"'from_timestamp' ({self.from_timestamp}) cannot be later "
                f"than 'to_timestamp' ({self.to_timestamp})."
            )

    @property
    def is_bounded(self) -> bool:
        """Return ``True`` if at least one filter narrows the query scope.

        Use-cases applying RN-12 should assert ``is_bounded`` before forwarding
        these params to the gateway, preventing unrestricted full-log scans.
        """
        return any(
            [
                self.user_id is not None,
                self.actor_role is not None,
                self.action is not None,
                self.resource_id is not None,
                self.from_timestamp is not None,
                self.to_timestamp is not None,
            ]
        )
