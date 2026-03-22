from typing import Final

AUTHZ_NOT_AUTHORIZED: Final[str] = "No está autorizado para realizar esta acción."
AUTHZ_NO_CURRENT_USER: Final[str] = "No se pudo recuperar el usuario activo. Revocando todos los accesos."
AUTHZ_INACTIVE_ACCOUNT: Final[str] = "La cuenta del usuario activo está desactivada."
AUTHZ_INVALID_MACHINE: Final[str] = "Operación no permitida desde esta máquina."
AUTHZ_MISSING_CREDENTIALS: Final[str] = "El médico no tiene credenciales registradas (CMP/RNE)."
AUTHZ_INSUFFICIENT_ROLE: Final[str] = "Privilegios insuficientes para la jerarquía de roles."
