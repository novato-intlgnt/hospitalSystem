"""Domain service for authorizing or deauthorizing workstations"""

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.ports.repositories.persistence import WorkstationRepository
from src.dev.domain.value_objects.user import EntityID


class WorkstationAuthorizerService:
    """
    Service to authorize or deauthorize a workstation.

    - Authorized workstations can perform their role-specific actions (RN-09).
    - Deauthorized workstations are blocked from all sensitive operations.
    """

    def __init__(
        self,
        workstation_repository: WorkstationRepository,
    ) -> None:
        self._workstation_repository = workstation_repository

    async def authorize(self, workstation_id: EntityID) -> Workstation:
        """
        Marks a workstation as authorized.

        :raises DomainError: if the workstation is not found.
        """
        workstation = await self._workstation_repository.get_by_id(workstation_id)
        if workstation is None:
            raise DomainError("Workstation not found.")

        if workstation.is_authorized:
            raise DomainError("Workstation is already authorized.")

        updated = Workstation(
            id_=workstation.id_,
            worksstation_data=self._build_data(workstation),
            is_authorized=True,
        )
        await self._workstation_repository.save(updated)
        return updated

    async def deauthorize(self, workstation_id: EntityID) -> Workstation:
        """
        Marks a workstation as deauthorized, blocking its sensitive operations.

        :raises DomainError: if the workstation is not found.
        """
        workstation = await self._workstation_repository.get_by_id(workstation_id)
        if workstation is None:
            raise DomainError("Workstation not found.")

        if not workstation.is_authorized:
            raise DomainError("Workstation is already deauthorized.")

        updated = Workstation(
            id_=workstation.id_,
            worksstation_data=self._build_data(workstation),
            is_authorized=False,
        )
        await self._workstation_repository.save(updated)
        return updated

    @staticmethod
    def _build_data(ws: Workstation):
        """Reconstruct WorkstationData from the entity's current state."""
        from src.dev.domain.value_objects.workstation import WorkstationData

        return WorkstationData(
            hardware_id=ws.hardware_id,
            network=ws.network,
            specs=ws.specs,
            location=ws.location,
            workstation_type=ws.type,
        )
