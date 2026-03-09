"""Workstation entity definition"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.workstationType import WorkstationType
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import (
    WorkstationData,
    HardwareID,
    NetworkAddress,
    WorkstationSpecs,
    PhysicalLocation,
)


class Workstation(BaseEntity[EntityID]):
    """Represents a workstation in the system"""

    def __init__(
        self,
        *,
        id_: EntityID,
        worksstation_data: WorkstationData,
        is_authorized: bool = True,
    ):
        super().__init__(id_=id_)
        self._hardware_id = worksstation_data.hardware_id
        self._type = worksstation_data.workstation_type
        self._network = worksstation_data.network
        self._specs = worksstation_data.specs
        self._location = worksstation_data.location
        self._is_authorized = is_authorized

    @property
    def can_upload_file(self) -> bool:
        """Only acquisition workstations can upload data."""
        return self._type == WorkstationType.ACQUISITION and self._is_authorized

    @property
    def can_handle_legal_reports(self) -> bool:
        """Only acquisition and reporting workstation can handle legal reports."""
        allowed = [WorkstationType.ACQUISITION, WorkstationType.REPORTING]
        return self._type in allowed and self._is_authorized

    @property
    def is_public_viewer(self) -> bool:
        """Only clinical workstation can be used as public viewers."""
        return self._type == WorkstationType.CLINICAL

    @property
    def hardware_id(self) -> HardwareID:
        """Get the workstation's hardware ID"""
        return self._hardware_id

    @property
    def type(self) -> WorkstationType:
        """Get the workstation's type"""
        return self._type

    @property
    def network(self) -> NetworkAddress:
        """Get the workstation's network address"""
        return self._network

    @property
    def specs(self) -> WorkstationSpecs:
        """Get the workstation's specifications"""
        return self._specs

    @property
    def location(self) -> PhysicalLocation:
        """Get the workstation's physical location"""
        return self._location

    @property
    def is_authorized(self) -> bool:
        """Check if the workstation is authorized"""
        return self._is_authorized
