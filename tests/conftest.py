from decimal import Decimal
from typing import override

import pytest

from audit.protocols import BitcoinClientProtocol, XClientProtocol


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("BITCOIN_RPC_USER", "test_user")
    monkeypatch.setenv("BITCOIN_RPC_PASSWORD", "test_password")
    monkeypatch.setenv("X_CONSUMER_KEY", "test_consumer_key")
    monkeypatch.setenv("X_CONSUMER_SECRET", "test_consumer_secret")
    monkeypatch.setenv("X_ACCESS_TOKEN", "test_access_token")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "test_access_token_secret")


class MockBitcoinClient(BitcoinClientProtocol):
    @override
    def get_block_height(self) -> int:
        return 942532

    @override
    def get_total_amount(self) -> Decimal:
        return Decimal("20007685.53030772")


class MockXClient(XClientProtocol):
    def __init__(self) -> None:
        self.posted: str | None = None

    @override
    def post(self, text: str) -> None:
        self.posted = text


@pytest.fixture
def bitcoin_client() -> MockBitcoinClient:
    return MockBitcoinClient()


@pytest.fixture
def x_client() -> MockXClient:
    return MockXClient()
