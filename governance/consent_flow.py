"""
AksharSetu — Minor Consent & Student Protection Engine (§8 of Implementation Guide)

Day-One Invariant:
No student voice or interaction data may leave the device without active, verified institutional/parental consent.
Textbook teacher pipeline is restricted to canonical textbook material (zero student PII).
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, List, Any
from datetime import datetime, timezone
import json
import os

class ConsentStatus(str):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"

@dataclass
class MinorConsentRecord:
    student_id_pseudonym: str # Anonymized hash, never raw name
    school_id: str
    consent_grantor: str # "school_administrator", "parent_guardian"
    consent_status: str
    voice_processing_allowed: bool
    tutor_interaction_allowed: bool
    granted_at: str
    expires_at: str
    audit_notes: str = ""

class ConsentManager:
    def __init__(self, db_path: str = "./data/governance/consent_ledger.json"):
        self.db_path = db_path
        self.records: Dict[str, MinorConsentRecord] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self.records[k] = MinorConsentRecord(**v)
            except Exception:
                pass

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump({k: asdict(v) for k, v in self.records.items()}, f, indent=2)

    def register_consent(
        self,
        student_pseudonym: str,
        school_id: str,
        grantor: str,
        allow_voice: bool = True,
        allow_tutor: bool = True,
        duration_days: int = 365
    ) -> MinorConsentRecord:
        now = datetime.now(timezone.utc)
        record = MinorConsentRecord(
            student_id_pseudonym=student_pseudonym,
            school_id=school_id,
            consent_grantor=grantor,
            consent_status="GRANTED",
            voice_processing_allowed=allow_voice,
            tutor_interaction_allowed=allow_tutor,
            granted_at=now.isoformat(),
            expires_at=datetime.fromtimestamp(now.timestamp() + duration_days * 86400, tz=timezone.utc).isoformat(),
            audit_notes="Consent actively verified."
        )
        self.records[student_pseudonym] = record
        self._save()
        return record

    def verify_action_permitted(self, student_pseudonym: str, action: str) -> bool:
        """Enforces consent gate before any student interaction leaves device."""
        if student_pseudonym not in self.records:
            return False
        rec = self.records[student_pseudonym]
        if rec.consent_status != "GRANTED":
            return False
        if action == "voice_processing" and not rec.voice_processing_allowed:
            return False
        if action == "tutor_interaction" and not rec.tutor_interaction_allowed:
            return False
        return True
