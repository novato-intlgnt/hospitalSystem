"""Tests for UserCreatorService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.user import User
from src.dev.domain.enum.user import UserRole
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.user.user_creator import UserCreatorService


def _make_service(user_repo=None, id_gen=None, hasher=None):
    user_repo = user_repo or AsyncMock()
    id_gen = id_gen or AsyncMock()
    hasher = hasher or AsyncMock()
    return (
        UserCreatorService(
            id_generator=id_gen,
            user_repository=user_repo,
            password_hasher=hasher,
        ),
        user_repo,
        id_gen,
        hasher,
    )


@pytest.mark.asyncio
async def test_create_user_success_admin():
    """Admin user is created successfully when username is unique"""
    user_repo = AsyncMock()
    id_gen = AsyncMock()
    hasher = AsyncMock()

    user_repo.get_by_username.return_value = None
    id_gen.generate_id.return_value = MagicMock()
    hasher.hash.return_value = MagicMock()

    user_data = MagicMock()
    person_data = MagicMock()
    person_data.role = UserRole.ADMIN

    service = UserCreatorService(
        id_generator=id_gen,
        user_repository=user_repo,
        password_hasher=hasher,
    )

    result = await service.create_user(user_data=user_data, person_data=person_data)

    assert isinstance(result, User)
    user_repo.get_by_username.assert_called_once_with(user_data.username)
    hasher.hash.assert_called_once()
    id_gen.generate_id.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_success_doctor():
    """Doctor user is created successfully when doctor_data is provided"""
    user_repo = AsyncMock()
    id_gen = AsyncMock()
    hasher = AsyncMock()

    user_repo.get_by_username.return_value = None
    id_gen.generate_id.return_value = MagicMock()
    hasher.hash.return_value = MagicMock()

    user_data = MagicMock()
    person_data = MagicMock()
    person_data.role = UserRole.DOCTOR
    doctor_data = MagicMock()

    service = UserCreatorService(
        id_generator=id_gen,
        user_repository=user_repo,
        password_hasher=hasher,
    )

    result = await service.create_user(
        user_data=user_data,
        person_data=person_data,
        doctor_data=doctor_data,
    )

    assert isinstance(result, User)


@pytest.mark.asyncio
async def test_create_user_doctor_without_doctor_data_raises():
    """RN-05: Creating a DOCTOR user without doctor_data must raise DomainError"""
    user_repo = AsyncMock()
    service = UserCreatorService(
        id_generator=AsyncMock(),
        user_repository=user_repo,
        password_hasher=AsyncMock(),
    )

    person_data = MagicMock()
    person_data.role = UserRole.DOCTOR

    with pytest.raises(DomainError, match="Doctor data"):
        await service.create_user(
            user_data=MagicMock(),
            person_data=person_data,
            doctor_data=None,
        )

    user_repo.get_by_username.assert_not_called()


@pytest.mark.asyncio
async def test_create_user_duplicate_username_raises():
    """RN-06: Creating a user with an existing username must raise DomainError"""
    user_repo = AsyncMock()
    existing = MagicMock()
    user_repo.get_by_username.return_value = existing

    service = UserCreatorService(
        id_generator=AsyncMock(),
        user_repository=user_repo,
        password_hasher=AsyncMock(),
    )

    user_data = MagicMock()
    user_data.username.value = "taken_user"
    person_data = MagicMock()
    person_data.role = UserRole.ADMIN

    with pytest.raises(DomainError, match="taken_user"):
        await service.create_user(user_data=user_data, person_data=person_data)
