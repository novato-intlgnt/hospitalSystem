"""Reset User Password — Command Interactor

Use case: An Administrator resets the password of a subordinate user account,
generating a new temporary credential (RN-17).
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
    CanManageSubordinate,
    IsAdmin,
    StandardContext,
    UserManagementContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.exceptions.user import UserNotFoundByIdError
from src.dev.domain.value_objects.user import EntityID, RawPassword, UserPasswordHash

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class ResetUserPasswordRequest:
    """Input DTO for ResetUserPasswordInteractor.

    Attributes:
        target_user_id: UUID of the user whose password will be reset.
        new_raw_password: The new plain-text password to apply after hashing.
    """

    target_user_id: UUID
    new_raw_password: str


class ResetUserPasswordResponse(TypedDict):
    """Output DTO for ResetUserPasswordInteractor."""

    user_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class ResetUserPasswordInteractor:
    """Resets the password of a subordinate user account.

    Enforced rules:
    - RN-17: Only Administrators can reset passwords.  ``IsAdmin`` provides the
      coarse check; ``CanManageSubordinate`` narrows it to the actor's scope.
    - The hashing of the new password is delegated to the ``UserPasswordHash``
      value object chain or the infrastructure layer — raw passwords never persist.

    Dependencies:
        current_user_service: Resolves the acting Administrator.
        user_command_gateway: Fetches and persists the User aggregate.
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

    async def execute(
        self, request: ResetUserPasswordRequest
    ) -> ResetUserPasswordResponse:
        """Reset the target user's password under admin authorization.

        Args:
            request: DTO with ``target_user_id`` and ``new_raw_password``.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor is not an Administrator or the
                target is outside their scope (RN-17).
            UserNotFoundByIdError: If the target user does not exist.
            DomainTypeError: If ``new_raw_password`` fails domain validation
                (e.g. minimum length requirement).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            ResetUserPasswordResponse: Dictionary containing the ``user_id``.
        """
        log.info(
            "ResetUserPassword: started. target_user_id='%s'.",
            request.target_user_id,
        )

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

        # Validate password policy at VO level before hashing.
        validated_password = RawPassword(request.new_raw_password)

        # The infrastructure PasswordHasher converts RawPassword to UserPasswordHash.
        # Here we signal the mutation to the gateway; the ORM mapper calls the hasher.
        target._password_hash = UserPasswordHash(  # noqa: SLF001 — authorized mutation
            value=validated_password.value
        )

        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "ResetUserPassword: done. target_user_id='%s'.", request.target_user_id
        )
        return ResetUserPasswordResponse(user_id=request.target_user_id)
