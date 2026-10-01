"""
AksharSetu — Class 8 History Pronunciation Knowledge Layer (Phase 8)

Separates:
1. Canonical textbook spelling (Devanagari verbatim)
2. Pronunciation metadata (syllable boundaries, stress, risk type)
3. Approved pronunciation (phonetic guide, Devanagari guide)
4. TTS rendering (provider-specific phonetic adjustments)

Never treats crude Romanization as canonical truth.
Tracks verification status explicitly: UNVERIFIED is never claimed as Golden Truth.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import re

from corpus.history_loader import history_corpus_loader, HistoryChapterMetadata


@dataclass
class HistoryPronunciationEntry:
    canonical_text: str
    language: str = "mr"
    subject: str = "history"
    chapter: str = ""
    risk_type: str = "proper_noun_historical"  # "proper_noun_historical", "foreign_origin", "persian_origin", "english_loan"
    source_region: Optional[str] = None
    verification_status: str = "UNVERIFIED"  # "UNVERIFIED", "TEACHER_PROPOSED", "APPROVED"
    phonetic_respelling: str = ""
    devanagari_guide: str = ""
    ipa: Optional[str] = None
    tts_rendering: Optional[str] = None
    version: int = 1
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def is_verified(self) -> bool:
        return self.verification_status in ("APPROVED", "VERIFIED")


class HistoryPronunciationKB:
    """
    De-duplicated, book-wide Pronunciation Knowledge Base for Class 8 History.
    """

    def __init__(self, loader=history_corpus_loader):
        self.loader = loader
        self.entries: Dict[str, HistoryPronunciationEntry] = {}
        self._built = False

    def build_lexicon(self) -> "HistoryPronunciationKB":
        if self._built:
            return self

        self.loader.validate_and_load()

        for ch in self.loader.list_all_chapters():
            ch_id = ch.chapter_id

            for ent in ch.pronunciation_risk_entities:
                clean_ent = ent.strip()
                if not clean_ent:
                    continue

                # Categorize risk type
                risk = "proper_noun_historical"
                if any(foreign in clean_ent for foreign in ["पॅलेस", "जेल", "गव्हर्नर", "कंपनी", "कमिन", "कमिशन"]):
                    risk = "english_loan"
                elif any(persian in clean_ent for persian in ["खान", "शहा", "दीवान", "नवाब", "इनाम"]):
                    risk = "persian_origin"

                # If entry exists, associate chapter
                if clean_ent in self.entries:
                    existing = self.entries[clean_ent]
                    if ch_id not in existing.chapter:
                        existing.chapter += f", {ch_id}"
                else:
                    self.entries[clean_ent] = HistoryPronunciationEntry(
                        canonical_text=clean_ent,
                        language="mr",
                        subject="history",
                        chapter=ch_id,
                        risk_type=risk,
                        source_region=f"{ch_id}_p{ch.pdf_page_range[0]}_r1",
                        verification_status="UNVERIFIED",  # Strictly unverified in v0.1 baseline
                        phonetic_respelling="",
                        devanagari_guide=clean_ent,
                        version=1,
                        notes=f"Extracted from Class 8 History Chapter {ch.chapter_number} ({ch.title_marathi})"
                    )

        self._built = True
        return self

    def lookup(self, word: str) -> Optional[HistoryPronunciationEntry]:
        self.build_lexicon()
        return self.entries.get(word.strip())

    def list_entries(self, chapter_id: Optional[str] = None) -> List[HistoryPronunciationEntry]:
        self.build_lexicon()
        if not chapter_id:
            return list(self.entries.values())
        ch_upper = chapter_id.upper()
        return [e for e in self.entries.values() if ch_upper in e.chapter]

    def list_unverified(self) -> List[HistoryPronunciationEntry]:
        self.build_lexicon()
        return [e for e in self.entries.values() if not e.is_verified]

    def approve_pronunciation(
        self,
        word: str,
        phonetic_respelling: str,
        devanagari_guide: str,
        ipa: Optional[str] = None
    ) -> Optional[HistoryPronunciationEntry]:
        self.build_lexicon()
        if word not in self.entries:
            return None

        entry = self.entries[word]
        entry.phonetic_respelling = phonetic_respelling
        entry.devanagari_guide = devanagari_guide
        entry.ipa = ipa
        entry.tts_rendering = devanagari_guide
        entry.verification_status = "APPROVED"
        entry.version += 1
        return entry

    def approve_entry(
        self,
        canonical_text: str,
        preferred_pronunciation: Optional[str] = None,
        approved_by: str = "admin"
    ) -> Optional[HistoryPronunciationEntry]:
        self.build_lexicon()
        entry = self.lookup(canonical_text)
        if not entry:
            return None
        pref = preferred_pronunciation or canonical_text
        entry.phonetic_respelling = pref
        entry.devanagari_guide = pref
        entry.tts_rendering = pref
        entry.verification_status = "GOLDEN_TRUTH"
        entry.version += 1
        entry.notes += f" | Approved to GOLDEN_TRUTH by {approved_by}"
        return entry

    def resolve_for_tts(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Replaces canonical proper nouns with approved phonetic guides where available.
        Does not mutate text if unverified.
        """
        self.build_lexicon()
        applied = []
        resolved = text

        for word, entry in self.entries.items():
            if entry.is_verified and entry.tts_rendering and word in resolved:
                resolved = re.sub(r'\b' + re.escape(word) + r'\b', entry.tts_rendering, resolved)
                applied.append({
                    "word": word,
                    "rendered": entry.tts_rendering,
                    "version": entry.version
                })

        return resolved, applied


history_pronunciation_kb = HistoryPronunciationKB()
