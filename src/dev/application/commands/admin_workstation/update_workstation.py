"""Update Workstation — Command Interactor

Use case: An Administrator updates an existing workstation's metadata or toggles
its authorization status (e.g. deauthorization for maintenance) (RN-08, RN-17).
"""

import logging
from dataclasses import dataclass
from typing import Optional, TypedDict
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
from src.dev.domain.enum.workstation import WorkstationStatus, WorkstationType
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import (
    HardwareID,
    NetworkAddress,
    PhysicalLocation,
    WorkstationData,
    WorkstationSpecs,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True, kw_only=True)
class UpdateWorkstationRequest:
    """Input DTO for UpdateWorkstationInteractor.

    All fields except ``workstation_id`` are optional.  Only non-``None`` fields
    will be applied to the aggregate; this follows a partial-update pattern.

    Attributes:
        workstation_id: UUID of the workstation record to update.
        hostname: New hostname string for the station specs.
        os_info: New OS / software stack descriptor.
        ip_address: New IPv4 address for the network interface.
        mac_address: New MAC address; required alongside ``ip_address``.
        hardware_id: New hardware serial / UUID identifier.
        building: New building label for the physical location.
        floor: New floor number for the physical location.
        room_number: New room designation for the physical location.
        workstation_type: New operational classification (ACQUISITION / REPORTING / CLINICAL).
        workstation_status: New status flag (ACTIVE / INACTIVE / MAINTENANCE).
        is_active: Logical activation toggle.
    """

    workstation_id: UUID
    hostname: Optional[str] = None
    os_info: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    hardware_id: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    room_number: Optional[str] = None
    workstation_type: Optional[WorkstationType] = None
    workstation_status: Optional[WorkstationStatus] = None
    is_active: Optional[bool] = None


class UpdateWorkstationResponse(TypedDict):
    """Output DTO for UpdateWorkstationInteractor."""

    workstation_id: UUID


# ---------------------------------------------------------------------------
# Interactor
# ---------------------------------------------------------------------------


class UpdateWorkstationInteractor:
    """Applies administrative updates to a registered workstation.

    Enforced rules:
    - RN-17: Only Administrators can modify workstation records.
    - The interactor uses a partial-update approach: only fields explicitly set
      in the request (non-``None``) are written to the aggregate's ``data``
      value object.  Unchanged fields are preserved from the loaded entity.

    Dependencies:
        current_user_service: Resolves and validates the acting Administrator.
        workstation_command_gateway: Hydrates and persists the Workstation aggregate.
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
        self, request: UpdateWorkstationRequest
    ) -> UpdateWorkstationResponse:
        """Apply partial updates to a workstation and persist the changes.

        Args:
            request: DTO with ``workstation_id`` and any fields to update.

        Raises:
            UnauthorizedAccessError: If the actor's token is invalid or inactive.
            InsufficientRoleError: If the actor is not an Administrator (RN-17).
            DomainError: If no workstation with ``workstation_id`` exists.
            ValueError: If the partial update produces an invalid ``WorkstationData``
                (e.g. IP address without MAC address).
            DataMapperError: If the persistence layer encounters a fatal error.

        Returns:
            UpdateWorkstationResponse: Dictionary containing the ``workstation_id``.
        """
        log.info(
            "UpdateWorkstation: started. workstation_id='%s'.", request.workstation_id
        )

        current_user = await self._current_user_service.get_current_user()
        authorize(IsAdmin(), context=StandardContext(subject=current_user))

        workstation_entity_id = EntityID(value=request.workstation_id)
        workstation = await self._workstation_gateway.read_by_id(
            workstation_entity_id, for_update=True
        )
        if workstation is None:
            raise DomainError(f"Workstation '{request.workstation_id}' not found.")

        # Extract current data fields and overlay any non-None request values
        # to implement the partial-update pattern on the immutable value object.
        current_data = workstation.data

        new_specs = WorkstationSpecs(
            hostname=request.hostname or current_data.specs.hostname,
            os_info=request.os_info or current_data.specs.os_info,
        )
        new_network = NetworkAddress(
            ip_address=request.ip_address or current_data.network.ip_address,
            mac_address=request.mac_address or current_data.network.mac_address,
        )
        new_location = PhysicalLocation(
            building=request.building or current_data.location.building,
            floor=(
                request.floor
                if request.floor is not None
                else current_data.location.floor
            ),
            room_number=request.room_number or current_data.location.room_number,
        )
        new_data = WorkstationData(
            hardware_id=(
                HardwareID(value=request.hardware_id)
                if request.hardware_id
                else current_data.hardware_id
            ),
            network=new_network,
            specs=new_specs,
            location=new_location,
            workstation_type=request.workstation_type or current_data.workstation_type,
            workstation_status=request.workstation_status
            or current_data.workstation_status,
            is_active=(
                request.is_active
                if request.is_active is not None
                else current_data.is_active
            ),
        )

        # Apply the new value object to the aggregate.
        workstation.update_data(new_data)

        await self._flusher.flush()
        await self._transaction_manager.commit()

        log.info(
            "UpdateWorkstation: done. workstation_id='%s'.", request.workstation_id
        )
        return UpdateWorkstationResponse(workstation_id=request.workstation_id)
