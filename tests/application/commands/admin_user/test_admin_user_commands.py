"""Unit tests for admin_user command interactors.

Covers: CreateUserInteractor, DeactivateUserInteractor, DeleteUserInteractor,
UpdateUserRoleInteractor, ResetUserPasswordInteractor.
"""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dev.application.commands.admin_user.create_user import (
    CreateUserInteractor,
    CreateUserRequest,
)
from src.dev.application.commands.admin_user.deactivate_user import (
    DeactivateUserInteractor,
    DeactivateUserRequest,
)
from src.dev.application.commands.admin_user.delete_user import (
    DeleteUserInteractor,
    DeleteUserRequest,
)
from src.dev.application.commands.admin_user.reset_user_password import (
    ResetUserPasswordInteractor,
    ResetUserPasswordRequest,
)
from src.dev.application.commands.admin_user.update_user_role import (
    UpdateUserRoleInteractor,
    UpdateUserRoleRequest,
)
from src.dev.domain.enum.user import UserRole


def _patch_authorize(module):
    original = module.authorize
    module.authorize = lambda perm, *, context: None
    return original


def _restore_authorize(module, original):
    module.authorize = original


# ==========================================================================
# CreateUserInteractor
# ==========================================================================


def _create_request(**overrides):
    defaults = dict(
        username="johndoe",       # >= 5 chars: Username VO enforces len >= 5
        email="jdoe@hospital.com",
        raw_password="secret123",
        role=UserRole.TECHNICIAN,
        first_name="John",
        paternal_last_name="Doe",
        maternal_last_name="Smith",
    )
    defaults.update(overrides)
    return CreateUserRequest(**defaults)


@pytest.fixture()
def create_deps():
    return {
        "current_user_service": AsyncMock(),
        "user_creator_service": AsyncMock(),
        "user_command_gateway": MagicMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def create_interactor(create_deps):
    return CreateUserInteractor(**create_deps)


@pytest.mark.asyncio
async def test_create_user_success(create_interactor, create_deps):
    """Happy path: admin creates a TECHNICIAN user."""
    create_deps["current_user_service"].get_current_user.return_value = MagicMock()
    user_mock = MagicMock()
    user_mock.id_.value = uuid4()
    create_deps["user_creator_service"].create_user.return_value = user_mock

    import src.dev.application.commands.admin_user.create_user as mod
    orig = _patch_authorize(mod)
    try:
        response = await create_interactor.execute(_create_request())
    finally:
        _restore_authorize(mod, orig)

    create_deps["user_command_gateway"].add.assert_called_once_with(user_mock)
    create_deps["transaction_manager"].commit.assert_awaited_once()
    assert "user_id" in response


@pytest.mark.asyncio
async def test_create_doctor_user_builds_doctor_data(create_interactor, create_deps):
    """Doctor role with valid CMP/RNE/specialty builds DoctorData correctly."""
    create_deps["current_user_service"].get_current_user.return_value = MagicMock()
    user_mock = MagicMock()
    user_mock.id_.value = uuid4()
    create_deps["user_creator_service"].create_user.return_value = user_mock

    import src.dev.application.commands.admin_user.create_user as mod
    orig = _patch_authorize(mod)
    try:
        await create_interactor.execute(
            _create_request(
                role=UserRole.DOCTOR,
                # CMPNumber VO expects pattern e.g. "12345" - 5-6 digits
                cmp="12345",
                rne="12345",
                specialty="Radiology",
            )
        )
    finally:
        _restore_authorize(mod, orig)

    # Verify doctor_data was built and passed to creator service
    call_kwargs = create_deps["user_creator_service"].create_user.call_args[1]
    assert call_kwargs.get("doctor_data") is not None


# ==========================================================================
# DeactivateUserInteractor
# ==========================================================================


@pytest.fixture()
def deactivate_deps():
    return {
        "current_user_service": AsyncMock(),
        "user_command_gateway": AsyncMock(),
        "access_revoker": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def deactivate_interactor(deactivate_deps):
    return DeactivateUserInteractor(**deactivate_deps)


@pytest.mark.asyncio
async def test_deactivate_user_success(deactivate_interactor, deactivate_deps):
    """Admin deactivates a subordinate; sessions are revoked after commit."""
    deactivate_deps["current_user_service"].get_current_user.return_value = MagicMock()
    target = MagicMock()
    deactivate_deps["user_command_gateway"].read_by_id.return_value = target

    import src.dev.application.commands.admin_user.deactivate_user as mod
    orig = _patch_authorize(mod)
    user_id = uuid4()
    try:
        await deactivate_interactor.execute(DeactivateUserRequest(target_user_id=user_id))
    finally:
        _restore_authorize(mod, orig)

    deactivate_deps["transaction_manager"].commit.assert_awaited_once()
    deactivate_deps["access_revoker"].remove_all_user_access.assert_awaited_once_with(user_id)


@pytest.mark.asyncio
async def test_deactivate_user_not_found_raises(deactivate_interactor, deactivate_deps):
    """Missing target raises an error."""
    deactivate_deps["current_user_service"].get_current_user.return_value = MagicMock()
    deactivate_deps["user_command_gateway"].read_by_id.return_value = None

    import src.dev.application.commands.admin_user.deactivate_user as mod
    orig = _patch_authorize(mod)
    try:
        with pytest.raises(Exception, match="not found"):
            await deactivate_interactor.execute(
                DeactivateUserRequest(target_user_id=uuid4())
            )
    finally:
        _restore_authorize(mod, orig)


# ==========================================================================
# DeleteUserInteractor
# ==========================================================================


@pytest.fixture()
def delete_deps():
    return {
        "current_user_service": AsyncMock(),
        "user_command_gateway": AsyncMock(),
        "access_revoker": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def delete_interactor(delete_deps):
    return DeleteUserInteractor(**delete_deps)


@pytest.mark.asyncio
async def test_delete_user_success(delete_interactor, delete_deps):
    """Admin hard-deletes a user; gateway.delete is called and sessions revoked."""
    delete_deps["current_user_service"].get_current_user.return_value = MagicMock()
    target = MagicMock()
    delete_deps["user_command_gateway"].read_by_id.return_value = target

    # Use MagicMock (not AsyncMock) for the non-async delete method
    delete_deps["user_command_gateway"].delete = MagicMock()

    import src.dev.application.commands.admin_user.delete_user as mod
    orig = _patch_authorize(mod)
    user_id = uuid4()
    try:
        await delete_interactor.execute(DeleteUserRequest(target_user_id=user_id))
    finally:
        _restore_authorize(mod, orig)

    delete_deps["user_command_gateway"].delete.assert_called_once_with(target)
    delete_deps["access_revoker"].remove_all_user_access.assert_awaited_once_with(user_id)


# ==========================================================================
# UpdateUserRoleInteractor
# ==========================================================================


@pytest.fixture()
def update_role_deps():
    return {
        "current_user_service": AsyncMock(),
        "user_command_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def update_role_interactor(update_role_deps):
    return UpdateUserRoleInteractor(**update_role_deps)


@pytest.mark.asyncio
async def test_update_user_role_success(update_role_interactor, update_role_deps):
    """Admin reassigns a user role; response contains new_role."""
    update_role_deps["current_user_service"].get_current_user.return_value = MagicMock()
    target = MagicMock()
    update_role_deps["user_command_gateway"].read_by_id.return_value = target
    user_id = uuid4()

    import src.dev.application.commands.admin_user.update_user_role as mod
    orig = _patch_authorize(mod)
    try:
        response = await update_role_interactor.execute(
            UpdateUserRoleRequest(target_user_id=user_id, new_role=UserRole.TECHNICIAN)
        )
    finally:
        _restore_authorize(mod, orig)

    assert response["user_id"] == user_id
    assert "new_role" in response


# ==========================================================================
# ResetUserPasswordInteractor
# ==========================================================================


@pytest.fixture()
def reset_pwd_deps():
    return {
        "current_user_service": AsyncMock(),
        "user_command_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def reset_pwd_interactor(reset_pwd_deps):
    return ResetUserPasswordInteractor(**reset_pwd_deps)


@pytest.mark.asyncio
async def test_reset_password_success(reset_pwd_interactor, reset_pwd_deps):
    """Admin resets password; commit is called and user_id returned."""
    reset_pwd_deps["current_user_service"].get_current_user.return_value = MagicMock()
    target = MagicMock()
    reset_pwd_deps["user_command_gateway"].read_by_id.return_value = target
    user_id = uuid4()

    import src.dev.application.commands.admin_user.reset_user_password as mod
    orig = _patch_authorize(mod)
    try:
        response = await reset_pwd_interactor.execute(
            ResetUserPasswordRequest(
                target_user_id=user_id, new_raw_password="newPass99"
            )
        )
    finally:
        _restore_authorize(mod, orig)

    reset_pwd_deps["transaction_manager"].commit.assert_awaited_once()
    assert response["user_id"] == user_id


@pytest.mark.asyncio
async def test_reset_password_user_not_found_raises(reset_pwd_interactor, reset_pwd_deps):
    """Missing user raises an error."""
    reset_pwd_deps["current_user_service"].get_current_user.return_value = MagicMock()
    reset_pwd_deps["user_command_gateway"].read_by_id.return_value = None

    import src.dev.application.commands.admin_user.reset_user_password as mod
    orig = _patch_authorize(mod)
    try:
        with pytest.raises(Exception, match="not found"):
            await reset_pwd_interactor.execute(
                ResetUserPasswordRequest(
                    target_user_id=uuid4(), new_raw_password="newPass99"
                )
            )
    finally:
        _restore_authorize(mod, orig)
