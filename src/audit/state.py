from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class State:
    """Snapshot persisted to state.json between daily runs.

    Key order (block_height, block_time, total) matches the on-disk
    convention set in commit 9743d0b and is what `to_dict` emits.
    """

    block_height: int
    block_time: int
    total: Decimal

    @classmethod
    def from_dict(cls, data: dict) -> "State":
        return cls(
            block_height=int(data["block_height"]),
            block_time=int(data["block_time"]),
            total=Decimal(data["total"]),
        )

    def to_dict(self) -> dict:
        return {
            "block_height": self.block_height,
            "block_time": self.block_time,
            "total": str(self.total),
        }
