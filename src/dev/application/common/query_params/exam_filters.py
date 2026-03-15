"""Exam filter query parameters for the application layer."""

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.enum.modality import Modality


@dataclass(frozen=True, slots=True, kw_only=True)
class ExamQueryParams:
    """Immutable filter parameters for exam worklist queries.

    Passed from use-cases to ``ExamQueryGateway.read_all`` to narrow the
    worklist.  All fields are optional; omitted filters are not applied by
    the gateway implementation.

    Args:
        patient_hc: Filter by the patient's Clinical History (HC) number.
                    Supports partial matches when the gateway allows it.
        status: Restrict the result to exams in a specific lifecycle state
                (e.g. ``ExamStatus.PENDING``, ``ExamStatus.IN_PROGRESS``).
        modality: Restrict to exams of a specific imaging modality
                  (e.g. ``Modality.CT``, ``Modality.MR``).
        exam_date_from: Lower bound (inclusive) for the exam's study date.
        exam_date_to: Upper bound (inclusive) for the exam's study date.

    Raises:
        ValueError: If ``exam_date_from`` is later than ``exam_date_to``
                    when both are provided.

    Example::

        filters = ExamQueryParams(
            status=ExamStatus.PENDING,
            modality=Modality.CT,
            exam_date_from=date(2025, 1, 1),
        )
    """

    patient_hc: Optional[str] = None
    status: Optional[ExamStatus] = None
    modality: Optional[Modality] = None
    exam_date_from: Optional[date] = None
    exam_date_to: Optional[date] = None

    def __post_init__(self) -> None:
        if (
            self.exam_date_from is not None
            and self.exam_date_to is not None
            and self.exam_date_from > self.exam_date_to
        ):
            raise ValueError(
                f"'exam_date_from' ({self.exam_date_from}) cannot be later "
                f"than 'exam_date_to' ({self.exam_date_to})."
            )

    @property
    def has_filters(self) -> bool:
        """Return ``True`` if at least one filter field is set."""
        return any(
            [
                self.patient_hc is not None,
                self.status is not None,
                self.modality is not None,
                self.exam_date_from is not None,
                self.exam_date_to is not None,
            ]
        )
