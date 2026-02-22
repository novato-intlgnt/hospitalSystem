from dataclasses import dataclass, field
from typing import Any, Self
import re

from src.dev.domain.value_objects.base import ValueObject

@dataclass(frozen=True)
class NetworkAddress(ValueObject):
    ip_address: str
    mac_address: str | None = None

    def __post_init__(self):
        # Validación simple de IP (v4)
        ip_pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        if not re.match(ip_pattern, self.ip_address):
            raise ValueError(f"Dirección IP inválida: {self.ip_address}")

@dataclass(frozen=True)
class WorkstationSpecs(ValueObject):
    hostname: str      # Ej: "RX-ROOM-01" o "TRAUMA-DESK-04"
    os_info: str       # Ej: "Windows 11 / MicroDICOM Viewer"
    
    def __post_init__(self):
        if not self.hostname.strip():
            raise ValueError("El hostname de la computadora es obligatorio.")

@dataclass(frozen=True)
class PhysicalLocation(ValueObject):
    building: str      # Ej: "Pabellón A"
    floor: int         # Ej: 2
    room_number: str   # Ej: "Sala de Rayos X 102"
