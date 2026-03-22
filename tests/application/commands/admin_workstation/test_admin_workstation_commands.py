"""Unit tests for admin_workstation command interactors.

Covers: AuthorizeWorkstationInteractor, UpdateWorkstationInteractor,
DeleteWorkstationInteractor.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dev.application.commands.admin_workstation.authorize_workstation import (
    AuthorizeWorkstationInteractor,
    AuthorizeWorkstationRequest,
)
from src.dev.application.commands.admin_workstation.delete_workstation import (
    DeleteWorkstationInteractor,
    DeleteWorkstationRequest,
)
from src.dev.application.commands.admin_workstation.update_workstation import (
    UpdateWorkstationInteractor,
    UpdateWorkstationRequest,
)


def _patch_authorize(module):
    original = module.authorize
    module.authorize = lambda perm, *, context: None
    return original


def _restore_authorize(module, original):
    module.authorize = original


# ==========================================================================
# AuthorizeWorkstationInteractor
# ==========================================================================


@pytest.fixture()
def authorize_ws_deps():
    return {
        "current_user_service": AsyncMock(),
        "workstation_command_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def authorize_ws_interactor(authorize_ws_deps):
    return AuthorizeWorkstationInteractor(**authorize_ws_deps)


@pytest.mark.asyncio
async def test_authorize_workstation_success(authorize_ws_interactor, authorize_ws_deps):
    """Admin approves a pending workstation; is_authorized is now True."""
    authorize_ws_deps["current_user_service"].get_current_user.return_value = MagicMock()
    ws_mock = MagicMock()
    ws_mock.authorize = MagicMock()
    ws_mock.is_authorized = True
    authorize_ws_deps["workstation_command_gateway"].read_by_id.return_value = ws_mock
    ws_id = uuid4()

    import src.dev.application.commands.admin_workstation.authorize_workstation as mod
    orig = _patch_authorize(mod)
    try:
        response = await authorize_ws_interactor.execute(
            AuthorizeWorkstationRequest(workstation_id=ws_id)
        )
    finally:
        _restore_authorize(mod, orig)

    ws_mock.authorize.assert_called_once()
    assert response["is_authorized"] is True
    assert response["workstation_id"] == ws_id


@pytest.mark.asyncio
async def test_authorize_workstation_not_found_raises(authorize_ws_interactor, authorize_ws_deps):
    """Missing workstation raises an error."""
    authorize_ws_deps["current_user_service"].get_current_user.return_value = MagicMock()
    authorize_ws_deps["workstation_command_gateway"].read_by_id.return_value = None

    import src.dev.application.commands.admin_workstation.authorize_workstation as mod
    orig = _patch_authorize(mod)
    try:
        with pytest.raises(Exception, match="not found"):
            await authorize_ws_interactor.execute(
                AuthorizeWorkstationRequest(workstation_id=uuid4())
            )
    finally:
        _restore_authorize(mod, orig)


# ==========================================================================
# UpdateWorkstationInteractor
# ==========================================================================


@pytest.fixture()
def update_ws_deps():
    return {
        "current_user_service": AsyncMock(),
        "workstation_command_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def update_ws_interactor(update_ws_deps):
    return UpdateWorkstationInteractor(**update_ws_deps)


@pytest.mark.asyncio
async def test_update_workstation_success(update_ws_interactor, update_ws_deps):
    """Admin updates hostname; only changed field is applied (partial update)."""
    update_ws_deps["current_user_service"].get_current_user.return_value = MagicMock()

    ws_mock = MagicMock()
    ws_mock.data.specs.hostname = "OLD-HOST"
    ws_mock.data.specs.os_info = "Win10"
    ws_mock.data.network.ip_address = "10.0.0.5"
    ws_mock.data.network.mac_address = "AA:BB"
    ws_mock.data.location.building = "A"
    ws_mock.data.location.floor = 1
    ws_mock.data.location.room_number = "101"
    ws_mock.data.workstation_type = MagicMock()
    ws_mock.data.workstation_status = MagicMock()
    ws_mock.data.hardware_id = MagicMock()
    ws_mock.data.is_active = True
    ws_mock.update_data = MagicMock()
    update_ws_deps["workstation_command_gateway"].read_by_id.return_value = ws_mock
    ws_id = uuid4()

    import src.dev.application.commands.admin_workstation.update_workstation as mod
    orig = _patch_authorize(mod)
    try:
        response = await update_ws_interactor.execute(
            UpdateWorkstationRequest(workstation_id=ws_id, hostname="NEW-HOST")
        )
    finally:
        _restore_authorize(mod, orig)

    ws_mock.update_data.assert_called_once()
    assert response["workstation_id"] == ws_id


@pytest.mark.asyncio
async def test_update_workstation_not_found_raises(update_ws_interactor, update_ws_deps):
    """Missing workstation raises an error."""
    update_ws_deps["current_user_service"].get_current_user.return_value = MagicMock()
    update_ws_deps["workstation_command_gateway"].read_by_id.return_value = None

    import src.dev.application.commands.admin_workstation.update_workstation as mod
    orig = _patch_authorize(mod)
    try:
        with pytest.raises(Exception, match="not found"):
            await update_ws_interactor.execute(
                UpdateWorkstationRequest(workstation_id=uuid4(), hostname="X")
            )
    finally:
        _restore_authorize(mod, orig)


# ==========================================================================
# DeleteWorkstationInteractor
# ==========================================================================


@pytest.fixture()
def delete_ws_deps():
    return {
        "current_user_service": AsyncMock(),
        "workstation_command_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def delete_ws_interactor(delete_ws_deps):
    return DeleteWorkstationInteractor(**delete_ws_deps)


@pytest.mark.asyncio
async def test_delete_workstation_success(delete_ws_interactor, delete_ws_deps):
    """Admin hard-deletes a workstation; gateway.delete is invoked."""
    delete_ws_deps["current_user_service"].get_current_user.return_value = MagicMock()
    ws_mock = MagicMock()
    delete_ws_deps["workstation_command_gateway"].read_by_id.return_value = ws_mock
    # delete() is a sync method: use plain MagicMock
    delete_ws_deps["workstation_command_gateway"].delete = MagicMock()
    ws_id = uuid4()

    import src.dev.application.commands.admin_workstation.delete_workstation as mod
    orig = _patch_authorize(mod)
    try:
        await delete_ws_interactor.execute(DeleteWorkstationRequest(workstation_id=ws_id))
    finally:
        _restore_authorize(mod, orig)

    delete_ws_deps["workstation_command_gateway"].delete.assert_called_once_with(ws_mock)
    delete_ws_deps["transaction_manager"].commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_workstation_not_found_raises(delete_ws_interactor, delete_ws_deps):
    """Missing workstation raises an error before delete is called."""
    delete_ws_deps["current_user_service"].get_current_user.return_value = MagicMock()
    delete_ws_deps["workstation_command_gateway"].read_by_id.return_value = None
    delete_ws_deps["workstation_command_gateway"].delete = MagicMock()

    import src.dev.application.commands.admin_workstation.delete_workstation as mod
    orig = _patch_authorize(mod)
    try:
        with pytest.raises(Exception, match="not found"):
            await delete_ws_interactor.execute(
                DeleteWorkstationRequest(workstation_id=uuid4())
            )
    finally:
        _restore_authorize(mod, orig)

    delete_ws_deps["workstation_command_gateway"].delete.assert_not_called()
