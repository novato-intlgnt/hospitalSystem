"""Audit Gateways — Application Layer Ports

Contracts for recording and querying audit trail entries that track
every significant action in the system (RN-12).
"""

from abc import abstractmethod
from datetime import datetime
from typing import Protocol, TypedDict
from uuid import UUID

from src.dev.domain.entities.audit_log import AuditLog

# ---------------------------------------------------------------------------
# Query Models (TypedDicts — plain data, no domain behaviour)
# ---------------------------------------------------------------------------


class AuditLogQM(TypedDict):
    """Flat read model representing a single audit log entry."""

    id_: UUID
    user_id: UUID | None
    action: str
    resource_id: UUID
    ip_address: str
    mac_address: str | None
    hardware_id: str
    timestamp: datetime


class AuditLogListQM(TypedDict):
    """Paginated result of audit log entries for the Admin console."""

    logs: list[AuditLogQM]
    total: int


# ---------------------------------------------------------------------------
# Command Gateway — write access, records domain AuditLog entities
# ---------------------------------------------------------------------------


class AuditCommandGateway(Protocol):
    """
    Contract to record audit trail events (RN-12).

    All significant business actions (login, upload, signing, etc.) must produce
    at least one AuditLog entity that captures the actor, action, resource, and context.
    """

    @abstractmethod
    def record(self, log: AuditLog) -> None:
        """
        :raises DataMapperError:

        Persist a new audit event linked to the acting user, the affected resource
        affected, and the terminal's network data (RN-12).
        """


# ---------------------------------------------------------------------------
# Query Gateway — read-only projections for the Admin console
# ---------------------------------------------------------------------------


class AuditQueryGateway(Protocol):
    """
    Contract for audit's complex query reserved for the Admin module.

    Support cross-filters by actor (who), event type (what), date range (when),
    and network address (where) (RN-12).
    """

    @abstractmethod
    async def search(
        self,
        limit: int,
        offset: int,
        user_id: UUID | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        ip_address: str | None = None,
    ) -> AuditLogListQM:
        """
        :raises ReaderError:

        Execute a paginated and filterable search over audit log records.
        All filter parameters are optional and combined (logical AND) when provided simultaneously.
        """
