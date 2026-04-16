from decimal import ROUND_DOWN, Decimal

type BTCAmount = Decimal

THEORETICAL_MAX: BTCAmount = Decimal("20999999.97690000")


def _format_btc(amount: BTCAmount) -> str:
    """Format a BTC amount with comma thousands separator and 8 decimal places."""
    return f"{amount:,.8f}"


def _format_duration(seconds: int) -> str:
    """Format a non-negative second count as `Xhrs Ymin Zsec`, switching to
    `Nday[s] Xhrs Ymin Zsec` once the duration reaches 25 hours. The 25-hour
    threshold (rather than 24h) keeps routine daily runs that drift slightly
    past 24h in the simpler hours-only form instead of showing `1day 0hrs …`.
    """
    if seconds < 25 * 3600:
        hrs, rem = divmod(seconds, 3600)
        minutes, sec = divmod(rem, 60)
        return f"{hrs}hrs {minutes}min {sec}sec"
    days, rem = divmod(seconds, 86400)
    hrs, rem = divmod(rem, 3600)
    minutes, sec = divmod(rem, 60)
    unit = "day" if days == 1 else "days"
    return f"{days}{unit} {hrs}hrs {minutes}min {sec}sec"


class PostCreator:
    """Composes the text for a daily Bitcoin audit post.

    Given the current and previous block height, circulating supply, and
    block timestamps, calculates the deltas and formats them into a
    ready-to-post string. Raises ValueError on construction if any of those
    would decrease between runs, which indicates corrupt or out-of-order state.
    """

    def __init__(
        self,
        height_current: int,
        block_time_current: int,
        total_current: BTCAmount,
        height_previous: int,
        block_time_previous: int,
        total_previous: BTCAmount,
    ) -> None:
        if height_current < height_previous:
            raise ValueError(
                f"Block height decreased: {height_previous} -> {height_current}"
            )
        if block_time_current < block_time_previous:
            raise ValueError(
                f"Block time decreased: {block_time_previous} -> {block_time_current}"
            )
        if total_current < total_previous:
            raise ValueError(
                f"Total supply decreased: {total_previous} -> {total_current}"
            )
        self.height_current = height_current
        self.height_previous = height_previous
        self.block_time_current = block_time_current
        self.block_time_previous = block_time_previous
        self.total_current = total_current
        self.total_previous = total_previous

    def block_height_increase_since_previous(self) -> int:
        return self.height_current - self.height_previous

    def total_increase_since_previous(self) -> BTCAmount:
        return self.total_current - self.total_previous

    def total_increase_since_previous_formatted(self) -> str:
        return _format_btc(self.total_increase_since_previous())

    def mined_percentage_formatted(self) -> str:
        pct = (self.total_current / THEORETICAL_MAX * 100).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )
        return f"{pct}%"

    def create_post(self) -> str:
        time_elapsed = _format_duration(
            self.block_time_current - self.block_time_previous
        )
        return _TEMPLATE.format(
            height=self.height_current,
            height_previous=self.height_previous,
            total=_format_btc(self.total_current),
            time_elapsed=time_elapsed,
            increase_blocks=f"{self.block_height_increase_since_previous():,}",
            increase_total=self.total_increase_since_previous_formatted(),
            mined=self.mined_percentage_formatted(),
        )


_TEMPLATE = """\
#Bitcoin block {height}

Δ since block {height_previous}:
+{time_elapsed}
+{increase_blocks} blocks
+{increase_total} BTC

Total supply: {total} BTC
Mined: {mined} of max supply\
"""
