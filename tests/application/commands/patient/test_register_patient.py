"""Unit tests for RegisterPatientInteractor."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dev.application.commands.patient.register_patient import (
    RegisterPatientInteractor,
    RegisterPatientRequest,
)


def _make_request(**overrides):
    defaults = dict(
        hc="HC-001",
        dni="12345678",
        first_name="Ana",
        second_name=None,
        paternal_last_name="Garcia",
        maternal_last_name="Lopez",
        birth_date=date(1990, 5, 15),
        gender=MagicMock(),
    )
    defaults.update(overrides)
    return RegisterPatientRequest(**defaults)


@pytest.fixture()
def deps():
    patient_gw = AsyncMock()
    patient_gw.add = MagicMock()
    return {
        "patient_command_gateway": patient_gw,
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def interactor(deps):
    return RegisterPatientInteractor(**deps)


@pytest.mark.asyncio
async def test_register_patient_success(interactor, deps):
    """Happy path: new patient is persisted and UUID returned."""
    deps["patient_command_gateway"].read_by_hc.return_value = None

    response = await interactor.execute(_make_request())

    deps["patient_command_gateway"].add.assert_called_once()
    deps["flusher"].flush.assert_awaited_once()
    deps["transaction_manager"].commit.assert_awaited_once()
    assert "patient_id" in response


@pytest.mark.asyncio
async def test_register_patient_duplicate_hc_raises(interactor, deps):
    """If HC already exists, a duplicate error is raised before any add (RN-01)."""
    deps["patient_command_gateway"].read_by_hc.return_value = MagicMock()

    with pytest.raises(Exception, match="already"):
        await interactor.execute(_make_request())

    deps["patient_command_gateway"].add.assert_not_called()
    deps["flusher"].flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_register_patient_with_second_name(interactor, deps):
    """Second name is optional — its presence should not break construction."""
    deps["patient_command_gateway"].read_by_hc.return_value = None

    response = await interactor.execute(_make_request(second_name="Maria"))

    assert "patient_id" in response
    deps["patient_command_gateway"].add.assert_called_once()
