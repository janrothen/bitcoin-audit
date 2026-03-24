import json
from decimal import Decimal

from audit.audit_bot import AuditBot

EXPECTED_POST = """\
#Bitcoin block 942022

Increase since yesterday:
+144 blocks
+843.75 BTC

Total supply: 20,006,091.78041419 BTC\
"""


def test_bot_posts_and_saves_state(bitcoin_client, x_client, tmp_path):
    state_file = tmp_path / "state.json"
    state_file.write_text(json.dumps({
        "block_height": 941878,
        "total": "20005248.03041419",
    }))

    bot = AuditBot(bitcoin_client, x_client, state_file=state_file)
    bot.run()

    assert x_client.posted == EXPECTED_POST

    saved = json.loads(state_file.read_text())
    assert saved["block_height"] == 942022
    assert saved["total"] == "20006091.78041419"
