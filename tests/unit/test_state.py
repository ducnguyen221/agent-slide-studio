import json
from pathlib import Path

import pytest

from presentation_studio.state import RunConflict, RunLock, StateStore, hash_inputs


def test_run_lock_contains_identity_and_conflicts(tmp_path: Path) -> None:
    lock = RunLock.acquire(tmp_path, run_id="run-1")
    data = json.loads((tmp_path / "writer.lock").read_text(encoding="utf-8"))
    assert data["pid"] > 0 and data["started_at"] and data["run_id"] == "run-1"
    with pytest.raises(RunConflict):
        RunLock.acquire(tmp_path, run_id="run-2")
    lock.release()


def test_state_is_atomic_and_input_hash_is_stable(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    store.write({"revision": 1})
    assert store.read() == {"revision": 1}
    assert not list(tmp_path.glob("*.tmp"))
    assert hash_inputs({"b": 2, "a": 1}) == hash_inputs({"a": 1, "b": 2})

