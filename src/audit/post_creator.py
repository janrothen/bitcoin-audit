from decimal import Decimal


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
        if total == 0:
            return "0"
        return f"{total:,}".rstrip("0").rstrip(".")

    def create_post(self):
        return _TEMPLATE.format(
            height=self.height_current,
            total=f"{self.total_current:,}",
            increase_blocks=f"{self.block_height_increase_since_yesterday():,}",
            increase_total=self.total_increase_since_yesterday_formatted(),
        )


_TEMPLATE = """\
#Bitcoin block {height}

Increase since yesterday:
+{increase_blocks} blocks
+{increase_total} BTC

Total supply: {total} BTC\
"""
