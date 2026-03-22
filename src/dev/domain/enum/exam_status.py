"""Exam Status"""

from enum import StrEnum


class ExamStatus(StrEnum):
    """Status of the exam in the workflow"""

    PENDING = "PENDING"  # Create in system, waiting for patient
    INCOMPLETE = "INCOMPLETE"  # Patient arrived, but images not uploaded yet
    COMPLETE = "COMPLETE"  # Images uploaded, waiting for interpretation
    REPORTED = "REPORTED"  # Report written, and signed by radiologist
    CANCELLED = "CANCELLED"  # Cancelled by administratives or technical reasons
