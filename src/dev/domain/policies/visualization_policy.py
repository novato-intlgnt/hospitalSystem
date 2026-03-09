"""
Domain Policy: VisualizationPolicy
"""

from typing import Optional

from src.dev.domain.entities.user import User
from src.dev.domain.entities.workstation import Workstation


class VisualizationPolicy:
    """
    Policy to determine if an exam can be visualized on a machine.
    RN-11: Permitir acceso sin login para máquinas de solo visualización
    """

    def is_satisfied_by(
        self, user: Optional[User], workstation: Workstation
    ) -> bool:
        """
        Validates if the user and workstation satisfy the rule.
        For public viewers, no user login is strictly required. For other workstations,
        a logged-in user is necessary.
        """
        if workstation.is_public_viewer:
            return True
            
        return user is not None
