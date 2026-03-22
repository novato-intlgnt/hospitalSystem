"""Deactivate User — Command Interactor

Use case: An Administrator soft-deletes a user account (logical deactivation),
preserving audit traceability, and revokes all active sessions (RN-17, RN-16).
"""

import logging
from dataclasses import dataclass
from uuid import UUID

from src.dev.application.common.ports.access_revoker import AccessRevoker
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.user_gateway import UserCommandGateway
from src.dev.application.common.services.authorization.authorize import authorize
from src.dev.application.common.services.authorization.permissions import (
    CanManageSubordinate,
    IsAdmin,
    StandardContext,
    UserManagementContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.exceptions.user import UserNotFoundByIdError
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DeactivateUserRequest:
    """Input DTO for DeactivateUserInteractor.

    Attributes:
        target_user_id: UUID of the user account to be deactivated.
    """

    target_user_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class DeactivateUserInteractor:
    """Soft-deactivates a user account and invalidates all their active sessions.

    Enforced rules:
    - RN-17: Only Administrators can deactivate accounts.  The coarse ``IsAdmin``
      check is applied first; then ``CanManageSubordinate`` verifies the target's
      role is within the actor's organizational scope.
    - RN-16: After deactivation, ``AccessRevoker`` forcefully removes all tokens
      and sessions associated with the deactivated account.
    - The account is logically deactivated (``is_active = False``); the record is
      never physically deleted, preserving audit integrity.

    Dependencies:
        current_user_service: Resolves the acting Administrator (RN-16).
        user_command_gateway: Reads the target user and persists the state change.
        access_revoker: Invalidates all active sessions for the target user.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        access_revoker: AccessRevoker,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_gateway = user_command_gateway
        self._access_revoker = access_revoker
        self._transaction_manager = transaction_manager

    async def execute(self, request: DeactivateUserRequest) -> None:
        """Soft-deactivate a user and revoke all their sessions.

        Args:
            request: DTO with ``target_user_id`` of the account to deactivate.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor is not an Administrator, or if
                the target's role is outside the actor's hierarchical scope (RN-17).
            UserNotFoundByIdError: If no user with ``target_user_id`` exists.
            DataMapperError: If the persistence layer encounters a fatal error.
        """
        log.info(
            "DeactivateUser: started. target_user_id='%s'.", request.target_user_id
        )

        # Coarse admin check — prevents non-admins from reaching the fetch step.
        current_user = await self._current_user_service.get_current_user()
        authorize(IsAdmin(), context=StandardContext(subject=current_user))

        # Fetch the target user with a write lock.
        target = await self._user_gateway.read_by_id(
            str(request.target_user_id), for_update=True
        )
        if target is None:
            raise UserNotFoundByIdError(EntityID(value=request.target_user_id))

        # Fine-grained scope check: actor must outrank the target (RN-17).
        authorize(
            CanManageSubordinate(),
            context=UserManagementContext(subject=current_user, target=target),
        )

        # Logical deactivation; domain entity carries ``is_active`` state.
        target._is_active = False  # noqa: SLF001 — domain mutation via interactor layer

        await self._transaction_manager.commit()

        # RN-16: Revoke all active tokens/sessions after the DB commit.
        await self._access_revoker.remove_all_user_access(request.target_user_id)

        log.info("DeactivateUser: done. target_user_id='%s'.", request.target_user_id)
