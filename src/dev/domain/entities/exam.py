"""Exam entity module"""

from datetime import date
from typing import List

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.entities.image import Image
from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.enum.modality import Modality
from src.dev.domain.value_objects.exam import ExamID
from src.dev.domain.value_objects.patient import PatientHC
from src.dev.domain.value_objects.user import EntityID


class Exam(BaseEntity[EntityID]):
    """Exam entity"""

    def __init__(
        self,
        *,
        id_: EntityID,
        exam_id: ExamID,
        patient_HC: PatientHC,
        modality: Modality,
        study_type: str,
        status: ExamStatus = ExamStatus.PENDING,
    ) -> None:
        super().__init__(id_=id_)
        self._patient_hc = patient_HC
        self._exam_id = exam_id
        self._modality = modality
        self._study_type = study_type
        self._date = date.today()
        self._status = status
        self._images: List["Image"] = []

    def add_image(self, image: "Image") -> None:
        """Add an Image to the exam."""
        if self._status == ExamStatus.REPORTED:
            raise ValueError("Cannot add images to a reported exam.")
        self._images.append(image)
        self._status = ExamStatus.IN_PROGRESS
