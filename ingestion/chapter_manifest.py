"""
AksharSetu — Explicit Chapter Manifest & Reader Hierarchy (§3 & Part 1 of Specification)

Treats:
PDF document -> chapter -> pages -> physical regions -> learning units -> spoken sequence
as one continuous hierarchy.

Guarantees:
- Explicit manifest with complete page, region, learning unit, and ordering inventory.
- Preserves separation of:
  1. PHYSICAL ORDER (2D layout coordinates)
  2. PEDAGOGICAL ORDER (textbook pedagogical narrative sequence)
  3. SPOKEN ORDER (canonical reading stream for audio presentation)
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

@dataclass
class PageSummary:
    page_id: str
    pdf_page: int
    printed_page: Optional[int]
    total_regions: int
    physical_region_ids: List[str]
    pedagogical_region_ids: List[str]

@dataclass
class ChapterManifest:
    chapter_id: str
    document_id: str
    title: str
    marathi_title: str
    subject: str
    pdf_start_page: int
    pdf_end_page: int
    printed_start_page: int
    printed_end_page: int
    total_pages: int
    total_physical_regions: int
    total_pedagogical_regions: int
    page_ids: List[str]
    pages_summary: List[Dict[str, Any]]
    learning_unit_ids: List[str]
    physical_region_ids: List[str]
    pedagogical_order: List[str]
    spoken_order: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
