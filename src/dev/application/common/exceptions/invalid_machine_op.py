"""Invalid machine operation exception for the application layer.

Business Rule: RN-10
"""

from src.dev.application.common.exceptions.base import ApplicationError


class InvalidMachineOperationError(ApplicationError):
    """Raised when a workstation attempts an operation not allowed by its type.

    Business rule **RN-10**: each workstation type (ACQUISITION, REPORTING,
    CLINICAL) has a fixed set of permitted operations.  Attempting an
    operation outside that set at the use-case level raises this exception.

    Args:
        machine_id: The hardware or system identifier of the workstation.
        machine_type: The workstation type (e.g. ``"CLINICAL"``).
        operation: A short description of the disallowed operation
                   (e.g. ``"upload_dicom_file"``, ``"sign_report"``).
    """

    def __init__(self, machine_id: str, machine_type: str, operation: str) -> None:
        super().__init__(
            f"Workstation {machine_id!r} of type {machine_type!r} "
            f"is not allowed to perform: {operation!r}."
        )
        self.machine_id = machine_id
        self.machine_type = machine_type
        self.operation = operation
