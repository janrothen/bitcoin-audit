import json
import logging
import os
from decimal import InvalidOperation
from pathlib import Path

from audit.config import config, project_root
from audit.post_creator import PostCreator
from audit.protocols import BitcoinClientProtocol, XClientProtocol
from audit.state import State

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

    def run(self) -> None:
        current = self._fetch_current()
        previous = self._fetch_previous()
        if previous is not None:
            self._post(current, previous)
        self._save_state(current)

    def _fetch_current(self) -> State:
        height = self.bitcoin_client.get_block_height()
        return State(
            block_height=height,
            block_time=self.bitcoin_client.get_block_time(height),
            total=self.bitcoin_client.get_total_amount(),
        )

    def _fetch_previous(self) -> State | None:
        """Load previous state. Returns None when no state file exists (bootstrap)."""
        try:
            data = json.loads(self.state_file.read_text())
            return State.from_dict(data)
        except FileNotFoundError:
            logger.warning(
                "No state file found at %s — bootstrapping. "
                "Current state saved; post will be made on next run.",
                self.state_file,
            )
            return None
        except (KeyError, InvalidOperation, ValueError) as e:
            raise RuntimeError(f"Corrupt state file at {self.state_file}: {e}") from e

    def _post(self, current: State, previous: State) -> None:
        creator = PostCreator(current, previous)
        self.x_client.post(creator.create_post())
        logger.info("Post created on X (block %d)", current.block_height)

    def _save_state(self, state: State) -> None:
        # Durable atomic write on a Pi that can lose power mid-run:
        #   - fsync(tmp) so os.replace swaps in content that's on disk, not just
        #     in the page cache.
        #   - os.replace is metadata-atomic, so state.json is never torn.
        #   - fsync(parent dir) so the rename itself survives a power cut —
        #     otherwise the directory entry can come back empty.
        tmp = self.state_file.with_suffix(".tmp")
        payload = json.dumps(state.to_dict())
        try:
            with open(tmp, "w") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self.state_file)
            dir_fd = os.open(self.state_file.parent, os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
