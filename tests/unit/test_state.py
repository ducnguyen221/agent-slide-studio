import json
from concurrent.futures import ThreadPoolExecutor
import os
from pathlib import Path
import subprocess
from threading import Event

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
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="run-1")
    data = json.loads((tmp_path / "writer.lock").read_text(encoding="utf-8"))
    assert data == lock.identity
    assert data["pid"] > 0
    assert data["started_at"]
    assert data["token"]
    with pytest.raises(RunConflict):
        RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="run-2")
    lock.release()


def test_atomic_json_uses_unique_temps_for_same_process_threads(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda value: atomic_json(path, {"value": value}), range(64)))
    assert json.loads(path.read_text(encoding="utf-8"))["value"] in range(64)
    assert not list(tmp_path.glob("*.tmp"))


def test_state_distinguishes_absent_from_required_missing(tmp_path: Path) -> None:
    store = StateStore(tmp_path, workspace_root=tmp_path)
    assert store.read() is None
    with pytest.raises(MissingState):
        store.read(required=True)


def test_bootstrap_is_one_time_and_refuses_an_active_writer(tmp_path: Path) -> None:
    store = StateStore(tmp_path, workspace_root=tmp_path)
    assert not hasattr(store, "write")
    store.bootstrap({"revision": 0})
    with pytest.raises(StateConflict):
        store.bootstrap({"revision": 1})

    other = tmp_path / "other"
    other.mkdir()
    locked_store = StateStore(other, workspace_root=tmp_path)
    lock = RunLock.acquire(other, workspace_root=tmp_path, run_id="r1")
    try:
        with pytest.raises(RunConflict):
            locked_store.bootstrap({"revision": 0})
    finally:
        lock.release()


def test_two_store_instances_cannot_commit_the_same_revision(tmp_path: Path) -> None:
    first_store = StateStore(tmp_path, workspace_root=tmp_path)
    second_store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    first_store.transition(
        lock, expected_revision=None, input_hash="a" * 64, status="started"
    )

    def end(store: StateStore) -> str:
        try:
            store.transition(
                lock, expected_revision=1, input_hash="a" * 64, status="ended"
            )
            return "committed"
        except StateConflict:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(end, (first_store, second_store)))
    assert sorted(outcomes) == ["committed", "conflict"]
    assert first_store.read(required=True)["revision"] == 2
    lock.release()


def test_journal_failure_does_not_advance_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import state as state_module

    store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    original = state_module._append_event

    def fail_journal(path: Path, event: dict[str, object]) -> None:
        raise OSError("synthetic journal failure")

    monkeypatch.setattr(state_module, "_append_event", fail_journal)
    with pytest.raises(OSError):
        store.transition(
            lock, expected_revision=None, input_hash="a" * 64, status="started"
        )
    assert store.read() is None
    assert (tmp_path / "state.pending.json").exists()
    monkeypatch.setattr(state_module, "_append_event", original)
    recovered = store.recover_pending(lock)
    assert recovered is not None and recovered["revision"] == 1
    assert store.read(required=True) == recovered
    lock.release()


def test_pending_transaction_can_be_recovered_after_state_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import state as state_module

    store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    original = state_module._atomic_json_unlocked
    failed = False

    def fail_state_once(path: Path, value: object) -> None:
        nonlocal failed
        if path.name == "state.json" and not failed:
            failed = True
            raise OSError("synthetic state state failure")
        original(path, value)

    monkeypatch.setattr(state_module, "_atomic_json_unlocked", fail_state_once)
    with pytest.raises(OSError):
        store.transition(
            lock, expected_revision=None, input_hash="a" * 64, status="started"
        )
    assert store.read() is None
    assert (tmp_path / "state.pending.json").exists()

    monkeypatch.setattr(state_module, "_atomic_json_unlocked", original)
    recovered = store.recover_pending(lock)
    assert recovered is not None and recovered["revision"] == 1
    assert store.read(required=True) == recovered
    assert not (tmp_path / "state.pending.json").exists()
    lock.release()


def test_pending_transaction_repairs_partial_journal_tail(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import state as state_module

    store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    original = state_module._append_event

    def write_partial_then_fail(path: Path, event: dict[str, object]) -> None:
        path.write_bytes(b'{"transaction_id":"partial')
        raise OSError("synthetic partial journal write")

    monkeypatch.setattr(state_module, "_append_event", write_partial_then_fail)
    with pytest.raises(OSError):
        store.transition(
            lock, expected_revision=None, input_hash="a" * 64, status="started"
        )
    monkeypatch.setattr(state_module, "_append_event", original)

    recovered = store.recover_pending(lock)

    events = (tmp_path / "events.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(events) == 1
    assert json.loads(events[0])["transaction_id"]
    assert recovered is not None and recovered["revision"] == 1
    lock.release()


def test_release_waits_until_state_transition_finishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import state as state_module

    store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    entered = Event()
    proceed = Event()
    original = state_module._append_event

    def blocked_append(path: Path, event: dict[str, object]) -> None:
        entered.set()
        assert proceed.wait(timeout=5)
        original(path, event)

    monkeypatch.setattr(state_module, "_append_event", blocked_append)
    with ThreadPoolExecutor(max_workers=2) as pool:
        transition_future = pool.submit(
            store.transition,
            lock,
            expected_revision=None,
            input_hash="a" * 64,
            status="started",
        )
        assert entered.wait(timeout=5)
        release_future = pool.submit(lock.release)
        assert not release_future.done()
        proceed.set()
        assert transition_future.result(timeout=5)["revision"] == 1
        release_future.result(timeout=5)
    assert not (tmp_path / "writer.lock").exists()


def test_state_transition_requires_verified_lock_revision_and_hash(tmp_path: Path) -> None:
    store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
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
    store = StateStore(tmp_path, workspace_root=tmp_path)
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    changed = {**lock.identity, "token": "another-token"}
    atomic_json(tmp_path / "writer.lock", changed)
    with pytest.raises(RunConflict):
        store.transition(
            lock, expected_revision=None, input_hash="a" * 64, status="started"
        )


def test_lock_release_detects_missing_or_changed_owner_without_deleting_new_lock(
    tmp_path: Path,
) -> None:
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    (tmp_path / "writer.lock").unlink()
    with pytest.raises(RunConflict):
        lock.release()

    replacement = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r2")
    with pytest.raises(RunConflict):
        lock.release()
    assert json.loads((tmp_path / "writer.lock").read_text(encoding="utf-8")) == replacement.identity
    replacement.release()


def test_stale_releaser_never_opens_a_window_for_a_third_acquirer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    stale = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    (tmp_path / "writer.lock").unlink()
    replacement = RunLock.acquire(
        tmp_path, workspace_root=tmp_path, run_id="r2"
    )
    entered = Event()
    proceed = Event()
    original_read = RunLock._read_identity_unlocked

    def blocked_read(lock: RunLock) -> dict[str, object]:
        if lock is stale:
            entered.set()
            assert proceed.wait(timeout=5)
        return original_read(lock)

    monkeypatch.setattr(RunLock, "_read_identity_unlocked", blocked_read)
    with ThreadPoolExecutor(max_workers=2) as pool:
        release_future = pool.submit(stale.release)
        assert entered.wait(timeout=5)
        acquire_future = pool.submit(
            RunLock.acquire,
            tmp_path,
            workspace_root=tmp_path,
            run_id="r3",
        )
        proceed.set()
        with pytest.raises(RunConflict):
            release_future.result(timeout=5)
        with pytest.raises(RunConflict):
            acquire_future.result(timeout=5)
    assert json.loads((tmp_path / "writer.lock").read_text(encoding="utf-8")) == replacement.identity
    replacement.release()


def test_explicit_recovery_records_aborted_event_and_requires_expected_identity(
    tmp_path: Path,
) -> None:
    lock = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    with pytest.raises(RunConflict):
        RunLock.recover(
            tmp_path,
            workspace_root=tmp_path,
            expected_identity={**lock.identity, "token": "wrong"},
            reason="stale",
        )
    assert (tmp_path / "writer.lock").exists()
    RunLock.recover(
        tmp_path,
        workspace_root=tmp_path,
        expected_identity=lock.identity,
        reason="operator-confirmed-stale",
    )
    assert not (tmp_path / "writer.lock").exists()
    event = json.loads((tmp_path / "events.jsonl").read_text(encoding="utf-8"))
    assert event["status"] == "aborted"
    assert event["run_id"] == "r1"


def test_stale_lock_recovery_resolves_pending_and_allows_a_new_writer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from presentation_studio import state as state_module

    store = StateStore(tmp_path, workspace_root=tmp_path)
    stale = RunLock.acquire(tmp_path, workspace_root=tmp_path, run_id="r1")
    original_append = state_module._append_event

    def fail_journal(path: Path, event: dict[str, object]) -> None:
        raise OSError("synthetic crash before journal commit")

    monkeypatch.setattr(state_module, "_append_event", fail_journal)
    with pytest.raises(OSError):
        store.transition(
            stale,
            expected_revision=None,
            input_hash="a" * 64,
            status="started",
        )
    monkeypatch.setattr(state_module, "_append_event", original_append)

    RunLock.recover(
        tmp_path,
        workspace_root=tmp_path,
        expected_identity=stale.identity,
        reason="operator-confirmed-crash",
    )

    assert not (tmp_path / "state.pending.json").exists()
    assert not (tmp_path / "writer.lock").exists()
    recovered = store.read(required=True)
    assert recovered["revision"] == 2
    assert recovered["status"] == "aborted"

    replacement = RunLock.acquire(
        tmp_path, workspace_root=tmp_path, run_id="r2"
    )
    started = store.transition(
        replacement,
        expected_revision=2,
        input_hash="b" * 64,
        status="started",
    )
    assert started["revision"] == 3
    assert started["run_id"] == "r2"
    replacement.release()


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
            StateStore(state_dir, workspace_root=project).bootstrap({"revision": 1})
        assert not (outside / "state.json").exists()
    finally:
        os.rmdir(state_dir)
