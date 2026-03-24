import pytest
from decimal import Decimal


@pytest.fixture(autouse=True)
def env_vars(monkeypatch):
    monkeypatch.setenv("BITCOIN_RPC_USER", "test_user")
    monkeypatch.setenv("BITCOIN_RPC_PASSWORD", "test_password")
    monkeypatch.setenv("X_CONSUMER_KEY", "test_consumer_key")
    monkeypatch.setenv("X_CONSUMER_SECRET", "test_consumer_secret")
    monkeypatch.setenv("X_ACCESS_TOKEN", "test_access_token")
    monkeypatch.setenv("X_ACCESS_TOKEN_SECRET", "test_access_token_secret")


class MockBitcoinClient:
    def get_block_height(self):
        return 942022

    def get_total_amount(self):
        return Decimal("20006091.78041419")


class MockXClient:
    def __init__(self):
        self.posted = None

    def post(self, text):
        self.posted = text


@pytest.fixture
def bitcoin_client():
    return MockBitcoinClient()


@pytest.fixture
def x_client():
    return MockXClient()
