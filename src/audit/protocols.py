from decimal import Decimal
from typing import Protocol


class BitcoinClientProtocol(Protocol):
    def get_block_height(self) -> int: ...
    def get_total_amount(self) -> Decimal: ...


class XClientProtocol(Protocol):
    def post(self, text: str) -> None: ...
