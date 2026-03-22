"""Create User — Command Interactor

Use case: An Administrator registers a new hospital system user (doctor, technician,
or admin staff) assigning a role within their hierarchical authority (RN-14).
"""

import logging
from dataclasses import dataclass
from typing import Optional, TypedDict
from uuid import UUID

from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.user_gateway import UserCommandGateway
from src.dev.application.common.services.authorization.authorize import authorize
from src.dev.application.common.services.authorization.permissions import (
    CanManageRole,
    RoleManagementContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.enum.user import UserRole
from src.dev.domain.exceptions.user import UsernameAlreadyExistsError
from src.dev.domain.services.user.user_creator import UserCreatorService
from src.dev.domain.value_objects.person import Name, PersonData, PersonName
from src.dev.domain.value_objects.user import (
    Email,
    EntityID,
    RawPassword,
    UserData,
    Username,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class CreateUserRequest:
    """Input DTO for CreateUserInteractor.

    Attributes:
        username: Login identifier — must be unique in the system.
        email: Contact email address; must be a valid format.
        raw_password: Plain-text password; hashed by the domain service.
        role: System role to be assigned — must be within the actor's authority.
        first_name: User's first given name.
        paternal_last_name: User's paternal last name.
        maternal_last_name: User's maternal last name.
        second_name: Optional second given name.
        cmp: CMP credential number; required when ``role`` is ``MEDICO``.
        rne: RNE credential number; required when ``role`` is ``MEDICO``.
        specialty: Medical specialty; required when ``role`` is ``MEDICO``.
    """

    username: str
    email: str
    raw_password: str
    role: UserRole
    first_name: str
    paternal_last_name: str
    maternal_last_name: str
    second_name: Optional[str] = None
    cmp: Optional[str] = None
    rne: Optional[str] = None
    specialty: Optional[str] = None


class CreateUserResponse(TypedDict):
    """Output DTO for CreateUserInteractor."""

    user_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class CreateUserInteractor:
    """Registers a new hospital user account under administrator authority.

    Enforced rules:
    - RN-14: Only the Administrator role may create users and assign roles.
      The ``CanManageRole`` permission verifies the actor's hierarchical authority
      over the ``target_role`` before any sensitive work begins.
    - RN-05: Doctor profiles require CMP, RNE, and specialty data; validated by
      ``UserCreatorService`` at the domain level.
    - Username uniqueness is enforced by the domain service and DB constraint.

    Dependencies:
        current_user_service: Resolves and validates the acting Administrator.
        user_creator_service: Orchestrates user entity creation with password
            hashing and uniqueness checks.
        user_command_gateway: Registers the new User aggregate in the repository.
        flusher: Surfaces DB-level unique constraint violations before commit.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_creator_service: UserCreatorService,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_creator_service = user_creator_service
        self._user_gateway = user_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """Create a new user account under the actor's hierarchical permissions.

        Args:
            request: Validated input DTO with credentials, role, and profile data.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor cannot assign the requested role (RN-14).
            DomainError: If doctor data is missing for a MEDICO role, or if the
                username already exists in the system.
            UsernameAlreadyExistsError: Surfaces from the flush if the DB unique
                constraint is violated.
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            CreateUserResponse: Dictionary containing the new ``user_id``.
        """
        log.info(
            "CreateUser: started. username='%s', role='%s'.",
            request.username,
            request.role,
        )

        # RN-14: Verify the administrator can assign the requested role.
        current_user = await self._current_user_service.get_current_user()
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=request.role,
            ),
        )

        # Build domain value objects from raw input.
        person_name = PersonName(
            first_name=Name(request.first_name),
            second_name=Name(request.second_name) if request.second_name else None,
            paternal_last_name=Name(request.paternal_last_name),
            maternal_last_name=Name(request.maternal_last_name),
        )
        user_data = UserData(
            username=Username(request.username),
            email=Email(request.email),
            password_hash=RawPassword(request.raw_password),  # hashed by domain service
        )
        person_data = PersonData(name=person_name, role=request.role)

        # Build optional doctor data if applicable.
        doctor_data = None
        if (
            request.role == UserRole.DOCTOR
            and request.cmp
            and request.rne
            and request.specialty
        ):
            from src.dev.domain.value_objects.doctor import (
                CMPNumber,
                DoctorData,
                RNENumber,
                Specialty,
            )

            doctor_data = DoctorData(
                specialty=Specialty(name=request.specialty),
                cmp_number=CMPNumber(number=request.cmp),
                rne_number=RNENumber(number=request.rne),
            )

        # Delegate creation to the domain service (hashes password, validates rules).
        user = await self._user_creator_service.create_user(
            user_data=user_data,
            person_data=person_data,
            doctor_data=doctor_data,
        )

        self._user_gateway.add(user)

        try:
            await self._flusher.flush()
        except UsernameAlreadyExistsError:
            raise

        await self._transaction_manager.commit()

        log.info("CreateUser: done. user_id='%s'.", user.id_.value)
        return CreateUserResponse(user_id=user.id_.value)
