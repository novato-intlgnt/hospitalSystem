"""Workstation entity definition"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.workstationType import WorkstationType
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import (
    NetworkAddress,
    PhysicalLocation,
    WorkstationSpecs,
)


class Workstation(BaseEntity[EntityID]):
    """Represents a workstation in the system"""

    def __init__(
        self,
        *,
        id_: EntityID,
        name: str,
        workstation_type: WorkstationType,
        network: NetworkAddress,
        specs: WorkstationSpecs,
        location: PhysicalLocation,
        is_active: bool = True,
    ):
        super().__init__(id_=id_)
        self._name = name
        self._type = workstation_type
        self._network = network
        self._specs = specs
        self._location = location
        self._is_active = is_active

    @property
    def permits_upload(self) -> bool:
        """Only acquisition workstations can upload data."""
        return self._type == WorkstationType.ACQUISITION and self._is_active
