from __future__ import annotations
import argparse, re, sys, unicodedata
from pathlib import Path
from pydantic import ValidationError
from .models import CLIError, CLIResult
from .workspace import init_project, load_project, resolve_paths, resolve_profile

_BACKENDS: dict[str, object] = {}
_RENDERERS: dict[str, object] = {}
def register_backend(backend_id: str, handler: object) -> None: _BACKENDS[backend_id] = handler
def register_renderer(backend_id: str, handler: object) -> None: _RENDERERS[backend_id] = handler
def _emit(result: CLIResult, json_mode: bool) -> int:
    if json_mode: print(result.model_dump_json())
    elif result.errors: print(result.errors[0].message_vi, file=sys.stderr)
    else: print(result.data)
    return result.exit_code
def _failed(command, code, message, exit_code):
    return CLIResult(command=command, status="failed", exit_code=exit_code, errors=[CLIError(code=code, message_vi=message)])
def _slug(value: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "presentation"
def run(argv=None) -> int:
    parser=argparse.ArgumentParser(prog="presentation"); sub=parser.add_subparsers(dest="command", required=True)
    p=sub.add_parser("init"); p.add_argument("--workspace"); p.add_argument("--home"); p.add_argument("--project"); p.add_argument("--title", required=True); p.add_argument("--json", action="store_true")
    p=sub.add_parser("build"); p.add_argument("--workspace", required=True); p.add_argument("--backend"); p.add_argument("--json", action="store_true")
    for command in ("doctor", "validate", "render", "audit", "export"):
        p=sub.add_parser(command); p.add_argument("--workspace", required=True); p.add_argument("--json", action="store_true")
        if command in ("render", "audit", "export"): p.add_argument("--build", required=True)
        if command == "render": p.add_argument("--backend")
        if command == "export": p.add_argument("--format", required=True)
    args=parser.parse_args(argv)
    try:
        if args.command == "init":
            pid=args.project or _slug(Path(args.workspace).name)
            paths=resolve_paths(home=Path(args.home) if args.home else None, workspace=Path(args.workspace) if args.workspace else None, project_id=pid)
            project=init_project(paths, project_id=pid, title=args.title)
            result=CLIResult(command="init", status="passed", exit_code=0, data={"project": project.model_dump(mode="json"), "workspace": str(paths.project_root)})
        elif args.command == "build":
            paths=resolve_paths(workspace=Path(args.workspace)); backend=args.backend
            if (paths.project_root / "project.yaml").exists():
                project=load_project(paths.project_root); backend=backend or project.backend
                if project.profile_ref:
                    try: resolve_profile(project.profile_ref, paths)
                    except FileNotFoundError: return _emit(_failed("build", "PROFILE_NOT_FOUND", f"Không tìm thấy profile: {project.profile_ref}", 2), args.json)
            if backend not in _BACKENDS: result=_failed("build", "CAPABILITY_UNAVAILABLE", f"Backend chưa khả dụng: {backend}", 3)
            else: result=_BACKENDS[backend](paths)
        elif args.command == "doctor":
            result=CLIResult(command="doctor", status="passed", exit_code=0, data={"core": "available", "backends": sorted(_BACKENDS), "renderers": sorted(_RENDERERS)})
        elif args.command == "render":
            paths=resolve_paths(workspace=Path(args.workspace)); backend=args.backend
            if not backend and (paths.project_root / "project.yaml").exists(): backend=load_project(paths.project_root).backend
            if backend not in _RENDERERS: result=_failed("render", "CAPABILITY_UNAVAILABLE", f"Renderer chưa khả dụng: {backend or 'unknown'}", 3)
            else: result=_RENDERERS[backend](paths, args.build)
        else:
            result=_failed(args.command, "CAPABILITY_UNAVAILABLE", f"Capability chưa khả dụng: {args.command}", 3)
    except (ValueError, ValidationError, FileExistsError) as exc:
        result=_failed(args.command, "INVALID_INPUT", str(exc), 2)
    return _emit(result, args.json)
def main(): raise SystemExit(run())
if __name__ == "__main__": main()
