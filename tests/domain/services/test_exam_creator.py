"""Tests for ExamCreatorService"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.dev.domain.entities.exam import Exam
from src.dev.domain.enum.exam_status import ExamStatus
from src.dev.domain.exceptions.base import DomainError
from src.dev.domain.services.exam_creator import ExamCreatorService


@pytest.mark.asyncio
async def test_create_exam_success():
    """Test exam creation successfully with an existing patient and valid workstation"""
    patient_repo = AsyncMock()
    workstation_repo = AsyncMock()

    patient_repo.exists_by_hc.return_value = True

    workstation_mock = MagicMock()
    workstation_mock.can_upload_file = True
    workstation_repo.get_by_network.return_value = workstation_mock

    service = ExamCreatorService(
        patient_repository=patient_repo,
        workstation_repository=workstation_repo,
    )

    id_mock = MagicMock()
    exam_code_mock = MagicMock()
    patient_hc_mock = MagicMock()
    modality_mock = MagicMock()
    study_type = "CT Brain"
    network_mock = MagicMock()

    exam = await service.create_exam(
        id_=id_mock,
        exam_code=exam_code_mock,
        patient_hc=patient_hc_mock,
        modality=modality_mock,
        study_type=study_type,
        workstation_network=network_mock,
    )

    # Assertions
    patient_repo.exists_by_hc.assert_called_once_with(patient_hc_mock)
    workstation_repo.get_by_network.assert_called_once_with(network_mock)

    assert isinstance(exam, Exam)
    assert exam.id_ == id_mock
    assert exam.exam_code == exam_code_mock
    assert exam.patient_hc == patient_hc_mock
    assert exam.modality == modality_mock
    assert exam.study_type == study_type
    assert exam.status == ExamStatus.PENDING


@pytest.mark.asyncio
async def test_create_exam_patient_does_not_exist():
    """Test exam creation fails if patient HC does not exist"""
    patient_repo = AsyncMock()
    workstation_repo = AsyncMock()

    patient_repo.exists_by_hc.return_value = False

    service = ExamCreatorService(
        patient_repository=patient_repo,
        workstation_repository=workstation_repo,
    )

    patient_hc_mock = MagicMock()
    patient_hc_mock.value = "HC-123"

    with pytest.raises(DomainError, match="Patient with HC HC-123 does not exist"):
        await service.create_exam(
            id_=MagicMock(),
            exam_code=MagicMock(),
            patient_hc=patient_hc_mock,
            modality=MagicMock(),
            study_type="CT Brain",
            workstation_network=MagicMock(),
        )


@pytest.mark.asyncio
async def test_create_exam_workstation_not_found():
    """Test exam creation fails if workstation network is unregistered"""
    patient_repo = AsyncMock()
    workstation_repo = AsyncMock()

    patient_repo.exists_by_hc.return_value = True
    workstation_repo.get_by_network.return_value = None

    service = ExamCreatorService(
        patient_repository=patient_repo,
        workstation_repository=workstation_repo,
    )

    with pytest.raises(
        DomainError, match="Workstation not found for the given network address"
    ):
        await service.create_exam(
            id_=MagicMock(),
            exam_code=MagicMock(),
            patient_hc=MagicMock(),
            modality=MagicMock(),
            study_type="CT Brain",
            workstation_network=MagicMock(),
        )


@pytest.mark.asyncio
async def test_create_exam_workstation_unauthorized():
    """Test exam creation fails if workstation cannot upload files (not ACQUISITION)"""
    patient_repo = AsyncMock()
    workstation_repo = AsyncMock()

    patient_repo.exists_by_hc.return_value = True

    workstation_mock = MagicMock()
    workstation_mock.can_upload_file = False
    workstation_repo.get_by_network.return_value = workstation_mock

    service = ExamCreatorService(
        patient_repository=patient_repo,
        workstation_repository=workstation_repo,
    )

    with pytest.raises(
        DomainError, match="Only authorized ACQUISITION workstations can create exams"
    ):
        await service.create_exam(
            id_=MagicMock(),
            exam_code=MagicMock(),
            patient_hc=MagicMock(),
            modality=MagicMock(),
            study_type="CT Brain",
            workstation_network=MagicMock(),
        )
