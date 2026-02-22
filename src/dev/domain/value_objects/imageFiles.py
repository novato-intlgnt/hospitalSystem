from dataclasses import dataclass, field
from typing import Any, Self

from src.dev.domain.value_objects.base import ValueObject

@dataclass(frozen=True)
class DicomMetadata(ValueObject):
    sop_instance_uid: str
    series_instance_uid: str
    content_date: str
    content_time: str

@dataclass(frozen=True)
class ImageReference(ValueObject):
    url: str
    file_size_bytes: int
    mime_type: str = "application/dicom"

    def __post_init__(self):
        if not self.url.startswith("https://"):
            raise ValueError("La URL de Supabase debe ser segura (HTTPS).")
