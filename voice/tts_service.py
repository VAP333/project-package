"""
AksharSetu — Pluggable TTS Provider Abstraction & SpeechStylePlan (§0, Part 5 & §10)

Decouples Pedagogical Behavior from Voice Synthesis Providers.
Provider-neutral architecture:
Canonical Text
        ↓
Text / Punctuation Analysis (speech_normalizer)
        ↓
Pronunciation Resolver (pronunciation_resolver)
        ↓
Resolved Speech Representation (ResolvedPronunciation)
        ↓
Prosody Planner (SpeechStylePlan / ProsodyPlan)
        ↓
Provider Adapter (SarvamPronunciationAdapter / IndicF5PronunciationAdapter)
        ↓
TTS Provider (Sarvam / IndicF5)
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from voice.sarvam_tts import sarvam_tts_service, structure_marathi_prosody
from orchestrator.speech_normalizer import speech_normalizer
from corpus.pronunciation_kb import (
    ResolvedPronunciation,
    SarvamPronunciationAdapter,
    IndicF5PronunciationAdapter,
    pronunciation_resolver
)

@dataclass
class SpeechStylePlan:
    style: str = "canonical" # "canonical" | "teacher" | "transition" | "dialogue"
    intent: str = "reading" # "reading" | "explanation" | "guidance" | "question"
    language: str = "mr-IN"
    pace: float = 1.0
    energy: str = "warm" # "steady" | "warm" | "inquisitive" | "melodic"
    temperature: float = 0.68
    pause_before_ms: int = 0
    pause_after_ms: int = 250
    emphasis_terms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def for_canonical_reading(cls, pace: float = 1.0) -> "SpeechStylePlan":
        return cls(
            style="canonical",
            intent="reading",
            language="mr-IN",
            pace=pace,
            energy="steady",
            temperature=0.68,
            pause_before_ms=0,
            pause_after_ms=250
        )

    @classmethod
    def for_teacher_transition(cls, pace: float = 1.0) -> "SpeechStylePlan":
        return cls(
            style="transition",
            intent="guidance",
            language="mr-IN",
            pace=pace,
            energy="warm",
            temperature=0.72,
            pause_before_ms=250,
            pause_after_ms=350
        )

    @classmethod
    def for_teacher_explanation(cls, pace: float = 1.0, emphasis: Optional[List[str]] = None) -> "SpeechStylePlan":
        return cls(
            style="teacher",
            intent="explanation",
            language="mr-IN",
            pace=max(0.7, pace * 0.95), # slightly more deliberate teacher pace
            energy="warm",
            temperature=0.74,
            pause_before_ms=200,
            pause_after_ms=500,
            emphasis_terms=emphasis or []
        )

class BaseTTSProvider(ABC):
    """Abstract interface for all Marathi TTS synthesis backends."""
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def synthesize(
        self,
        text: str,
        plan: SpeechStylePlan,
        speaker: str = "shreya",
        resolved_pronunciations: Optional[List[ResolvedPronunciation]] = None
    ) -> Dict[str, Any]:
        """Synthesizes text into base64 audio according to SpeechStylePlan and resolved pronunciations."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if this provider is ready to synthesize."""
        pass


class SarvamTTSProvider(BaseTTSProvider):
    """
    Production / Demo Marathi TTS Provider using Sarvam AI bulbul:v3.
    Consumes provider-neutral ResolvedPronunciation and SpeechStylePlan.
    """
    def __init__(self):
        self.service = sarvam_tts_service

    @property
    def provider_name(self) -> str:
        return "sarvam"

    def is_available(self) -> bool:
        return bool(self.service.api_key)

    def synthesize(
        self,
        text: str,
        plan: SpeechStylePlan,
        speaker: str = "shreya",
        resolved_pronunciations: Optional[List[ResolvedPronunciation]] = None
    ) -> Dict[str, Any]:
        # 1. Translate via SarvamPronunciationAdapter
        adapted_text = SarvamPronunciationAdapter.adapt(text, resolved_pronunciations or [])

        # 2. Temperature and pace shaping
        effective_temp = plan.temperature
        if plan.style == "teacher":
            effective_temp = max(effective_temp, 0.72)
        elif plan.style == "canonical":
            effective_temp = min(effective_temp, 0.68)

        res = self.service.synthesize(
            text=adapted_text,
            pace=plan.pace,
            speaker=speaker,
            is_tutor=(plan.style in ("teacher", "transition")),
            temperature=effective_temp
        )
        res["provider"] = self.provider_name
        res["style"] = plan.style
        res["intent"] = plan.intent
        return res


class IndicF5TTSProviderWrapper(BaseTTSProvider):
    """
    Adapter wrapper for local experimental IndicF5 TTS provider.
    Consumes provider-neutral ResolvedPronunciation including reference audio conditioning.
    """
    def __init__(self):
        from voice.indicf5_provider import IndicF5TTSProvider
        self.provider = IndicF5TTSProvider()

    @property
    def provider_name(self) -> str:
        return "indicf5"

    def is_available(self) -> bool:
        return self.provider.is_available()

    def synthesize(
        self,
        text: str,
        plan: SpeechStylePlan,
        speaker: str = "teacher_marathi_1",
        resolved_pronunciations: Optional[List[ResolvedPronunciation]] = None
    ) -> Dict[str, Any]:
        # 1. Translate via IndicF5PronunciationAdapter
        adapted = IndicF5PronunciationAdapter.adapt(text, resolved_pronunciations or [])

        res = self.provider.synthesize(
            text=adapted["text"],
            pace=plan.pace,
            speaker=speaker,
            ref_audio_path=adapted.get("ref_audio")
        )
        res["provider"] = self.provider_name
        res["style"] = plan.style
        res["intent"] = plan.intent
        return res


class TTSService:
    """
    Central TTS Dispatcher and Provider Registry.
    Guarantees Tutor and Reader never directly couple to a single vendor.
    """
    def __init__(self):
        self.providers: Dict[str, BaseTTSProvider] = {}
        # Register standard providers
        self.register_provider(SarvamTTSProvider())
        self.register_provider(IndicF5TTSProviderWrapper())
        self.default_provider_name = "sarvam"

    def register_provider(self, provider: BaseTTSProvider):
        self.providers[provider.provider_name] = provider

    def get_provider(self, name: Optional[str] = None) -> BaseTTSProvider:
        prov_name = name or self.default_provider_name
        if prov_name not in self.providers:
            prov_name = self.default_provider_name
        return self.providers[prov_name]

    def synthesize(
        self,
        text: str,
        plan: Optional[SpeechStylePlan] = None,
        speaker: str = "shreya",
        provider_name: Optional[str] = None,
        resolved_pronunciations: Optional[List[ResolvedPronunciation]] = None
    ) -> Dict[str, Any]:
        style_plan = plan or SpeechStylePlan.for_canonical_reading()
        provider = self.get_provider(provider_name)
        return provider.synthesize(
            text=text,
            plan=style_plan,
            speaker=speaker,
            resolved_pronunciations=resolved_pronunciations
        )

    def list_providers(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": name,
                "available": prov.is_available(),
                "is_default": (name == self.default_provider_name)
            }
            for name, prov in self.providers.items()
        ]

tts_service = TTSService()
IndicF5TTSProvider = IndicF5TTSProviderWrapper
