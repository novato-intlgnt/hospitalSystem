"""Delete Workstation — Command Interactor

Use case: An Administrator permanently removes a decommissioned workstation
from the system registry (RN-17).
"""

import logging
from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class DeleteWorkstationRequest:
    """Input DTO for DeleteWorkstationInteractor.

    Attributes:
        workstation_id: UUID of the workstation record to permanently remove.
    """

    workstation_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class DeleteWorkstationInteractor:
    """Permanently removes a workstation from the hospital registry.

    Enforced rules:
    - RN-17: Only Administrators can remove workstation records.
    - The workstation record is physically deleted — no logical-deactivation
      pattern is applied here, as decommissioned hardware should not retain
      references in the live system.

    > [!IMPORTANT]
    > Deleting an **authorized** workstation will immediately prevent any
    > further enforcement of machine-level rules (RN-09, RN-10) for that IP.
    > Deauthorize the station first via ``UpdateWorkstationInteractor`` before
    > scheduling a deletion.

    Dependencies:
        current_user_service: Resolves and validates the acting Administrator.
        workstation_command_gateway: Fetches and hard-deletes the aggregate.
        flusher: Flushes the pending ORM delete before commit.
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

    async def execute(self, request: DeleteWorkstationRequest) -> None:
        """Permanently delete a workstation from the hospital registry.

        Args:
            request: DTO with ``workstation_id`` of the station to remove.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor is not an Administrator (RN-17).
            DomainError: If no workstation with ``workstation_id`` exists.
            DataMapperError: If the persistence layer encounters a fatal error.
        """
        log.info(
            "DeleteWorkstation: started. workstation_id='%s'.", request.workstation_id
        )

        current_user = await self._current_user_service.get_current_user()
        authorize(IsAdmin(), context=StandardContext(subject=current_user))

        workstation_entity_id = EntityID(value=request.workstation_id)
        workstation = await self._workstation_gateway.read_by_id(
            workstation_entity_id, for_update=True
        )
        if workstation is None:
            raise DomainError(f"Workstation '{request.workstation_id}' not found.")

        self._workstation_gateway.delete(workstation)
        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "DeleteWorkstation: done. workstation_id='%s'.", request.workstation_id
        )
