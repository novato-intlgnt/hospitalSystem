from collections.abc import Mapping
from typing import Final

from src.dev.domain.enum.user import UserRole

"""
Predefined mapping dictating the hierarchical management privileges.
The keys represent an administrative actor role, and their values denote a Set 
of subordinate roles they hold jurisdiction over (to create, manage, or delete).

- Administrators manage everyone else beneath them.
- Doctors, Techs, and Admin Staff cannot manage any downstream roles.

Applies dynamically to operations referencing Business Rules RN-14 and RN-17.
"""
SUBORDINATE_ROLES: Final[Mapping[UserRole, set[UserRole]]] = {
    UserRole.ADMIN: {UserRole.DOCTOR, UserRole.TECHNICIAN, UserRole.RECEPTIONIST},
    UserRole.DOCTOR: set(),
    UserRole.TECHNICIAN: set(),
    UserRole.RECEPTIONIST: set(),
}
