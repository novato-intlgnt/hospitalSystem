"""Patient Gateways — Application Layer Ports

Contracts that segregate read (Query) and write (Command) access
to the Patient aggregate, following ISP and CQRS principles.
"""

from abc import abstractmethod
from datetime import date
from typing import Protocol, TypedDict
from uuid import UUID

from src.dev.domain.entities.patient import Patient
from src.dev.domain.enum.gender import Gender
from src.dev.domain.value_objects.patient import PatientHC
from src.dev.domain.value_objects.user import EntityID

# ---------------------------------------------------------------------------
# Query Models (TypedDicts — plain data, no domain behaviour)
# ---------------------------------------------------------------------------


class PatientQM(TypedDict):
    """Flat read model for a single patient — safe to send to the presentation layer."""

    id_: UUID
    hc: str
    dni: str
    first_name: str
    last_name: str
    birth_date: date
    gender: Gender


class ListPatientsQM(TypedDict):
    """Paginated result of patients."""

    patients: list[PatientQM]
    total: int


# ---------------------------------------------------------------------------
# Command Gateway — mutable access, works with rich domain entities
# ---------------------------------------------------------------------------


class PatientCommandGateway(Protocol):
    """
    Contract to write operations on the patient aggregate.

    Moisturizes and persists rich domain entities (RN-01).
    """

    @abstractmethod
    def add(self, patient: Patient) -> None:
        """
        :raises DataMapperError:

        Record a new patient in the system. Does not produce return;
        the ID is assigned in the domain before calling this method.
        """

    @abstractmethod
    async def read_by_id(
        self,
        patient_id: EntityID,
        for_update: bool = False,
    ) -> Patient | None:
        """
        :raises DataMapperError:

        Recupera un paciente por su ID de entidad, opcionalmente bloqueándolo
        para escritura (SELECT FOR UPDATE) dentro de la transacción activa.
        """

    @abstractmethod
    async def read_by_hc(
        self,
        hc: PatientHC,
        for_update: bool = False,
    ) -> Patient | None:
        """
        :raises DataMapperError:

        Recover a patient by their History Code
        Used to verify uniqueness before registering a new patient.
        """


# ---------------------------------------------------------------------------
# Query Gateway — read-only projections, never returns domain entities
# ---------------------------------------------------------------------------


class PatientQueryGateway(Protocol):
    """
    Contract to optimized read queries on patients.

    The implementations must execute direct read SQL against the DB,
    returning DTOs plains without moisturizing domain entities.
    """

    @abstractmethod
    async def read_all(
        self,
        limit: int,
        offset: int,
        search_term: str | None = None,
    ) -> ListPatientsQM:
        """
        :raises ReaderError:

        Returns a paginated list of patients for the UI grid.
        Accepts optionally a free search term (by DNI or name).
        """

    @abstractmethod
    async def read_by_dni(self, dni: str) -> PatientQM | None:
        """
        :raises ReaderError:

        Searches for a patient by exact DNI. Useful for the admission flow
        Busca un paciente por DNI exacto. Útil para el flujo de admisión
        in reception (RN-01).
        """
