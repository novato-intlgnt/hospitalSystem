"""Update User Role — Command Interactor

Use case: An Administrator re-assigns the system role of an existing user,
subject to hierarchical scope constraints (RN-17).
"""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.user_gateway import UserCommandGateway
from src.dev.application.common.services.authorization.authorize import authorize
from src.dev.application.common.services.authorization.permissions import (
    CanManageRole,
    CanManageSubordinate,
    RoleManagementContext,
    UserManagementContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.enum.user import UserRole
from src.dev.domain.exceptions.user import UserNotFoundByIdError
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateUserRoleRequest:
    """Input DTO for UpdateUserRoleInteractor.

    Attributes:
        target_user_id: UUID of the user whose role should be reassigned.
        new_role: Target role to assign — must be within the actor's hierarchy.
    """

    target_user_id: UUID
    new_role: UserRole


class UpdateUserRoleResponse(TypedDict):
    """Output DTO for UpdateUserRoleInteractor."""

    user_id: UUID
    new_role: str


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class UpdateUserRoleInteractor:
    """Reassigns a user's system role under administrator authority.

    Enforced rules:
    - RN-17: The actor must be an Administrator with hierarchical authority
      over *both* the target user's current role and the new role being assigned.
      This is enforced by two sequential ``authorize`` calls:
        1. ``CanManageRole`` — can the actor bestow ``new_role``?
        2. ``CanManageSubordinate`` — is the target within the actor's scope?

    Dependencies:
        current_user_service: Resolves the acting Administrator.
        user_command_gateway: Fetches and persists the updated User aggregate.
        flusher: Flushes ORM state before commit.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_gateway = user_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: UpdateUserRoleRequest) -> UpdateUserRoleResponse:
        """Assign a new role to the target user after scope validation.

        Args:
            request: DTO with ``target_user_id`` and ``new_role``.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor cannot bestow ``new_role`` or the
                target is outside their hierarchical scope (RN-17).
            UserNotFoundByIdError: If no user with ``target_user_id`` exists.
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            UpdateUserRoleResponse: Dictionary with ``user_id`` and ``new_role``.
        """
        log.info(
            "UpdateUserRole: started. target_user_id='%s', new_role='%s'.",
            request.target_user_id,
            request.new_role,
        )

        current_user = await self._current_user_service.get_current_user()

        # First: can the actor grant the new role at all?
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject=current_user,
                target_role=request.new_role,
            ),
        )

        # Fetch the target user with a write lock.
        target = await self._user_gateway.read_by_id(
            str(request.target_user_id), for_update=True
        )
        if target is None:
            raise UserNotFoundByIdError(EntityID(value=request.target_user_id))

        # Second: is the target user within the actor's organizational scope?
        authorize(
            CanManageSubordinate(),
            context=UserManagementContext(subject=current_user, target=target),
        )

        # Apply the role mutation directly on the domain entity.
        target._role = request.new_role  # noqa: SLF001 — authorized mutation

        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "UpdateUserRole: done. target_user_id='%s', new_role='%s'.",
            request.target_user_id,
            request.new_role,
        )
        return UpdateUserRoleResponse(
            user_id=request.target_user_id,
            new_role=str(request.new_role),
        )
