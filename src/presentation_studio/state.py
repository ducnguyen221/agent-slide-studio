from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib, json, os
from pathlib import Path
from typing import Any

class RunConflict(RuntimeError): pass
def _now(): return datetime.now(timezone.utc).isoformat()
def hash_inputs(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()).hexdigest()
def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    os.replace(temp, path)
class StateStore:
    def __init__(self, state_dir: Path): self.path = state_dir / "state.json"
    def read(self): return json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
    def write(self, value): atomic_json(self.path, value)
@dataclass
class RunLock:
    path: Path
    run_id: str
    @classmethod
    def acquire(cls, state_dir: Path, *, run_id: str):
        state_dir.mkdir(parents=True, exist_ok=True); path = state_dir / "writer.lock"
        payload = json.dumps({"pid": os.getpid(), "started_at": _now(), "run_id": run_id})
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        except FileExistsError as exc: raise RunConflict("project already has a writer lock") from exc
        with os.fdopen(fd, "w", encoding="utf-8") as stream: stream.write(payload)
        return cls(path, run_id)
    def release(self):
        if not self.path.exists(): return
        data = json.loads(self.path.read_text(encoding="utf-8"))
        if data.get("run_id") != self.run_id: raise RunConflict("lock ownership changed")
        self.path.unlink()

