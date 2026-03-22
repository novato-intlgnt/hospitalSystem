"""Public API for the application-layer common exceptions package."""

from src.dev.application.common.exceptions.base import ApplicationError
from src.dev.application.common.exceptions.duplicate_patient import DuplicatePatientError
from src.dev.application.common.exceptions.immutable_report import ImmutableReportError
from src.dev.application.common.exceptions.inactive_account import InactiveAccountError
from src.dev.application.common.exceptions.invalid_machine_op import (
    InvalidMachineOperationError,
)
from src.dev.application.common.exceptions.invalid_state_transition import (
    InvalidExamStateTransitionError,
)
from src.dev.application.common.exceptions.unauthorized_access import (
    UnauthorizedAccessError,
)

__all__ = [
    "ApplicationError",
    "DuplicatePatientError",
    "ImmutableReportError",
    "InactiveAccountError",
    "InvalidMachineOperationError",
    "InvalidExamStateTransitionError",
    "UnauthorizedAccessError",
]
from .insufficient_role import InsufficientRoleError
from .missing_doctor_credentials import MissingDoctorCredentialsError

__all__ += [
    "InsufficientRoleError",
    "MissingDoctorCredentialsError",
]
