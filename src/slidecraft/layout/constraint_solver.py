"""Grid Constraint Solver for Slidecraft Layouts."""
from dataclasses import dataclass
from typing import List, Tuple
from slidecraft.ir.theme_schema import CanvasConfig


@dataclass
class BoundingBox:
    left_inch: float
    top_inch: float
    width_inch: float
    height_inch: float

    @property
    def right_inch(self) -> float:
        return self.left_inch + self.width_inch

    @property
    def bottom_inch(self) -> float:
        return self.top_inch + self.height_inch


class ConstraintSolver:
    """Calculates non-overlapping coordinate grids adhering to safe slide boundaries."""
    
    def __init__(self, canvas: CanvasConfig):
        self.canvas = canvas
        
        # Calculate safe workspace bounds
        self.safe_left = canvas.left_margin_inch
        self.safe_top = canvas.top_margin_inch
        self.safe_width = canvas.width_inch - canvas.left_margin_inch - canvas.right_margin_inch
        self.safe_height = canvas.height_inch - canvas.top_margin_inch - canvas.bottom_margin_inch
        self.safe_bottom = self.safe_top + self.safe_height
        
        # Header area standard reservation
        self.header_height = 1.15  # Title + category badge + margin below
        self.content_top = self.safe_top + self.header_height
        self.content_height = self.safe_height - self.header_height

    def get_header_box(self) -> BoundingBox:
        """Returns the header bounding box for Title and Category."""
        return BoundingBox(
            left_inch=self.safe_left,
            top_inch=self.safe_top,
            width_inch=self.safe_width,
            height_inch=self.header_height
        )

    def calculate_columns(self, num_cols: int, custom_top: float = None, custom_height: float = None) -> List[BoundingBox]:
        """Calculates horizontally distributed columns (e.g. 2-card, 3-card, 4-card)."""
        if num_cols < 1:
            raise ValueError("num_cols must be at least 1")
            
        top = custom_top if custom_top is not None else self.content_top
        height = custom_height if custom_height is not None else self.content_height
        
        total_gutter = (num_cols - 1) * self.canvas.gutter_inch
        col_width = (self.safe_width - total_gutter) / num_cols
        
        boxes = []
        for i in range(num_cols):
            left = self.safe_left + (i * (col_width + self.canvas.gutter_inch))
            boxes.append(BoundingBox(
                left_inch=left,
                top_inch=top,
                width_inch=col_width,
                height_inch=height
            ))
        return boxes

    def calculate_split_content_visual(self, content_ratio: float = 0.55) -> Tuple[BoundingBox, BoundingBox]:
        """Calculates a 2-part split layout: Content side + Visual Asset side."""
        content_width = (self.safe_width - self.canvas.gutter_inch) * content_ratio
        visual_width = (self.safe_width - self.canvas.gutter_inch) * (1.0 - content_ratio)
        
        content_box = BoundingBox(
            left_inch=self.safe_left,
            top_inch=self.content_top,
            width_inch=content_width,
            height_inch=self.content_height
        )
        visual_box = BoundingBox(
            left_inch=self.safe_left + content_width + self.canvas.gutter_inch,
            top_inch=self.content_top,
            width_inch=visual_width,
            height_inch=self.content_height
        )
        return content_box, visual_box

    def calculate_2x2_grid(self) -> List[BoundingBox]:
        """Calculates a 2x2 matrix grid (4 boxes)."""
        col_width = (self.safe_width - self.canvas.gutter_inch) / 2.0
        row_height = (self.content_height - self.canvas.gutter_inch) / 2.0
        
        boxes = []
        for row in range(2):
            for col in range(2):
                left = self.safe_left + col * (col_width + self.canvas.gutter_inch)
                top = self.content_top + row * (row_height + self.canvas.gutter_inch)
                boxes.append(BoundingBox(
                    left_inch=left,
                    top_inch=top,
                    width_inch=col_width,
                    height_inch=row_height
                ))
        return boxes
