"""Independent components; null means evidence is missing or not applicable."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    passed: bool | None
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def strict_conjunction(values: list[bool | None]) -> bool | None:
    """A failure disproves success; unknown evidence never establishes success."""
    if any(v is False for v in values):
        return False
    return True if values and all(v is True for v in values) else None


def ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None

