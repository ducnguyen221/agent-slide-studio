"""Theme and Styling Schemas for Slidecraft."""
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class PaletteConfig(BaseModel):
    background: str = Field(default="#FFFFFF", description="Slide background hex color")
    surface_card: str = Field(default="#F8FAFC", description="Card background hex color")
    surface_card_border: str = Field(default="#E2E8F0", description="Card border stroke color")
    primary_text: str = Field(default="#0F172A", description="Heading text color")
    secondary_text: str = Field(default="#475569", description="Body text color")
    accent_primary: str = Field(default="#2563EB", description="Primary brand accent color")
    accent_secondary: str = Field(default="#0D9488", description="Secondary accent color")
    accent_tertiary: str = Field(default="#F59E0B", description="Warning/Highlight accent color")
    muted_badge: str = Field(default="#EEF2F6", description="Tag/Badge background color")


class TypographyConfig(BaseModel):
    title_font: str = Field(default="Calibri", description="Font family for titles")
    body_font: str = Field(default="Calibri", description="Font family for body text")
    code_font: str = Field(default="Consolas", description="Font family for code snippets")
    title_size_pt: float = Field(default=28.0, description="Title font size in points")
    subtitle_size_pt: float = Field(default=16.0, description="Subtitle font size in points")
    body_size_pt: float = Field(default=13.0, description="Body font size in points")
    caption_size_pt: float = Field(default=10.5, description="Caption/metadata font size in points")
    kpi_size_pt: float = Field(default=36.0, description="Big number/metric font size in points")


class CanvasConfig(BaseModel):
    width_inch: float = Field(default=13.333, description="Slide width in inches (16:9 standard)")
    height_inch: float = Field(default=7.5, description="Slide height in inches (16:9 standard)")
    top_margin_inch: float = Field(default=0.8, description="Top safe margin in inches")
    bottom_margin_inch: float = Field(default=0.6, description="Bottom safe margin in inches")
    left_margin_inch: float = Field(default=0.8, description="Left safe margin in inches")
    right_margin_inch: float = Field(default=0.8, description="Right safe margin in inches")
    gutter_inch: float = Field(default=0.35, description="Space between cards/columns in inches")


class ThemeSchema(BaseModel):
    profile_name: str = Field(default="", description="Unique profile identifier")
    display_name: str = Field(default="", description="Human readable theme name")
    description: str = Field(default="", description="Theme description and usage purpose")
    canvas: CanvasConfig = Field(default_factory=CanvasConfig)
    palette: PaletteConfig = Field(default_factory=PaletteConfig)
    typography: TypographyConfig = Field(default_factory=TypographyConfig)

    @model_validator(mode="before")
    @classmethod
    def handle_name_alias(cls, data: dict):
        if isinstance(data, dict):
            if "name" in data and not data.get("profile_name"):
                data["profile_name"] = data["name"]
        return data
