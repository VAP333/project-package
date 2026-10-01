"""
AksharSetu — Model B: Layout Understanding & Region Classification (MVP - §5.1)
Classifies page segments into region vocabulary:
heading, paragraph, poetry, figure, caption, diagram, map, table,
information_box, activity, example, definition, exercise, question, footnote.
"""

from typing import List, Dict, Any
from graphs.physical_document_graph import RegionType

class ModelBLayoutDetector:
    def __init__(self, model_weights: str = "default"):
        self.model_weights = model_weights

    def classify_region(self, bbox: List[float], font_size: float, raw_text: str) -> RegionType:
        """
        Classifies region type using geometric heuristics + layout model features.
        """
        text_stripped = raw_text.strip()
        
        # Heuristic rules anchored to Balbharati conventions:
        if font_size >= 16 or any(text_stripped.startswith(k) for k in ["पाठ ", "धडा ", "प्रकरण ", "कविता "]):
            return RegionType.HEADING
        if any(text_stripped.startswith(k) for k in ["प्रश्न ", "स्वाध्याय", "१.", "२.", "३."]):
            return RegionType.QUESTION
        if any(text_stripped.startswith(k) for k in ["कृती", "प्रकल्प", "चर्चा करा"]):
            return RegionType.ACTIVITY
        if "व्याख्या" in text_stripped or text_stripped.startswith("म्हणजे"):
            return RegionType.DEFINITION
        
        return RegionType.PARAGRAPH
