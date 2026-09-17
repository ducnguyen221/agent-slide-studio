from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from presentation_studio.models import BackendCapabilities, BuildInput, BuildResult
from presentation_studio.workspace import WorkspacePaths


@dataclass(frozen=True)
class BackendIssue:
    code: str
    message_vi: str
    slide_id: str | None = None
    element_id: str | None = None
    evidence_ref: str | None = None


class BackendValidationError(ValueError):
    def __init__(self, issues: list[BackendIssue]):
        self.issues = tuple(issues)
        super().__init__("; ".join(issue.message_vi for issue in issues))


class PresentationBackend(ABC):
    """Hợp đồng tối thiểu cho backend biên dịch presentation."""

    @abstractmethod
    def capabilities(self) -> BackendCapabilities:
        raise NotImplementedError

    @abstractmethod
    def build(self, build_input: BuildInput, paths: WorkspacePaths) -> BuildResult:
        raise NotImplementedError
