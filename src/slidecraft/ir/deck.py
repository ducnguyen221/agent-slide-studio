"""Deck and Slide schemas for Slidecraft Canonical IR."""
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field
from slidecraft.ir.components import CardNode, MetricNode, ProcessStepNode, TimelineNode, AssetNode
from slidecraft.ir.theme_schema import ThemeSchema


class SlideLayoutArchetype(str, Enum):
    HERO_TITLE = "hero_title"
    CARDS_GRID = "cards_grid"
    PROCESS_FLOW = "process_flow"
    HORIZONTAL_TIMELINE = "horizontal_timeline"
    KPI_GRID = "kpi_grid"
    COMPARISON_2COL = "comparison_2col"
    SPLIT_CONTENT_VISUAL = "split_content_visual"
    QUOTE_SPOTLIGHT = "quote_spotlight"


class SlideSchema(BaseModel):
    slide_id: str = Field(..., description="Unique slide ID (e.g. 'slide_01')")
    title: str = Field(..., description="Slide main headline")
    subtitle: Optional[str] = Field(default=None, description="Secondary context header")
    category_badge: Optional[str] = Field(default=None, description="Topic/Chapter indicator on top")
    archetype: SlideLayoutArchetype = Field(default=SlideLayoutArchetype.CARDS_GRID)
    
    # Component data payload
    cards: Optional[List[CardNode]] = None
    metrics: Optional[List[MetricNode]] = None
    process_steps: Optional[List[ProcessStepNode]] = None
    timeline_nodes: Optional[List[TimelineNode]] = None
    
    # Visual illustration asset
    visual_asset: Optional[AssetNode] = None
    
    # Pedagogical & Presenter metadata
    speaker_notes: Optional[str] = Field(default=None, description="Notes for the speaker")
    bloom_verb: Optional[str] = Field(default=None, description="Bloom's taxonomy verb (e.g. 'Analyze', 'Understand')")
    objective_id: Optional[str] = Field(default=None, description="Course objective linkage")


class DeckSchema(BaseModel):
    title: str = Field(..., description="Presentation title")
    subject: str = Field(..., description="Course subject / topic")
    target_audience: str = Field(default="General", description="Audience level (Undergraduate, Professional, etc.)")
    profile_name: str = Field(default="academic_light", description="Theme profile to apply")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    slides: List[SlideSchema] = Field(default_factory=list)
