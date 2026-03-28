from decimal import ROUND_DOWN, Decimal

type BTCAmount = Decimal

THEORETICAL_MAX: BTCAmount = Decimal("20999999.97690000")


def _format_btc(amount: BTCAmount) -> str:
    """Format a BTC amount with comma thousands separator and 8 decimal places."""
    return f"{amount:,.8f}"


class PostCreator:
    """Composes the text for a daily Bitcoin audit post.

    Given the current and previous block height and circulating supply,
    calculates the deltas and formats them into a ready-to-post string.
    Raises ValueError if the block height or total supply would decrease
    between runs, which indicates corrupt or out-of-order state.
    """

    height_current: int
    height_previous: int
    total_current: BTCAmount
    total_previous: BTCAmount

    def __init__(
        self,
        height_current: int,
        total_current: BTCAmount,
        height_previous: int,
        total_previous: BTCAmount,
    ) -> None:
        self.height_current = height_current
        self.height_previous = height_previous
        self.total_current = total_current
        self.total_previous = total_previous

    def block_height_increase_since_previous(self) -> int:
        return self.height_current - self.height_previous

    def total_increase_since_previous(self) -> BTCAmount:
        return self.total_current - self.total_previous

    def total_increase_since_previous_formatted(self) -> str:
        return _format_btc(self.total_increase_since_previous())

    def mined_percentage(self) -> str:
        pct = (self.total_current / THEORETICAL_MAX * 100).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )
        return f"{pct}"

    def create_post(self) -> str:
        if self.block_height_increase_since_previous() < 0:
            raise ValueError(
                f"Block height decreased: {self.height_previous} -> {self.height_current}"
            )
        if self.total_increase_since_previous() < 0:
            raise ValueError(
                f"Total supply decreased: {self.total_previous} -> {self.total_current}"
            )
        return _TEMPLATE.format(
            height=self.height_current,
            height_previous=self.height_previous,
            total=_format_btc(self.total_current),
            increase_blocks=f"{self.block_height_increase_since_previous():,}",
            increase_total=self.total_increase_since_previous_formatted(),
            mined=self.mined_percentage(),
        )


_TEMPLATE = """\
#Bitcoin block {height}

Δ since block {height_previous}:
+{increase_blocks} blocks
+{increase_total} BTC

Total supply: {total} BTC
Mined: {mined}% of max supply\
"""
