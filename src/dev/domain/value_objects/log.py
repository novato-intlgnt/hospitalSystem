"""Log value object"""

from dataclasses import dataclass
from typing import Optional

from src.dev.domain.value_objects.base import BaseValueObject
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import HardwareID, NetworkAddress


@dataclass(frozen=True)
class LogEntry(BaseValueObject):
    """Value object representing a log entry for user actions"""

    hardware_id: HardwareID
    action: str
    resource_id: EntityID
    network_info: NetworkAddress
    user_id: Optional[EntityID] = None
