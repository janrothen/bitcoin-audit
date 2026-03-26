from decimal import Decimal
from functools import cached_property

from bitcoinrpc.authproxy import AuthServiceProxy

from audit.config import config, env


class BitcoinClient:
    @cached_property
    def _txoutsetinfo(self) -> dict:
        cfg = config()["bitcoin"]["rpc"]
        url = f'http://{env("BITCOIN_RPC_USER")}:{env("BITCOIN_RPC_PASSWORD")}@{cfg["ip"]}:{cfg["port"]}'
        return AuthServiceProxy(url, timeout=cfg["timeout"]).gettxoutsetinfo()

    def get_block_height(self) -> int:
        return self._txoutsetinfo["height"]

    def get_total_amount(self) -> Decimal:
        return self._txoutsetinfo["total_amount"]
