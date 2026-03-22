"""Application Layer — Common Ports

Public re-export point for all port contracts (Protocols) used across
Commands and Queries in the hospital system.
"""

from .audit_gateway import AuditCommandGateway, AuditQueryGateway
from .exam_gateway import ExamCommandGateway, ExamQueryGateway
from .flusher import Flusher
from .patient_gateway import PatientCommandGateway, PatientQueryGateway
from .report_gateway import ReportCommandGateway, ReportQueryGateway
from .transaction_manager import TransactionManager
from .workstation_gateway import WorkstationCommandGateway, WorkstationQueryGateway

__all__ = [
    "TransactionManager",
    "Flusher",
    "PatientCommandGateway",
    "PatientQueryGateway",
    "ExamCommandGateway",
    "ExamQueryGateway",
    "ReportCommandGateway",
    "ReportQueryGateway",
    "AuditCommandGateway",
    "AuditQueryGateway",
    "WorkstationQueryGateway",
    "WorkstationCommandGateway",
]
from .access_revoker import AccessRevoker
from .identity_provider import IdentityProvider
from .user_gateway import UserCommandGateway

__all__ += [
    "AccessRevoker",
    "IdentityProvider",
    "UserCommandGateway",
]
