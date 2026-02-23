"""Value objects related to the workstation entity in the hospital domain model."""

import re
from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class NetworkAddress(BaseValueObject):
    """Value object representing a workstation's network address"""

    ip_address: str
    mac_address: str | None = None

    def __post_init__(self):
        # Validación simple de IP (v4)
        ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if not re.match(ip_pattern, self.ip_address):
            raise ValueError(f"Dirección IP inválida: {self.ip_address}")


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
