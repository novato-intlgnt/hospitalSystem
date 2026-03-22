"""Authorize Workstation — Command Interactor

Use case: An Administrator approves a pending workstation registration request,
classifying it as ACQUISITION, REPORTING, or CLINICAL and making it operational (RN-08).
"""

import logging
from dataclasses import dataclass
from typing import TypedDict
from uuid import UUID

from src.dev.application.common.ports.flusher import Flusher
from src.dev.application.common.ports.transaction_manager import TransactionManager
from src.dev.application.common.ports.workstation_gateway import (
    WorkstationCommandGateway,
)
from src.dev.application.common.services.authorization.authorize import authorize
from src.dev.application.common.services.authorization.permissions import (
    IsAdmin,
    StandardContext,
)
from src.dev.application.common.services.current_user import CurrentUserService
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.user import EntityID

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizeWorkstationRequest:
    """Input DTO for AuthorizeWorkstationInteractor.

    Attributes:
        workstation_id: UUID of the pending workstation registration to approve.
    """

    workstation_id: UUID


class AuthorizeWorkstationResponse(TypedDict):
    """Output DTO for AuthorizeWorkstationInteractor."""

    workstation_id: UUID
    is_authorized: bool


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class AuthorizeWorkstationInteractor:
    """Approves a pending workstation and marks it as authorized.

    Enforced rules:
    - RN-08: Only Administrators can authorize workstations.
    - The ``WorkstationAuthorizerService`` (domain) handles state-machine logic:
      it raises ``DomainError`` when the workstation is already authorized.

    Dependencies:
        current_user_service: Resolves and validates the acting Administrator.
        workstation_command_gateway: Fetches and persists the Workstation aggregate.
        flusher: Flushes ORM state before commit.
        transaction_manager: Commits the unit of work.
    """

    def __init__(
        self,
        current_user_service: CurrentUserService,
        workstation_command_gateway: WorkstationCommandGateway,
        flusher: Flusher,
        transaction_manager: TransactionManager,
    ) -> None:
        self._current_user_service = current_user_service
        self._workstation_gateway = workstation_command_gateway
        self._flusher = flusher
        self._transaction_manager = transaction_manager

    async def execute(
        self, request: AuthorizeWorkstationRequest
    ) -> AuthorizeWorkstationResponse:
        """Approve a pending workstation and place it in authorized state.

        Args:
            request: DTO with ``workstation_id`` of the station to authorize.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor is not an Administrator (RN-08).
            DomainError: If the workstation is not found or already authorized.
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            AuthorizeWorkstationResponse: Dictionary with the ``workstation_id`` and
                ``is_authorized`` flag confirming the transition.
        """
        log.info(
            "AuthorizeWorkstation: started. workstation_id='%s'.",
            request.workstation_id,
        )

        current_user = await self._current_user_service.get_current_user()
        authorize(IsAdmin(), context=StandardContext(subject=current_user))

        workstation_entity_id = EntityID(value=request.workstation_id)
        workstation = await self._workstation_gateway.read_by_id(
            workstation_entity_id, for_update=True
        )
        if workstation is None:
            raise DomainError(f"Workstation '{request.workstation_id}' not found.")

        # Domain entity handles the authorization state transition.
        workstation.authorize()

        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "AuthorizeWorkstation: done. workstation_id='%s', authorized=%s.",
            request.workstation_id,
            workstation.is_authorized,
        )
        return AuthorizeWorkstationResponse(
            workstation_id=request.workstation_id,
            is_authorized=workstation.is_authorized,
        )
