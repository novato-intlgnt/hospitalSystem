"""Value objects related to the workstation entity in the hospital domain model."""

import ipaddress
from dataclasses import dataclass

from src.dev.domain.enum.workstationType import WorkstationType
from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class HardwareID(BaseValueObject):
    """Identificador único de hardware (UUID o Serial)"""

    value: str


@dataclass(frozen=True)
class NetworkAddress(BaseValueObject):
    """Value object representing a workstation's network address"""

    ip_address: str
    mac_address: str | None = None

    def __post_init__(self):
        if not self.ip_address or not self.mac_address:
            raise ValueError("The network address must have both IP and MAC addresses.")

        try:
            ipaddress.ip_address(self.ip_address)
        except ValueError as exc:
            raise ValueError(f"Invalid IP address: {self.ip_address}") from exc


@dataclass(frozen=True)
class WorkstationSpecs(BaseValueObject):
    """Value object representing the specifications of a workstation"""

    hostname: str  # Ej: "RX-ROOM-01" o "TRAUMA-DESK-04"
    os_info: str  # Ej: "Windows 11 / MicroDICOM Viewer"

    def __post_init__(self):
        if not self.hostname.strip():
            raise ValueError("El hostname de la computadora es obligatorio.")


@dataclass(frozen=True)
class PhysicalLocation(BaseValueObject):
    """Value object representing the physical location of a workstation within the hospital"""

    building: str  # Ej: "Pabellón A"
    floor: int  # Ej: 2
    room_number: str  # Ej: "Sala de Rayos X 102"


@dataclass(frozen=True)
class WorkstationData(BaseValueObject):
    """Value object representing the data required to create a workstation"""

    hardware_id: HardwareID
    network: NetworkAddress
    specs: WorkstationSpecs
    location: PhysicalLocation
    workstation_type: WorkstationType
