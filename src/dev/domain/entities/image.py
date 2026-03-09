"""Image entity"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.enum.images import ImageType
from src.dev.domain.value_objects.imageFiles import DicomMetadata, ImageReference
from src.dev.domain.value_objects.user import EntityID


class Image(BaseEntity[EntityID]):
    """Represents an image associated with a medical exam."""

    def __init__(
        self,
        *,
        id_: EntityID,
        exam_id: EntityID,
        image_type: ImageType,
        reference: ImageReference,
        metadata: DicomMetadata | None = None,
    ) -> None:
        super().__init__(id_=id_)

        self._exam_id = exam_id
        self._image_type = image_type
        self._reference = reference
        self._metadata = metadata

        self._validate_invariants()

    def _validate_invariants(self) -> None:
        if self._image_type == ImageType.DICOM and self._metadata is None:
            raise ValueError("DICOM images must contain metadata.")

        if self._image_type == ImageType.STATIC and self._metadata is not None:
            raise ValueError("Static images cannot contain DICOM metadata.")

    @property
    def exam_id(self) -> EntityID:
        """Get the exam ID associated with this image."""
        return self._exam_id

    @property
    def image_type(self) -> ImageType:
        """Get the type of the image."""
        return self._image_type

    @property
    def reference(self) -> ImageReference:
        """Get the reference to the image file."""
        return self._reference

    @property
    def metadata(self) -> DicomMetadata | None:
        """Get the DICOM metadata if this is a DICOM image, otherwise None."""
        return self._metadata

    def is_dicom(self) -> bool:
        """Check if the image is of type DICOM."""
        return self._image_type == ImageType.DICOM
