"""Tests for WorkstationCreatorService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.workstation import Workstation
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.workstation_creator import WorkstationCreatorService


@pytest.mark.asyncio
async def test_create_workstation_success():
    """Workstation is created when the network address is unique"""
    ws_repo = AsyncMock()
    id_gen = AsyncMock()

    ws_repo.esists_by_network_address.return_value = False
    id_gen.generate_id.return_value = MagicMock()

    service = WorkstationCreatorService(
        id_generator=id_gen,
        workstation_repository=ws_repo,
    )

    ws_data = MagicMock()
    result = await service.create_workstation(workstation_data=ws_data, is_authorized=True)

    assert isinstance(result, Workstation)
    ws_repo.esists_by_network_address.assert_called_once_with(ws_data.network)
    id_gen.generate_id.assert_called_once()


@pytest.mark.asyncio
async def test_create_workstation_duplicate_network_raises():
    """RN-09: DomainError is raised when the network address already exists"""
    ws_repo = AsyncMock()
    ws_repo.esists_by_network_address.return_value = True

    service = WorkstationCreatorService(
        id_generator=AsyncMock(),
        workstation_repository=ws_repo,
    )

    ws_data = MagicMock()
    ws_data.network.ip_address = "192.168.1.10"
    ws_data.network.mac_address = "AA:BB:CC:DD:EE:FF"

    with pytest.raises(DomainError, match="192.168.1.10"):
        await service.create_workstation(workstation_data=ws_data)


@pytest.mark.asyncio
async def test_create_workstation_unauthorized():
    """Workstation can be created with is_authorized=False"""
    ws_repo = AsyncMock()
    id_gen = AsyncMock()

    ws_repo.esists_by_network_address.return_value = False
    id_gen.generate_id.return_value = MagicMock()

    service = WorkstationCreatorService(
        id_generator=id_gen,
        workstation_repository=ws_repo,
    )

    result = await service.create_workstation(
        workstation_data=MagicMock(),
        is_authorized=False,
    )

    assert isinstance(result, Workstation)
    assert result.is_authorized is False
