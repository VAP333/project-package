"""
AksharSetu — Narration Planner & Natural Chunking Engine (§1, §10, §11)

Transforms high-level Semantic Blocks into structured Narration Plans:
1. PARAGRAPH-FIRST NARRATION:
   Paragraph is the default narration unit.
2. CHUNKING RULE:
   Unusually long paragraphs are split into coherent 2-3 sentence narration chunks.
   Never split because a PDF line ended.
3. DIALOGUE AS DIALOGUE:
   Produces turn-by-turn conversational plans with speaker roles, natural pauses,
   and differentiated prosody.
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from graphs.semantic_blocks import SemanticNarrationBlock, SemanticBlockType, DialogueTurn
from orchestrator.prosody_planner import prosody_planner, ProsodyPlan
from corpus.pronunciation_kb import pronunciation_resolver

@dataclass
class NarrationChunk:
    chunk_id: str
    text: str
    speech_text: str # Text with pre-TTS phonetic adjustments applied
    sentence_indices: List[int]
    pause_before_ms: int = 0
    pause_after_ms: int = 250
    prosody_plan: Optional[Dict[str, Any]] = None
    applied_pronunciations: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DialogueTurnPlan:
    turn_id: str
    speaker: str
    speaker_role: str # "teacher" | "student"
    text: str
    speech_text: str
    voice_profile: str
    prosody_plan: Dict[str, Any]
    pause_after_ms: int = 400

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class NarrationPlan:
    block_id: str
    block_type: str
    canonical_text: str
    chunks: List[NarrationChunk] = field(default_factory=list)
    dialogue_turns: List[DialogueTurnPlan] = field(default_factory=list)
    overall_style: str = "teacher_narration"
    total_duration_estimate_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["chunks"] = [c.to_dict() for c in self.chunks]
        d["dialogue_turns"] = [t.to_dict() for t in self.dialogue_turns]
        return d

class NarrationPlanner:
    """
    Transforms SemanticNarrationBlocks into structured audio narration plans.
    """
    def __init__(self):
        self.prosody = prosody_planner
        self.pronunciation = pronunciation_resolver

    def plan_narration(
        self,
        block: SemanticNarrationBlock,
        document_id: Optional[str] = None,
        subject: Optional[str] = None,
        base_pace: float = 1.0
    ) -> NarrationPlan:
        # Handle Dialogue Block
        if block.block_type == SemanticBlockType.DIALOGUE_BLOCK and block.dialogue_turns:
            return self._plan_dialogue_block(block, document_id, subject, base_pace)

        # Handle Standard Paragraph / Prose / Stanza / Activity
        return self._plan_paragraph_block(block, document_id, subject, base_pace)

    def _plan_paragraph_block(
        self,
        block: SemanticNarrationBlock,
        document_id: Optional[str],
        subject: Optional[str],
        base_pace: float
    ) -> NarrationPlan:
        sentences = block.sentences
        text = block.canonical_text.strip()
        chunks: List[NarrationChunk] = []

        from orchestrator.marathi_number_normalizer import marathi_number_normalizer

        # Discourse intent derived from block type
        if block.block_type == SemanticBlockType.HEADING:
            intent = "heading"
            is_ch_start = getattr(block, "is_chapter_title", False) or (getattr(block, "printed_page", 1) == 1 and getattr(block, "sequence_index", 0) <= 1)
            seq_idx = getattr(block, "sequence_index", 0)
            text_for_speech = marathi_number_normalizer.format_heading_for_speech(text, is_chapter_start=is_ch_start, heading_index=seq_idx)
        elif block.block_type in (SemanticBlockType.EXERCISE, SemanticBlockType.QUESTION):
            intent = "question"
            text_for_speech = text
        elif block.block_type in (SemanticBlockType.ACTIVITY, SemanticBlockType.DISCUSSION):
            intent = "question"
            text_for_speech = text
        elif block.block_type == SemanticBlockType.DEFINITION:
            intent = "explanation"
            text_for_speech = text
        else:
            intent = "narration"
            text_for_speech = text

        # Apply Chunking Rule:
        # If paragraph has > 3 sentences or length > 220 chars, chunk into 2-3 coherent sentences
        if (len(sentences) > 3 or len(text) > 220) and block.block_type != SemanticBlockType.HEADING:
            current_chunk_sents = []
            current_chunk_text = []

            for idx, s in enumerate(sentences):
                current_chunk_sents.append(idx)
                current_chunk_text.append(s.text)

                # Split after 2-3 sentences or when length exceeds threshold
                combined_len = sum(len(t) for t in current_chunk_text)
                if len(current_chunk_sents) >= 2 and (combined_len >= 120 or idx == len(sentences) - 1):
                    chunk_str = " ".join(current_chunk_text)
                    resolved_text, audit = self.pronunciation.resolve_speech_text(
                        chunk_str, document_id=document_id, subject=subject
                    )
                    pp = self.prosody.plan_prosody(chunk_str, discourse_intent=intent, base_pace=base_pace)
                    chunks.append(NarrationChunk(
                        chunk_id=f"{block.block_id}_chk_{len(chunks) + 1}",
                        text=chunk_str,
                        speech_text=resolved_text,
                        sentence_indices=list(current_chunk_sents),
                        pause_before_ms=pp.pause_before_ms,
                        pause_after_ms=pp.pause_after_ms,
                        prosody_plan=pp.to_dict(),
                        applied_pronunciations=audit
                    ))
                    current_chunk_sents = []
                    current_chunk_text = []

            if current_chunk_text:
                chunk_str = " ".join(current_chunk_text)
                resolved_text, audit = self.pronunciation.resolve_speech_text(
                    chunk_str, document_id=document_id, subject=subject
                )
                pp = self.prosody.plan_prosody(chunk_str, discourse_intent=intent, base_pace=base_pace)
                chunks.append(NarrationChunk(
                    chunk_id=f"{block.block_id}_chk_{len(chunks) + 1}",
                    text=chunk_str,
                    speech_text=resolved_text,
                    sentence_indices=list(current_chunk_sents),
                    pause_before_ms=pp.pause_before_ms,
                    pause_after_ms=pp.pause_after_ms,
                    prosody_plan=pp.to_dict(),
                    applied_pronunciations=audit
                ))
        else:
            # Paragraph or Heading as a single natural narration unit
            resolved_text, audit = self.pronunciation.resolve_speech_text(
                text_for_speech, document_id=document_id, subject=subject
            )
            pp = self.prosody.plan_prosody(text_for_speech, discourse_intent=intent, base_pace=base_pace)
            chunks.append(NarrationChunk(
                chunk_id=f"{block.block_id}_chk_1",
                text=text,
                speech_text=resolved_text,
                sentence_indices=list(range(len(sentences))),
                pause_before_ms=pp.pause_before_ms,
                pause_after_ms=pp.pause_after_ms,
                prosody_plan=pp.to_dict(),
                applied_pronunciations=audit
            ))

        return NarrationPlan(
            block_id=block.block_id,
            block_type=block.block_type.value,
            canonical_text=text,
            chunks=chunks,
            dialogue_turns=[],
            overall_style="teacher_narration"
        )

    def _plan_dialogue_block(
        self,
        block: SemanticNarrationBlock,
        document_id: Optional[str],
        subject: Optional[str],
        base_pace: float
    ) -> NarrationPlan:
        turn_plans: List[DialogueTurnPlan] = []

        for turn in block.dialogue_turns:
            # Clean text for speech (keep textbook line accurate, omit speaker prefix for synthesis)
            clean_turn_text = re.sub(r'^[^\s:]{2,15}\s*[:\t]\s*', '', turn.text).strip()
            if not clean_turn_text:
                clean_turn_text = turn.text.strip()

            resolved_text, _ = self.pronunciation.resolve_speech_text(
                clean_turn_text, document_id=document_id, subject=subject
            )

            # Assign distinct voice profile & prosody by speaker role
            if turn.speaker_role == "student":
                voice = "shubh" if "राहुल" in turn.speaker else "priya"
                pp = self.prosody.plan_prosody(
                    clean_turn_text, discourse_intent="dialogue_student", speaker_role="student", base_pace=base_pace
                )
            else:
                voice = "shreya" # Default teacher voice
                pp = self.prosody.plan_prosody(
                    clean_turn_text, discourse_intent="dialogue_teacher", speaker_role="teacher", base_pace=base_pace
                )

            turn_plans.append(DialogueTurnPlan(
                turn_id=turn.turn_id,
                speaker=turn.speaker,
                speaker_role=turn.speaker_role,
                text=turn.text,
                speech_text=resolved_text,
                voice_profile=voice,
                prosody_plan=pp.to_dict(),
                pause_after_ms=pp.pause_after_ms
            ))

        return NarrationPlan(
            block_id=block.block_id,
            block_type=block.block_type.value,
            canonical_text=block.canonical_text,
            chunks=[],
            dialogue_turns=turn_plans,
            overall_style="dialogue_conversation"
        )

narration_planner = NarrationPlanner()
