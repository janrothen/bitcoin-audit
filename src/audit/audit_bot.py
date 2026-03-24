import json
from decimal import Decimal
from pathlib import Path

from audit.config import config, project_root
from audit.post_creator import PostCreator

_state_path = project_root() / config()["state"]["file"]


class AuditBot:
    def __init__(self, bitcoin_client, x_client, state_file=None):
        self.bitcoin_client = bitcoin_client
        self.x_client = x_client
        self.state_file = Path(state_file) if state_file else _state_path

    def run(self):
        self._fetch_current()
        self._fetch_yesterday()
        self._post()
        self._save_state()

    def _fetch_current(self):
        self.current_block_height = self.bitcoin_client.get_block_height()
        self.current_total = self.bitcoin_client.get_total_amount()

    def _fetch_yesterday(self):
        state = json.loads(self.state_file.read_text())
        self.yesterdays_block_height = state["block_height"]
        self.yesterdays_total = Decimal(state["total"])

    def _post(self):
        creator = PostCreator(
            self.current_block_height,
            self.current_total,
            self.yesterdays_block_height,
            self.yesterdays_total,
        )
        self.post = creator.create_post()
        self.x_client.post(self.post)

    def _save_state(self):
        state = {
            "block_height": self.current_block_height,
            "total": str(self.current_total),
        }
        self.state_file.write_text(json.dumps(state))
