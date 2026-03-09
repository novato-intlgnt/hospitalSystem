"""Persistence protocols for the application."""

from abc import abstractmethod
from typing import List, Optional, Protocol

from src.dev.domain.entities.audit_log import AuditLog
from src.dev.domain.entities.exam import Exam
from src.dev.domain.entities.patient import Patient
from src.dev.domain.entities.report import Report
from src.dev.domain.entities.user import User
from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.patient import PatientDNI, PatientHC
from src.dev.domain.value_objects.user import EntityID, Username
from src.dev.domain.value_objects.workstation import NetworkAddress


class PatientRepository(Protocol):
    """Port for patient repository"""

    @abstractmethod
    async def exists_by_hc(self, hc: PatientHC) -> bool:
        """Check if a patient exists by their history code."""

    @abstractmethod
    async def get_by_id(self, id_: EntityID) -> Optional[Patient]:
        """Get a patient by their ID."""

    @abstractmethod
    async def get_by_hc(self, hc: PatientHC) -> Optional[Patient]:
        """Get a patient by their history code."""

    @abstractmethod
    async def get_by_dni(self, dni: PatientDNI) -> Optional[Patient]:
        """Get a patient by their dni."""

    @abstractmethod
    async def save(self, patient: Patient) -> None:
        """Save a patient."""


class ExamRepository(Protocol):
    """Port for exam repository"""

    @abstractmethod
    async def get_by_id(self, id_: EntityID) -> Optional[Exam]:
        """Get an exam by its ID."""

    @abstractmethod
    async def get_by_exam_id(self, exam_id: ExamCode) -> Optional[Exam]:
        """Get an exam by its ID."""

    @abstractmethod
    async def list_by_patient_hc(self, hc: PatientHC) -> List[Exam]:
        """List exams by patient history code."""

    @abstractmethod
    async def save(self, exam: Exam) -> None:
        """Save an exam."""


class ReportRepository(Protocol):
    """Port for report repository"""

    @abstractmethod
    async def save(self, report: Report) -> None:
        """Save a reporta."""

    @abstractmethod
    async def get_versions(self, exam_id: ExamCode) -> List[Report]:
        """Get all versions of a report for a given exam ID."""


class UserRepository(Protocol):
    """Port for user repository"""

    @abstractmethod
    async def exists_by_id(self, id_: EntityID) -> bool:
        """Check if a user exists by their ID."""

    @abstractmethod
    async def get_by_id(self, id_: EntityID) -> Optional[User]:
        """Get a user by their ID."""

    @abstractmethod
    async def get_by_username(self, username: Username) -> Optional[User]:
        """Get a user by their username"""

    @abstractmethod
    async def save(self, user: User) -> None:
        """Save a user."""


class WorkstationRepository(Protocol):
    """Port for workstation repository"""

    @abstractmethod
    async def get_by_id(self, id_: EntityID) -> Optional[Workstation]:
        """Get a workstation by its ID."""

    @abstractmethod
    async def get_by_network(self, network: NetworkAddress) -> Optional[Workstation]:
        """Get a workstation by its network address."""

    @abstractmethod
    async def save(self, workstation: Workstation) -> None:
        """Save a new workstation."""

    @abstractmethod
    async def esists_by_network_address(self, network: NetworkAddress) -> bool:
        """Check if a workstation exists by its network address."""


class AuditRepository(Protocol):
    """Port for audit repository"""

    @abstractmethod
    async def save(self, entry: AuditLog) -> None:
        """Save an audit log entry."""
