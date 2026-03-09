"""Exam entity module"""

from datetime import date
from typing import List

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.entities.image import Image
from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.enum.modality import Modality
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.patient import PatientHC
from src.dev.domain.value_objects.user import EntityID


class Exam(BaseEntity[EntityID]):
    """Exam entity"""

    def __init__(
        self,
        *,
        id_: EntityID,
        exam_code: ExamCode,
        patient_HC: PatientHC,
        modality: Modality,
        study_type: str,
        status: ExamStatus = ExamStatus.PENDING,
    ) -> None:
        super().__init__(id_=id_)
        self._patient_hc = patient_HC
        self._exam_code = exam_code
        self._modality = modality
        self._study_type = study_type
        self._date = date.today()
        self._status = status
        self._images: List["Image"] = []

    @property
    def has_images(self) -> bool:
        """Check if the exam has images"""
        return len(self._images) > 0

    @property
    def status(self) -> ExamStatus:
        """Get the current status of the exam"""
        return self._status

    @property
    def patient_hc(self) -> PatientHC:
        """Get the patient HC linked to this exam"""
        return self._patient_hc

    @property
    def exam_code(self) -> ExamCode:
        """Get the exam code"""
        return self._exam_code

    @property
    def modality(self) -> Modality:
        """Get the modality of the exam"""
        return self._modality

    @property
    def study_type(self) -> str:
        """Get the study type of the exam"""
        return self._study_type

    @property
    def date(self) -> date:
        """Get the date of the exam"""
        return self._date

    @property
    def images(self) -> List["Image"]:
        """Get the images associated with the exam"""
        return self._images

    def mark_as_reported(self) -> None:
        """Mark the exam as reported."""
        if self._status == ExamStatus.REPORTED:
            raise DomainError("Exam is already reported")
        if not self.has_images:
            raise DomainError("Cannot report an exam without images")
        self._status = ExamStatus.REPORTED

    def cancel(self) -> None:
        """Cancel the exam."""
        if self._status in [ExamStatus.REPORTED, ExamStatus.DELIVERED]:
            raise DomainError(f"Cannot cancel an exam in {self._status} status")
        self._status = ExamStatus.CANCELLED

    def add_image(self, image: "Image") -> None:
        """Add an Image to the exam."""
        if self._status == ExamStatus.REPORTED:
            raise ValueError("Cannot add images to a reported exam.")
        self._images.append(image)
        self._status = ExamStatus.IN_PROGRESS
