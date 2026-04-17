from decimal import ROUND_DOWN, Decimal

from audit.state import State

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
    if seconds < 0:
        raise ValueError(f"seconds must be non-negative, got {seconds}")
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

    Given snapshots of the current and previous run, calculates the deltas in
    block height, circulating supply, and block timestamp, and formats them
    into a ready-to-post string. Raises ValueError on construction if any of
    those would decrease between runs, which indicates corrupt or out-of-order
    state.
    """

    def __init__(self, current: State, previous: State) -> None:
        if current.block_height < previous.block_height:
            raise ValueError(
                f"Block height decreased: "
                f"{previous.block_height} -> {current.block_height}"
            )
        if current.block_time < previous.block_time:
            raise ValueError(
                f"Block time decreased: {previous.block_time} -> {current.block_time}"
            )
        if current.total < previous.total:
            raise ValueError(
                f"Total supply decreased: {previous.total} -> {current.total}"
            )
        self.current = current
        self.previous = previous

    def block_height_increase_since_previous(self) -> int:
        return self.current.block_height - self.previous.block_height

    def total_increase_since_previous(self) -> BTCAmount:
        return self.current.total - self.previous.total

    def total_increase_since_previous_formatted(self) -> str:
        return _format_btc(self.total_increase_since_previous())

    def mined_percentage_formatted(self) -> str:
        pct = (self.current.total / THEORETICAL_MAX * 100).quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        )
        return f"{pct}%"

    def create_post(self) -> str:
        time_elapsed = _format_duration(
            self.current.block_time - self.previous.block_time
        )
        return _TEMPLATE.format(
            height=self.current.block_height,
            height_previous=self.previous.block_height,
            total=_format_btc(self.current.total),
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
