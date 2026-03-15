"""Workstation Types for the hospital's imaging system"""

from enum import StrEnum


class WorkstationType(StrEnum):
    """Enum to WorkstationType"""

    ACQUISITION = "ACQUISITION"  # Stations in X-ray/CT rooms. They allow file uploads.
    CLINICAL = (
        "CLINICAL"  # PCs in Emergency/Traumatology. Image viewer and reports only.
    )
    REPORTING = (
        "REPORTING"  # Radiologist Workstation. Optimized for dictation and signature.
    )

    @property
    def can_upload_files(self) -> bool:
        """Only ACQUISITION can upload files"""
        return self == WorkstationType.ACQUISITION

    @property
    def can_view_images(self) -> bool:
        """Clinical and reporting stations can view images"""
        return self in (WorkstationType.CLINICAL, WorkstationType.REPORTING)


class WorkstationStatus(StrEnum):
    """Enum to workstation status"""

    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    REJECTED = "REJECTED"

    @property
    def is_authorized(self) -> bool:
        """Only AUTHORIZED stations can perform actions"""
        return self == WorkstationStatus.AUTHORIZED

    def authorize(self) -> "WorkstationStatus":
        """Authorize the workstation"""
        if self == WorkstationStatus.PENDING:
            return WorkstationStatus.AUTHORIZED
        raise ValueError("Only pending workstations can be authorized.")

    def deauthorize(self) -> "WorkstationStatus":
        """Deauthorize the workstation"""
        if self == WorkstationStatus.AUTHORIZED:
            return WorkstationStatus.REJECTED
        raise ValueError("Only authorized workstations can be deauthorized.")
