from pydantic import Field
from typing import Literal

from .common import Identifier, RelativePath, SchemaVersion, StrictModel


class Budget(StrictModel):
    max_image_requests: int = Field(default=0, ge=0)
    max_repair_rounds: int = Field(default=0, ge=0)
    max_provider_cost: float | None = Field(default=None, ge=0)


class Limits(StrictModel):
    render_timeout_seconds: float = Field(default=120, gt=0)
    max_yaml_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    max_yaml_depth: int = Field(default=64, gt=0)
    max_yaml_nodes: int = Field(default=100_000, gt=0)


class ProjectConfig(StrictModel):
    schema_version: SchemaVersion = "1.0"
    project_id: Identifier
    title: str = Field(min_length=1)
    language: str = "vi"
    purpose: str | None = None
    authoring_mode: Literal["semantic", "html"] = "semantic"
    backend: Identifier = "pptx-native"
    profile_ref: str | None = None
    deck_path: RelativePath = "storyboard/deck.yaml"
    requested_outputs: list[Identifier] = Field(
        default_factory=lambda: ["pptx"], min_length=1
    )
    network_policy: Literal["offline", "local-only", "allowlist", "open"] = "local-only"
    approval_policy: Literal["interactive", "ask", "auto-safe", "full"] = "interactive"
    budget: Budget = Field(default_factory=Budget)
    limits: Limits = Field(default_factory=Limits)
