"""Persistence protocols for the application."""

from typing import List, Optional, Protocol
from uuid import UUID

from src.dev.domain.entities.audit_log import AuditLog
from src.dev.domain.entities.exam import Exam
from src.dev.domain.entities.patient import Patient
from src.dev.domain.entities.report import Report
from src.dev.domain.entities.user import User
from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.value_objects.exam import ExamID
from src.dev.domain.value_objects.patient import PatientDNI, PatientHC
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import NetworkAddress


class PatientRepository(Protocol):
    """Port for patient repository"""

    async def exists_by_hc(self, hc: PatientHC) -> bool:
        """Check if a patient exists by their history code."""
        ...

    async def get_by_id(self, id_: EntityID) -> Optional[Patient]:
        """Get a patient by their ID."""
        ...

    async def get_by_hc(self, hc: PatientHC) -> Optional[Patient]:
        """Get a patient by their history code."""
        ...

    async def get_by_dni(self, dni: PatientDNI) -> Optional[Patient]:
        """Get a patient by their dni."""
        ...


class ExamRepository(Protocol):
    """Port for exam repository"""

    async def get_by_id(self, id_: EntityID) -> Optional[Exam]:
        """Get an exam by its ID."""
        ...

    async def get_by_exam_id(self, exam_id: ExamID) -> Optional[Exam]:
        """Get an exam by its ID."""
        ...

    async def list_by_patient_hc(self, hc: PatientHC) -> List[Exam]:
        """List exams by patient history code."""
        ...

    async def save(self, exam: Exam) -> None:
        """Save an exam."""


class ReportRepository(Protocol):
    """Port for reporrt repository"""

    async def save(self, report: UUID) -> None:
        """Save a reporta."""

    async def get_versions(self, exam_id: ExamID) -> List[Report]:
        """Get all versions of a report for a given exam ID."""
        ...


class UserRepository(Protocol):
    """Port for user repository"""

    async def exists_by_id(self, id_: EntityID) -> bool:
        """Check if a user exists by their ID."""
        ...

    async def save(self, user: User) -> None:
        """Save a user."""


class WorkstationRepository(Protocol):
    """Port for workstation repository"""

    async def get_by_network(self, network: NetworkAddress) -> Optional[Workstation]:
        """Get a workstation by its network address."""
        ...


class AuditRepository(Protocol):
    """Port for audit repository"""

    async def save(self, entry: AuditLog) -> None:
        """Save an audit log entry."""
