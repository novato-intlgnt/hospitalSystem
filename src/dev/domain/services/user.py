from src.dev.domain.ports.repositories.persistence import UserRepository
from src.dev.domain.ports.services.generator import IDGenerator
from src.dev.domain.ports.services.security import AuthenticationPort, PasswordHasher
from src.dev.domain.value_objects.user import UserData


class UserService:
    def __init__(
        self,
        id_generator: IDGenerator,
        user_repository: UserRepository,
        authentication_port: AuthenticationPort,
        password_hasher: PasswordHasher,
    ) -> None:
        self._id_generator = id_generator
        self._user_repository = user_repository
        self._authentication_port = authentication_port
        self._password_hasher = password_hasher

    def create_user(self, user_data: UserData) -> None:
        """Create a new user with the given data."""
