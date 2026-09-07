from typing import Any, Literal
from pydantic import Field, model_validator
from .common import SchemaVersion, StrictModel
class CLIError(StrictModel):
    code: str
    message_vi: str
    field: str | None = None
    slide_id: str | None = None
    evidence_ref: str | None = None
class CLIResult(StrictModel):
    schema_version: SchemaVersion = "1.0"
    command: str
    status: Literal["passed", "failed", "unverified"]
    exit_code: int = Field(ge=0, le=6)
    data: dict[str, Any] = Field(default_factory=dict)
    errors: list[CLIError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    @model_validator(mode="after")
    def status_matches_exit_code(self):
        if self.status == "passed" and self.exit_code != 0:
            raise ValueError("passed status requires exit_code 0")
        if self.status == "failed" and self.exit_code == 0:
            raise ValueError("failed status requires non-zero exit_code")
        return self
class BackendCapabilities(StrictModel):
    backend_id: str
    available: bool
    authoring_modes: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
class BuildInput(StrictModel):
    project: dict[str, Any]
    deck: dict[str, Any]
    profile_lock: dict[str, Any] | None = None
    template_locks: list[dict[str, Any]] = Field(default_factory=list)
    asset_manifest: dict[str, Any] = Field(default_factory=dict)
    input_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    backend_options: dict[str, Any] = Field(default_factory=dict)
class ProcessResult(StrictModel):
    started: bool
    exit_code: int | None = None
    timed_out: bool = False
    elapsed_seconds: float = Field(ge=0)
    pid: int | None = None
    started_at: str | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    failure_kind: str | None = None
class OutputArtifact(StrictModel):
    path: str
    media_type: str
    sha256: str
    slide_count: int = Field(ge=0)
    editability: Literal["native", "raster", "mixed", "not_applicable"]
    notes_included: bool
    limitations: list[str] = Field(default_factory=list)
class BuildResult(StrictModel):
    build_id: str
    backend: str
    status: Literal["passed", "failed", "unverified"]
    input_hash: str
    outputs: list[OutputArtifact] = Field(default_factory=list)
    slide_results: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    process_result: ProcessResult | None = None
class RenderResult(StrictModel):
    build_id: str
    status: Literal["passed", "failed", "unverified"]
    slides: dict[str, dict[str, str]] = Field(default_factory=dict)
    renderer_version: str | None = None
    font_manifest: list[str] = Field(default_factory=list)
    dimensions: dict[str, int] = Field(default_factory=dict)
    errors: list[CLIError] = Field(default_factory=list)
class QAReport(StrictModel):
    schema_version: SchemaVersion = "1.0"
    build_id: str
    input_hash: str
    checks: list[dict[str, Any]] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
