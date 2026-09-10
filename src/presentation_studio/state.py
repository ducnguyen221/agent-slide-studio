from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from threading import Lock
from typing import Any, Iterator, Literal
from uuid import uuid4


_atomic_locks_guard = Lock()
_atomic_locks: dict[Path, Lock] = {}


class RunConflict(RuntimeError):
    pass


class StateConflict(RuntimeError):
    pass


class MissingState(StateConflict):
    pass


class StatePathError(StateConflict):
    pass


def _verified_state_dir(state_dir: Path, workspace_root: Path) -> Path:
    resolved_root = workspace_root.expanduser().resolve()
    resolved = state_dir.expanduser().resolve()
    if not resolved.is_relative_to(resolved_root):
        raise StatePathError("state directory escapes its workspace")
    return resolved


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_inputs(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _fsync_directory(directory: Path) -> None:
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def _atomic_lock(path: Path) -> Lock:
    resolved = path.absolute()
    with _atomic_locks_guard:
        return _atomic_locks.setdefault(resolved, Lock())


@contextmanager
def _protocol_lock(path: Path) -> Iterator[None]:
    """Serialize a short file protocol across instances and processes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with _atomic_lock(path):
        descriptor = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
        locked = False
        try:
            if os.name == "nt":
                import msvcrt

                if os.fstat(descriptor).st_size == 0:
                    os.write(descriptor, b"\0")
                    os.fsync(descriptor)
                os.lseek(descriptor, 0, os.SEEK_SET)
                try:
                    msvcrt.locking(descriptor, msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    raise RunConflict("state operation is already in progress") from exc
            else:
                import fcntl

                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError as exc:
                    raise RunConflict("state operation is already in progress") from exc
            locked = True
            yield
        finally:
            if locked:
                if os.name == "nt":
                    import msvcrt

                    os.lseek(descriptor, 0, os.SEEK_SET)
                    msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl

                    fcntl.flock(descriptor, fcntl.LOCK_UN)
            os.close(descriptor)


def atomic_json(path: Path, value: Any) -> None:
    with _atomic_lock(path):
        _atomic_json_unlocked(path, value)


def _atomic_json_unlocked(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = (json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        offset = 0
        while offset < len(line):
            offset += os.write(descriptor, line[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateConflict("state transaction cannot be read") from exc
    if not isinstance(value, dict):
        raise StateConflict("state transaction is invalid")
    return value


def _event_exists(
    path: Path, transaction_id: str, expected_event: dict[str, Any]
) -> bool:
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise StateConflict("state journal cannot be read") from exc

    complete_bytes = raw
    if raw and not raw.endswith(b"\n"):
        last_newline = raw.rfind(b"\n")
        complete_bytes = raw[: last_newline + 1] if last_newline >= 0 else b""
        try:
            with path.open("r+b") as stream:
                stream.truncate(len(complete_bytes))
                stream.flush()
                os.fsync(stream.fileno())
        except OSError as exc:
            raise StateConflict("state journal tail cannot be repaired") from exc
        _fsync_directory(path.parent)

    for raw_line in complete_bytes.splitlines():
        try:
            event = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise StateConflict("state journal is invalid") from exc
        if isinstance(event, dict) and event.get("transaction_id") == transaction_id:
            if event != expected_event:
                raise StateConflict("state journal transaction does not match pending state")
            return True
    return False


class StateStore:
    def __init__(self, state_dir: Path, *, workspace_root: Path):
        self.state_dir = state_dir
        self.workspace_root = workspace_root
        self.path = state_dir / "state.json"
        self.events_path = state_dir / "events.jsonl"

    def _paths(self) -> tuple[Path, Path, Path, Path]:
        state_dir = _verified_state_dir(self.state_dir, self.workspace_root)
        return (
            state_dir / "state.json",
            state_dir / "events.jsonl",
            state_dir / "state.pending.json",
            state_dir / ".state.protocol",
        )

    def read(self, *, required: bool = False) -> dict[str, Any] | None:
        path, _, _, _ = self._paths()
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            if required:
                raise MissingState("required state is missing") from None
            return None
        if not isinstance(value, dict):
            raise StateConflict("state is invalid")
        return value

    def bootstrap(self, value: dict[str, Any]) -> None:
        """Create initial state only when neither state nor writer lock exists."""
        state_path, _, pending_path, protocol_path = self._paths()
        with _protocol_lock(protocol_path):
            with _protocol_lock(state_path.parent / ".writer-lock.protocol"):
                if state_path.exists() or pending_path.exists():
                    raise StateConflict("state is already initialized")
                if (state_path.parent / "writer.lock").exists():
                    raise RunConflict("cannot bootstrap state while a writer lock exists")
                _atomic_json_unlocked(state_path, value)

    def _recover_pending_unlocked(
        self,
        lock: RunLock,
        state_path: Path,
        events_path: Path,
        pending_path: Path,
    ) -> dict[str, Any] | None:
        if not pending_path.exists():
            return None
        transaction = _read_json(pending_path)
        if transaction.get("lock_identity") != lock.identity:
            raise StateConflict("pending state transaction belongs to another writer")
        state = transaction.get("state")
        event = transaction.get("event")
        base_state = transaction.get("base_state")
        transaction_id = transaction.get("transaction_id")
        if (
            not isinstance(state, dict)
            or not isinstance(event, dict)
            or not isinstance(transaction_id, str)
        ):
            raise StateConflict("pending state transaction is invalid")
        if not _event_exists(events_path, transaction_id, event):
            _append_event(events_path, event)
        current = self.read()
        if current == state:
            pass
        elif current == base_state:
            _atomic_json_unlocked(state_path, state)
        else:
            raise StateConflict("state changed while recovering a transaction")
        pending_path.unlink()
        _fsync_directory(pending_path.parent)
        return state

    def _commit_transaction_unlocked(
        self,
        lock: RunLock,
        *,
        current: dict[str, Any] | None,
        state: dict[str, Any],
        event: dict[str, Any],
        state_path: Path,
        events_path: Path,
        pending_path: Path,
    ) -> dict[str, Any]:
        _atomic_json_unlocked(
            pending_path,
            {
                "transaction_id": event["transaction_id"],
                "lock_identity": lock.identity,
                "base_state": current,
                "state": state,
                "event": event,
            },
        )
        _append_event(events_path, event)
        _atomic_json_unlocked(state_path, state)
        pending_path.unlink()
        _fsync_directory(pending_path.parent)
        return state

    def recover_pending(self, lock: RunLock) -> dict[str, Any] | None:
        state_path, events_path, pending_path, protocol_path = self._paths()
        with _protocol_lock(protocol_path):
            with _protocol_lock(state_path.parent / ".writer-lock.protocol"):
                if lock._read_identity_unlocked() != lock.identity:
                    raise RunConflict("lock ownership changed")
                return self._recover_pending_unlocked(
                    lock, state_path, events_path, pending_path
                )

    def transition(
        self,
        lock: RunLock,
        *,
        expected_revision: int | None,
        input_hash: str,
        status: Literal["started", "ended", "aborted"],
    ) -> dict[str, Any]:
        state_path, events_path, pending_path, protocol_path = self._paths()
        with _protocol_lock(protocol_path):
            with _protocol_lock(state_path.parent / ".writer-lock.protocol"):
                if lock._read_identity_unlocked() != lock.identity:
                    raise RunConflict("lock ownership changed")
                self._recover_pending_unlocked(
                    lock, state_path, events_path, pending_path
                )
                current = self.read()
                if current is None:
                    if expected_revision is not None or status != "started":
                        raise StateConflict("state does not exist at expected revision")
                    revision = 1
                else:
                    revision = current.get("revision")
                    if not isinstance(revision, int) or revision != expected_revision:
                        raise StateConflict("state revision is stale")
                    current_status = current.get("status")
                    if current_status == "started":
                        if current.get("input_hash") != input_hash:
                            raise StateConflict("state input hash changed")
                        if current.get("run_id") != lock.run_id:
                            raise StateConflict("state belongs to another run")
                        if status == "started":
                            raise StateConflict("invalid state transition")
                    elif current_status in {"ended", "aborted"}:
                        if status != "started":
                            raise StateConflict("invalid state transition")
                    else:
                        raise StateConflict("state status is invalid")
                    revision += 1
                transaction_id = uuid4().hex
                state = {
                    "revision": revision,
                    "input_hash": input_hash,
                    "status": status,
                    "run_id": lock.run_id,
                    "lock_token": lock.token,
                    "updated_at": _now(),
                }
                event = {
                    "transaction_id": transaction_id,
                    "revision": revision,
                    "input_hash": input_hash,
                    "status": status,
                    "run_id": lock.run_id,
                    "lock_token": lock.token,
                    "occurred_at": state["updated_at"],
                }
                return self._commit_transaction_unlocked(
                    lock,
                    current=current,
                    state=state,
                    event=event,
                    state_path=state_path,
                    events_path=events_path,
                    pending_path=pending_path,
                )


@dataclass(frozen=True)
class RunLock:
    path: Path
    workspace_root: Path
    run_id: str
    token: str
    pid: int
    started_at: str

    @property
    def identity(self) -> dict[str, str | int]:
        return {
            "pid": self.pid,
            "started_at": self.started_at,
            "run_id": self.run_id,
            "token": self.token,
        }

    @classmethod
    def acquire(
        cls, state_dir: Path, *, workspace_root: Path, run_id: str
    ) -> RunLock:
        state_dir = _verified_state_dir(state_dir, workspace_root)
        state_dir.mkdir(parents=True, exist_ok=True)
        state_dir = _verified_state_dir(state_dir, workspace_root)
        path = state_dir / "writer.lock"
        protocol_path = state_dir / ".writer-lock.protocol"
        lock = cls(
            path=path,
            workspace_root=workspace_root.expanduser().resolve(),
            run_id=run_id,
            token=uuid4().hex,
            pid=os.getpid(),
            started_at=_now(),
        )
        payload = (json.dumps(lock.identity, sort_keys=True) + "\n").encode("utf-8")
        with _protocol_lock(protocol_path):
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError as exc:
                raise RunConflict("project already has a writer lock") from exc
            try:
                os.write(descriptor, payload)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        _fsync_directory(state_dir)
        return lock

    def _state_dir(self) -> Path:
        return _verified_state_dir(self.path.parent, self.workspace_root)

    def _read_identity_unlocked(self) -> dict[str, Any]:
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise RunConflict("writer lock is missing") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise RunConflict("writer lock cannot be verified") from exc
        if not isinstance(value, dict):
            raise RunConflict("writer lock identity is invalid")
        return value

    def verify(self) -> None:
        state_dir = self._state_dir()
        with _protocol_lock(state_dir / ".writer-lock.protocol"):
            if self._read_identity_unlocked() != self.identity:
                raise RunConflict("lock ownership changed")

    def release(self) -> None:
        state_dir = self._state_dir()
        with _protocol_lock(state_dir / ".state.protocol"):
            with _protocol_lock(state_dir / ".writer-lock.protocol"):
                if self._read_identity_unlocked() != self.identity:
                    raise RunConflict("lock ownership changed")
                self.path.unlink()
                _fsync_directory(state_dir)

    @classmethod
    def recover(
        cls,
        state_dir: Path,
        *,
        workspace_root: Path,
        expected_identity: dict[str, Any],
        reason: str,
    ) -> None:
        state_dir = _verified_state_dir(state_dir, workspace_root)
        path = state_dir / "writer.lock"
        with _protocol_lock(state_dir / ".state.protocol"):
            with _protocol_lock(state_dir / ".writer-lock.protocol"):
                try:
                    actual = json.loads(path.read_text(encoding="utf-8"))
                except FileNotFoundError as exc:
                    raise RunConflict("writer lock is missing") from exc
                except (OSError, json.JSONDecodeError) as exc:
                    raise RunConflict("writer lock cannot be verified") from exc
                if actual != expected_identity:
                    raise RunConflict("lock ownership changed")
                try:
                    stale_lock = cls(
                        path=path,
                        workspace_root=workspace_root.expanduser().resolve(),
                        run_id=str(actual["run_id"]),
                        token=str(actual["token"]),
                        pid=int(actual["pid"]),
                        started_at=str(actual["started_at"]),
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    raise RunConflict("writer lock identity is invalid") from exc
                store = StateStore(state_dir, workspace_root=workspace_root)
                state_path, events_path, pending_path, _ = store._paths()
                store._recover_pending_unlocked(
                    stale_lock, state_path, events_path, pending_path
                )
                current = store.read()
                if current is not None and current.get("status") == "started":
                    if (
                        current.get("run_id") != stale_lock.run_id
                        or current.get("lock_token") != stale_lock.token
                        or not isinstance(current.get("revision"), int)
                        or not isinstance(current.get("input_hash"), str)
                    ):
                        raise StateConflict(
                            "active state does not match the stale writer lock"
                        )
                    occurred_at = _now()
                    aborted = {
                        **current,
                        "revision": current["revision"] + 1,
                        "status": "aborted",
                        "updated_at": occurred_at,
                    }
                    event = {
                        "transaction_id": uuid4().hex,
                        "revision": aborted["revision"],
                        "input_hash": current["input_hash"],
                        "status": "aborted",
                        "run_id": stale_lock.run_id,
                        "lock_token": stale_lock.token,
                        "reason": reason,
                        "occurred_at": occurred_at,
                    }
                    store._commit_transaction_unlocked(
                        stale_lock,
                        current=current,
                        state=aborted,
                        event=event,
                        state_path=state_path,
                        events_path=events_path,
                        pending_path=pending_path,
                    )
                elif current is None or current.get("status") in {"ended", "aborted"}:
                    _append_event(
                        events_path,
                        {
                            "status": "aborted",
                            "run_id": stale_lock.run_id,
                            "lock_token": stale_lock.token,
                            "reason": reason,
                            "occurred_at": _now(),
                        },
                    )
                else:
                    raise StateConflict("state status is invalid during lock recovery")
                path.unlink()
                _fsync_directory(state_dir)
