from enum import StrEnum

class WorkstationType(StrEnum):
    ACQUISITION = "ACQUISITION"  # Stations in X-ray/CT rooms. They allow file uploads.
    CLINICAL = "CLINICAL"        # PCs in Emergency/Traumatology. Image viewer and reports only.
    REPORTING = "REPORTING"      # Radiologist Workstation. Optimized for dictation and signature.

    @property
    def can_upload_files(self) -> bool:
        return self == WorkstationType.ACQUISITION

    @property
    def can_view_images(self) -> bool:
        return self in (WorkstationType.CLINICAL, WorkstationType.REPORTING)
