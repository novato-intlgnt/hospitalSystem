"""Unit tests for UploadExamImageInteractor and CompleteExamInteractor."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dev.application.commands.exam.complete_exam import (
    CompleteExamInteractor,
    CompleteExamRequest,
)
from src.dev.application.commands.exam.upload_exam_image import (
    UploadExamImageInteractor,
    UploadImageRequest,
)
from src.dev.domain.enum.workstation import WorkstationType


def _workstation_qm(ws_type=WorkstationType.ACQUISITION, authorized=True):
    return {
        "id_": uuid4(),
        "type": ws_type,
        "is_authorized": authorized,
        "hostname": "ACQ-01",
        "hardware_id": "HW-001",
        "ip_address": "10.0.0.5",
        "mac_address": "AA:BB:CC",
        "location": "Tower B",
    }


# ==========================================================================
# UploadExamImageInteractor
# ==========================================================================


@pytest.fixture()
def upload_deps():
    return {
        "exam_command_gateway": AsyncMock(),
        "workstation_query_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def upload_interactor(upload_deps):
    return UploadExamImageInteractor(**upload_deps)


def _upload_request(**overrides):
    defaults = dict(
        exam_id=uuid4(),
        image_url="https://store.example.com/dicom/scan.dcm",
        file_size_bytes=1024,
        requester_ip="10.0.0.5",
    )
    defaults.update(overrides)
    return UploadImageRequest(**defaults)


@pytest.mark.asyncio
async def test_upload_image_success(upload_interactor, upload_deps):
    """Happy path: ACQUISITION station attaches image to a valid exam."""
    upload_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()
    exam_mock = MagicMock()
    exam_mock.add_image = MagicMock()
    upload_deps["exam_command_gateway"].read_by_id.return_value = exam_mock

    response = await upload_interactor.execute(_upload_request())

    exam_mock.add_image.assert_called_once()
    upload_deps["flusher"].flush.assert_awaited_once()
    assert "image_id" in response
    assert "exam_id" in response


@pytest.mark.asyncio
async def test_upload_image_reporting_station_raises(upload_interactor, upload_deps):
    """REPORTING station is not allowed to upload images (RN-09/RN-10)."""
    upload_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm(
        ws_type=WorkstationType.REPORTING
    )

    with pytest.raises(Exception, match="not allowed"):
        await upload_interactor.execute(_upload_request())

    upload_deps["exam_command_gateway"].read_by_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_upload_image_exam_not_found_raises(upload_interactor, upload_deps):
    """Missing exam raises an error."""
    upload_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()
    upload_deps["exam_command_gateway"].read_by_id.return_value = None

    with pytest.raises(Exception, match="not found"):
        await upload_interactor.execute(_upload_request())


@pytest.mark.asyncio
async def test_upload_image_reported_exam_raises(upload_interactor, upload_deps):
    """Domain entity raises ValueError when exam is already REPORTED (RN-04)."""
    upload_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()
    exam_mock = MagicMock()
    exam_mock.add_image.side_effect = ValueError("Exam is in REPORTED status")
    upload_deps["exam_command_gateway"].read_by_id.return_value = exam_mock

    with pytest.raises(ValueError, match="REPORTED"):
        await upload_interactor.execute(_upload_request())


# ==========================================================================
# CompleteExamInteractor
# ==========================================================================


@pytest.fixture()
def complete_deps():
    return {
        "exam_command_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def complete_interactor(complete_deps):
    return CompleteExamInteractor(**complete_deps)


@pytest.mark.asyncio
async def test_complete_exam_success(complete_interactor, complete_deps):
    """Exam is marked as REPORTED after mark_as_reported is called."""
    exam_mock = MagicMock()
    exam_mock.mark_as_reported = MagicMock()
    exam_mock.status = "REPORTED"
    complete_deps["exam_command_gateway"].read_by_id.return_value = exam_mock

    response = await complete_interactor.execute(CompleteExamRequest(exam_id=uuid4()))

    exam_mock.mark_as_reported.assert_called_once()
    complete_deps["transaction_manager"].commit.assert_awaited_once()
    assert response["status"] == "REPORTED"


@pytest.mark.asyncio
async def test_complete_exam_not_found_raises(complete_interactor, complete_deps):
    """Non-existent exam raises an error."""
    complete_deps["exam_command_gateway"].read_by_id.return_value = None

    with pytest.raises(Exception, match="not found"):
        await complete_interactor.execute(CompleteExamRequest(exam_id=uuid4()))


@pytest.mark.asyncio
async def test_complete_exam_invalid_state_raises(complete_interactor, complete_deps):
    """Domain raises DomainError on invalid state → wrapped as InvalidExamStateTransitionError."""
    from src.dev.application.common.exceptions.invalid_state_transition import (
        InvalidExamStateTransitionError,
    )
    from src.dev.domain.exceptions.base import DomainError as SrcDomainError

    exam_mock = MagicMock()
    exam_mock.mark_as_reported.side_effect = SrcDomainError("Cannot transition")
    exam_mock.status = "PENDING"
    complete_deps["exam_command_gateway"].read_by_id.return_value = exam_mock

    with pytest.raises(Exception, match="transition|state|Cannot"):
        await complete_interactor.execute(CompleteExamRequest(exam_id=uuid4()))
