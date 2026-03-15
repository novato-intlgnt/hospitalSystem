"""
Domain Policy: WorkstationAccessPolicy
"""

from src.dev.domain.entities.user import User
from src.dev.domain.entities.workstation import Workstation


class WorkstationAccessPolicy:
    """
    Policy to determine if a doctor can access legal/diagnostic functions on a given machine.
    RN-10: Only doctors on authorized machines (Workstation of Acquisition)
    """

    def is_satisfied_by(self, user: User, workstation: Workstation) -> bool:
        """
        Validates if the user and workstation satisfy the rule.
        """
        return user.is_doctor and workstation.can_handle_legal_reports
