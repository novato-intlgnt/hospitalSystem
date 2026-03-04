"""Ports for image storage."""

from abc import abstractmethod
from typing import Protocol

from src.dev.domain.entities.image import Image
from src.dev.domain.value_objects.exam import ExamID
from src.dev.domain.value_objects.imageFiles import DicomMetadata


class ImageStoragePortService(Protocol):
    """Protocols for image storage"""

    @abstractmethod
    async def store(
        self, exam_id: ExamID, files: list[Image], destination_path: str
    ) -> None:
        """Store images for a given exam ID."""

    @abstractmethod
    async def exists_for_exam(self, exam_id: ExamID) -> bool:
        """Check if images exist for a given exam ID."""

    @abstractmethod
    async def get_image_url(
        self,
        exam_id: ExamID,
    ) -> str:
        """Get the url to view the image for a given exam ID."""


class DicomProcessorPortService(Protocol):
    """Protocols for DICOM processing"""

    @abstractmethod
    def extract_metadata(self, content: bytes) -> DicomMetadata:
        """Extract DICOM metadata from the given content."""
