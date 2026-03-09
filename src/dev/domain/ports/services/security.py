"""Security protocols for user authentication and password hashing"""

from abc import abstractmethod
from typing import Protocol

from src.dev.domain.entities.user import User
from src.dev.domain.enum.workstationType import WorkstationType
from src.dev.domain.value_objects.report import ReportSignature
from src.dev.domain.value_objects.user import RawPassword, UserData, UserPasswordHash


class AuthenticationPort(Protocol):
    """Protocol for user authentication"""

    @abstractmethod
    async def authenticate(self, credentials: UserData) -> User:
        """Authenticate a user with the given credentials and return the user entity"""


class PasswordHasher(Protocol):
    """Protocol for password hashing and verification"""

    @abstractmethod
    async def hash(self, raw_password: RawPassword) -> UserPasswordHash:
        """Hash a raw password"""

    @abstractmethod
    async def verify(self, raw_password: RawPassword, hashed: UserPasswordHash) -> bool:
        """Verify a raw password against a hashed password"""


class SignatureService(Protocol):
    """RN-07: Garantiza la integridad legal del informe."""

    @abstractmethod
    def generate_hash(self, content: str, medical_license: str) -> ReportSignature:
        """Generate a hash for the given content and medical license."""

    @abstractmethod
    def verify_signature(self, signature: ReportSignature) -> bool:
        """Verify the integrity of the report based on the signature"""


class NetworkService(Protocol):
    """RN-10 y RN-11: Validación central de accesos por hardware."""

    @abstractmethod
    def validate_access(self, workstation_type: WorkstationType, action: str) -> bool:
        """Validate acces to the system based on the workstation type and the action."""
