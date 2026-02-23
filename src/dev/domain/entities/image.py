"""Image entity"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.value_objects.imageFiles import DicomMetadata, ImageReference
from src.dev.domain.value_objects.user import EntityID


class Image(BaseEntity[EntityID]):
    """Represents an image in the system"""

    def __init__(
        self,
        *,
        id_: EntityID,
        exam_id: str,
        reference: ImageReference,
        metadata: DicomMetadata | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self._exam_id = exam_id
        self._reference = reference
        self._metadata = metadata
