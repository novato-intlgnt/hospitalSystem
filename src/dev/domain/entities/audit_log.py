"""Audit log entity"""

from datetime import datetime

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.log import LogEntry
from src.dev.domain.value_objects.user import EntityID


class AuditLog(BaseEntity[EntityID]):
    def __init__(
        self,
        *,
        id_: EntityID,
        log_data: LogEntry,
        timestamp: datetime = datetime.now(),
    ):
        super().__init__(id_=id_)
        self.user_id = log_data.user_id
        self.action = log_data.action
        self.resource_id = log_data.resource_id
        self.network_info = log_data.network_info
        self.timestamp = timestamp
