"""Workstation Gateways — Application Layer Ports

Contracts for both read-only classification of workstation terminals and
write access for administrative management. Enforces machine-level business
rules (RN-08, RN-09, RN-10, RN-17).
"""

from abc import abstractmethod
from typing import Protocol, TypedDict
from uuid import UUID

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.enum.workstation import WorkstationType
from src.dev.domain.value_objects.user import EntityID
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
# Query Gateway — read-only projections, never returns domain entities
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


# ---------------------------------------------------------------------------
# Command Gateway — mutable access, works with rich domain entities
# ---------------------------------------------------------------------------


class WorkstationCommandGateway(Protocol):
    """Contract for write operations on the Workstation aggregate.

    Used by administrator command interactors to approve, modify, and remove
    workstation registrations (RN-08, RN-17).
    """

    @abstractmethod
    def add(self, workstation: Workstation) -> None:
        """Register a new Workstation aggregate in the persistence store.

        The entity's ``id_`` and all mandatory fields must be set before
        calling this method.

        :raises DataMapperError: On fatal persistence errors.
        """

    @abstractmethod
    async def read_by_id(
        self,
        workstation_id: EntityID,
        for_update: bool = False,
    ) -> Workstation | None:
        """Retrieve a Workstation entity by its internal identifier.

        Args:
            workstation_id: The ``EntityID`` of the workstation to fetch.
            for_update: If ``True``, acquires a row-level lock
                (``SELECT FOR UPDATE``) for safe concurrent modification.

        Returns:
            The hydrated ``Workstation`` entity if found, otherwise ``None``.

        :raises DataMapperError: On fatal read failures.
        """

    @abstractmethod
    def delete(self, workstation: Workstation) -> None:
        """Mark a Workstation aggregate for hard deletion in the active transaction.

        The record is physically removed on ``TransactionManager.commit``.

        :raises DataMapperError: On fatal persistence errors.
        """
