"""
AksharSetu — Class 8 Science Pronunciation Knowledge Layer (Phase 8)

Separates:
1. Canonical textbook spelling (Devanagari verbatim)
2. Pronunciation metadata (syllable boundaries, stress, risk type)
3. Approved pronunciation (phonetic guide, Devanagari guide)
4. TTS rendering (provider-specific phonetic adjustments)

Ingests:
- 19 chapters' pronunciation risk terms (chemical compounds, taxa, physics units, foreign scientist names).
- Pre-existing textbook-authored back-matter शब्दसूची glossary (~150 terms with phonetic Marathi guide).
- Never treats crude Romanization as canonical truth.
- Tracks verification status explicitly: UNVERIFIED is never claimed as Golden Truth.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import re

from corpus.science_loader import science_corpus_loader, ScienceChapterMetadata


@dataclass
class SciencePronunciationEntry:
    canonical_text: str
    language: str = "mr"
    subject: str = "science"
    chapter: str = ""
    risk_type: str = "technical_term"  # "technical_term", "scientist_name", "chemical_compound", "biology_taxa", "physics_unit", "english_loan"
    source_region: Optional[str] = None
    verification_status: str = "UNVERIFIED"  # "UNVERIFIED", "TEACHER_PROPOSED", "APPROVED"
    phonetic_respelling: str = ""
    devanagari_guide: str = ""
    ipa: Optional[str] = None
    tts_rendering: Optional[str] = None
    english_gloss: Optional[str] = None
    version: int = 1
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def is_verified(self) -> bool:
        return self.verification_status in ("APPROVED", "VERIFIED")


class SciencePronunciationKB:
    """
    De-duplicated, book-wide Pronunciation Knowledge Base for Class 8 Science.
    Seeds from both Chapter Pronunciation Risks and the Back-Matter Glossary.
    """

    def __init__(self, loader=science_corpus_loader):
        self.loader = loader
        self.entries: Dict[str, SciencePronunciationEntry] = {}
        self._built = False

    def build_lexicon(self) -> "SciencePronunciationKB":
        if self._built:
            return self

        self.loader.validate_and_load()

        # 1. Ingest Chapter Pronunciation Risks across all 19 chapters
        for ch in self.loader.list_all_chapters():
            ch_id = ch.chapter_id

            for ent in ch.pronunciation_risk_entities:
                clean_ent = ent.strip()
                if not clean_ent:
                    continue

                # Categorize risk type
                risk = "technical_term"
                if any(sci in clean_ent for sci in ["लिनिअस", "हेकेल", "चॅटन", "कोपलँड", "व्हिटाकर", "डॅल्टन", "थॉमसन", "रुदरफोर्ड", "बोहर", "आर्किमिडीज", "गॉल्गी", "हार्वे", "लँडस्टायनर", "न्यूटन"]):
                    risk = "scientist_name"
                elif any(bio in clean_ent for bio in ["बॅसिलाय", "अमिबा", "फाज", "मोनेरा", "प्रोटिस्टा", "कवके", "शैवाल", "पेशी", "मायटोकॉन्ड्रिया"]):
                    risk = "biology_taxa"
                elif any(chem in clean_ent for chem in ["अम्ल", "आम्लारी", "ऑक्साईड", "सल्फ्यूरिक", "हायड्रोजन", "ऑक्सिजन", "संयुग", "रेणू"]):
                    risk = "chemical_compound"
                elif any(phys in clean_ent for phys in ["पास्कल", "ज्यूल", "कॅलरी", "हर्ट्झ", "वॅट", "न्यूटन"]):
                    risk = "physics_unit"

                if clean_ent in self.entries:
                    existing = self.entries[clean_ent]
                    if ch_id not in existing.chapter:
                        existing.chapter += f", {ch_id}"
                else:
                    self.entries[clean_ent] = SciencePronunciationEntry(
                        canonical_text=clean_ent,
                        language="mr",
                        subject="science",
                        chapter=ch_id,
                        risk_type=risk,
                        source_region=f"{ch_id}_p{ch.pdf_page_range[0]}_r1",
                        verification_status="UNVERIFIED",
                        phonetic_respelling="",
                        devanagari_guide=clean_ent,
                        version=1,
                        notes=f"Extracted from Class 8 Science Chapter {ch.chapter_number} ({ch.title_marathi})"
                    )

        # 2. Ingest Back-Matter शब्दसूची Glossary terms
        for g_term in self.loader.glossary_terms:
            word = g_term.marathi_term.strip()
            if not word:
                continue

            # If word is already in entries, enrich with glossary phonetic transliteration and English gloss
            if word in self.entries:
                entry = self.entries[word]
                entry.english_gloss = g_term.english_term
                entry.devanagari_guide = g_term.phonetic_transliteration
                entry.notes += f" | Glossary: {g_term.english_term} ({g_term.phonetic_transliteration})"
            else:
                self.entries[word] = SciencePronunciationEntry(
                    canonical_text=word,
                    language="mr",
                    subject="science",
                    chapter="GLOSSARY",
                    risk_type="technical_term",
                    source_region=f"GLOSSARY_p{g_term.page_number}",
                    verification_status="UNVERIFIED",
                    phonetic_respelling=g_term.english_term,
                    devanagari_guide=g_term.phonetic_transliteration,
                    english_gloss=g_term.english_term,
                    version=1,
                    notes=f"Class 8 Science Glossary seed: {g_term.english_term} -> {g_term.phonetic_transliteration}"
                )

        self._built = True
        return self

    def lookup(self, word: str) -> Optional[SciencePronunciationEntry]:
        self.build_lexicon()
        clean = word.strip().rstrip(".,!?|।:;")
        return self.entries.get(clean)

    def list_entries(self, chapter_id: Optional[str] = None) -> List[SciencePronunciationEntry]:
        self.build_lexicon()
        if not chapter_id:
            return sorted(self.entries.values(), key=lambda e: e.canonical_text)
        ch_upper = chapter_id.upper()
        return [
            e for e in self.entries.values()
            if ch_upper in e.chapter.split(", ") or e.chapter == ch_upper
        ]

    def approve_entry(
        self,
        canonical_text: str,
        preferred_pronunciation: Optional[str] = None,
        approved_by: str = "admin"
    ) -> Optional[SciencePronunciationEntry]:
        """Approves a candidate into verified Golden Truth."""
        self.build_lexicon()
        entry = self.entries.get(canonical_text)
        if not entry:
            return None

        entry.verification_status = "APPROVED"
        if preferred_pronunciation:
            entry.devanagari_guide = preferred_pronunciation.strip()
            entry.phonetic_respelling = preferred_pronunciation.strip()
        entry.version += 1
        entry.notes += f" | Approved by {approved_by}"
        return entry


science_pronunciation_kb = SciencePronunciationKB()
