"""Transaction Manager port — Application Layer"""

from abc import abstractmethod
from typing import Protocol


class TransactionManager(Protocol):
    """
    Contrato para gestionar el ciclo de vida de una transacción de negocio.

    Permite confirmar (commit) o revertir (rollback) los cambios producidos
    por un Command. La implementación concreta puede ser una sesión de
    SQLAlchemy u otro gestor de UoW.
    """

    @abstractmethod
    async def commit(self) -> None:
        """
        :raises DataMapperError:

        Confirma el resultado exitoso de la transacción de negocio actual.
        Debe invocarse al final de cada Command una vez que toda la lógica
        de dominio ha sido aplicada sin errores.
        """

    @abstractmethod
    async def rollback(self) -> None:
        """
        :raises DataMapperError:

        Revierte todos los cambios pendientes de la transacción actual.
        Debe invocarse en caso de error para garantizar la consistencia
        de los datos persistidos.
        """
