from decimal import Decimal
from functools import cached_property
from urllib.parse import quote

from bitcoinrpc.authproxy import AuthServiceProxy

from audit.config import config, env


class BitcoinClient:
    def _proxy(self) -> AuthServiceProxy:
        cfg = config()["bitcoin"]["rpc"]
        user = quote(env("BITCOIN_RPC_USER"), safe="")
        password = quote(env("BITCOIN_RPC_PASSWORD"), safe="")
        scheme = cfg.get("scheme", "http")
        url = f"{scheme}://{user}:{password}@{cfg['ip']}:{cfg['port']}"
        return AuthServiceProxy(url, timeout=cfg["timeout"])

    @cached_property
    def _txoutsetinfo(self) -> dict:
        return self._proxy().gettxoutsetinfo()

    def get_block_height(self) -> int:
        return self._txoutsetinfo["height"]

    def get_total_amount(self) -> Decimal:
        return Decimal(str(self._txoutsetinfo["total_amount"]))

    def get_block_time(self, height: int) -> int:
        proxy = self._proxy()
        block_hash = proxy.getblockhash(height)
        return int(proxy.getblockheader(block_hash)["time"])
