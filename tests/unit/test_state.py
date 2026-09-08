import json
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess

import pytest

from presentation_studio.state import (
    MissingState,
    RunConflict,
    RunLock,
    StateConflict,
    StatePathError,
    StateStore,
    atomic_json,
    hash_inputs,
)


def test_run_lock_contains_full_identity_and_conflicts(tmp_path: Path) -> None:
    lock = RunLock.acquire(tmp_path, run_id="run-1")
    data = json.loads((tmp_path / "writer.lock").read_text(encoding="utf-8"))
    assert data == lock.identity
    assert data["pid"] > 0
    assert data["started_at"]
    assert data["token"]
    with pytest.raises(RunConflict):
        RunLock.acquire(tmp_path, run_id="run-2")
    lock.release()


def test_atomic_json_uses_unique_temps_for_same_process_threads(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda value: atomic_json(path, {"value": value}), range(64)))
    assert json.loads(path.read_text(encoding="utf-8"))["value"] in range(64)
    assert not list(tmp_path.glob("*.tmp"))


def test_state_distinguishes_absent_from_required_missing(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    assert store.read() is None
    with pytest.raises(MissingState):
        store.read(required=True)


def test_state_transition_requires_verified_lock_revision_and_hash(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    lock = RunLock.acquire(tmp_path, run_id="r1")
    first = store.transition(
        lock, expected_revision=None, input_hash="a" * 64, status="started"
    )
    assert first["revision"] == 1
    with pytest.raises(StateConflict):
        store.transition(
            lock, expected_revision=0, input_hash="a" * 64, status="ended"
        )
    with pytest.raises(StateConflict):
        store.transition(
            lock, expected_revision=1, input_hash="b" * 64, status="ended"
        )
    ended = store.transition(
        lock, expected_revision=1, input_hash="a" * 64, status="ended"
    )
    assert ended["revision"] == 2
    events = [
        json.loads(line)
        for line in (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [event["status"] for event in events] == ["started", "ended"]
    lock.release()


def test_state_transition_rejects_changed_lock_owner(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    lock = RunLock.acquire(tmp_path, run_id="r1")
    changed = {**lock.identity, "token": "another-token"}
    atomic_json(tmp_path / "writer.lock", changed)
    with pytest.raises(RunConflict):
        store.transition(
            lock, expected_revision=None, input_hash="a" * 64, status="started"
        )


def test_lock_release_detects_missing_or_changed_owner_without_deleting_new_lock(
    tmp_path: Path,
) -> None:
    lock = RunLock.acquire(tmp_path, run_id="r1")
    (tmp_path / "writer.lock").unlink()
    with pytest.raises(RunConflict):
        lock.release()

    replacement = RunLock.acquire(tmp_path, run_id="r2")
    with pytest.raises(RunConflict):
        lock.release()
    assert json.loads((tmp_path / "writer.lock").read_text(encoding="utf-8")) == replacement.identity
    replacement.release()


def test_explicit_recovery_records_aborted_event_and_requires_expected_identity(
    tmp_path: Path,
) -> None:
    lock = RunLock.acquire(tmp_path, run_id="r1")
    with pytest.raises(RunConflict):
        RunLock.recover(
            tmp_path,
            expected_identity={**lock.identity, "token": "wrong"},
            reason="stale",
        )
    assert (tmp_path / "writer.lock").exists()
    RunLock.recover(
        tmp_path,
        expected_identity=lock.identity,
        reason="operator-confirmed-stale",
    )
    assert not (tmp_path / "writer.lock").exists()
    event = json.loads((tmp_path / "events.jsonl").read_text(encoding="utf-8"))
    assert event["status"] == "aborted"
    assert event["run_id"] == "r1"


def test_hash_inputs_is_stable() -> None:
    assert hash_inputs({"b": 2, "a": 1}) == hash_inputs({"a": 1, "b": 2})


@pytest.mark.skipif(os.name != "nt", reason="Windows junction behavior")
def test_state_write_rechecks_junction_containment(tmp_path: Path) -> None:
    project = tmp_path / "project"
    state_dir = project / ".presentation"
    outside = tmp_path / "outside"
    project.mkdir()
    outside.mkdir()
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(state_dir), str(outside)],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("junction creation unavailable")
    try:
        with pytest.raises(StatePathError):
            StateStore(state_dir).write({"revision": 1})
        assert not (outside / "state.json").exists()
    finally:
        os.rmdir(state_dir)
