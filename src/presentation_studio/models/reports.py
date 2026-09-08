from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, model_validator

from .assets import AssetManifest
from .common import EvidenceRef, Identifier, RelativePath, SHA256, SchemaVersion, SemVer, StrictModel
from .deck import DeckSpec
from .profile import ProfileLock
from .project import ProjectConfig


ErrorCode = Annotated[str, Field(pattern=r"^[A-Z][A-Z0-9_]{0,63}$")]


class CLIError(StrictModel):
    code: ErrorCode
    message_vi: str
    field: str | None = None
    slide_id: Identifier | None = None
    evidence_ref: str | None = None


class CLIResult(StrictModel):
    schema_version: SchemaVersion = "1.0"
    command: str
    status: Literal["passed", "failed", "unverified"]
    exit_code: Literal[0, 2, 3, 4, 5, 6]
    data: dict[str, str | int | float | bool | None | list | dict] = Field(
        default_factory=dict
    )
    errors: list[CLIError] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_matches_exit_code(self) -> CLIResult:
        if self.status == "passed" and (self.exit_code != 0 or self.errors):
            raise ValueError("passed status requires exit_code 0 and no errors")
        if self.status == "failed" and (self.exit_code == 0 or not self.errors):
            raise ValueError("failed status requires a non-zero exit code and errors")
        if self.status == "unverified" and self.exit_code not in {0, 4}:
            raise ValueError("unverified status requires exit_code 0 or 4")
        return self


class FeatureVerification(StrictModel):
    status: Literal["passed", "failed", "unverified", "not_applicable"]
    evidence_ref: str | None = None
    environment: str | None = None


class RenderCapabilities(StrictModel):
    png: bool = False
    pdf: bool = False
    dimensions: bool = False


class BackendCapabilities(StrictModel):
    backend_id: Identifier
    adapter_version: SemVer
    engine_version: str | None = None
    available: bool
    unavailable_reason: str | None = None
    supported_inputs: list[Identifier] = Field(default_factory=list)
    supported_outputs: list[Identifier] = Field(default_factory=list)
    supported_elements: list[Identifier] = Field(default_factory=list)
    editable_elements: list[Identifier] = Field(default_factory=list)
    notes_support_by_output: dict[Identifier, bool] = Field(default_factory=dict)
    animation_support: bool = False
    requires_network: bool = False
    render_capabilities: RenderCapabilities = Field(default_factory=RenderCapabilities)
    verification_by_feature: dict[Identifier, FeatureVerification] = Field(
        default_factory=dict
    )

    @model_validator(mode="after")
    def availability_has_reason(self) -> BackendCapabilities:
        if not self.available and not self.unavailable_reason:
            raise ValueError("unavailable backend requires unavailable_reason")
        return self


class TemplateLock(StrictModel):
    template_id: Identifier
    version: SemVer
    sha256: SHA256


class BackendOptions(StrictModel):
    timeout_seconds: float | None = Field(default=None, gt=0)
    extensions: dict[Identifier, str | int | float | bool | None] = Field(
        default_factory=dict
    )


class BuildInput(StrictModel):
    project: ProjectConfig
    deck: DeckSpec
    profile_lock: ProfileLock | None = None
    template_locks: list[TemplateLock] = Field(default_factory=list)
    asset_manifest: AssetManifest = Field(default_factory=AssetManifest)
    input_hash: SHA256
    backend_options: BackendOptions = Field(default_factory=BackendOptions)


class ProcessResult(StrictModel):
    started: bool
    exit_code: int | None = None
    timed_out: bool = False
    elapsed_seconds: float = Field(ge=0)
    pid: int | None = Field(default=None, gt=0)
    started_at: datetime | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    failure_kind: Identifier | None = None

    @model_validator(mode="after")
    def lifecycle_is_consistent(self) -> ProcessResult:
        if self.started:
            if self.pid is None or self.started_at is None:
                raise ValueError("started process requires pid and started_at")
        elif self.pid is not None or self.started_at is not None or self.exit_code is not None:
            raise ValueError("process that did not start cannot have process identity or exit code")
        if self.timed_out:
            if not self.started or self.exit_code == 0 or self.failure_kind != "timeout":
                raise ValueError("timed out process requires timeout failure_kind and no success")
        if self.exit_code is not None and self.exit_code != 0 and self.failure_kind is None:
            raise ValueError("non-zero exit requires failure_kind")
        if self.exit_code == 0 and self.failure_kind is not None:
            raise ValueError("successful exit cannot have failure_kind")
        return self

    @property
    def succeeded(self) -> bool:
        return self.started and not self.timed_out and self.exit_code == 0


class OutputArtifact(StrictModel):
    path: RelativePath
    media_type: str
    sha256: SHA256
    slide_count: int = Field(gt=0)
    editability: Literal["native", "raster", "mixed", "not_applicable"]
    notes_included: bool
    limitations: list[str] = Field(default_factory=list)


class SlideBuildResult(StrictModel):
    slide_id: Identifier
    status: Literal["passed", "failed", "unverified"]
    artifact_paths: list[RelativePath] = Field(default_factory=list)
    errors: list[CLIError] = Field(default_factory=list)


class BuildResult(StrictModel):
    build_id: Identifier
    backend: Identifier
    status: Literal["passed", "failed", "unverified"]
    input_hash: SHA256
    outputs: list[OutputArtifact] = Field(default_factory=list)
    slide_results: list[SlideBuildResult] = Field(default_factory=list)
    expected_slide_ids: list[Identifier] = Field(default_factory=list)
    actual_slide_ids: list[Identifier] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    process_result: ProcessResult | None = None

    @model_validator(mode="after")
    def success_is_complete(self) -> BuildResult:
        if self.status == "passed":
            if not self.outputs:
                raise ValueError("passed build requires output artifacts")
            if self.process_result is None or not self.process_result.succeeded:
                raise ValueError("passed build requires a successful terminal process")
            if not self.expected_slide_ids or self.expected_slide_ids != self.actual_slide_ids:
                raise ValueError("passed build requires all expected slides in order")
            if any(output.slide_count != len(self.actual_slide_ids) for output in self.outputs):
                raise ValueError("output slide_count must match actual slides")
        return self


class RenderedSlide(StrictModel):
    path: RelativePath
    sha256: SHA256


class RenderDimensions(StrictModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class RenderResult(StrictModel):
    build_id: Identifier
    status: Literal["passed", "failed", "unverified"]
    slides: dict[Identifier, RenderedSlide] = Field(default_factory=dict)
    renderer_version: str | None = None
    font_manifest: list[str] = Field(default_factory=list)
    dimensions: RenderDimensions | None = None
    errors: list[CLIError] = Field(default_factory=list)


class QACheck(StrictModel):
    rule_id: Identifier
    slide_id: Identifier | None = None
    element_id: Identifier | None = None
    severity: Literal["error", "warning", "info"]
    status: Literal["passed", "failed", "unverified", "not_applicable"]
    evidence_refs: list[EvidenceRef] = Field(default_factory=list)
    explanation_vi: str
    suggested_action_vi: str


class QASummary(StrictModel):
    passed: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    unverified: int = Field(default=0, ge=0)
    not_applicable: int = Field(default=0, ge=0)


class QAReport(StrictModel):
    schema_version: SchemaVersion = "1.0"
    build_id: Identifier
    input_hash: SHA256
    checks: list[QACheck] = Field(default_factory=list)
    summary: QASummary = Field(default_factory=QASummary)
