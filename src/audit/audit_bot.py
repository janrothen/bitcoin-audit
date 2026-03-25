import json
import logging
import os
from decimal import Decimal
from pathlib import Path

from audit.config import config, project_root
from audit.post_creator import PostCreator

logger = logging.getLogger(__name__)

_state_path = project_root() / config()["state"]["file"]


class AuditBot:
    def __init__(self, bitcoin_client, x_client, state_file=None):
        self.bitcoin_client = bitcoin_client
        self.x_client = x_client
        self.state_file = Path(state_file) if state_file else _state_path

    def run(self):
        try:
            self._fetch_current()
            bootstrapped = self._fetch_previous()
            if bootstrapped:
                self._save_state()
            else:
                self._post()
                self._save_state()
        except Exception:
            logger.exception("Audit run failed")
            raise

    def _fetch_current(self):
        self.current_block_height = self.bitcoin_client.get_block_height()
        self.current_total = self.bitcoin_client.get_total_amount()

    def _fetch_previous(self):
        """Load previous state. Returns True if bootstrapping (no state file existed)."""
        try:
            state = json.loads(self.state_file.read_text())
        except FileNotFoundError:
            logger.warning(
                "No state file found at %s — bootstrapping. "
                "Current state saved; post will be made on next run.",
                self.state_file,
            )
            return True
        self.previous_block_height = state["block_height"]
        self.previous_total = Decimal(state["total"])
        return False

    def _post(self):
        creator = PostCreator(
            self.current_block_height,
            self.current_total,
            self.previous_block_height,
            self.previous_total,
        )
        self.post = creator.create_post()
        self.x_client.post(self.post)
        logger.info("Posted:\n%s", self.post)

    def _save_state(self):
        state = {
            "block_height": self.current_block_height,
            "total": str(self.current_total),
        }
        # Write to a temp file first, then atomically replace the real state file.
        # os.replace() is POSIX-atomic: the old file is never left partially overwritten,
        # so a crash or disk-full error between post and save can't corrupt state.json.
        tmp = self.state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state))
        os.replace(tmp, self.state_file)
