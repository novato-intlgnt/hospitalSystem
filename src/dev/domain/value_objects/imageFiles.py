"""Value objects related to image files and their metadata"""

from dataclasses import dataclass

from src.dev.domain.value_objects.base import BaseValueObject


@dataclass(frozen=True)
class DicomMetadata(BaseValueObject):
    """Value object representing DICOM metadata for an image file"""

    sop_instance_uid: str
    series_instance_uid: str
    content_date: str
    content_time: str


@dataclass(frozen=True)
class ImageReference(BaseValueObject):
    """Value object representing a reference to an image file stored"""

    url: str
    file_size_bytes: int
    mime_type: str = "application/dicom"

    def __post_init__(self):
        if not self.url.startswith("https://"):
            raise ValueError("The URL must be secure (HTTPS).")
