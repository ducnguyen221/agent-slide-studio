from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field
SchemaVersion = Literal["1.0"]
Identifier = Annotated[str, Field(pattern=r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$", min_length=1, max_length=80)]
class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)
class EvidenceRef(StrictModel):
    ref: str
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    note: str | None = None
class ObservedValue(StrictModel):
    value: str | float | int | bool
    origin: Literal["measured", "inferred", "user-specified"]
    confidence: float = Field(default=1.0, ge=0, le=1)
    evidence: list[EvidenceRef] = Field(default_factory=list)

