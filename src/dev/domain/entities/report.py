"""Report entity"""

from src.dev.domain.entities.base import BaseEntity
from src.dev.domain.exceptions.report import FinalizeReport
from src.dev.domain.value_objects.doctor import DoctorID
from src.dev.domain.value_objects.exam import ExamCode
from src.dev.domain.value_objects.report import (
    ReportContent,
    ReportData,
    ReportNumber,
    ReportSignature,
)
from src.dev.domain.value_objects.user import EntityID


class Report(BaseEntity[EntityID]):
    """Report aggregate root"""

    def __init__(
        self,
        *,
        id_: EntityID,
        report_data: ReportData,
        signature: ReportSignature | None = None,
        doctor_id: DoctorID,
        version: int = 1,
    ) -> None:
        super().__init__(id_=id_)
        self._exam_code = report_data.exam_code
        self._report_num = report_data.report_num
        self._doctor_id = doctor_id
        self._content = report_data.content
        self._signature = signature
        self._version = version

    @property
    def is_final(self) -> bool:
        """Check if the report is finalized"""
        return self._signature is not None

    @property
    def version(self) -> int:
        """Get the current version of the report"""
        return self._version

    @property
    def content(self) -> ReportContent:
        """Get the report's content"""
        return self._content

    @property
    def exam_code(self) -> ExamCode:
        """Get the exam code linked to this report"""
        return self._exam_code

    @property
    def report_num(self) -> ReportNumber:
        """Get the report number"""
        return self._report_num

    @property
    def signature(self) -> ReportSignature | None:
        """Get the digital signature of the report if it is finalized"""
        return self._signature

    @property
    def doctor_id(self) -> DoctorID:
        """Get the doctor ID linked to this report"""
        return self._doctor_id

    def update_content(self, content: ReportContent) -> None:
        """Update the content of the report"""
        if self.is_final:
            raise FinalizeReport(self.id_)

        self._content = content

    def sign(self, signature: ReportSignature) -> None:
        """Sign the report, finalizing it"""
        if self.is_final:
            raise FinalizeReport(self.id_)
        self._signature = signature

    def create_amendment(
        self, new_id: EntityID, new_content: ReportContent
    ) -> "Report":
        """
        Create a new Report instance as an amendment to the current one
        """
        if not self.is_final:
            raise ValueError("Can only amend finalized reports.")

        new_report_data = ReportData(
            exam_code=self._exam_code,
            report_num=self._report_num,
            content=new_content,
        )

        return Report(
            id_=new_id,
            report_data=new_report_data,
            doctor_id=self._doctor_id,
            version=self._version + 1,
            signature=None,
        )
