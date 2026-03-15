"""Workstation Query Gateway — Application Layer Ports

Read-only contract for classifying workstation terminals by type and
authorization status. Used to enforce machine-level business rules
(RN-08: only ACQUISITION stations can upload images, RN-10: doctor
login restricted to authorized stations).
"""

from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from src.dev.domain.enum.workstation import WorkstationType
from src.dev.domain.value_objects.workstation import HardwareID

# ---------------------------------------------------------------------------
# Query Model (TypedDict — plain data, no domain behaviour)
# ---------------------------------------------------------------------------


class WorkstationQM(TypedDict):
    """
    Flat read model for a workstation.
    Contains only the fields required to enforce machine-level rules.
    """

    id_: UUID
    hardware_id: str
    ip_address: str
    mac_address: str | None
    type: WorkstationType
    is_authorized: bool
    hostname: str
    location: str  # Human-readable: building + floor + room


# ---------------------------------------------------------------------------
# Query Gateway — read-only, no command counterpart for this layer
# ---------------------------------------------------------------------------


class WorkstationQueryGateway(Protocol):
    """
    Contract of read-only to classify and validate workstations.

    Las workstations son administradas por el equipo de IT fuera del flujo
    de negocio principal, por lo que este layer solo necesita consultarlas.

    Usado por:
    - `CreateExamInteractor` para verificar que la solicitud proviene de
      una estación ACQUISITION (RN-09).
    - `SignReportInteractor` para verificar que el médico opera desde
      una terminal autorizada (RN-10, RN-16).
    """

    @abstractmethod
    async def read_by_ip(self, ip_address: str) -> WorkstationQM | None:
        """
        :raises ReaderError:

        Busca una workstation registrada por su dirección IP de red.
        Retorna None si no existe ninguna terminal registrada con esa IP.
        """

    @abstractmethod
    async def read_by_hardware_id(
        self, hardware_id: HardwareID
    ) -> WorkstationQM | None:
        """
        :raises ReaderError:

        Busca una workstation por su identificador único de hardware (UUID
        o serial del equipo). Útil para validaciones de auditoría donde se
        dispone del hardware ID en lugar de la IP (RN-12).
        """
