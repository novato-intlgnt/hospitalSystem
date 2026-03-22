"""Unit tests for DraftReportInteractor, SignReportInteractor, AmendReportInteractor."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.dev.application.commands.report.amend_report import (
    AmendReportInteractor,
    AmendReportRequest,
)
from src.dev.application.commands.report.draft_report import (
    DraftReportInteractor,
    DraftReportRequest,
)
from src.dev.application.commands.report.sign_report import (
    SignReportInteractor,
    SignReportRequest,
)
from src.dev.domain.enum.workstation import WorkstationType


def _workstation_qm(ws_type=WorkstationType.REPORTING, authorized=True):
    return {
        "id_": uuid4(),
        "type": ws_type,
        "is_authorized": authorized,
        "hostname": "RPT-01",
        "hardware_id": "HW-002",
        "ip_address": "10.0.0.20",
        "mac_address": "11:22:33:44:55:66",
        "location": "Tower C / F3",
    }


def _doctor_user():
    user = MagicMock()
    user.legal_signature = "CMP-12345:RNE-67890"
    return user


# ==========================================================================
# DraftReportInteractor
# ==========================================================================


@pytest.fixture()
def draft_deps():
    report_gw = AsyncMock()
    report_gw.add = MagicMock()
    return {
        "current_user_service": AsyncMock(),
        "report_command_gateway": report_gw,
        "workstation_query_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def draft_interactor(draft_deps):
    return DraftReportInteractor(**draft_deps)


def _draft_request(**overrides):
    defaults = dict(
        exam_code="EX-001",
        report_number="RPT-001",
        content="Normal chest X-Ray.",
        doctor_id=uuid4(),
        requester_ip="10.0.0.20",
    )
    defaults.update(overrides)
    return DraftReportRequest(**defaults)


@pytest.mark.asyncio
async def test_draft_report_success(draft_interactor, draft_deps):
    """Happy path: doctor from REPORTING station creates a draft."""
    draft_deps["current_user_service"].get_current_user.return_value = _doctor_user()
    draft_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()

    import src.dev.application.commands.report.draft_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        response = await draft_interactor.execute(_draft_request())
    finally:
        mod.authorize = original

    draft_deps["report_command_gateway"].add.assert_called_once()
    draft_deps["transaction_manager"].commit.assert_awaited_once()
    assert "report_id" in response


@pytest.mark.asyncio
async def test_draft_report_clinical_station_raises(draft_interactor, draft_deps):
    """CLINICAL station cannot draft reports (RN-11)."""
    draft_deps["current_user_service"].get_current_user.return_value = _doctor_user()
    draft_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm(
        ws_type=WorkstationType.CLINICAL
    )

    import src.dev.application.commands.report.draft_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        with pytest.raises(Exception, match="not allowed"):
            await draft_interactor.execute(_draft_request())
    finally:
        mod.authorize = original


# ==========================================================================
# SignReportInteractor
# ==========================================================================


@pytest.fixture()
def sign_deps():
    return {
        "current_user_service": AsyncMock(),
        "report_command_gateway": AsyncMock(),
        "workstation_query_gateway": AsyncMock(),
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def sign_interactor(sign_deps):
    return SignReportInteractor(**sign_deps)


@pytest.mark.asyncio
async def test_sign_report_success(sign_interactor, sign_deps):
    """Happy path: doctor signs an unsigned report."""
    sign_deps["current_user_service"].get_current_user.return_value = _doctor_user()
    sign_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()

    report_mock = MagicMock()
    report_mock.exam_code.value = "EX-001"
    report_mock.content.value = "Normal findings."
    report_mock.sign = MagicMock()
    sign_deps["report_command_gateway"].read_by_id.return_value = report_mock

    import src.dev.application.commands.report.sign_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        response = await sign_interactor.execute(
            SignReportRequest(report_id=uuid4(), requester_ip="10.0.0.20")
        )
    finally:
        mod.authorize = original

    report_mock.sign.assert_called_once()
    assert "report_id" in response
    assert "signed_at" in response


@pytest.mark.asyncio
async def test_sign_report_not_found_raises(sign_interactor, sign_deps):
    """Missing report raises an error."""
    sign_deps["current_user_service"].get_current_user.return_value = _doctor_user()
    sign_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()
    sign_deps["report_command_gateway"].read_by_id.return_value = None

    import src.dev.application.commands.report.sign_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        with pytest.raises(Exception, match="not found"):
            await sign_interactor.execute(
                SignReportRequest(report_id=uuid4(), requester_ip="10.0.0.20")
            )
    finally:
        mod.authorize = original


@pytest.mark.asyncio
async def test_sign_already_signed_report_raises(sign_interactor, sign_deps):
    """Report.sign raises → wrapped as ImmutableReportError (RN-06)."""
    sign_deps["current_user_service"].get_current_user.return_value = _doctor_user()
    sign_deps["workstation_query_gateway"].read_by_ip.return_value = _workstation_qm()

    report_mock = MagicMock()
    report_mock.exam_code.value = "EX-001"
    report_mock.content.value = "Signed."
    report_mock.sign.side_effect = Exception("Already signed")
    sign_deps["report_command_gateway"].read_by_id.return_value = report_mock

    import src.dev.application.commands.report.sign_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        with pytest.raises(Exception, match="immutable|finalized|Already"):
            await sign_interactor.execute(
                SignReportRequest(report_id=uuid4(), requester_ip="10.0.0.20")
            )
    finally:
        mod.authorize = original


# ==========================================================================
# AmendReportInteractor
# ==========================================================================


@pytest.fixture()
def amend_deps():
    report_gw = AsyncMock()
    report_gw.add = MagicMock()
    return {
        "current_user_service": AsyncMock(),
        "report_command_gateway": report_gw,
        "flusher": AsyncMock(),
        "transaction_manager": AsyncMock(),
    }


@pytest.fixture()
def amend_interactor(amend_deps):
    return AmendReportInteractor(**amend_deps)


@pytest.mark.asyncio
async def test_amend_report_success(amend_interactor, amend_deps):
    """Happy path: signed report produces an amendment with incremented version."""
    amend_deps["current_user_service"].get_current_user.return_value = _doctor_user()

    amended_mock = MagicMock()
    amended_mock.version = 2
    source_mock = MagicMock()
    source_mock.create_amendment.return_value = amended_mock
    amend_deps["report_command_gateway"].read_by_id.return_value = source_mock

    import src.dev.application.commands.report.amend_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        response = await amend_interactor.execute(
            AmendReportRequest(report_id=uuid4(), new_content="Correction: normal.")
        )
    finally:
        mod.authorize = original

    amend_deps["report_command_gateway"].add.assert_called_once_with(amended_mock)
    assert response["version"] == 2
    assert "new_report_id" in response


@pytest.mark.asyncio
async def test_amend_report_source_not_found_raises(amend_interactor, amend_deps):
    """Missing source report raises an error."""
    amend_deps["current_user_service"].get_current_user.return_value = _doctor_user()
    amend_deps["report_command_gateway"].read_by_id.return_value = None

    import src.dev.application.commands.report.amend_report as mod
    original = mod.authorize
    mod.authorize = lambda perm, *, context: None
    try:
        with pytest.raises(Exception, match="not found"):
            await amend_interactor.execute(
                AmendReportRequest(report_id=uuid4(), new_content="Correction.")
            )
    finally:
        mod.authorize = original
