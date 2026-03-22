from collections.abc import Mapping
from dataclasses import dataclass

from src.dev.application.common.exceptions.insufficient_role import (
    InsufficientRoleError,
)
from src.dev.application.common.exceptions.missing_doctor_credentials import (
    MissingDoctorCredentialsError,
)
from src.dev.application.common.services.authorization.base import (
    Permission,
    PermissionContext,
)
from src.dev.application.common.services.authorization.role_hierarchy import (
    SUBORDINATE_ROLES,
)
from src.dev.domain.entities.user import User
from src.dev.domain.enum.user import UserRole


@dataclass(frozen=True, kw_only=True)
class UserManagementContext(PermissionContext):
    """
    Context evaluated when an actor (subject) requests an operation
    over another user profile (target).
    """

    subject: User
    target: User


class CanManageSelf(Permission[UserManagementContext]):
    """
    Allows operations targeted exclusively towards the user's explicit profile
    (e.g., retrieving own data). Evaluates True if subject and target match.
    """

    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        return context.subject == context.target


class CanManageSubordinate(Permission[UserManagementContext]):
    """
    Evaluates hierarchical privileges (RN-17) authorizing an administrator
    to delete or modify users mapped as subordinates in the hierarchy.
    """

    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: UserManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        if context.target.role not in allowed_roles:
            raise InsufficientRoleError()
        return True


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    """
    Context evaluated when an actor attempts to create or update another
    user assigning them a specific new Role.
    """

    subject: User
    target_role: UserRole


class CanManageRole(Permission[RoleManagementContext]):
    """
    Validates if the Actor (subject) holds the authority to bestow
    or revoke a specific target_role to another entity, enforcing RN-14
    (Only Admins can assign roles).
    """

    def __init__(
        self,
        role_hierarchy: Mapping[UserRole, set[UserRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject.role, set())
        if context.target_role not in allowed_roles:
            raise InsufficientRoleError(
                f"Role {context.subject.role.value} is not authorized to manage role {context.target_role.value}."
            )
        return True


@dataclass(frozen=True, kw_only=True)
class StandardContext(PermissionContext):
    """
    Generic context containing only the executing subject (Actor).
    Used for broadly scoped system permissions.
    """

    subject: User


class IsAdmin(Permission[StandardContext]):
    """
    Blanket authorization rule allowing only Administrator profiles
    (e.g., global Workstation approval operations).
    """

    def is_satisfied_by(self, context: StandardContext) -> bool:
        if context.subject.role != UserRole.ADMIN:
            raise InsufficientRoleError("Only Administrators can perform this action.")
        return True


class IsDoctor(Permission[StandardContext]):
    """
    Verifies that the actor is a registered Doctor AND possesses active
    mandatory credentials (CMP/RNE). Enforces RN-05 and RN-16 before signing reports.
    """

    def is_satisfied_by(self, context: StandardContext) -> bool:
        if context.subject.role != UserRole.DOCTOR:
            raise InsufficientRoleError(
                "Only Medical profiles can perform this action."
            )

        # Validates domain rule RN-16: Credentials present
        if not context.subject.cmp or not context.subject.rne:
            raise MissingDoctorCredentialsError()

        return True
