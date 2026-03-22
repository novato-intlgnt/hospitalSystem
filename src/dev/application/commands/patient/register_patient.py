"""Register Patient — Command Interactor

Use case: Admit a new patient into the hospital system after verifying
that the Clinical History code (HC) is unique across the registry (RN-01).
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import TypedDict
from uuid import UUID, uuid4

from src.dev.application.common.exceptions.duplicate_patient import (
    DuplicatePatientError,
)
from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.patient_gateway import PatientCommandGateway
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.domain.entities.patient import Patient
from src.dev.domain.enum.gender import Gender
from src.dev.domain.value_objects.patient import PatientData, PatientDNI, PatientHC
from src.dev.domain.value_objects.person import Name, PersonName
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class RegisterPatientRequest:
    """Input DTO for RegisterPatientInteractor.

    Attributes:
        hc: Clinical History code — must be unique in the system (RN-01).
        dni: National identity document — exactly 8 digits.
        first_name: Patient's first given name.
        second_name: Optional second given name.
        paternal_last_name: Patient's paternal last name.
        maternal_last_name: Patient's maternal last name.
        birth_date: ISO date of birth; must not be in the future.
        gender: Biological or registered gender of the patient.
    """

    hc: str
    dni: str
    first_name: str
    second_name: str | None
    paternal_last_name: str
    maternal_last_name: str
    birth_date: date
    gender: Gender


class RegisterPatientResponse(TypedDict):
    """Output DTO — exposes only the newly generated patient identifier."""

    patient_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class RegisterPatientInteractor:
    """Registers a new patient in the hospital system.

    Validates HC uniqueness (RN-01) before persisting the aggregate.
    No authentication context required — admission is an open flow;
    machine-level controls (workstation type) are enforced upstream.

    Dependencies:
        patient_command_gateway: Write access to the Patient aggregate.
        flusher: Flushes the ORM buffer within the active transaction so that
            DB-level unique constraints on HC surface before the commit.
        transaction_manager: Commits or rolls back the active unit of work.
    """

    def __init__(
        self,
        patient_command_gateway: PatientCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._patient_gateway = patient_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: RegisterPatientRequest) -> RegisterPatientResponse:
        """Register a new patient after ensuring HC uniqueness.

        Args:
            request: Validated input DTO with patient demographics.

        Raises:
            DuplicatePatientError: If the provided HC already exists (RN-01).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            RegisterPatientResponse: Dictionary containing the new ``patient_id``.
        """
        log.info(
            "RegisterPatient: started. HC='%s', DNI='%s'.",
            request.hc,
            request.dni,
        )

        hc = PatientHC(value=request.hc)

        # RN-01: HC uniqueness check at the application layer before flush.
        existing = await self._patient_gateway.read_by_hc(hc)
        if existing is not None:
            raise DuplicatePatientError("History Code", request.hc)

        # Build value objects from raw input.
        person_name = PersonName(
            first_name=Name(request.first_name),
            second_name=Name(request.second_name) if request.second_name else None,
            paternal_last_name=Name(request.paternal_last_name),
            maternal_last_name=Name(request.maternal_last_name),
        )
        patient_data = PatientData(
            hc=hc,
            dni=PatientDNI(value=request.dni),
            name=person_name,
        )
        patient_id = EntityID(value=uuid4())
        patient = Patient(
            id_=patient_id,
            data=patient_data,
            birth_date=request.birth_date,
            gender=request.gender,
        )

        self._patient_gateway.add(patient)

        # Flush before commit: surfaces DB-level HC constraint violations early.
        try:
            await self._flusher.flush()
        except DuplicatePatientError as exc:
            raise DuplicatePatientError("All", "Some data already exists") from exc

        await self._transaction_manager.commit()

        log.info("RegisterPatient: done. patient_id='%s'.", patient_id.value)
        return RegisterPatientResponse(patient_id=patient_id.value)
