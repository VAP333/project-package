"""
AksharSetu — Golden Corpus Schema & Verification State Machine (§3.3 of Implementation Guide)
Enforces three-tier promotion:
  1. TEACHER_OUTPUT: Hypothesis from Gemini Flash teacher (unverified, never in production cache)
  2. VERIFIED_TRAINING_SAMPLE: Machine-verified via critical-token / dictionary pipeline or peer review
  3. GOLDEN_TRUTH: Subject expert / teacher confirmed ground truth. Only this tier is production truth.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class VerificationTier(str, Enum):
    TEACHER_OUTPUT = "TEACHER_OUTPUT"
    VERIFIED_TRAINING_SAMPLE = "VERIFIED_TRAINING_SAMPLE"
    GOLDEN_TRUTH = "GOLDEN_TRUTH"

class VerificationSource(str, Enum):
    GEMINI_TEACHER = "GEMINI_TEACHER"
    CRITICAL_TOKEN_VERIFIER = "CRITICAL_TOKEN_VERIFIER"
    HUMAN_SUBJECT_EXPERT = "HUMAN_SUBJECT_EXPERT"
    TEACHER_INSPECTION = "TEACHER_INSPECTION"

class PromotionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass

@dataclass
class GoldenCorpusRecord:
    document_id: str
    edition: str
    book: str
    subject: str
    chapter: str
    page: int
    region_id: str
    source_hash: str
    canonical_text: str
    region_type: str
    coordinates: List[float] # [x0, y0, x1, y1] normalized or points
    reading_order: int
    semantic_relations: List[Dict[str, Any]] = field(default_factory=list)
    learning_units: List[str] = field(default_factory=list)
    verification_status: VerificationTier = VerificationTier.TEACHER_OUTPUT
    verification_source: VerificationSource = VerificationSource.GEMINI_TEACHER
    model_version: str = "v1.0.0"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    provenance: Dict[str, Any] = field(default_factory=dict)
    reviewer_notes: Optional[str] = None

    def promote_to_verified_sample(self, verifier_source: VerificationSource, notes: str = "") -> None:
        """Promotes Teacher Output hypothesis to Verified Training Sample."""
        if self.verification_status != VerificationTier.TEACHER_OUTPUT:
            raise PromotionError(
                f"Cannot promote to VERIFIED_TRAINING_SAMPLE from current status: {self.verification_status}"
            )
        self.verification_status = VerificationTier.VERIFIED_TRAINING_SAMPLE
        self.verification_source = verifier_source
        self.reviewer_notes = notes
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def promote_to_golden_truth(self, expert_id: str, notes: str = "") -> None:
        """
        Promotes to GOLDEN_TRUTH. Only authorized human teachers/subject experts
        or verified ground truth from authoring authority can perform this.
        """
        if self.verification_status not in (VerificationTier.TEACHER_OUTPUT, VerificationTier.VERIFIED_TRAINING_SAMPLE):
            raise PromotionError(f"Cannot promote to GOLDEN_TRUTH from {self.verification_status}")
        
        self.verification_status = VerificationTier.GOLDEN_TRUTH
        self.verification_source = VerificationSource.HUMAN_SUBJECT_EXPERT
        self.reviewer_notes = f"Approved by {expert_id}: {notes}"
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def demote_or_reject(self, reason: str) -> None:
        """Demotes back to hypothesis or flags for manual re-annotation."""
        self.verification_status = VerificationTier.TEACHER_OUTPUT
        self.reviewer_notes = f"Flagged/Demoted: {reason}"
        self.timestamp = datetime.now(timezone.utc).isoformat()

    @property
    def is_production_truth(self) -> bool:
        """Principle 5: Only GOLDEN_TRUTH is production truth."""
        return self.verification_status == VerificationTier.GOLDEN_TRUTH

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["verification_status"] = self.verification_status.value
        data["verification_source"] = self.verification_source.value
        data["is_production_truth"] = self.is_production_truth
        return data
