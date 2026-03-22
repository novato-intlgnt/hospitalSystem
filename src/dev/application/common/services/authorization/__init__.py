from .authorize import authorize
from .base import Permission, PermissionContext
from .composite import AllOf, AnyOf
from .permissions import (
    CanManageRole,
    CanManageSelf,
    CanManageSubordinate,
    IsAdmin,
    IsDoctor,
    RoleManagementContext,
    StandardContext,
    UserManagementContext,
)
from .role_hierarchy import SUBORDINATE_ROLES

__all__ = [
    "authorize",
    "Permission",
    "PermissionContext",
    "AllOf",
    "AnyOf",
    "CanManageRole",
    "CanManageSelf",
    "CanManageSubordinate",
    "IsAdmin",
    "IsDoctor",
    "RoleManagementContext",
    "StandardContext",
    "UserManagementContext",
    "SUBORDINATE_ROLES",
]
