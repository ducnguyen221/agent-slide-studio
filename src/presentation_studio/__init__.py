"""Public core API for Agent Presentation Studio."""

from .models import DeckSpec, ProfileLock, ProjectConfig
from .workspace import (
    WorkspacePaths,
    init_project,
    load_deck,
    load_project,
    resolve_paths,
    resolve_profile,
)

__all__ = [
    "DeckSpec",
    "ProfileLock",
    "ProjectConfig",
    "WorkspacePaths",
    "init_project",
    "load_deck",
    "load_project",
    "resolve_paths",
    "resolve_profile",
]
__version__ = "0.1.0"
