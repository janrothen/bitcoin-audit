import json
import logging
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from audit.config import config, project_root
from audit.post_creator import PostCreator
from audit.protocols import BitcoinClientProtocol, XClientProtocol

logger = logging.getLogger(__name__)


class AuditBot:
    """Orchestrates the daily Bitcoin audit run.

    Fetches the current block height and circulating supply from a Bitcoin node,
    compares them against the previous run's snapshot, posts the delta to X,
    and persists the new snapshot to state.json.

    On first run (no state file), it bootstraps by saving the current state
    without posting — the first post is made on the second run.
    """

    def __init__(
        self,
        bitcoin_client: BitcoinClientProtocol,
        x_client: XClientProtocol,
        state_file: Path | str | None = None,
    ) -> None:
        self.bitcoin_client = bitcoin_client
        self.x_client = x_client
        self.state_file = (
            Path(state_file)
            if state_file
            else project_root() / config()["state"]["file"]
        )
        self.current_block_height: int | None = None
        self.current_total: Decimal | None = None
        self.current_block_time: int | None = None
        self.previous_block_height: int | None = None
        self.previous_total: Decimal | None = None
        self.previous_block_time: int | None = None
        self.post: str | None = None

    def run(self) -> None:
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

    def _fetch_current(self) -> None:
        self.current_block_height = self.bitcoin_client.get_block_height()
        self.current_total = self.bitcoin_client.get_total_amount()
        self.current_block_time = self.bitcoin_client.get_block_time(
            self.current_block_height
        )

    def _fetch_previous(self) -> bool:
        """Load previous state. Returns True if bootstrapping (no state file existed)."""
        try:
            state = json.loads(self.state_file.read_text())
            self.previous_block_height = state["block_height"]
            self.previous_total = Decimal(state["total"])
            self.previous_block_time = int(state["block_time"])
        except FileNotFoundError:
            logger.warning(
                "No state file found at %s — bootstrapping. "
                "Current state saved; post will be made on next run.",
                self.state_file,
            )
            return True
        except (json.JSONDecodeError, KeyError, InvalidOperation, ValueError) as e:
            raise RuntimeError(f"Corrupt state file at {self.state_file}: {e}") from e
        return False

    def _post(self) -> None:
        assert self.current_block_height is not None
        assert self.current_block_time is not None
        assert self.current_total is not None
        assert self.previous_block_height is not None
        assert self.previous_block_time is not None
        assert self.previous_total is not None
        creator = PostCreator(
            self.current_block_height,
            self.current_block_time,
            self.current_total,
            self.previous_block_height,
            self.previous_block_time,
            self.previous_total,
        )
        self.post = creator.create_post()
        self.x_client.post(self.post)
        logger.info("Post created on X (block %d)", self.current_block_height)

    def _save_state(self) -> None:
        state = {
            "block_height": self.current_block_height,
            "block_time": self.current_block_time,
            "total": str(self.current_total),
        }
        # Write to a temp file first, then atomically replace the real state file.
        # os.replace() is POSIX-atomic: the old file is never left partially overwritten,
        # so a crash or disk-full error between post and save can't corrupt state.json.
        tmp = self.state_file.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(state))
            os.replace(tmp, self.state_file)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
