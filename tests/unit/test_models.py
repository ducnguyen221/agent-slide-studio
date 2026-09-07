import pytest
from pydantic import ValidationError

from presentation_studio.models import CLIResult, DeckSpec, Profile, ProjectConfig


def test_project_and_deck_are_strict_and_ids_are_validated() -> None:
    project = ProjectConfig(project_id="bao-cao-quy", title="Báo cáo quý")
    assert project.schema_version == "1.0"
    with pytest.raises(ValidationError):
        ProjectConfig(project_id="../escape", title="x")
    with pytest.raises(ValidationError):
        ProjectConfig(project_id="ok", title="x", secret="forbidden")
    with pytest.raises(ValidationError):
        DeckSpec(title="Deck", audience="Lãnh đạo", purpose="Báo cáo", slides=[])


def test_deck_rejects_duplicate_slide_ids() -> None:
    slide = {"slide_id": "s01", "title": "Một", "layout": "content"}
    with pytest.raises(ValidationError):
        DeckSpec(title="Deck", audience="A", purpose="P", slides=[slide, slide])


def test_profile_requires_evidence_for_inferred_values() -> None:
    with pytest.raises(ValidationError):
        Profile(
            id="editorial-light", version="1.0.0", display_name="Sáng biên tập",
            description="Trung tính", palette_by_role={"accent": {"value": "#123456", "origin": "inferred"}},
        )

def test_cli_result_status_and_exit_code_cannot_disagree() -> None:
    with pytest.raises(ValidationError):
        CLIResult(command="build", status="passed", exit_code=3)
    with pytest.raises(ValidationError):
        CLIResult(command="build", status="failed", exit_code=0)
