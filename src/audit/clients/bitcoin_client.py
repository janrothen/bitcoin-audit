from decimal import Decimal
from functools import cached_property
from itertools import count
from typing import Any

import requests

from audit.config import config, env


class BitcoinRPCError(RuntimeError):
    """The node answered with a JSON-RPC error object."""

    def __init__(self, method: str, error: dict) -> None:
        self.code = error.get("code")
        self.rpc_message = error.get("message")
        super().__init__(f"RPC {method} failed ({self.code}): {self.rpc_message}")


class BitcoinClient:
    """Minimal JSON-RPC client for a local Bitcoin Core node.

    Credentials are sent via HTTP Basic auth and never embedded in the URL,
    so they cannot leak through exception messages or logs. JSON numbers are
    parsed as Decimal so BTC amounts stay exact.
    """

    def __init__(self) -> None:
        self._ids = count(1)

    @cached_property
    def _session(self) -> requests.Session:
        session = requests.Session()
        session.auth = (env("BITCOIN_RPC_USER"), env("BITCOIN_RPC_PASSWORD"))
        session.headers["Content-Type"] = "application/json"
        return session

    @cached_property
    def _url(self) -> str:
        cfg = config()["bitcoin"]["rpc"]
        scheme = cfg.get("scheme", "http")
        return f"{scheme}://{cfg['ip']}:{cfg['port']}/"

    @cached_property
    def _timeout(self) -> float:
        return config()["bitcoin"]["rpc"]["timeout"]

    def _call(self, method: str, *params: Any) -> Any:
        payload = {
            "jsonrpc": "1.0",
            "id": next(self._ids),
            "method": method,
            "params": list(params),
        }
        response = self._session.post(
            self._url,
            json=payload,
            timeout=self._timeout,
            allow_redirects=False,
        )
        # Bitcoin Core reports RPC errors with a non-2xx status *and* a JSON
        # body; prefer the body's error so the message is useful. Auth
        # failures (401) have an empty body and fall through to
        # raise_for_status.
        try:
            body = response.json(parse_float=Decimal)
        except ValueError:
            body = None
        if isinstance(body, dict) and body.get("error"):
            raise BitcoinRPCError(method, body["error"])
        response.raise_for_status()
        if not isinstance(body, dict) or "result" not in body:
            raise BitcoinRPCError(
                method, {"code": None, "message": "malformed JSON-RPC response"}
            )
        return body["result"]

    @cached_property
    def _txoutsetinfo(self) -> dict:
        return self._call("gettxoutsetinfo")

    def get_block_height(self) -> int:
        return self._txoutsetinfo["height"]

    def get_total_amount(self) -> Decimal:
        return Decimal(str(self._txoutsetinfo["total_amount"]))

    def get_block_time(self, height: int) -> int:
        block_hash = self._call("getblockhash", height)
        return int(self._call("getblockheader", block_hash)["time"])
