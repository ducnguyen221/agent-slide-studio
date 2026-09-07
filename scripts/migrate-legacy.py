from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
def main():
    p=argparse.ArgumentParser(); p.add_argument("--source", required=True); p.add_argument("--workspace", required=True); g=p.add_mutually_exclusive_group(required=True); g.add_argument("--dry-run", action="store_true"); g.add_argument("--apply", action="store_true"); a=p.parse_args()
    source=Path(a.source).resolve(); target=Path(a.workspace).resolve()
    candidates=[x for x in source.rglob("*.yaml") if x.is_file()]
    items=[{"source":str(x), "relative_path":str(x.relative_to(source)), "sha256":hashlib.sha256(x.read_bytes()).hexdigest()} for x in candidates]
    if a.apply:
        target.mkdir(parents=True, exist_ok=True)
        for item in items:
            src=Path(item["source"]); dst=(target / "sources" / item["relative_path"]).resolve()
            if not dst.is_relative_to(target): raise SystemExit(2)
            dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(src.read_bytes())
    print(json.dumps({"schema_version":"1.0","command":"migrate","status":"passed","exit_code":0,"data":{"dry_run":a.dry_run,"planned_files":len(items),"files":items},"errors":[],"warnings":[]}, ensure_ascii=False))
if __name__ == "__main__": main()

