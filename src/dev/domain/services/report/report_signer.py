"""
Domain Service: ReportSignerService

"""

from src.dev.domain.entities.report import Report
from src.dev.domain.entities.user import User
from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.exceptions.report import UnauthorizedSignerError
from src.dev.domain.policies.workstation_access_policy import WorkstationAccessPolicy
from src.dev.domain.ports.services.security import SignatureService


class ReportSignerService:
    """
    Domain Service that encapsulates the business logic for signing medical reports.
    """

    def __init__(self, signature_service: SignatureService) -> None:
        self._signature_service = signature_service
        self._access_policy = WorkstationAccessPolicy()

    def sign(self, report: Report, doctor: User, workstation: Workstation) -> None:
        """
        Signs a medical report with the doctor's credentials.
        Validates both the user role and the workstation access.
        """

        if not self._access_policy.is_satisfied_by(doctor, workstation):
            raise UnauthorizedSignerError(doctor.id_, doctor.role)

        license_info = doctor.legal_signature

        signature = self._signature_service.generate_hash(
            content=str(report.content),
            medical_license=license_info,
        )

        report.sign(signature)
