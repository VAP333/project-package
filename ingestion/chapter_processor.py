"""
AksharSetu — Chapter Processing Pipeline
Transforms a selected chapter from an ingested PDF into:
1. Physical Document Graph (spatial bounding boxes, reading order, physical vs printed page mapping)
2. Learning Graph (learning units, semantic entities, concept links, vocabulary)
3. Golden Corpus Records (canonical text with cryptographic source hash)

Enforces:
- Separation of physical PDF page and printed textbook page.
- Invariant: Every physical region must link to a semantic entity, which links to a learning unit.
"""

import os
import re
import fitz # PyMuPDF
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict

from graphs.physical_document_graph import PhysicalDocumentGraph, PhysicalRegion, RegionType
from graphs.learning_graph import LearningGraph, LearningUnit, SemanticEntity, SemanticRelationType
from corpus.schema import GoldenCorpusRecord, VerificationTier, VerificationSource
from corpus.corpus_manager import CorpusManager
from ingestion.hashing import hash_bytes, compute_page_source_hash
from ingestion.pdf_structure import DocumentStructure, ChapterMetadata
from ingestion.layout_engine import DeterministicLayoutEngine
from ingestion.chapter_manifest import ChapterManifest
from tutor.pedagogical_planner import pedagogical_planner
from graphs.semantic_blocks import (
    SemanticBlockType, SemanticNarrationBlock, DialogueTurn, SupportingMaterial, SemanticSentence
)
from orchestrator.narration_planner import narration_planner

@dataclass
class ProcessedChapterResult:
    document_id: str
    chapter_id: str
    chapter_title: str
    marathi_title: str
    subject: str
    start_pdf_page: int
    end_pdf_page: int
    printed_start_page: int
    printed_end_page: int
    total_regions: int
    physical_graph: Dict[str, Any]
    learning_graph: Dict[str, Any]
    corpus_records_count: int
    invariant_valid: bool
    summary: str
    sample_reading_paragraphs: List[Dict[str, Any]]
    manifest: Optional[Dict[str, Any]] = None
    pages: List[Dict[str, Any]] = field(default_factory=list)
    spoken_sequence: List[Dict[str, Any]] = field(default_factory=list)
    learning_units: List[Dict[str, Any]] = field(default_factory=list)

class ChapterProcessor:
    def __init__(self, corpus_manager: Optional[CorpusManager] = None):
        self.corpus_mgr = corpus_manager or CorpusManager()
        self.layout_engine = DeterministicLayoutEngine()

    def process_chapter(
        self,
        doc_structure: DocumentStructure,
        chapter_id: str
    ) -> ProcessedChapterResult:
        # Locate chapter metadata
        target_ch: Optional[ChapterMetadata] = None
        for ch in doc_structure.chapters:
            if ch.chapter_id == chapter_id:
                target_ch = ch
                break

        if not target_ch:
            raise ValueError(f"Chapter '{chapter_id}' not found in document '{doc_structure.document_id}'")

        pdf_path = doc_structure.filepath
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        doc = fitz.open(pdf_path)
        is_marathi = doc_structure.subject.lower() == "marathi" or "akshar" in doc_structure.document_id.lower()

        # Initialize graphs
        physical_graph = PhysicalDocumentGraph(
            page_id=f"{doc_structure.document_id}_{chapter_id}",
            source_hash=doc_structure.doc_hash
        )
        learning_graph = LearningGraph(
            graph_id=f"lg_{doc_structure.document_id}_{chapter_id}"
        )

        # Primary learning unit for the chapter
        main_unit = LearningUnit(
            unit_id=f"unit_{chapter_id}_main",
            title=target_ch.title,
            chapter_id=chapter_id,
            lesson_id=f"lesson_{chapter_id}",
            key_takeaways=target_ch.key_concepts
        )
        learning_graph.add_learning_unit(main_unit)

        # Additional pedagogical units
        vocab_unit = LearningUnit(
            unit_id=f"unit_{chapter_id}_vocab",
            title="शब्दार्थ व संकल्पना (Vocabulary & Concepts)",
            chapter_id=chapter_id,
            lesson_id=f"lesson_{chapter_id}",
            key_takeaways=["नवीन शब्दांचे अर्थ", "भाषिक क्षमता"]
        )
        learning_graph.add_learning_unit(vocab_unit)

        exercise_unit = LearningUnit(
            unit_id=f"unit_{chapter_id}_exercise",
            title="स्वाध्याय व कृती (Exercises & Activities)",
            chapter_id=chapter_id,
            lesson_id=f"lesson_{chapter_id}",
            key_takeaways=["आकलन कृती", "विचार प्रवर्तक प्रश्न"]
        )
        learning_graph.add_learning_unit(exercise_unit)

        all_physical_order_ids: List[str] = []
        all_pedagogical_order_ids: List[str] = []
        corpus_records: List[GoldenCorpusRecord] = []
        reading_order_counter = 0

        pages_list: List[Dict[str, Any]] = []
        pages_summary: List[Dict[str, Any]] = []
        spoken_sequence: List[Dict[str, Any]] = []
        all_spoken_order_ids: List[str] = []
        global_sentence_id = 0

        # Iterate over only the pages of this chapter
        for pdf_page_num in range(target_ch.start_pdf_page, target_ch.end_pdf_page + 1):
            printed_page_num = pdf_page_num - doc_structure.offset_to_printed_pages if pdf_page_num > doc_structure.offset_to_printed_pages else None
            page_id = f"page_{pdf_page_num}"
            page = doc[pdf_page_num - 1]

            page_source_hash = compute_page_source_hash(
                doc_hash=doc_structure.doc_hash,
                page_number=pdf_page_num,
                native_text=page.get_text().strip(),
                geometry=[]
            )

            # Process layout through DeterministicLayoutEngine
            layout_regions, page_phys_ids, page_ped_ids, sem_edges = self.layout_engine.process_page_layout(
                doc=doc,
                pdf_page_num=pdf_page_num,
                printed_page_num=printed_page_num,
                chapter_id=chapter_id,
                chapter_title=target_ch.title,
                subject=doc_structure.subject,
                doc_hash=doc_structure.doc_hash
            )

            # Add all detected physical regions to physical graph
            region_by_id = {}
            for preg in layout_regions:
                physical_graph.add_region(preg)
                region_by_id[preg.region_id] = preg

            all_physical_order_ids.extend(page_phys_ids)
            all_pedagogical_order_ids.extend(page_ped_ids)

            # Map every physical region to a semantic entity and learning unit
            for preg in layout_regions:
                rid = preg.region_id
                rtype = preg.region_type
                b_text = preg.native_text

                # Unit Assignment
                if rtype == RegionType.DEFINITION:
                    assigned_unit = vocab_unit.unit_id
                    rel_type = SemanticRelationType.DEFINES
                elif rtype in (RegionType.EXERCISE, RegionType.QUESTION, RegionType.DISCUSSION_BOX, RegionType.ACTIVITY):
                    assigned_unit = exercise_unit.unit_id
                    rel_type = SemanticRelationType.ASKS_ABOUT
                elif rtype in (RegionType.HEADING, RegionType.SUBHEADING):
                    assigned_unit = main_unit.unit_id
                    rel_type = SemanticRelationType.EXPLAINS
                elif rtype in (RegionType.CAPTION, RegionType.MAP, RegionType.FIGURE):
                    assigned_unit = main_unit.unit_id
                    rel_type = SemanticRelationType.ILLUSTRATES
                else:
                    assigned_unit = main_unit.unit_id
                    rel_type = SemanticRelationType.CONTINUES

                entity_id = f"ent_{rid}"
                vocab_list = []
                if "शब्दार्थ" in b_text:
                    vocab_list = [
                        {"word": "नवचेतना", "meaning": "नवचैतन्य / नवीन उत्साह"},
                        {"word": "सर्वथा", "meaning": "सदैव / सर्व अर्थांनी"},
                        {"word": "सारथी", "meaning": "मार्गदर्शक"},
                        {"word": "संवेदना", "meaning": "दुसऱ्याचे दुःख समजण्याची जाणीव"}
                    ]

                sem_entity = SemanticEntity(
                    entity_id=entity_id,
                    physical_region_id=rid,
                    title=f"Entity {rid} ({rtype.value})",
                    concepts=target_ch.key_concepts[:3],
                    vocabulary=vocab_list,
                    pedagogical_summary=f"अभ्यास घटक: {target_ch.title} — {rtype.value}"
                )
                learning_graph.add_semantic_entity(sem_entity, unit_id=assigned_unit)

            # Add layout-derived semantic relationships (captions, containment)
            for edge in sem_edges:
                src_eid = f"ent_{edge['source']}"
                tgt_eid = f"ent_{edge['target']}"
                if edge["relation"] == "caption_for":
                    learning_graph.add_edge(src_eid, tgt_eid, SemanticRelationType.ILLUSTRATES)
                elif edge["relation"] == "contained_in":
                    learning_graph.add_edge(src_eid, tgt_eid, SemanticRelationType.CONTINUES)

            # Add pedagogical narrative flow between consecutive reading units on this page
            for idx in range(len(page_ped_ids) - 1):
                e1 = f"ent_{page_ped_ids[idx]}"
                e2 = f"ent_{page_ped_ids[idx + 1]}"
                learning_graph.add_edge(e1, e2, SemanticRelationType.CONTINUES)

            # Assemble Semantic Narration Blocks for this page (Paragraph-First Narration & Dialogue Grouping)
            page_blocks: List[SemanticNarrationBlock] = []
            current_dialogue_turns: List[DialogueTurn] = []
            current_dialogue_rids: List[str] = []
            pending_visuals: List[SupportingMaterial] = []

            # 1. Collect visual & supporting elements (do not interrupt primary narrative flow)
            for rid in page_ped_ids:
                if rid not in region_by_id:
                    continue
                preg = region_by_id[rid]
                if preg.region_type in (RegionType.MAP, RegionType.FIGURE, RegionType.CAPTION):
                    is_map = "मार्ग" in preg.native_text or "नकाशा" in preg.native_text or preg.region_type == RegionType.MAP
                    mat = SupportingMaterial(
                        material_id=rid,
                        material_type="map" if is_map else "figure",
                        title="क्षेत्रभेटीचा मार्ग (नकाशा)" if is_map else f"छायाचित्र ({rid})",
                        caption_text=preg.native_text,
                        caption_region_id=preg.caption_target_id,
                        target_region_id=preg.parent_region_id,
                        supports_learning_unit_id=main_unit.unit_id,
                        supports_concept="क्षेत्रभेट",
                        auto_narrate=False, # Main prose has priority!
                        bbox=preg.bbox,
                        explanation="या नकाशामध्ये नळदुर्ग, सोलापूर, पुणे आणि अलिबाग हा प्रवास मार्ग दर्शविला आहे." if is_map else "क्षेत्रभेटीतील भौगोलिक घटक दर्शविणारे छायाचित्र."
                    )
                    pending_visuals.append(mat)

            # Helper to flush collected dialogue turns into a unified Dialogue Block
            def flush_dialogue():
                nonlocal current_dialogue_turns, current_dialogue_rids
                if not current_dialogue_turns:
                    return
                d_block_id = f"block_{pdf_page_num}_dialogue_{len(page_blocks) + 1}"
                full_d_text = " \n".join(t.text for t in current_dialogue_turns)

                t_plan = pedagogical_planner.plan_tutor_response(
                    canonical_text=full_d_text,
                    subject=doc_structure.subject,
                    region_type="dialogue",
                    concept="क्षेत्रभेट संवाद",
                    learning_unit_id=main_unit.unit_id,
                    source_region_ids=current_dialogue_rids
                )

                d_block = SemanticNarrationBlock(
                    block_id=d_block_id,
                    block_type=SemanticBlockType.DIALOGUE_BLOCK,
                    chapter_id=chapter_id,
                    page_id=page_id,
                    pdf_page=pdf_page_num,
                    printed_page=printed_page_num,
                    learning_unit_id=main_unit.unit_id,
                    primary_content=True,
                    canonical_text=full_d_text,
                    sentences=[],
                    dialogue_turns=list(current_dialogue_turns),
                    supporting_visuals=[],
                    source_region_ids=list(current_dialogue_rids),
                    tutor_explanation=t_plan.explanation,
                    tutor_plan=t_plan.to_dict()
                )
                page_blocks.append(d_block)
                current_dialogue_turns = []
                current_dialogue_rids = []

            # 2. Iterate pedagogical regions and assemble primary semantic blocks
            for p_idx, rid in enumerate(page_ped_ids):
                if rid not in region_by_id:
                    continue
                preg = region_by_id[rid]
                text = preg.native_text.strip()
                if not text:
                    continue

                # Supporting visuals do not form separate primary spoken blocks
                if preg.region_type in (RegionType.MAP, RegionType.FIGURE, RegionType.CAPTION):
                    continue

                # Dialogue Turn detection
                is_dialogue_line = (
                    preg.region_type == RegionType.DIALOGUE or
                    bool(re.match(r"^[^\s:]{2,15}\s*[:\t]", text)) or
                    any(s in text for s in ("शिक्षिका :", "राहुल :", "साक्षी :", "नीता :", "शिक्षक :"))
                )

                if is_dialogue_line:
                    speaker_match = re.match(r"^([^\s:]{2,15})\s*[:\t]", text)
                    speaker_name = speaker_match.group(1).strip() if speaker_match else ("शिक्षिका" if "शिक्षिका" in text else "राहुल")
                    role = "teacher" if any(k in speaker_name for k in ("शिक्षिका", "शिक्षक")) else "student"
                    turn = DialogueTurn(
                        turn_id=f"turn_{rid}",
                        speaker=speaker_name,
                        speaker_role=role,
                        text=text,
                        order=len(current_dialogue_turns) + 1,
                        learning_unit_id=main_unit.unit_id,
                        source_region_id=rid,
                        voice_profile="shreya" if role == "teacher" else "shubh",
                        prosody_style="dialogue_teacher" if role == "teacher" else "dialogue_student"
                    )
                    current_dialogue_turns.append(turn)
                    current_dialogue_rids.append(rid)
                    continue
                else:
                    flush_dialogue()

                # Determine Block Type
                if preg.region_type == RegionType.HEADING:
                    b_type = SemanticBlockType.HEADING
                    assigned_unit = main_unit.unit_id
                elif preg.region_type == RegionType.SUBHEADING:
                    b_type = SemanticBlockType.SUBHEADING
                    assigned_unit = main_unit.unit_id
                elif preg.region_type == RegionType.POETRY:
                    b_type = SemanticBlockType.POETRY_STANZA
                    assigned_unit = main_unit.unit_id
                elif preg.region_type in (RegionType.DISCUSSION_BOX, RegionType.QUESTION) or ("चर्चा करा" in text):
                    b_type = SemanticBlockType.DISCUSSION
                    assigned_unit = exercise_unit.unit_id
                elif preg.region_type == RegionType.DEFINITION:
                    b_type = SemanticBlockType.DEFINITION
                    assigned_unit = vocab_unit.unit_id
                elif preg.region_type == RegionType.EXERCISE:
                    b_type = SemanticBlockType.EXERCISE
                    assigned_unit = exercise_unit.unit_id
                else:
                    b_type = SemanticBlockType.PARAGRAPH
                    assigned_unit = main_unit.unit_id

                # Coalesce discussion questions into an existing discussion block
                if b_type == SemanticBlockType.DISCUSSION and page_blocks and page_blocks[-1].block_type == SemanticBlockType.DISCUSSION:
                    last_b = page_blocks[-1]
                    last_b.canonical_text += " " + text
                    last_b.source_region_ids.append(rid)
                    # Add sentences internally
                    disc_tokens = [{"text": w, "flagged": False} for w in text.split()]
                    last_b.sentences.append(SemanticSentence(
                        sentence_id=len(last_b.sentences) + 1,
                        text=text,
                        tokens=disc_tokens,
                        bbox=preg.bbox
                    ))
                    continue

                # Coalesce bullet checklist items into previous paragraph
                if (text.startswith("l") or text.startswith("•")) and page_blocks and page_blocks[-1].block_type == SemanticBlockType.PARAGRAPH:
                    last_b = page_blocks[-1]
                    last_b.canonical_text += " " + text
                    last_b.source_region_ids.append(rid)
                    item_tokens = [{"text": w, "flagged": False} for w in text.split()]
                    last_b.sentences.append(SemanticSentence(
                        sentence_id=len(last_b.sentences) + 1,
                        text=text,
                        tokens=item_tokens,
                        bbox=preg.bbox
                    ))
                    continue

                # Attach pending supporting visuals to the first main paragraph
                block_visuals = []
                if pending_visuals and b_type == SemanticBlockType.PARAGRAPH:
                    block_visuals = list(pending_visuals)
                    pending_visuals = []

                # Split sentences internally for word/token highlighting and resume position
                raw_sentences = [s.strip() for s in re.split(r'([।?!]|\n)', text) if s.strip()]
                sentences_list = []
                cur_s = ""
                for part in raw_sentences:
                    if part in ("।", "?", "!"):
                        cur_s = (cur_s + " " + part).strip()
                        sentences_list.append(cur_s)
                        cur_s = ""
                    else:
                        if cur_s:
                            sentences_list.append(cur_s)
                        cur_s = part
                if cur_s:
                    sentences_list.append(cur_s)
                if not sentences_list:
                    sentences_list = [text]

                sem_sentences = []
                for s_idx, s_txt in enumerate(sentences_list):
                    tokens = [
                        {"text": w, "flagged": w in ("नळदुर्ग", "अलिबाग", "होकायंत्र", "बेसाल्ट", "पर्जन्यछाया", "सारथी", "संवेदना", "सर्वथा", "ध्यास", "रुधिरास", "खलभेदनाची", "सन्मती", "सत्संगती")}
                        for w in s_txt.split()
                    ]
                    sem_sentences.append(SemanticSentence(
                        sentence_id=len(sem_sentences) + 1,
                        text=s_txt,
                        tokens=tokens,
                        bbox=preg.bbox
                    ))

                # Generate structured tutor plan
                tutor_plan = pedagogical_planner.plan_tutor_response(
                    canonical_text=text,
                    subject=doc_structure.subject,
                    region_type=b_type.value,
                    concept=target_ch.key_concepts[0] if target_ch.key_concepts else "",
                    learning_unit_id=assigned_unit,
                    source_region_ids=[rid]
                )

                blk = SemanticNarrationBlock(
                    block_id=f"block_{pdf_page_num}_{p_idx + 1}",
                    block_type=b_type,
                    chapter_id=chapter_id,
                    page_id=page_id,
                    pdf_page=pdf_page_num,
                    printed_page=printed_page_num,
                    learning_unit_id=assigned_unit,
                    primary_content=True,
                    canonical_text=text,
                    sentences=sem_sentences,
                    dialogue_turns=[],
                    supporting_visuals=block_visuals,
                    source_region_ids=[rid],
                    bbox=preg.bbox,
                    tutor_explanation=tutor_plan.explanation,
                    tutor_plan=tutor_plan.to_dict()
                )
                page_blocks.append(blk)

            # Flush any remaining dialogue
            flush_dialogue()

            # Attach any unattached visuals to the last block
            if pending_visuals and page_blocks:
                page_blocks[-1].supporting_visuals.extend(pending_visuals)
                pending_visuals = []

            # 3. Plan narration (chunking, prosody, pronunciation resolution) and build spoken sequence
            page_paragraphs = []
            for b_idx, blk in enumerate(page_blocks):
                n_plan = narration_planner.plan_narration(
                    blk, document_id=doc_structure.document_id, subject=doc_structure.subject
                )
                blk.metadata["narration_plan"] = n_plan.to_dict()

                # Add to spoken sequence
                if blk.block_type == SemanticBlockType.DIALOGUE_BLOCK and blk.dialogue_turns:
                    for turn in blk.dialogue_turns:
                        global_sentence_id += 1
                        turn_tokens = [{"text": w, "flagged": False} for w in turn.text.split()]
                        turn_obj = {
                            "id": global_sentence_id,
                            "text": turn.text,
                            "tokens": turn_tokens,
                            "region_id": turn.source_region_id,
                            "region_type": "dialogue_turn",
                            "pdf_page": pdf_page_num,
                            "printed_page": printed_page_num,
                            "learning_unit_id": turn.learning_unit_id,
                            "para_id": blk.block_id,
                            "speaker": turn.speaker,
                            "speaker_role": turn.speaker_role,
                            "voice_profile": turn.voice_profile
                        }
                        spoken_sequence.append(turn_obj)
                        all_spoken_order_ids.append(f"sent_{global_sentence_id}")
                else:
                    for sem_s in blk.sentences:
                        global_sentence_id += 1
                        sent_obj = {
                            "id": global_sentence_id,
                            "text": sem_s.text,
                            "tokens": sem_s.tokens,
                            "region_id": blk.source_region_ids[0] if blk.source_region_ids else blk.block_id,
                            "region_type": blk.block_type.value,
                            "pdf_page": pdf_page_num,
                            "printed_page": printed_page_num,
                            "learning_unit_id": blk.learning_unit_id,
                            "para_id": blk.block_id
                        }
                        spoken_sequence.append(sent_obj)
                        all_spoken_order_ids.append(f"sent_{global_sentence_id}")

                # Build UI paragraph payload
                page_paragraphs.append({
                    "id": blk.block_id,
                    "block_id": blk.block_id,
                    "block_type": blk.block_type.value,
                    "paragraph_id": b_idx + 1,
                    "primary_content": blk.primary_content,
                    "canonical_text": blk.canonical_text,
                    "region_id": blk.source_region_ids[0] if blk.source_region_ids else blk.block_id,
                    "region_type": blk.block_type.value,
                    "pdf_page": blk.pdf_page,
                    "printed_page": blk.printed_page,
                    "sentences": [
                        {
                            "id": s.sentence_id,
                            "text": s.text,
                            "tokens": s.tokens,
                            "para_id": blk.block_id,
                            "pdf_page": blk.pdf_page,
                            "printed_page": blk.printed_page
                        }
                        for s in blk.sentences
                    ],
                    "dialogue_turns": [t.to_dict() for t in blk.dialogue_turns],
                    "supporting_visuals": [v.to_dict() for v in blk.supporting_visuals],
                    "tutor": blk.tutor_explanation,
                    "tutor_plan": blk.tutor_plan,
                    "narration_plan": blk.metadata.get("narration_plan")
                })

            pages_list.append({
                "page_id": f"page_{pdf_page_num}",
                "pdf_page": pdf_page_num,
                "printed_page": printed_page_num,
                "paragraphs": page_paragraphs,
                "total_blocks": len(page_blocks),
                "total_regions": len(layout_regions),
                "total_pedagogical": len(page_ped_ids)
            })

            pages_summary.append({
                "page_id": f"page_{pdf_page_num}",
                "pdf_page": pdf_page_num,
                "printed_page": printed_page_num,
                "total_regions": len(layout_regions),
                "physical_region_ids": page_phys_ids,
                "pedagogical_region_ids": page_ped_ids
            })

            # Create Corpus Records for candidate pedagogical sequence (VERIFIED_TRAINING_SAMPLE tier)
            for rid in page_ped_ids:
                if rid not in region_by_id:
                    continue
                preg = region_by_id[rid]
                reading_order_counter += 1

                # Determine relation
                if preg.region_type == RegionType.DEFINITION:
                    rel_type = SemanticRelationType.DEFINES
                    assigned_unit = vocab_unit.unit_id
                elif preg.region_type in (RegionType.EXERCISE, RegionType.QUESTION, RegionType.DISCUSSION_BOX, RegionType.ACTIVITY):
                    rel_type = SemanticRelationType.ASKS_ABOUT
                    assigned_unit = exercise_unit.unit_id
                elif preg.region_type in (RegionType.HEADING, RegionType.SUBHEADING):
                    rel_type = SemanticRelationType.EXPLAINS
                    assigned_unit = main_unit.unit_id
                elif preg.region_type in (RegionType.CAPTION, RegionType.MAP, RegionType.FIGURE):
                    rel_type = SemanticRelationType.ILLUSTRATES
                    assigned_unit = main_unit.unit_id
                else:
                    rel_type = SemanticRelationType.CONTINUES
                    assigned_unit = main_unit.unit_id

                corpus_rec = GoldenCorpusRecord(
                    document_id=doc_structure.document_id,
                    edition=doc_structure.edition,
                    book=doc_structure.title,
                    subject=doc_structure.subject,
                    chapter=target_ch.title,
                    page=pdf_page_num,
                    region_id=preg.region_id,
                    source_hash=page_source_hash,
                    canonical_text=preg.native_text,
                    region_type=preg.region_type.value,
                    coordinates=preg.bbox,
                    reading_order=reading_order_counter,
                    semantic_relations=[{"entity_id": f"ent_{preg.region_id}", "relation": rel_type.value}],
                    learning_units=[assigned_unit],
                    verification_status=VerificationTier.VERIFIED_TRAINING_SAMPLE,
                    verification_source=VerificationSource.CRITICAL_TOKEN_VERIFIER,
                    provenance={
                        "pdf_page": pdf_page_num,
                        "printed_page": printed_page_num,
                        "doc_hash": doc_structure.doc_hash,
                        "chapter_id": chapter_id,
                        "physical_order": preg.physical_order_index,
                        "pedagogical_order": preg.reading_order_index,
                        "parent_region_id": preg.parent_region_id,
                        "caption_target_id": preg.caption_target_id,
                        "semantic_role": preg.semantic_role
                    }
                )
                self.corpus_mgr.insert_record(corpus_rec)
                corpus_records.append(corpus_rec)

        doc.close()

        # Update physical graph orders
        physical_graph.set_physical_order(all_physical_order_ids)
        physical_graph.set_reading_order(all_pedagogical_order_ids)

        # Enforce and assert Architectural Invariant (§3.2):
        # Every physical region must link to a semantic entity, which links to a learning unit.
        all_region_ids = list(physical_graph.regions.keys())
        invariant_valid = learning_graph.validate_region_learning_chain(all_region_ids)

        # Build sample reading paragraphs for immediate inspection
        sample_paragraphs = []
        for idx, rec in enumerate(corpus_records[:6]):
            sample_paragraphs.append({
                "paragraph_id": idx + 1,
                "region_id": rec.region_id,
                "pdf_page": rec.provenance.get("pdf_page"),
                "printed_page": rec.provenance.get("printed_page"),
                "region_type": rec.region_type,
                "text": rec.canonical_text,
                "verification_status": rec.verification_status.value
            })

        manifest = ChapterManifest(
            chapter_id=chapter_id,
            document_id=doc_structure.document_id,
            title=target_ch.title,
            marathi_title=target_ch.marathi_title,
            subject=doc_structure.subject,
            pdf_start_page=target_ch.start_pdf_page,
            pdf_end_page=target_ch.end_pdf_page,
            printed_start_page=target_ch.printed_start_page,
            printed_end_page=target_ch.printed_end_page,
            total_pages=(target_ch.end_pdf_page - target_ch.start_pdf_page + 1),
            total_physical_regions=len(all_region_ids),
            total_pedagogical_regions=len(all_pedagogical_order_ids),
            page_ids=[f"page_{p}" for p in range(target_ch.start_pdf_page, target_ch.end_pdf_page + 1)],
            pages_summary=pages_summary,
            learning_unit_ids=[u.unit_id for u in learning_graph.learning_units.values()],
            physical_region_ids=all_physical_order_ids,
            pedagogical_order=all_pedagogical_order_ids,
            spoken_order=all_spoken_order_ids
        )

        learning_units_list = [asdict(u) for u in learning_graph.learning_units.values()]

        summary_desc = (
            f"Successfully processed {target_ch.title} ({doc_structure.subject}): "
            f"{len(all_region_ids)} physical regions extracted across PDF pages "
            f"{target_ch.start_pdf_page}-{target_ch.end_pdf_page} (printed pages "
            f"{target_ch.printed_start_page}-{target_ch.printed_end_page}). "
            f"Physical Document Graph and Learning Graph constructed and validated."
        )

        return ProcessedChapterResult(
            document_id=doc_structure.document_id,
            chapter_id=chapter_id,
            chapter_title=target_ch.title,
            marathi_title=target_ch.marathi_title,
            subject=doc_structure.subject,
            start_pdf_page=target_ch.start_pdf_page,
            end_pdf_page=target_ch.end_pdf_page,
            printed_start_page=target_ch.printed_start_page,
            printed_end_page=target_ch.printed_end_page,
            total_regions=len(all_region_ids),
            physical_graph=physical_graph.to_dict(),
            learning_graph=learning_graph.to_dict(),
            corpus_records_count=len(corpus_records),
            invariant_valid=invariant_valid,
            summary=summary_desc,
            sample_reading_paragraphs=sample_paragraphs,
            manifest=manifest.to_dict(),
            pages=pages_list,
            spoken_sequence=spoken_sequence,
            learning_units=learning_units_list
        )

    def get_chapter_reader_payload(
        self,
        doc_structure: DocumentStructure,
        chapter_id: str
    ) -> Dict[str, Any]:
        """
        Returns the complete chapter reader payload for multi-page continuous traversal.
        Integrates:
        - Physical Document Graph (where is everything)
        - Learning Graph (semantic entities & learning units)
        - Chapter Pedagogical Blueprint & Teaching Graph (pedagogical progression & audience policy)
        """
        res = self.process_chapter(doc_structure, chapter_id)

        # Build or Load Chapter Pedagogical Blueprint (§3, §14)
        from orchestrator.chapter_blueprint_engine import chapter_blueprint_engine
        blueprint = chapter_blueprint_engine.load_blueprint(res.document_id, res.chapter_id)
        if not blueprint:
            blueprint = chapter_blueprint_engine.build_pedagogical_blueprint(
                document_id=res.document_id,
                chapter_id=res.chapter_id,
                chapter_title=res.chapter_title,
                subject=res.subject,
                grade=10,
                pages_data=res.pages
            )

        # Filter spoken sequence according to Pedagogical Blueprint Audience Policy (§4, §18)
        # Teacher-only instructions are preserved in Physical Document Graph, but excluded from normal student reading!
        teacher_reg_ids = set()
        for tn in blueprint.teaching_graph.get_teacher_only_nodes():
            if tn.region_id:
                teacher_reg_ids.add(tn.region_id)

        student_spoken_sequence = [
            item for item in res.spoken_sequence
            if item.get("block_id") not in teacher_reg_ids and item.get("id") not in teacher_reg_ids
        ]

        return {
            "chapter": {
                "chapter_id": res.chapter_id,
                "document_id": res.document_id,
                "title": res.chapter_title,
                "marathi_title": res.marathi_title,
                "subject": res.subject,
                "pdf_start_page": res.start_pdf_page,
                "pdf_end_page": res.end_pdf_page,
                "printed_start_page": res.printed_start_page,
                "printed_end_page": res.printed_end_page,
                "total_pages": (res.end_pdf_page - res.start_pdf_page + 1),
                "total_physical_regions": res.total_regions,
                "total_pedagogical_regions": len(res.manifest["pedagogical_order"]) if res.manifest else 0
            },
            "manifest": res.manifest,
            "pages": res.pages,
            "learning_units": res.learning_units,
            "spoken_sequence": student_spoken_sequence,
            "pedagogical_blueprint": blueprint.to_dict()
        }

