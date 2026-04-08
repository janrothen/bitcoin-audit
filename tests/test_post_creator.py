from decimal import Decimal

import pytest

from audit.post_creator import PostCreator

EXPECTED_POST = """\
#Bitcoin block 942532

Δ since block 942377:
+155 blocks
+484.37498232 BTC

Total supply: 20,007,685.53030772 BTC
Mined: 95.27% of max supply\
"""


def test_create_post():
    creator = PostCreator(
        942532,
        Decimal("20007685.53030772"),
        942377,
        Decimal("20007201.15532540"),
    )
    assert creator.create_post() == EXPECTED_POST


@pytest.mark.parametrize(
    "current, previous, expected",
    [
        (Decimal("0"), Decimal("0"), "0.00000000"),
        (Decimal("10"), Decimal("9"), "1.00000000"),
        (Decimal("10.5"), Decimal("9.49999999"), "1.00000001"),
        (Decimal("10.50000000"), Decimal("9.40000000"), "1.10000000"),
        (Decimal("20007685.53030772"), Decimal("20007201.15532540"), "484.37498232"),
    ],
)
def test_total_increase_formatted(current, previous, expected):
    creator = PostCreator(0, current, 0, previous)
    assert creator.total_increase_since_previous_formatted() == expected


def test_block_height_increase():
    creator = PostCreator(
        942532, Decimal("20007685.53030772"), 942377, Decimal("20007201.15532540")
    )
    assert creator.block_height_increase_since_previous() == 155


def test_mined_percentage_formatted():
    creator = PostCreator(0, Decimal("19243704.10556611"), 0, Decimal("0"))
    assert creator.mined_percentage_formatted() == "91.63%"


def test_raises_on_negative_block_delta():
    with pytest.raises(ValueError, match="Block height decreased"):
        PostCreator(
            941878, Decimal("20006091.78041419"), 942022, Decimal("20005248.03041419")
        )


def test_raises_on_negative_total_delta():
    with pytest.raises(ValueError, match="Total supply decreased"):
        PostCreator(
            942022, Decimal("20005248.03041419"), 941878, Decimal("20006091.78041419")
        )
