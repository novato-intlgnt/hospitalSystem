import logging

from src.dev.application.common.exceptions.unauthorized_access import (
    UnauthorizedAccessError,
)
from src.dev.application.common.ports.access_revoker import AccessRevoker
from src.dev.application.common.ports.identity_provider import IdentityProvider
from src.dev.application.common.ports.user_gateway import UserCommandGateway
from src.dev.application.common.services.constants import (
    AUTHZ_NO_CURRENT_USER,
    AUTHZ_NOT_AUTHORIZED,
)
from src.dev.domain.entities.user import User

log = logging.getLogger(__name__)


class CurrentUserService:
    """
    Application service src.devoted to resolving and validating the active User
    behind the current execution context. Consumed by Interactors requiring
    strict, context-aware user authorization checks or hardware audits (RN-13, RN-16).
    """

    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_command_gateway: UserCommandGateway,
        access_revoker: AccessRevoker,
    ) -> None:
        self._identity_provider = identity_provider
        self._user_command_gateway = user_command_gateway
        self._access_revoker = access_revoker

    async def get_current_user(self, for_update: bool = False) -> User:
        """
        Retrieves the authenticated user performing the request, ensuring
        they exist within the system and their account remains active.

        If a token exists but the corresponding user account has been disabled
        recently, this method actively blocks the usage by forcefully revoking
        the associated access tokens via the configured AccessRevoker.

        Args:
            for_update (bool, optional): Indicates if the database read should hold a lock
                (e.g., SELECT ... FOR UPDATE) for the transaction duration. Defaults to False.

        Raises:
            UnauthorizedAccessError: Raised broadly if the user cannot be identified,
                is not found in the repository, or their account is deactivated. (RN-16)

        Returns:
            User: The hydrated Domain Entity of the current user.
        """
        try:
            current_user_id = await self._identity_provider.get_current_user_id()
        except UnauthorizedAccessError:
            # Re-raise standard unauthorized error gracefully if no token is found
            log.debug("IdentityProvider failed to retrieve an active user_id.")
            raise

        user: User | None = await self._user_command_gateway.read_by_id(
            current_user_id,
            for_update=for_update,
        )

        # Apply strict logical authorization rules (RN-16 Account Activeness)
        if user is None or not user.is_active:
            log.warning("%s ID: %s.", AUTHZ_NO_CURRENT_USER, current_user_id)
            # Force cleanup of orphaned sessions or malicious stale token usage
            await self._access_revoker.remove_all_user_access(current_user_id)
            raise UnauthorizedAccessError(AUTHZ_NOT_AUTHORIZED)

        return user
