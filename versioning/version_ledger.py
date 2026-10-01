"""
AksharSetu — Versioning Ledger (§11 of Implementation Guide)
Maintains version identifiers for all models, prompts, datasets, and pipeline stages.
The pinned Gemini model string lives here as data — NEVER hardcoded in prompts or business logic.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
import os

@dataclass(frozen=True)
class VersionConfig:
    textbook_edition: str = "2024.1"
    dataset_version: str = "v0.9.0-pilot"
    annotation_version: str = "v1.2.0"
    model_version: str = "aksharsetu-a-ocr-v0.1.0"
    prompt_version: str = "teacher-marathi-v2.1"
    teacher_model: str = os.getenv("GEMINI_TEACHER_MODEL", "gemini-3.7-flash")
    golden_corpus_version: str = "gc-v1.0.0"
    tts_version: str = "indic-f5-marathi-v1.0"
    schema_version: str = "2.0.0"

class VersionLedger:
    _current: VersionConfig = VersionConfig()
    _history: list = []

    @classmethod
    def get_current(cls) -> VersionConfig:
        return cls._current

    @classmethod
    def get_teacher_model(cls) -> str:
        """Returns pinned teacher model role identifier."""
        return cls._current.teacher_model

    @classmethod
    def update_teacher_model(cls, new_model_name: str, notes: str = "") -> None:
        """Controlled deprecation and upgrade workflow for Gemini teacher model (§4)."""
        old_config = cls._current
        cls._history.append({
            "previous_config": asdict(old_config),
            "updated_field": "teacher_model",
            "new_value": new_model_name,
            "notes": notes
        })
        cls._current = VersionConfig(
            textbook_edition=old_config.textbook_edition,
            dataset_version=old_config.dataset_version,
            annotation_version=old_config.annotation_version,
            model_version=old_config.model_version,
            prompt_version=old_config.prompt_version,
            teacher_model=new_model_name,
            golden_corpus_version=old_config.golden_corpus_version,
            tts_version=old_config.tts_version,
            schema_version=old_config.schema_version
        )

    @classmethod
    def get_provenance_meta(cls) -> Dict[str, Any]:
        """Provides metadata stamp for provenance chains."""
        return asdict(cls._current)
