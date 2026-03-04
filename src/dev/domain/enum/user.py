"""User management and RBAC"""

from enum import StrEnum


class UserRole(StrEnum):
    """User enum for RBAC"""

    ADMIN = "ADMIN"  # User management and full auditing
    DOCTOR = "DOCTOR"  # Radiologist: can interpret images and sign reports
    TECHNICIAN = "TECHNICIAN"  # Technologist: take and upload images
    RECEPTIONIST = "RECEPTIONIST"  # Patient registration and delivery of results

    @property
    def permissions(self) -> set[str]:
        """Define permissions for each role"""
        mapping = {
            UserRole.ADMIN: {"audit", "manage_users"},
            UserRole.DOCTOR: {"interpret", "sign_report"},
            UserRole.TECHNICIAN: {"upload_images"},
            UserRole.RECEPTIONIST: {"register_patient"},
        }
        return mapping[self]

    def can(self, permission: str) -> bool:
        """Check if the role has a specific permission"""
        return permission in self.permissions
