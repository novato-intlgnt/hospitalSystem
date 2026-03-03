"""Images enums"""

from enum import StrEnum


class ImageType(StrEnum):
    """Image types"""

    DICOM = "dicom"
    STATIC = "static"
