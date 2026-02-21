from dataclasses import dataclass, fields
from typing import Any, Self

@dataclass(frozen=True, slots=True, repr=False)
class ValueObject:
    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls is ValueObject:
            raise TypeError("ValueObject cannot be instantiated directly")
        if not fields(cls):
            raise TypeError(f"{cls.__name__} must have at least one field")
        return object.__new__(cls)

    def __post_init__(self) -> None:
        """Hook for additional initialization and ensuring invariants."""

    def __repr__(self) -> str:
        """
        Return a string representation of value object
        """
        return f"{type(self).__name__}({self.__repr_value()})"

    def __repr_value(self) -> str:
        """
        Build a string representation of the value object fields
        - If one field, returns its value.
        - Otherwise, returns a comma-separated list of `name=value` pairs.
        """
        items = [f for f in fields(self) if f.repr]
        if not items:
            return "<hidden>"
        if len(items) == 1:
            return f"{getattr(self, items[0].name)!r}"
        return ", ".join(f"{f.name}={getattr(self, f.name)!r}" for f in items)
