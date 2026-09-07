from typing import Any, Literal
from pydantic import Field
from .common import Identifier, SchemaVersion, StrictModel
class ProjectConfig(StrictModel):
    schema_version: SchemaVersion = "1.0"
    project_id: Identifier
    title: str = Field(min_length=1)
    language: str = "vi"
    purpose: str | None = None
    authoring_mode: Literal["semantic", "html"] = "semantic"
    backend: Identifier = "pptx-native"
    profile_ref: str | None = None
    deck_path: str = "storyboard/deck.yaml"
    requested_outputs: list[str] = Field(default_factory=lambda: ["pptx"])
    network_policy: Literal["offline", "allowlist", "open"] = "offline"
    approval_policy: Literal["ask", "auto-safe", "full"] = "ask"
    budget: dict[str, float] = Field(default_factory=dict)
    limits: dict[str, Any] = Field(default_factory=dict)

