"""Public core API for Agent Presentation Studio."""
from .models import DeckSpec, ProjectConfig
from .workspace import WorkspacePaths, init_project, load_deck, load_project, resolve_paths
__all__ = ["DeckSpec", "ProjectConfig", "WorkspacePaths", "init_project", "load_deck", "load_project", "resolve_paths"]
__version__ = "0.1.0"

