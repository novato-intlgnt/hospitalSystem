"""Domain service for updating workstation data"""

from typing import Optional

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.enum.workstation import WorkstationType
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import WorkstationRepository
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import (
    NetworkAddress,
    PhysicalLocation,
    WorkstationData,
    WorkstationSpecs,
)


class WorkstationUpdaterService:
    """Service to update a workstation's mutable data."""

    def __init__(
        self,
        workstation_repository: WorkstationRepository,
    ) -> None:
        self._workstation_repository = workstation_repository

    async def update(
        self,
        workstation_id: EntityID,
        new_network: Optional[NetworkAddress] = None,
        new_specs: Optional[WorkstationSpecs] = None,
        new_location: Optional[PhysicalLocation] = None,
        new_type: Optional[WorkstationType] = None,
    ) -> Workstation:
        """
        Updates one or more mutable fields of the workstation.

        Enforces rules:
        - RN-09: If the network address changes, the new address must be unique.

        :raises DomainError: if the workstation is not found or rules are violated.
        """
        workstation = await self._workstation_repository.get_by_id(workstation_id)
        if workstation is None:
            raise DomainError("Workstation not found.")

        # Validate new network address uniqueness (RN-09)
        if new_network is not None and new_network != workstation.network:
            already_exists = (
                await self._workstation_repository.esists_by_network_address(
                    new_network
                )
            )
            if already_exists:
                raise DomainError(
                    f"A workstation with network address "
                    f"'{new_network.ip_address}' / '{new_network.mac_address}' already exists."
                )

        updated_data = WorkstationData(
            hardware_id=workstation.hardware_id,
            network=new_network if new_network is not None else workstation.network,
            specs=new_specs if new_specs is not None else workstation.specs,
            location=new_location if new_location is not None else workstation.location,
            workstation_type=new_type if new_type is not None else workstation.type,
            workstation_status=workstation.status,
            is_active=workstation.is_active,
        )

        updated = Workstation(
            id_=workstation.id_,
            workstation_data=updated_data,
        )
        await self._workstation_repository.save(updated)
        return updated
