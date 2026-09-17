"""Component and Node models for Slidecraft Canonical IR."""
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ShapeRole(str, Enum):
    CARD = "card"
    METRIC = "metric"
    TIMELINE_NODE = "timeline_node"
    PROCESS_STEP = "process_step"
    BADGE = "badge"
    QUOTE = "quote"
    ASSET_SLOT = "asset_slot"


class CardNode(BaseModel):
    title: str = Field(..., description="Card headline or key concept")
    subtitle: Optional[str] = Field(default=None, description="Optional supporting subtitle")
    points: List[str] = Field(default_factory=list, description="Bullet points (max 4-5 recommended)")
    badge_text: Optional[str] = Field(default=None, description="Category tag on top of card")
    accent_color: Optional[str] = Field(default=None, description="Custom accent border/header color")
    icon_name: Optional[str] = Field(default=None, description="Icon symbol key (e.g. check, lightning, brain)")


class MetricNode(BaseModel):
    value: str = Field(..., description="KPI/Highlight Value (e.g. '98.5%', '3.4x', '150ms')")
    label: str = Field(..., description="Primary metric label (e.g. 'Accuracy Rate')")
    subtitle: Optional[str] = Field(default=None, description="Secondary context or delta (e.g. '+12% vs baseline')")
    icon_name: Optional[str] = Field(default=None)


class ProcessStepNode(BaseModel):
    step_number: int = Field(..., description="Sequential step number (1, 2, 3...)")
    title: str = Field(..., description="Step title / Action name")
    description: str = Field(..., description="Brief step explanation")
    is_active: bool = Field(default=True, description="Whether this step is in focus")


class TimelineNode(BaseModel):
    time_label: str = Field(..., description="Phase or Year label (e.g. 'Phase 1', 'Q3 2026')")
    title: str = Field(..., description="Milestone title")
    description: str = Field(..., description="Key deliverable or event summary")
    tag: Optional[str] = Field(default=None, description="Status or category tag")


class AssetSlotType(str, Enum):
    HERO = "hero"
    SPOT_ICON = "spot_icon"
    CARD_ILLUSTRATION = "card_illustration"
    BACKGROUND_ACCENT = "background_accent"


class AssetNode(BaseModel):
    asset_id: str = Field(..., description="Unique ID for this visual asset")
    prompt_subject: str = Field(..., description="The conceptual subject to generate (e.g. 'deep learning neural graph')")
    slot_type: AssetSlotType = Field(default=AssetSlotType.HERO)
    aspect_ratio: str = Field(default="16:9", description="Target aspect ratio ('16:9', '1:1', '4:3')")
    alt_text: str = Field(default="", description="Accessibility alt-text description")
    file_path: Optional[str] = Field(default=None, description="Resolved local path to generated image")
