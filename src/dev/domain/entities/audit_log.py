"""Audit log entity"""

from datetime import datetime
from typing import Optional

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.log import LogEntry
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import NetworkAddress


class AuditLog(BaseEntity[EntityID]):
    """Entity representing an audit log entry for actions performed in the system."""

    def __init__(
        self,
        *,
        id_: EntityID,
        log_data: LogEntry,
        timestamp: datetime = datetime.now(),
    ):
        super().__init__(id_=id_)
        self._user_id = log_data.user_id
        self._action = log_data.action
        self._resource_id = log_data.resource_id
        self._network_info = log_data.network_info
        self._timestamp = timestamp

    @property
    def user_id(self) -> Optional[EntityID]:
        """Get the user ID that triggered the action."""
        return self._user_id

    @property
    def action(self) -> str:
        """Get the performed action."""
        return self._action

    @property
    def resource_id(self) -> EntityID:
        """Get the ID of the affected resource."""
        return self._resource_id

    @property
    def network_info(self) -> NetworkAddress:
        """Get the network information of the user performing the action."""
        return self._network_info

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp of the action."""
        return self._timestamp
