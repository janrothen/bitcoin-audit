from decimal import Decimal
from unittest.mock import patch

import pytest

from audit.clients.bitcoin_client import BitcoinClient

MOCK_TXOUTSETINFO = {
    "height": 942022,
    "total_amount": Decimal("20006091.78041419"),
}


@pytest.fixture
def client():
    with patch("audit.clients.bitcoin_client.AuthServiceProxy") as mock_proxy:
        mock_proxy.return_value.gettxoutsetinfo.return_value = MOCK_TXOUTSETINFO
        yield BitcoinClient(), mock_proxy


def test_get_block_height(client):
    bitcoin_client, _ = client
    assert bitcoin_client.get_block_height() == 942022


def test_get_total_amount(client):
    bitcoin_client, _ = client
    assert bitcoin_client.get_total_amount() == Decimal("20006091.78041419")


def test_rpc_called_once(client):
    bitcoin_client, mock_proxy = client
    bitcoin_client.get_block_height()
    bitcoin_client.get_total_amount()
    mock_proxy.return_value.gettxoutsetinfo.assert_called_once()
