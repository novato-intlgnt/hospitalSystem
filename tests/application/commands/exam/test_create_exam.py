"""Unit tests for CreateExamInteractor."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dev.application.commands.exam.create_exam import (
    CreateExamInteractor,
    CreateExamRequest,
)
from src.dev.domain.enum.workstation import WorkstationType


def _workstation_qm(ws_type=WorkstationType.ACQUISITION, authorized=True):
    return {
        "id_": uuid4(),
        "type": ws_type,
        "is_authorized": authorized,
        "hostname": "ACQ-01",
        "hardware_id": "HW-001",
        "ip_address": "192.168.1.10",
        "mac_address": "AA:BB:CC:DD:EE:FF",
        "location": "Building A / Floor 1 / Room 101",
    }


@pytest.fixture()
def deps():
    exam_gw = AsyncMock()
    exam_gw.add = MagicMock()
    return {
        "exam_command_gateway": exam_gw,
        "patient_command_gateway": AsyncMock(),
        "workstation_query_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def interactor(deps):
    return CreateExamInteractor(**deps)


def _request(**overrides):
    defaults = dict(
        patient_hc="HC-001",
        exam_code="EX-001",
        modality=MagicMock(),
        study_type="CT Brain",
        requester_ip="192.168.1.10",
    )
    defaults.update(overrides)
    return CreateExamRequest(**defaults)


@pytest.mark.asyncio
async def test_create_exam_success(interactor, deps):
    """Happy path: valid ACQUISITION workstation + existing patient."""
    deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()
    deps["patient_command_gateway"].read_by_hc.return_value = MagicMock()

    response = await interactor.execute(_request())

    deps["exam_command_gateway"].add.assert_called_once()
    deps["flusher"].flush.assert_awaited_once()
    deps["transaction_manager"].commit.assert_awaited_once()
    assert "exam_id" in response


@pytest.mark.asyncio
async def test_create_exam_unknown_workstation_raises(interactor, deps):
    """Unregistered IP raises an error (RN-09)."""
    deps["workstation_query_gateway"].read_by_ip.return_value = None

    with pytest.raises(Exception, match="not allowed"):
        await interactor.execute(_request())

    deps["exam_command_gateway"].add.assert_not_called()


@pytest.mark.asyncio
async def test_create_exam_reporting_workstation_raises(interactor, deps):
    """REPORTING-type station cannot create exams (RN-09)."""
    deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm(
        ws_type=WorkstationType.REPORTING
    )

    with pytest.raises(Exception, match="not allowed"):
        await interactor.execute(_request())


@pytest.mark.asyncio
async def test_create_exam_patient_not_found_raises(interactor, deps):
    """Missing patient raises an error before any exam is added."""
    deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()
    deps["patient_command_gateway"].read_by_hc.return_value = None

    with pytest.raises(Exception, match="Patient"):
        await interactor.execute(_request())

    deps["exam_command_gateway"].add.assert_not_called()
