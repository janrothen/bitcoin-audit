from decimal import Decimal

import pytest

from audit.post_creator import PostCreator, _format_duration

EXPECTED_POST = """\
#Bitcoin block 942532

Δ since block 942377:
+23hrs 59min 12sec
+155 blocks
+484.37498232 BTC

Total supply: 20,007,685.53030772 BTC
Mined: 95.27% of max supply\
"""


def test_create_post():
    creator = PostCreator(
        942532,
        Decimal("20007685.53030772"),
        1_700_086_512,
        942377,
        Decimal("20007201.15532540"),
        1_700_000_160,
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
    creator = PostCreator(0, current, 0, 0, previous, 0)
    assert creator.total_increase_since_previous_formatted() == expected


def test_block_height_increase():
    creator = PostCreator(
        942532,
        Decimal("20007685.53030772"),
        0,
        942377,
        Decimal("20007201.15532540"),
        0,
    )
    assert creator.block_height_increase_since_previous() == 155


def test_mined_percentage_formatted():
    creator = PostCreator(0, Decimal("19243704.10556611"), 0, 0, Decimal("0"), 0)
    assert creator.mined_percentage_formatted() == "91.63%"


def test_raises_on_negative_block_delta():
    with pytest.raises(ValueError, match="Block height decreased"):
        PostCreator(
            941878,
            Decimal("20006091.78041419"),
            0,
            942022,
            Decimal("20005248.03041419"),
            0,
        )


def test_raises_on_negative_total_delta():
    with pytest.raises(ValueError, match="Total supply decreased"):
        PostCreator(
            942022,
            Decimal("20005248.03041419"),
            0,
            941878,
            Decimal("20006091.78041419"),
            0,
        )


def test_raises_on_negative_time_delta():
    with pytest.raises(ValueError, match="Block time decreased"):
        PostCreator(
            942532,
            Decimal("20007685.53030772"),
            1_700_000_000,
            942377,
            Decimal("20007201.15532540"),
            1_700_086_400,
        )


@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "0hrs 0min 0sec"),
        (45, "0hrs 0min 45sec"),
        (3600, "1hrs 0min 0sec"),
        (86_352, "23hrs 59min 12sec"),
        (88_620, "24hrs 37min 0sec"),
        (25 * 3600 - 1, "24hrs 59min 59sec"),
        (25 * 3600, "1day 1hrs 0min 0sec"),
        (90_794, "1day 1hrs 13min 14sec"),
        (48 * 3600, "2days 0hrs 0min 0sec"),
        (208_800, "2days 10hrs 0min 0sec"),
        (209_093, "2days 10hrs 4min 53sec"),
    ],
)
def test_format_duration(seconds, expected):
    assert _format_duration(seconds) == expected
