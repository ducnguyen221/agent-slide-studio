from pathlib import PurePosixPath, PureWindowsPath

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field
from typing import Annotated, Literal

SchemaVersion = Literal["1.0"]
Identifier = Annotated[
    str, Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$", min_length=1, max_length=64)
]
SemVer = Annotated[str, Field(pattern=r"^\d+\.\d+\.\d+$")]
SHA256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]


def _relative_path(value: object) -> object:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ValueError("path must be a normalized relative POSIX path")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or PureWindowsPath(value).is_absolute()
        or path.as_posix() != value
    ):
        raise ValueError("path must be relative and traversal-free")
    return value


RelativePath = Annotated[str, BeforeValidator(_relative_path)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class EvidenceRef(StrictModel):
    ref: str
    sha256: SHA256 | None = None
    note: str | None = None


class ObservedValue(StrictModel):
    value: str | float | int | bool
    origin: Literal["measured", "inferred", "user-specified"]
    confidence: float = Field(default=1.0, ge=0, le=1)
    evidence: list[EvidenceRef] = Field(default_factory=list)
