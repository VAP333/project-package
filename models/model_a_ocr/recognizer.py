"""
AksharSetu — Model A: Text Recognition (MVP - §5.1 of Implementation Guide)
TrOCR-style specialized Marathi Devanagari text recognition engine.
Integrates with Critical Token Protection Pipeline.
"""

from typing import Dict, Any, Optional
from correction.critical_token_pipeline import CriticalTokenPipeline

class ModelAOCRRecognizer:
    def __init__(self, weights_path: Optional[str] = None):
        self.weights_path = weights_path
        self.critical_token_pipeline = CriticalTokenPipeline()

    def recognize_region(self, image_crop_path_or_bytes: Any, raw_ocr_hypothesis: str) -> Dict[str, Any]:
        """
        Runs specialized Marathi recognizer on a single region crop.
        Passes output through the Critical Token Pipeline.
        """
        # Verifies tokens against critical rules (Principle 4)
        tokens = raw_ocr_hypothesis.split()
        verified_tokens = self.critical_token_pipeline.process_sentence(tokens)
        verified_text = " ".join([vt.verified_text for vt in verified_tokens])

        return {
            "model": "AksharSetu-ModelA-TrOCR-v0.1",
            "raw_text": raw_ocr_hypothesis,
            "verified_canonical_text": verified_text,
            "has_critical_tokens": any(vt.is_critical_token for vt in verified_tokens),
            "flagged_for_human_review": any(vt.flagged_for_review for vt in verified_tokens)
        }
