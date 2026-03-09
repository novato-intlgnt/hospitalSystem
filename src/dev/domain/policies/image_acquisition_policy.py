"""
Domain Policy: ImageAcquisitionPolicy
"""

from src.dev.domain.entities.user import User
from src.dev.domain.entities.workstation import Workstation


class ImageAcquisitionPolicy:
    """
    Policy to determine if an image can be uploaded from a specific workstation.
    RN-09: Solo máquinas de adquisición pueden subir
    """

    def is_satisfied_by(self, user: User, workstation: Workstation) -> bool:
        """
        Validates if the user and workstation satisfy the rule.
        The user parameter is available for extensibility if future rules require it.
        """
        return workstation.can_upload_file
