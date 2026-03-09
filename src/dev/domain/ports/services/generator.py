"""Ports for ID o codes generation"""

from abc import abstractmethod
from typing import Protocol

from src.dev.domain.value_objects.user import EntityID


class IDGenerator(Protocol):
    """ID generator service ports"""

    @abstractmethod
    async def generate_id(self) -> EntityID:
        """Generates a unique entity ID"""


class Patient(Protocol):
    """Patient services ports"""

    @abstractmethod
    async def generate_hc(self) -> str:
        """Generates a unique clinical history code (HC)"""


class Exam(Protocol):
    """Exam services ports"""

    @abstractmethod
    async def generate_exam_code(self) -> str:
        """Generates a unique exam code"""


class Report(Protocol):
    """Report services ports"""

    @abstractmethod
    async def generate_report_number(self) -> str:
        """Generates a unique report number"""
