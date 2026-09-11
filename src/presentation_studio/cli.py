from __future__ import annotations

import argparse
from collections.abc import Callable
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from .models import CLIError, CLIResult
from .state import RunConflict, StateConflict
from .workspace import (
    InvalidYAML,
    PathOutsideWorkspace,
    ProjectConflict,
    WorkspaceInputError,
    init_project,
    load_project,
    resolve_paths,
    resolve_profile,
)


Handler = Callable[..., object]
_BACKENDS: dict[str, Handler] = {}
_RENDERERS: dict[str, Handler] = {}
_KNOWN_COMMANDS = frozenset(
    {"init", "build", "doctor", "validate", "render", "audit", "export", "migrate"}
)


class CLIUsageError(ValueError):
    pass


class ResultArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CLIUsageError(message)


def register_backend(backend_id: str, handler: Handler) -> None:
    _BACKENDS[backend_id] = handler


def register_renderer(backend_id: str, handler: Handler) -> None:
    _RENDERERS[backend_id] = handler


def _emit(result: CLIResult, json_mode: bool) -> int:
    if json_mode:
        print(result.model_dump_json())
    elif result.errors:
        print(result.errors[0].message_vi, file=sys.stderr)
    else:
        print(result.data)
    return result.exit_code


def _failed(
    command: str,
    code: str,
    message: str,
    exit_code: int,
    *,
    evidence_ref: str | None = None,
) -> CLIResult:
    return CLIResult(
        command=command,
        status="failed",
        exit_code=exit_code,
        errors=[
            CLIError(
                code=code,
                message_vi=message,
                evidence_ref=evidence_ref,
            )
        ],
    )


def _emit_technical_error(command: str, category: str, exc: Exception) -> str:
    safe_command = command if command in _KNOWN_COMMANDS else "unknown"
    exception_type = re.sub(r"[^A-Za-z0-9_]", "_", type(exc).__name__)[:64]
    diagnostic_id = uuid4().hex
    print(
        "technical-error "
        f"diagnostic_id={diagnostic_id} "
        f"command={safe_command} category={category} "
        f"exception_type={exception_type or 'Exception'}",
        file=sys.stderr,
    )
    return diagnostic_id


def _slug(value: str) -> str:
    value = value.replace("Đ", "D").replace("đ", "d")
    ascii_value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-") or "presentation"


def _validation_message(exc: ValidationError) -> str:
    messages = []
    for error in exc.errors(
        include_url=False, include_context=False, include_input=False
    ):
        location = ".".join(str(part) for part in error["loc"])
        messages.append(f"{location}: {error['msg']}" if location else error["msg"])
    return "; ".join(messages)


def _command_hint(argv: list[str]) -> str:
    for value in argv:
        if value in _KNOWN_COMMANDS:
            return value
    return "unknown"


def _parser() -> ResultArgumentParser:
    parser = ResultArgumentParser(prog="presentation")
    sub = parser.add_subparsers(dest="command", required=True, parser_class=ResultArgumentParser)

    command = sub.add_parser("init")
    command.add_argument("--workspace")
    command.add_argument("--home")
    command.add_argument("--project")
    command.add_argument("--title", required=True)
    command.add_argument("--json", action="store_true")

    command = sub.add_parser("build")
    command.add_argument("--workspace", required=True)
    command.add_argument("--deck")
    command.add_argument("--backend")
    command.add_argument("--json", action="store_true")

    for name in ("doctor", "validate", "render", "audit", "export"):
        command = sub.add_parser(name)
        command.add_argument("--workspace", required=True)
        command.add_argument("--json", action="store_true")
        if name in ("render", "audit", "export"):
            command.add_argument("--build", required=True)
        if name == "render":
            command.add_argument("--backend")
        if name == "export":
            command.add_argument("--format", required=True)

    command = sub.add_parser("migrate")
    command.add_argument("--source", required=True)
    command.add_argument("--workspace", required=True)
    command.add_argument("--deck")
    mode = command.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    command.add_argument("--json", action="store_true")
    return parser


def _validate_init_form(args: argparse.Namespace) -> tuple[Path | None, Path | None, str]:
    if args.project is not None:
        if args.home is None or args.workspace is not None:
            raise CLIUsageError("--project requires --home and cannot use --workspace")
        return Path(args.home), None, args.project
    if args.workspace is None or args.home is not None:
        raise CLIUsageError("use either --workspace or --home with --project")
    workspace = Path(args.workspace)
    return None, workspace, _slug(workspace.name)


def _invoke_handler(
    *, command: str, handler: Handler, args: tuple[Any, ...]
) -> CLIResult:
    try:
        result = handler(*args)
    except Exception as exc:
        diagnostic_id = _emit_technical_error(command, "backend", exc)
        return _failed(
            command,
            "BACKEND_FAILURE",
            "Backend thất bại; mã chẩn đoán đã được ghi vào stderr.",
            5,
            evidence_ref=f"diagnostic:{diagnostic_id}",
        )
    if not isinstance(result, CLIResult) or result.command != command:
        return _failed(
            command,
            "HANDLER_CONTRACT_ERROR",
            "Backend trả kết quả không đúng hợp đồng lệnh.",
            5,
        )
    return result


def _run_command(args: argparse.Namespace) -> CLIResult:
    if args.command == "init":
        home, workspace, project_id = _validate_init_form(args)
        paths = resolve_paths(
            home=home, workspace=workspace, project_id=project_id
        )
        project = init_project(paths, project_id=project_id, title=args.title)
        return CLIResult(
            command="init",
            status="passed",
            exit_code=0,
            data={
                "project": project.model_dump(mode="json"),
                "workspace": str(paths.project_root),
            },
        )

    if args.command == "build":
        paths = resolve_paths(workspace=Path(args.workspace))
        backend = args.backend
        if (paths.project_root / "project.yaml").exists():
            project = load_project(paths.project_root)
            backend = backend or project.backend
            if project.profile_ref:
                try:
                    resolve_profile(project.profile_ref, paths)
                except FileNotFoundError:
                    return _failed(
                        "build",
                        "PROFILE_NOT_FOUND",
                        f"Không tìm thấy profile: {project.profile_ref}",
                        2,
                    )
        if backend not in _BACKENDS:
            return _failed(
                "build",
                "CAPABILITY_UNAVAILABLE",
                f"Backend chưa khả dụng: {backend or 'unknown'}",
                3,
            )
        return _invoke_handler(
            command="build", handler=_BACKENDS[backend], args=(paths,)
        )

    if args.command == "doctor":
        return CLIResult(
            command="doctor",
            status="passed",
            exit_code=0,
            data={
                "core": "available",
                "backends": sorted(_BACKENDS),
                "renderers": sorted(_RENDERERS),
            },
        )

    if args.command == "render":
        paths = resolve_paths(workspace=Path(args.workspace))
        backend = args.backend
        if not backend and (paths.project_root / "project.yaml").exists():
            backend = load_project(paths.project_root).backend
        if backend not in _RENDERERS:
            return _failed(
                "render",
                "CAPABILITY_UNAVAILABLE",
                f"Renderer chưa khả dụng: {backend or 'unknown'}",
                3,
            )
        return _invoke_handler(
            command="render",
            handler=_RENDERERS[backend],
            args=(paths, args.build),
        )

    if args.command == "migrate":
        from .migration import migrate_result

        return migrate_result(
            Path(args.source),
            Path(args.workspace),
            apply=args.apply,
            deck_path=args.deck,
        )

    return _failed(
        args.command,
        "CAPABILITY_UNAVAILABLE",
        f"Capability chưa khả dụng: {args.command}",
        3,
    )


def run(argv: list[str] | None = None) -> int:
    values = list(sys.argv[1:] if argv is None else argv)
    json_mode = "--json" in values
    command = _command_hint(values)
    try:
        args = _parser().parse_args(values)
        json_mode = args.json
        command = args.command
        result = _run_command(args)
    except CLIUsageError:
        result = _failed(
            command,
            "INVALID_INPUT",
            "Tham số dòng lệnh không hợp lệ.",
            2,
        )
    except (WorkspaceInputError, InvalidYAML) as exc:
        result = _failed(command, "INVALID_INPUT", str(exc), 2)
    except ValidationError as exc:
        result = _failed(command, "INVALID_INPUT", _validation_message(exc), 2)
    except ProjectConflict:
        result = _failed(command, "PROJECT_CONFLICT", "Project đã tồn tại với cấu hình khác.", 6)
    except (RunConflict, StateConflict):
        result = _failed(command, "STATE_CONFLICT", "Trạng thái project đã thay đổi.", 6)
    except PermissionError:
        result = _failed(command, "PERMISSION_DENIED", "Không đủ quyền truy cập tài nguyên.", 3)
    except FileNotFoundError:
        result = _failed(command, "INPUT_NOT_FOUND", "Không tìm thấy đầu vào được yêu cầu.", 2)
    except OSError:
        result = _failed(command, "FILESYSTEM_FAILURE", "Thao tác hệ thống tệp thất bại.", 5)
    except Exception as exc:
        diagnostic_id = _emit_technical_error(command, "internal", exc)
        result = _failed(
            command,
            "INTERNAL_ERROR",
            "Lỗi nội bộ đã được lọc; mã chẩn đoán đã được ghi vào stderr.",
            5,
            evidence_ref=f"diagnostic:{diagnostic_id}",
        )
    return _emit(result, json_mode)


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    raise SystemExit(run())


if __name__ == "__main__":
    main()
