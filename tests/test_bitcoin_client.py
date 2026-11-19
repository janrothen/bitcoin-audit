import json
from decimal import Decimal

import pytest
import requests

from audit.clients.bitcoin_client import BitcoinClient, BitcoinRPCError

# Raw JSON text, as the node sends it, so Decimal parsing is exercised for real.
TXOUTSETINFO_BODY = (
    '{"result": {"height": 942022, "total_amount": 20006091.78041419},'
    ' "error": null, "id": 1}'
)


def _response(status: int, body: str, url: str = "http://node/") -> requests.Response:
    resp = requests.Response()
    resp.status_code = status
    resp._content = body.encode()
    resp.url = url
    resp.reason = {200: "OK", 401: "Unauthorized", 500: "Internal Server Error"}.get(
        status, ""
    )
    return resp


class FakeSession(requests.Session):
    """Records calls and returns canned responses keyed by RPC method."""

    def __init__(self, responses: dict[str, requests.Response]) -> None:
        super().__init__()
        self.responses = responses
        self.calls: list[dict] = []

    def post(self, url, json=None, **kwargs):  # noqa: A002 - mirrors requests API
        self.calls.append({"url": url, "json": json, **kwargs})
        return self.responses[json["method"]]


@pytest.fixture
def make_client(monkeypatch):
    def _make(responses: dict[str, requests.Response]):
        session = FakeSession(responses)
        monkeypatch.setattr(
            "audit.clients.bitcoin_client.requests.Session", lambda: session
        )
        return BitcoinClient(), session

    return _make


@pytest.fixture
def client(make_client):
    return make_client({"gettxoutsetinfo": _response(200, TXOUTSETINFO_BODY)})


def test_get_block_height(client):
    bitcoin_client, _ = client
    assert bitcoin_client.get_block_height() == 942022


def test_get_total_amount_is_exact_decimal(client):
    bitcoin_client, _ = client
    total = bitcoin_client.get_total_amount()
    assert isinstance(total, Decimal)
    assert total == Decimal("20006091.78041419")


def test_rpc_called_once(client):
    bitcoin_client, session = client
    bitcoin_client.get_block_height()
    bitcoin_client.get_block_height()
    bitcoin_client.get_total_amount()
    bitcoin_client.get_total_amount()
    assert [c["json"]["method"] for c in session.calls] == ["gettxoutsetinfo"]


def test_credentials_use_basic_auth_not_url(client):
    bitcoin_client, session = client
    bitcoin_client.get_block_height()
    call = session.calls[0]
    assert session.auth == ("test_user", "test_password")
    assert "test_user" not in call["url"]
    assert "test_password" not in call["url"]
    assert call["url"] == "http://192.168.2.100:8332/"


def test_request_shape(client):
    bitcoin_client, session = client
    bitcoin_client.get_block_height()
    call = session.calls[0]
    assert call["json"]["method"] == "gettxoutsetinfo"
    assert call["json"]["params"] == []
    assert call["timeout"] == 900
    assert call["allow_redirects"] is False


def test_get_block_time(make_client):
    bitcoin_client, session = make_client(
        {
            "getblockhash": _response(200, '{"result": "00abc", "error": null}'),
            "getblockheader": _response(
                200, '{"result": {"time": 1700086512}, "error": null}'
            ),
        }
    )
    assert bitcoin_client.get_block_time(942022) == 1_700_086_512
    assert session.calls[0]["json"]["params"] == [942022]
    assert session.calls[1]["json"]["params"] == ["00abc"]


def test_rpc_error_raises(make_client):
    body = json.dumps(
        {"result": None, "error": {"code": -8, "message": "Block height out of range"}}
    )
    bitcoin_client, _ = make_client({"getblockhash": _response(500, body)})
    with pytest.raises(BitcoinRPCError, match="Block height out of range") as exc:
        bitcoin_client.get_block_time(10**9)
    assert exc.value.code == -8


def test_http_401_raises_without_leaking_credentials(make_client):
    bitcoin_client, _ = make_client({"gettxoutsetinfo": _response(401, "")})
    with pytest.raises(requests.HTTPError, match="401") as exc:
        bitcoin_client.get_block_height()
    assert "test_password" not in str(exc.value)


def test_malformed_response_raises(make_client):
    bitcoin_client, _ = make_client({"gettxoutsetinfo": _response(200, "[]")})
    with pytest.raises(BitcoinRPCError, match="malformed"):
        bitcoin_client.get_block_height()
