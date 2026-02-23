"""Audit log entity"""

from datetime import datetime
from uuid import UUID

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import NetworkAddress


class AuditLog(BaseEntity[EntityID]):
    def __init__(
        self,
        *,
        id_: EntityID,
        user_id: UUID,
        action: str,
        resource_id: str,
        network_info: NetworkAddress,
        timestamp: datetime = datetime.now(),
    ):
        super().__init__(id_=id_)
        self.user_id = user_id
        self.action = action
        self.resource_id = resource_id
        self.network_info = network_info
        self.timestamp = timestamp
