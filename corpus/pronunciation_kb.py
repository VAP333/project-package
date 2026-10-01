"""
AksharSetu — Persistent Pronunciation Knowledge Base & Resolver (§7, §8, §9, §10, §12)

HARDENING INVARIANTS:
1. CANONICAL SPELLING IMMUTABILITY:
   Displayed textbook text is NEVER modified. Pronunciation phonetic representations
   and reference audio are stored separately and resolved strictly for TTS.
2. REFERENCE AUDIO PRESERVATION:
   When voice pronunciation is taught by an admin, the reference audio is saved, versioned,
   and linked to the entry. History is preserved upon re-recording.
3. ASR IS LEXICAL CONFIRMATION, NOT PRONUNCIATION AUTHORITY:
   ASR confirms what word was said; phonetic representation and reference audio provide the acoustic evidence.
4. PROVIDER-NEUTRAL RESOLVED PRONUNCIATION:
   ResolvedPronunciation dataclass feeds provider adapters (Sarvam, IndicF5, future models).
5. PUNCTUATION SANITIZATION:
   Pre-TTS normalization guarantees punctuation is converted to acoustic cadence, never spoken words.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

from orchestrator.speech_normalizer import speech_normalizer

PRONUNCIATION_DB_PATH = os.path.join("corpus", "pronunciation_kb.json")
PRONUNCIATION_AUDIO_DIR = os.path.join("data", "audio", "pronunciations")

@dataclass
class PronunciationEntry:
    canonical_text: str # Exact Marathi textbook spelling (e.g. "सिंहगडाजवळ", "नळदुर्ग")
    language: str = "mr-IN"
    preferred_pronunciation: str = "" # Phonetic respelling or Devanagari guide (e.g. "सिंह-गडा-जवळ", "नळ-दुर्ग")
    phonetic_form: str = "" # IPA or Latin phonetic (e.g. "sinh-aa-gadh-aa-javal", "nal-durga")
    detected_pronunciation: Optional[str] = None # Decoded from admin voice (e.g. "sinh-aa-gadh-aa-javal")
    syllable_boundaries: List[str] = field(default_factory=list) # ["सिंह", "गडा", "जवळ"]
    phoneme_sequence: List[str] = field(default_factory=list) # ["s", "i", "nh", "aa", ...]
    acoustic_metrics: Dict[str, Any] = field(default_factory=dict)
    ipa: Optional[str] = None # Optional IPA notation
    reference_audio: Optional[str] = None # Path to versioned teacher voice recording
    audio_ref: Optional[str] = None # Backward compatibility alias
    pronunciation_type: str = "phonetic_respelling" # "phonetic_respelling" | "admin_voice_reference"
    notes: str = "" # Description of intended inflection / stress
    source: str = "admin" # "admin" | "admin_voice" | "verified_teacher"
    scope: str = "global" # "document" | "textbook" | "subject" | "global"
    target_id: Optional[str] = None # document_id / textbook_id / subject when scoped
    version: int = 1
    approved: bool = True
    history: List[Dict[str, Any]] = field(default_factory=list) # Prior approved versions

    def __post_init__(self):
        # Keep reference_audio and audio_ref in sync
        if self.reference_audio and not self.audio_ref:
            self.audio_ref = self.reference_audio
        elif self.audio_ref and not self.reference_audio:
            self.reference_audio = self.audio_ref

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ResolvedPronunciation:
    """
    Provider-neutral representation of a resolved pronunciation.
    Decoupled from specific TTS engine APIs.
    """
    canonical_text: str
    pronunciation_text: str
    phonetic_form: str
    detected_pronunciation: Optional[str] = None
    syllable_boundaries: List[str] = field(default_factory=list)
    phoneme_sequence: List[str] = field(default_factory=list)
    acoustic_metrics: Dict[str, Any] = field(default_factory=dict)
    reference_audio: Optional[str] = None
    language: str = "mr-IN"
    scope: str = "global"
    version: int = 1
    pronunciation_type: str = "phonetic_respelling"
    ipa: Optional[str] = None
    notes: str = ""
    source: str = "admin"
    approved: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PronunciationKnowledgeBase:
    """
    Persistent store for approved Marathi pronunciation corrections.
    Survives page changes, chapter changes, application restarts, and TTS provider changes.
    """
    def __init__(self, db_path: str = PRONUNCIATION_DB_PATH):
        self.db_path = db_path
        self.entries: Dict[str, List[PronunciationEntry]] = {} # canonical_word -> list of entries
        os.makedirs(PRONUNCIATION_AUDIO_DIR, exist_ok=True)
        self._load()

    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for word, items in data.items():
                        self.entries[word] = [PronunciationEntry(**item) for item in items]
                return
            except Exception as e:
                print(f"[PronunciationKB] Warning loading {self.db_path}: {e}")

        # Seed initial verified educational pronunciation guides
        self._seed_default_pronunciations()
        self._save()

    def _seed_default_pronunciations(self):
        defaults = [
            PronunciationEntry(
                canonical_text="नळदुर्ग",
                preferred_pronunciation="नळ-दुर्ग",
                phonetic_form="nal-durga",
                notes="स्पष्ट 'ळ' उच्चार आणि 'दुर्ग' वर हलका आघात",
                scope="global",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="सिंहगडाजवळ",
                preferred_pronunciation="सिंह-गडा-जवळ",
                phonetic_form="singha-gada-jawal",
                notes="स्पष्ट 'सिंह' आणि 'गडाजवळ' संयुक्त उच्चार",
                scope="global",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="अलिबाग",
                preferred_pronunciation="अलि-बाग",
                phonetic_form="ali-baag",
                notes="दीर्घ 'बाग' उच्चार",
                scope="global",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="पर्जन्यछायेचा",
                preferred_pronunciation="पर्जन्य छायेचा",
                phonetic_form="parjanya-chayecha",
                notes="संयुक्त अक्षराचा स्पष्ट उच्चार",
                scope="subject",
                target_id="Geography",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="बेसाल्ट",
                preferred_pronunciation="बेसाल्ट",
                phonetic_form="besalt",
                notes="इंग्रजी भौगोलिक संज्ञा, स्पष्ट 'ट'",
                scope="subject",
                target_id="Geography",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="होकायंत्र",
                preferred_pronunciation="होका-यंत्र",
                phonetic_form="hoka-yantra",
                notes="'होका' आणि 'यंत्र' यांच्यात सूक्ष्म विराम",
                scope="global",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="खलभेदनाची",
                preferred_pronunciation="खल-भेदनाची",
                phonetic_form="khal-bhedanachi",
                notes="महाप्राण 'ख' आणि 'भ' स्पष्ट उच्चार",
                scope="subject",
                target_id="Marathi",
                approved=True
            ),
            PronunciationEntry(
                canonical_text="रंध्रातुनी",
                preferred_pronunciation="रंध्रा-तुनी",
                phonetic_form="randhra-tooni",
                notes="अनुनासिक 'रंध्र' उच्चार",
                scope="subject",
                target_id="Marathi",
                approved=True
            )
        ]
        for e in defaults:
            self.entries.setdefault(e.canonical_text, []).append(e)

    def _save(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        serializable = {
            word: [e.to_dict() for e in items]
            for word, items in self.entries.items()
        }
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)

    def add_entry(self, entry: PronunciationEntry) -> PronunciationEntry:
        word = entry.canonical_text.strip()
        if not word:
            raise ValueError("Canonical word cannot be empty")

        if word not in self.entries:
            self.entries[word] = []

        # Find existing entry with matching scope and target_id
        existing_idx = None
        for i, e in enumerate(self.entries[word]):
            if e.scope == entry.scope and e.target_id == entry.target_id:
                existing_idx = i
                break

        if existing_idx is not None:
            # Preserve history & increment version without erasing
            old_entry = self.entries[word][existing_idx]
            history = list(old_entry.history)
            old_dict = old_entry.to_dict()
            old_dict.pop("history", None)
            history.append(old_dict)

            entry.version = old_entry.version + 1
            entry.history = history
            self.entries[word][existing_idx] = entry
        else:
            self.entries[word].append(entry)

        self._save()
        return entry

    def add_voice_pronunciation(
        self,
        canonical_text: str,
        audio_bytes: bytes,
        audio_format: str = "webm",
        preferred_pronunciation: Optional[str] = None,
        phonetic_form: Optional[str] = None,
        notes: str = "",
        scope: str = "global",
        target_id: Optional[str] = None
    ) -> PronunciationEntry:
        """
        Stores voice-taught reference audio, increments version, and registers pronunciation entry.
        """
        word = canonical_text.strip()
        existing = [e for e in self.get_entries_for_word(word) if e.scope == scope and e.target_id == target_id]
        next_version = (existing[0].version + 1) if existing else 1

        # Versioned reference audio file
        safe_name = re.sub(r'[^a-zA-Z0-9_\u0900-\u097F]', '_', word)
        filename = f"{safe_name}_v{next_version}.{audio_format}"
        file_path = os.path.join(PRONUNCIATION_AUDIO_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Decode the acoustic pronunciation demonstrated by the administrator
        from corpus.pronunciation_decoder import pronunciation_decoder
        decoded = pronunciation_decoder.decode_pronunciation(
            canonical_word=word,
            audio_bytes=audio_bytes,
            audio_format=audio_format,
            reference_audio_path=file_path
        )

        disp_phonetic = preferred_pronunciation or decoded.preferred_pronunciation
        disp_roman = phonetic_form or decoded.phonetic_form

        entry = PronunciationEntry(
            canonical_text=word,
            preferred_pronunciation=disp_phonetic,
            phonetic_form=disp_roman,
            detected_pronunciation=decoded.detected_pronunciation,
            syllable_boundaries=decoded.syllable_boundaries,
            phoneme_sequence=decoded.phoneme_sequence,
            acoustic_metrics=decoded.acoustic_metrics,
            reference_audio=file_path,
            pronunciation_type="admin_voice_reference",
            source="admin_voice",
            scope=scope,
            target_id=target_id,
            notes=notes or f"Voice-taught pronunciation (confidence {decoded.confidence})",
            version=next_version,
            approved=True
        )

        return self.add_entry(entry)

    def get_entries_for_word(self, word: str) -> List[PronunciationEntry]:
        return self.entries.get(word.strip(), [])

    def list_all_entries(self) -> List[Dict[str, Any]]:
        all_items = []
        for word, items in self.entries.items():
            for it in items:
                all_items.append(it.to_dict())
        return all_items


class PronunciationResolver:
    """
    Resolves canonical words to their approved phonetic representations
    immediately before TTS synthesis.

    Resolution Hierarchy:
    1. Approved document-specific pronunciation
    2. Approved textbook-specific pronunciation
    3. Approved subject-specific pronunciation
    4. Approved global pronunciation
    5. Normal TTS text (unchanged)
    """
    def __init__(self, kb: Optional[PronunciationKnowledgeBase] = None):
        self.kb = kb or PronunciationKnowledgeBase()

    def resolve_word(
        self,
        word: str,
        document_id: Optional[str] = None,
        textbook_id: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Optional[PronunciationEntry]:
        clean = word.strip().strip(",।?!.–—;:'\"[]()|")
        entries = self.kb.get_entries_for_word(clean)
        if not entries:
            return None

        # Filter only approved entries
        approved = [e for e in entries if e.approved]
        if not approved:
            return None

        # 1. Document Scope
        if document_id:
            doc_matches = [e for e in approved if e.scope == "document" and e.target_id == document_id]
            if doc_matches:
                return doc_matches[0]

        # 2. Textbook Scope
        if textbook_id:
            tb_matches = [e for e in approved if e.scope == "textbook" and e.target_id == textbook_id]
            if tb_matches:
                return tb_matches[0]

        # 3. Subject Scope
        if subject:
            sub_matches = [e for e in approved if e.scope == "subject" and (e.target_id or "").lower() == subject.lower()]
            if sub_matches:
                return sub_matches[0]

        # 4. Global Scope
        global_matches = [e for e in approved if e.scope == "global"]
        if global_matches:
            return global_matches[0]

        return approved[0]

    def resolve_to_neutral(
        self,
        word: str,
        document_id: Optional[str] = None,
        textbook_id: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Optional[ResolvedPronunciation]:
        entry = self.resolve_word(word, document_id, textbook_id, subject)
        if not entry:
            return None
        return ResolvedPronunciation(
            canonical_text=entry.canonical_text,
            pronunciation_text=entry.preferred_pronunciation,
            phonetic_form=entry.phonetic_form,
            detected_pronunciation=entry.detected_pronunciation,
            syllable_boundaries=entry.syllable_boundaries,
            phoneme_sequence=entry.phoneme_sequence,
            acoustic_metrics=entry.acoustic_metrics,
            reference_audio=entry.reference_audio,
            language=entry.language,
            scope=entry.scope,
            version=entry.version,
            pronunciation_type=entry.pronunciation_type,
            ipa=entry.ipa,
            notes=entry.notes,
            source=entry.source,
            approved=entry.approved
        )

    def resolve_speech_text(
        self,
        text: str,
        document_id: Optional[str] = None,
        textbook_id: Optional[str] = None,
        subject: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Transforms canonical text into pronunciation-resolved and speech-safe text.
        Executes:
        Canonical Text
            ↓
        Punctuation Analysis & Pronunciation Resolution
            ↓
        TTS-Safe Speech Representation (Punctuation sanitized to acoustic pauses)
        """
        # First resolve approved pronunciation words
        words = text.split()
        resolved_tokens = []
        applied_resolutions = []

        for w in words:
            clean = re.sub(r'[,।?!.–—;:\'\"\[\]\(\)\|]', '', w).strip()
            entry = self.resolve_word(clean, document_id, textbook_id, subject)
            if entry and entry.preferred_pronunciation:
                replaced = w.replace(clean, entry.preferred_pronunciation)
                resolved_tokens.append(replaced)
                applied_resolutions.append({
                    "original": w,
                    "canonical_word": clean,
                    "phonetic_replacement": entry.preferred_pronunciation,
                    "reference_audio": entry.reference_audio,
                    "scope": entry.scope,
                    "source": entry.source,
                    "version": entry.version
                })
            else:
                resolved_tokens.append(w)

        intermediate_text = " ".join(resolved_tokens)

        # Apply strict TTS Speech Normalization:
        # Ensures punctuation (| [ ] etc.) acts as pauses, NEVER spoken literally as words.
        tts_safe_text = speech_normalizer.normalize_for_tts(intermediate_text)

        return tts_safe_text, applied_resolutions


# Adapters for TTS Providers
class SarvamPronunciationAdapter:
    """Adapts ResolvedPronunciation into Sarvam Bulbul supported Devanagari phonetic text."""
    @staticmethod
    def adapt(resolved_text: str, neutral_pronunciations: List[ResolvedPronunciation]) -> str:
        # Sarvam Bulbul:v3 natively interprets hyphenated Devanagari syllables and punctuation pauses
        return speech_normalizer.normalize_for_tts(resolved_text)

class IndicF5PronunciationAdapter:
    """Adapts ResolvedPronunciation into IndicF5 reference-audio conditioning & phonetic text."""
    @staticmethod
    def adapt(resolved_text: str, neutral_pronunciations: List[ResolvedPronunciation]) -> Dict[str, Any]:
        ref_audios = [p.reference_audio for p in neutral_pronunciations if p.reference_audio]
        effective_ref_audio = ref_audios[0] if ref_audios else None
        return {
            "text": speech_normalizer.normalize_for_tts(resolved_text),
            "ref_audio": effective_ref_audio,
            "has_voice_guidance": bool(effective_ref_audio)
        }

pronunciation_kb = PronunciationKnowledgeBase()
pronunciation_resolver = PronunciationResolver(pronunciation_kb)
