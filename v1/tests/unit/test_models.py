import pytest
from pydantic import ValidationError

from presentation_studio.models import (
    AssetManifest,
    BackendCapabilities,
    BuildInput,
    BuildResult,
    CLIError,
    CLIResult,
    DeckSpec,
    OutputArtifact,
    ProcessResult,
    Profile,
    ProjectConfig,
    QAReport,
    TemplateDraft,
)


SHA_A = "a" * 64
SHA_B = "b" * 64


def _deck() -> DeckSpec:
    return DeckSpec(
        title="Deck",
        audience="Lãnh đạo",
        purpose="Báo cáo",
        slides=[
            {
                "slide_id": "s01",
                "title": "Một",
                "layout_ref": "builtin:content@1.0.0",
                "elements": [
                    {"element_id": "e01", "kind": "text", "content": "Nội dung"}
                ],
            }
        ],
    )


def _process(
    *, exit_code: int = 0, timed_out: bool = False, failure_kind: str | None = None
) -> ProcessResult:
    return ProcessResult(
        started=True,
        pid=12,
        started_at="2026-01-01T00:00:00Z",
        elapsed_seconds=1,
        exit_code=exit_code,
        timed_out=timed_out,
        failure_kind=failure_kind,
    )


def _artifact() -> OutputArtifact:
    return OutputArtifact(
        path="exports/x.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        sha256=SHA_A,
        slide_count=1,
        editability="native",
        notes_included=True,
    )


def test_project_and_deck_are_strict_and_ids_are_validated() -> None:
    project = ProjectConfig(project_id="bao-cao-quy", title="Báo cáo quý")
    assert project.schema_version == "1.0"
    with pytest.raises(ValidationError):
        ProjectConfig(project_id="../escape", title="x")
    with pytest.raises(ValidationError):
        ProjectConfig(project_id="ok", title="x", secret="forbidden")
    with pytest.raises(ValidationError):
        DeckSpec(title="Deck", audience="Lãnh đạo", purpose="Báo cáo", slides=[])


def test_deck_rejects_duplicate_slide_ids_unknown_fields_and_missing_sources() -> None:
    slide = {
        "slide_id": "s01",
        "title": "Một",
        "layout_ref": "builtin:content@1.0.0",
        "elements": [],
    }
    with pytest.raises(ValidationError):
        DeckSpec(title="Deck", audience="A", purpose="P", slides=[slide, slide])
    with pytest.raises(ValidationError):
        DeckSpec(
            title="Deck",
            audience="A",
            purpose="P",
            slides=[{**slide, "source_refs": ["missing"]}],
        )
    with pytest.raises(ValidationError):
        DeckSpec(
            title="Deck",
            audience="A",
            purpose="P",
            slides=[
                {
                    **slide,
                    "elements": [
                        {"element_id": "e01", "kind": "magic", "content": "x"}
                    ],
                }
            ],
        )
    with pytest.raises(ValidationError):
        DeckSpec(
            title="Deck",
            audience="A",
            purpose="P",
            slides=[
                {
                    **slide,
                    "elements": [
                        {
                            "element_id": "e01",
                            "kind": "text",
                            "content": "x",
                            "unknown": 1,
                        }
                    ],
                }
            ],
        )


def test_profile_requires_evidence_for_every_inferred_value() -> None:
    with pytest.raises(ValidationError):
        Profile(
            id="editorial-light",
            version="1.0.0",
            display_name="Sáng biên tập",
            description="Trung tính",
            composition={"density": {"value": "airy", "origin": "inferred"}},
        )


@pytest.mark.parametrize("exit_code", [1, 7, -1])
def test_cli_result_rejects_unsupported_exit_codes(exit_code: int) -> None:
    with pytest.raises(ValidationError):
        CLIResult(
            command="build",
            status="failed",
            exit_code=exit_code,
            errors=[CLIError(code="X", message_vi="x")],
        )


def test_cli_result_status_errors_and_exit_code_are_consistent() -> None:
    with pytest.raises(ValidationError):
        CLIResult(command="build", status="passed", exit_code=3)
    with pytest.raises(ValidationError):
        CLIResult(command="build", status="failed", exit_code=2)
    with pytest.raises(ValidationError):
        CLIResult(
            command="build",
            status="passed",
            exit_code=0,
            errors=[CLIError(code="X", message_vi="x")],
        )


@pytest.mark.parametrize(
    "path",
    [
        "../deck.yaml",
        "C:/deck.yaml",
        "/deck.yaml",
        "storyboard\\deck.yaml",
        "storyboard//deck.yaml",
        "./deck.yaml",
    ],
)
def test_paths_are_relative_and_normalized(path: str) -> None:
    with pytest.raises(ValidationError):
        ProjectConfig(project_id="ok", title="x", deck_path=path)


def test_process_result_invariants_reject_false_success() -> None:
    with pytest.raises(ValidationError):
        ProcessResult(started=True, elapsed_seconds=1, exit_code=0)
    with pytest.raises(ValidationError):
        ProcessResult(started=False, elapsed_seconds=1, pid=12)
    with pytest.raises(ValidationError):
        _process(exit_code=0, timed_out=True, failure_kind="timeout")
    with pytest.raises(ValidationError):
        _process(exit_code=2)


def test_build_result_invariants_reject_false_success() -> None:
    common = {
        "build_id": "b1",
        "backend": "pptx-native",
        "status": "passed",
        "input_hash": SHA_B,
        "process_result": _process(),
        "expected_slide_ids": ["s01"],
        "actual_slide_ids": ["s01"],
        "slide_results": [{"slide_id": "s01", "status": "passed"}],
    }
    with pytest.raises(ValidationError):
        BuildResult(**common, outputs=[])
    with pytest.raises(ValidationError):
        BuildResult(**{**common, "actual_slide_ids": []}, outputs=[_artifact()])
    with pytest.raises(ValidationError):
        BuildResult(
            **{
                **common,
                "process_result": _process(exit_code=2, failure_kind="engine"),
            },
            outputs=[_artifact()],
        )
    with pytest.raises(ValidationError):
        BuildResult(**{**common, "process_result": None}, outputs=[_artifact()])
    with pytest.raises(ValidationError):
        BuildResult(
            **{
                **common,
                "expected_slide_ids": ["s01", "s01"],
                "actual_slide_ids": ["s01", "s01"],
                "slide_results": [
                    {"slide_id": "s01", "status": "passed"},
                    {"slide_id": "s01", "status": "passed"},
                ],
            },
            outputs=[{**_artifact().model_dump(), "slide_count": 2}],
        )


@pytest.mark.parametrize(
    "slide_results",
    [
        [],
        [{"slide_id": "s01", "status": "failed"}],
        [{"slide_id": "s01", "status": "unverified"}],
        [
            {"slide_id": "s01", "status": "passed"},
            {"slide_id": "s01", "status": "passed"},
        ],
    ],
)
def test_passed_build_requires_one_passed_result_per_expected_slide(
    slide_results: list[dict[str, str]],
) -> None:
    common = {
        "build_id": "b1",
        "backend": "pptx-native",
        "status": "passed",
        "input_hash": SHA_B,
        "process_result": _process(),
        "expected_slide_ids": ["s01"],
        "actual_slide_ids": ["s01"],
        "outputs": [_artifact()],
    }

    with pytest.raises(ValidationError):
        BuildResult(**common, slide_results=slide_results)


def test_passed_build_accepts_complete_ordered_slide_results() -> None:
    result = BuildResult(
        build_id="b1",
        backend="pptx-native",
        status="passed",
        input_hash=SHA_B,
        process_result=_process(),
        expected_slide_ids=["s01"],
        actual_slide_ids=["s01"],
        slide_results=[{"slide_id": "s01", "status": "passed"}],
        outputs=[_artifact()],
    )

    assert result.status == "passed"


def test_nested_contracts_are_strict_and_typed() -> None:
    capabilities = {
        "backend_id": "pptx-native",
        "adapter_version": "1.0.0",
        "available": True,
        "supported_inputs": ["semantic"],
        "supported_outputs": ["pptx"],
    }
    with pytest.raises(ValidationError):
        BackendCapabilities(**capabilities, surprise=True)
    with pytest.raises(ValidationError):
        QAReport(
            build_id="b",
            input_hash=SHA_A,
            checks=[
                {
                    "rule_id": "r",
                    "severity": "error",
                    "status": "failed",
                    "explanation_vi": "x",
                    "suggested_action_vi": "y",
                    "unknown": 1,
                }
            ],
        )
    with pytest.raises(ValidationError):
        AssetManifest(
            assets=[
                {
                    "id": "a",
                    "relative_path": "a.png",
                    "sha256": SHA_A,
                    "media_type": "image/png",
                    "role": "hero",
                    "alt_text": "x",
                    "source_kind": "public",
                    "rights": {"surprise": True},
                }
            ]
        )
    draft = TemplateDraft(source_ref="source.pptx", source_sha256=SHA_A)
    assert draft.uncertain == []


def test_build_input_uses_contract_models_instead_of_untyped_dicts() -> None:
    with pytest.raises(ValidationError):
        BuildInput(
            project={"project_id": "p", "title": "P", "unknown": 1},
            deck=_deck(),
            input_hash=SHA_A,
        )
