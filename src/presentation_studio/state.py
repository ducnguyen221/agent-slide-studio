from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from threading import Lock
from typing import Any, Literal
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


def _verified_state_dir(state_dir: Path) -> Path:
    expected_root = state_dir.parent.resolve() if state_dir.name == ".presentation" else state_dir.resolve()
    resolved = state_dir.resolve()
    if not resolved.is_relative_to(expected_root):
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
        os.write(descriptor, line)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class StateStore:
    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.path = state_dir / "state.json"
        self.events_path = state_dir / "events.jsonl"
        self._mutex = Lock()

    def _paths(self) -> tuple[Path, Path]:
        state_dir = _verified_state_dir(self.state_dir)
        return state_dir / "state.json", state_dir / "events.jsonl"

    def read(self, *, required: bool = False) -> dict[str, Any] | None:
        path, _ = self._paths()
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            if required:
                raise MissingState("required state is missing") from None
            return None

    def write(self, value: dict[str, Any]) -> None:
        path, _ = self._paths()
        atomic_json(path, value)

    def transition(
        self,
        lock: RunLock,
        *,
        expected_revision: int | None,
        input_hash: str,
        status: Literal["started", "ended", "aborted"],
    ) -> dict[str, Any]:
        with self._mutex:
            state_path, events_path = self._paths()
            lock.verify()
            current = self.read()
            if current is None:
                if expected_revision is not None or status != "started":
                    raise StateConflict("state does not exist at expected revision")
                revision = 1
            else:
                revision = current.get("revision")
                if not isinstance(revision, int) or revision != expected_revision:
                    raise StateConflict("state revision is stale")
                if current.get("input_hash") != input_hash:
                    raise StateConflict("state input hash changed")
                if current.get("run_id") != lock.run_id:
                    raise StateConflict("state belongs to another run")
                if current.get("status") != "started" or status == "started":
                    raise StateConflict("invalid state transition")
                revision += 1
            state = {
                "revision": revision,
                "input_hash": input_hash,
                "status": status,
                "run_id": lock.run_id,
                "lock_token": lock.token,
                "updated_at": _now(),
            }
            atomic_json(state_path, state)
            _append_event(
                events_path,
                {
                    "revision": revision,
                    "input_hash": input_hash,
                    "status": status,
                    "run_id": lock.run_id,
                    "lock_token": lock.token,
                    "occurred_at": state["updated_at"],
                },
            )
            return state


@dataclass(frozen=True)
class RunLock:
    path: Path
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
    def acquire(cls, state_dir: Path, *, run_id: str) -> RunLock:
        state_dir = _verified_state_dir(state_dir)
        state_dir.mkdir(parents=True, exist_ok=True)
        path = state_dir / "writer.lock"
        lock = cls(
            path=path,
            run_id=run_id,
            token=uuid4().hex,
            pid=os.getpid(),
            started_at=_now(),
        )
        payload = (json.dumps(lock.identity, sort_keys=True) + "\n").encode("utf-8")
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

    def _read_identity(self, path: Path | None = None) -> dict[str, Any]:
        target = path or self.path
        try:
            value = json.loads(target.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise RunConflict("writer lock is missing") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise RunConflict("writer lock cannot be verified") from exc
        if not isinstance(value, dict):
            raise RunConflict("writer lock identity is invalid")
        return value

    def verify(self) -> None:
        if self._read_identity() != self.identity:
            raise RunConflict("lock ownership changed")

    @staticmethod
    def _restore_foreign_lock(tombstone: Path, path: Path) -> None:
        try:
            os.link(tombstone, path)
        except FileExistsError:
            return
        tombstone.unlink()

    def release(self) -> None:
        tombstone = self.path.with_name(f".{self.path.name}.{uuid4().hex}.release")
        try:
            os.replace(self.path, tombstone)
        except FileNotFoundError as exc:
            raise RunConflict("writer lock is missing") from exc
        actual = self._read_identity(tombstone)
        if actual != self.identity:
            self._restore_foreign_lock(tombstone, self.path)
            raise RunConflict("lock ownership changed")
        tombstone.unlink()
        _fsync_directory(self.path.parent)

    @classmethod
    def recover(
        cls,
        state_dir: Path,
        *,
        expected_identity: dict[str, Any],
        reason: str,
    ) -> None:
        state_dir = _verified_state_dir(state_dir)
        path = state_dir / "writer.lock"
        tombstone = path.with_name(f".{path.name}.{uuid4().hex}.recovery")
        try:
            os.replace(path, tombstone)
        except FileNotFoundError as exc:
            raise RunConflict("writer lock is missing") from exc
        try:
            actual = json.loads(tombstone.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            cls._restore_foreign_lock(tombstone, path)
            raise RunConflict("writer lock cannot be verified") from exc
        if actual != expected_identity:
            cls._restore_foreign_lock(tombstone, path)
            raise RunConflict("lock ownership changed")
        _append_event(
            state_dir / "events.jsonl",
            {
                "status": "aborted",
                "run_id": actual["run_id"],
                "lock_token": actual["token"],
                "reason": reason,
                "occurred_at": _now(),
            },
        )
        tombstone.unlink()
        _fsync_directory(state_dir)
