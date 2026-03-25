from decimal import Decimal, ROUND_DOWN

THEORETICAL_MAX = Decimal("20999999.97690000")


class PostCreator:
    def __init__(self, height_current, total_current, height_yesterday, total_yesterday):
        self.height_current = height_current
        self.height_yesterday = height_yesterday
        self.total_current = total_current
        self.total_yesterday = total_yesterday

    def block_height_increase_since_yesterday(self):
        return self.height_current - self.height_yesterday

    def total_increase_since_yesterday(self):
        return self.total_current - self.total_yesterday

    def total_increase_since_yesterday_formatted(self):
        total = self.total_increase_since_yesterday()
        return f"{total:,.8f}"

    def mined_percentage(self):
        pct = (self.total_current / THEORETICAL_MAX * 100).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        return f"{pct}"

    def create_post(self):
        return _TEMPLATE.format(
            height=self.height_current,
            height_yesterday=self.height_yesterday,
            total=f"{self.total_current:,.8f}",
            increase_blocks=f"{self.block_height_increase_since_yesterday():,}",
            increase_total=self.total_increase_since_yesterday_formatted(),
            mined=self.mined_percentage(),
        )


_TEMPLATE = """\
#Bitcoin block {height}
Δ since block {height_yesterday}:
+{increase_blocks} blocks
+{increase_total} BTC

Total supply:    {total} BTC
Theoretical max: 20,999,999.97690000 BTC
Mined:           {mined}% of max supply\
"""
