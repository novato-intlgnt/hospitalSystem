from enum import StrEnum

class ExamStatus(StrEnum):
    PENDING = "PENDING"          # Create in system, waiting for patient
    IN_PROGRESS = "IN_PROGRESS"  # Images uploaded, waiting for interpretation
    REPORTED = "REPORTED"        # Report written, and signed by radiologist
    DELIVERED = "DELIVERED"      # Result delivered to patient
    CANCELLED = "CANCELLED"      # Cancelled by administratives or technical reasons
