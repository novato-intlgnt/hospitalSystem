"""Domain service for workstation creation"""

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import WorkstationRepository
from src.dev.domain.ports.services.generator import IDGenerator
from src.dev.domain.value_objects.user import EntityID
from src.dev.domain.value_objects.workstation import WorkstationData


class WorkstationCreatorService:
    """Service to handle the creation of workstations enforcing domain rules."""

    def __init__(
        self,
        id_generator: IDGenerator,
        workstation_repository: WorkstationRepository,
    ) -> None:
        self._id_generator = id_generator
        self._workstation_repository = workstation_repository

    async def create_workstation(
        self,
        workstation_data: WorkstationData,
    ) -> Workstation:
        """
        Creates a new Workstation.

        Enforces rules:
        - RN-09: A workstation's network address (IP + MAC) must be unique in the system.
        """
        already_exists = await self._workstation_repository.esists_by_network_address(
            workstation_data.network
        )
        if already_exists:
            raise DomainError(
                f"A workstation with network address "
                f"'{workstation_data.network.ip_address}' / "
                f"'{workstation_data.network.mac_address}' already exists."
            )

        id_: EntityID = await self._id_generator.generate_id()

        return Workstation(
            id_=id_,
            workstation_data=workstation_data,
        )
