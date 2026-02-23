"""Modality enumeration for medical imaging"""

from enum import StrEnum


class Modality(StrEnum):
    """Modality enum"""

    CT = "CT"  # Computed Tomography
    MR = "MR"  # Magnetic Resonance
    US = "US"  # Ultrasound
    DX = "DX"  # Digital Radiography
    MG = "MG"  # Mammography
    CR = "CR"  # Computed Radiography
    XA = "XA"  # X-Ray Angiography
