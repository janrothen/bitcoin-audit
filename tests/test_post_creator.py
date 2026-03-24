from decimal import Decimal

import pytest

from audit.post_creator import PostCreator

EXPECTED_POST = """\
#Bitcoin block 942022

Increase since yesterday:
+144 blocks
+843.75 BTC

Total supply: 20,006,091.78041419 BTC\
"""


def test_create_post():
    creator = PostCreator(
        942022,
        Decimal("20006091.78041419"),
        941878,
        Decimal("20005248.03041419"),
    )
    assert creator.create_post() == EXPECTED_POST


@pytest.mark.parametrize("current, yesterday, expected", [
    (Decimal("0"),               Decimal("0"),               "0"),
    (Decimal("10"),              Decimal("9"),               "1"),
    (Decimal("10.5"),            Decimal("9.49999999"),      "1.00000001"),
    (Decimal("10.50000000"),     Decimal("9.40000000"),      "1.1"),
    (Decimal("20006091.78041419"), Decimal("20005248.03041419"), "843.75"),
])
def test_total_increase_formatted(current, yesterday, expected):
    creator = PostCreator(0, current, 0, yesterday)
    assert creator.total_increase_since_yesterday_formatted() == expected


def test_block_height_increase():
    creator = PostCreator(942022, Decimal("20006091.78041419"), 941878, Decimal("20005248.03041419"))
    assert creator.block_height_increase_since_yesterday() == 144
