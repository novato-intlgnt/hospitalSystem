"""Delete User — Command Interactor

Use case: An Administrator permanently deletes a user record from the system.
Prefer ``DeactivateUserInteractor`` for most cases; hard deletion is reserved
for exceptional circumstances such as GDPR removal requests (RN-17).
"""

import logging
from dataclasses import dataclass
from uuid import UUID

from src.dev.application.common.ports.access_revoker import AccessRevoker
from src.dev.application.common.ports.flusher import Flusher
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
class DeleteUserRequest:
    """Input DTO for DeleteUserInteractor.

    Attributes:
        target_user_id: UUID of the user account to be permanently removed.
    """

    target_user_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class DeleteUserInteractor:
    """Permanently removes a user account from the system.

    Enforced rules:
    - RN-17: Only Administrators can delete accounts.  Double authorization
      (``IsAdmin`` → ``CanManageSubordinate``) is applied before any mutation.
    - RN-16: All active sessions are revoked immediately after deletion.

    > [!IMPORTANT]
    > Hard deletion irreversibly removes the user record.  Use
    > ``DeactivateUserInteractor`` for standard account management.

    Dependencies:
        current_user_service: Resolves and validates the acting Administrator.
        user_command_gateway: Fetches and deletes the user aggregate.
        access_revoker: Invalidates all sessions post-deletion.
        flusher: Flushes the ORM delete before commit.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        user_command_gateway: UserCommandGateway,
        access_revoker: AccessRevoker,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._user_gateway = user_command_gateway
        self._access_revoker = access_revoker
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(self, request: DeleteUserRequest) -> None:
        """Permanently delete a user account and remove their active sessions.

        Args:
            request: DTO with ``target_user_id`` of the account to delete.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor is not an Administrator or the
                target's role is out of scope (RN-17).
            UserNotFoundByIdError: If no user with ``target_user_id`` exists.
            DataMapperError: If the persistence layer encounters a fatal error.
        """
        log.info("DeleteUser: started. target_user_id='%s'.", request.target_user_id)

        current_user = await self._current_user_service.get_current_user()
        authorize(IsAdmin(), context=StandardContext(subject=current_user))

        target = await self._user_gateway.read_by_id(
            str(request.target_user_id), for_update=True
        )
        if target is None:
            raise UserNotFoundByIdError(EntityID(value=request.target_user_id))

        authorize(
            CanManageSubordinate(),
            context=UserManagementContext(subject=current_user, target=target),
        )

        self._user_gateway.delete(target)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        # Revoke sessions after commit to ensure consistency.
        await self._access_revoker.remove_all_user_access(request.target_user_id)

        log.info("DeleteUser: done. target_user_id='%s'.", request.target_user_id)
