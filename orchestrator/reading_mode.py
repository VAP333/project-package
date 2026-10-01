"""
AksharSetu — Reading Mode Orchestrator (§0 Principle 1, 2, 6 & §12)

NON-NEGOTIABLE ARCHITECTURAL PRINCIPLE:
Reading Mode outputs MUST be traceable verbatim to source.
Generative AI never silently rewrites canonical content.
The textbook's native text and verified Golden Corpus entries are ground truth.
No synthetic fluency rewriting is permitted on this path.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from corpus.schema import GoldenCorpusRecord, VerificationTier

@dataclass
class ReadingToken:
    text: str
    is_critical: bool = False
    flagged: bool = False
    confidence: float = 1.0

@dataclass
class ReadingSentence:
    sentence_id: int
    text: str
    tokens: List[ReadingToken] = field(default_factory=list)
    audio_cue: Optional[str] = None # Standard audio cue, never tutor cue

@dataclass
class ReadingParagraph:
    paragraph_id: int
    region_id: str
    canonical_text: str
    sentences: List[ReadingSentence] = field(default_factory=list)
    reading_order_idx: int = 0
    verification_tier: str = "GOLDEN_TRUTH"

@dataclass
class ReadingModePage:
    page_id: str
    source_hash: str
    book: str
    edition: str
    chapter: str
    paragraphs: List[ReadingParagraph] = field(default_factory=list)

class ReadingModeOrchestrator:
    """
    Renders canonical page text directly from Golden Corpus / Native PDF evidence.
    Fidelity above all.
    """
    def __init__(self):
        pass

    def build_reading_page(
        self,
        page_id: str,
        book: str,
        edition: str,
        chapter: str,
        source_hash: str,
        records: List[GoldenCorpusRecord]
    ) -> ReadingModePage:
        # Sort strictly by reading order index
        sorted_records = sorted(records, key=lambda r: r.reading_order)
        paragraphs: List[ReadingParagraph] = []

        sentence_counter = 1
        for p_idx, rec in enumerate(sorted_records, start=1):
            raw_text = rec.canonical_text.strip()
            # Split sentences cleanly on Marathi / Devanagari full stops ('।' or '.')
            raw_sentences = [s.strip() for s in raw_text.replace("।", ".").split(".") if s.strip()]
            sentences: List[ReadingSentence] = []

            for s_text in raw_sentences:
                token_objs = []
                for w in s_text.split():
                    token_objs.append(ReadingToken(
                        text=w,
                        confidence=1.0 if rec.verification_status == VerificationTier.GOLDEN_TRUTH else 0.85
                    ))
                sentences.append(ReadingSentence(
                    sentence_id=sentence_counter,
                    text=s_text,
                    tokens=token_objs
                ))
                sentence_counter += 1

            paragraphs.append(ReadingParagraph(
                paragraph_id=p_idx,
                region_id=rec.region_id,
                canonical_text=raw_text,
                sentences=sentences,
                reading_order_idx=rec.reading_order,
                verification_tier=rec.verification_status.value
            ))

        return ReadingModePage(
            page_id=page_id,
            source_hash=source_hash,
            book=book,
            edition=edition,
            chapter=chapter,
            paragraphs=paragraphs
        )
