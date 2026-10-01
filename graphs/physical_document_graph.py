"""
AksharSetu — Physical Document Graph (§3.1 of Implementation Guide)
Answers: "Where is everything?"
Models spatial layout, bounding boxes, parent-child hierarchies, and adjacent navigation links.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set
from enum import Enum

class RegionType(str, Enum):
    HEADING = "heading"
    SUBHEADING = "subheading"
    PARAGRAPH = "paragraph"
    POETRY = "poetry"
    DIALOGUE = "dialogue"
    FIGURE = "figure"
    MAP = "map"
    CAPTION = "caption"
    TABLE = "table"
    INFORMATION_BOX = "information_box"
    DISCUSSION_BOX = "discussion_box"
    ACTIVITY = "activity"
    EXAMPLE = "example"
    DEFINITION = "definition"
    EXERCISE = "exercise"
    QUESTION = "question"
    ANSWER = "answer"
    SUPPLEMENTARY_CONTENT = "supplementary_content"
    HEADER = "header"
    FOOTER = "footer"
    PAGE_NUMBER = "page_number"
    DECORATIVE_ELEMENT = "decorative_element"
    UNKNOWN = "unknown"

@dataclass
class PhysicalRegion:
    region_id: str
    page_id: str
    bbox: List[float] # [x0, y0, x1, y1] points
    region_type: RegionType
    native_text: str
    source_coordinates: Dict[str, Any] = field(default_factory=dict)
    visual_content_path: Optional[str] = None
    parent_region_id: Optional[str] = None
    adjacent_region_ids: List[str] = field(default_factory=list)
    preceding_region_id: Optional[str] = None
    following_region_id: Optional[str] = None
    physical_order_index: int = 0
    reading_order_index: int = 0
    caption_target_id: Optional[str] = None
    semantic_role: Optional[str] = None
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["region_type"] = self.region_type.value
        return data

@dataclass
class PhysicalDocumentGraph:
    page_id: str
    source_hash: str
    regions: Dict[str, PhysicalRegion] = field(default_factory=dict)
    physical_order: List[str] = field(default_factory=list)
    pedagogical_order: List[str] = field(default_factory=list)
    reading_order: List[str] = field(default_factory=list) # Kept for backward compatibility

    def add_region(self, region: PhysicalRegion) -> None:
        self.regions[region.region_id] = region
        if region.region_id not in self.reading_order:
            self.reading_order.append(region.region_id)
        if region.region_id not in self.physical_order:
            self.physical_order.append(region.region_id)
        if region.region_id not in self.pedagogical_order:
            self.pedagogical_order.append(region.region_id)

    def set_physical_order(self, ordered_region_ids: List[str]) -> None:
        self.physical_order = [rid for rid in ordered_region_ids if rid in self.regions]
        for idx, rid in enumerate(self.physical_order):
            self.regions[rid].physical_order_index = idx

    def set_reading_order(self, ordered_region_ids: List[str]) -> None:
        valid_ids = [rid for rid in ordered_region_ids if rid in self.regions]
        self.pedagogical_order = valid_ids
        self.reading_order = valid_ids
        for idx, rid in enumerate(self.pedagogical_order):
            self.regions[rid].reading_order_index = idx
            self.regions[rid].preceding_region_id = self.pedagogical_order[idx - 1] if idx > 0 else None
            self.regions[rid].following_region_id = self.pedagogical_order[idx + 1] if idx < len(self.pedagogical_order) - 1 else None

    def get_ordered_regions(self) -> List[PhysicalRegion]:
        order = self.pedagogical_order if self.pedagogical_order else self.reading_order
        return [self.regions[rid] for rid in order if rid in self.regions]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "source_hash": self.source_hash,
            "physical_order": self.physical_order,
            "pedagogical_order": self.pedagogical_order,
            "reading_order": self.reading_order,
            "regions": {k: v.to_dict() for k, v in self.regions.items()}
        }
