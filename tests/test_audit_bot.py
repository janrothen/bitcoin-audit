import json

import pytest

from audit.audit_bot import AuditBot

EXPECTED_POST = """\
#Bitcoin block 942532

Δ since block 942377:
+155 blocks
+484.37498232 BTC

Total supply: 20,007,685.53030772 BTC
Mined: 95.27% of max supply\
"""


def test_bot_posts_and_saves_state(bitcoin_client, x_client, tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text(
        json.dumps(
            {
                "block_height": 942377,
                "total": "20007201.15532540",
            }
        )
    )

    bot = AuditBot(bitcoin_client, x_client, state_file=state_file)
    bot.run()

    assert x_client.posted == EXPECTED_POST

    saved = json.loads(state_file.read_text())
    assert saved["block_height"] == 942532
    assert saved["total"] == "20007685.53030772"


def test_bot_bootstraps_when_no_state_file(bitcoin_client, x_client, tmp_path):
    state_file = tmp_path / "state.json"  # intentionally not created

    bot = AuditBot(bitcoin_client, x_client, state_file=state_file)
    bot.run()

    assert x_client.posted is None  # no post on first run

    saved = json.loads(state_file.read_text())
    assert saved["block_height"] == 942532
    assert saved["total"] == "20007685.53030772"


def test_state_not_saved_on_post_failure(bitcoin_client, x_client, tmp_path):
    state_file = tmp_path / "state.json"
    original = {"block_height": 942377, "total": "20007201.15532540"}
    state_file.write_text(json.dumps(original))

    def raise_error(text):
        raise RuntimeError("X API error")

    x_client.post = raise_error

    bot = AuditBot(bitcoin_client, x_client, state_file=state_file)
    with pytest.raises(RuntimeError):
        bot.run()

    assert json.loads(state_file.read_text()) == original


@pytest.mark.parametrize(
    "content",
    [
        "not json",
        '{"block_height": 942377}',  # missing "total" key
        '{"block_height": 942377, "total": "not-a-decimal"}',
    ],
)
def test_corrupt_state_file_raises(bitcoin_client, x_client, tmp_path, content):
    state_file = tmp_path / "state.json"
    state_file.write_text(content)

    bot = AuditBot(bitcoin_client, x_client, state_file=state_file)
    with pytest.raises(RuntimeError, match="Corrupt state file"):
        bot.run()


def test_no_tmp_file_left_after_successful_run(bitcoin_client, x_client, tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text(
        json.dumps({"block_height": 942377, "total": "20007201.15532540"})
    )

    bot = AuditBot(bitcoin_client, x_client, state_file=state_file)
    bot.run()

    assert not state_file.with_suffix(".tmp").exists()
