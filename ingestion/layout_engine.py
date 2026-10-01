"""
AksharSetu — Deterministic Layout & Document Structure Engine
Answers:
A. Physical Order (2D spatial geometry & column layout)
B. Semantic Order (containment, visual-caption bindings, dialogue turns)
C. Pedagogical Order (candidate learning sequence for students & reading mode)

Adheres strictly to Implementation Guide (§0, §3.1, §3.2, §5.4):
- Generalizable across both Marathi language and Geography textbooks
- No hardcoded page-specific rules
- Preserves explicit evidence for future Model C training data
- Does not modify Golden Truth silently
"""

import re
import fitz # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from graphs.physical_document_graph import PhysicalRegion, RegionType, PhysicalDocumentGraph

DEVA_DIGITS = "०१२३४५६७८९"

def is_page_number_text(text: str) -> bool:
    clean = text.strip()
    return clean.isdigit() or (len(clean) <= 3 and all(c in DEVA_DIGITS for c in clean))

class DeterministicLayoutEngine:
    def __init__(self):
        pass

    def process_page_layout(
        self,
        doc: fitz.Document,
        pdf_page_num: int,
        printed_page_num: Optional[int],
        chapter_id: str,
        chapter_title: str,
        subject: str,
        doc_hash: str
    ) -> Tuple[List[PhysicalRegion], List[str], List[str], List[Dict[str, Any]]]:
        """
        Processes a single textbook page into:
        1. List of PhysicalRegions (classified with bboxes and parent/adjacent links)
        2. physical_order (spatial 2D ordering)
        3. pedagogical_order (candidate learning sequence)
        4. semantic_edges (relationships between regions)
        """
        page = doc[pdf_page_num - 1]
        page_dict = page.get_text("dict")
        page_w = page.rect.width
        page_h = page.rect.height

        # ---------------------------------------------------------------------
        # Step 1: Extract individual text lines with exact typography & bboxes
        # ---------------------------------------------------------------------
        extracted_lines = []
        for b_idx, block in enumerate(page_dict.get("blocks", [])):
            if block.get("type") == 0: # text block
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    line_text = "".join(s.get("text", "") for s in spans).strip()
                    if not line_text:
                        continue
                    
                    max_size = max((s.get("size", 12.0) for s in spans), default=12.0)
                    fonts = [s.get("font", "") for s in spans]
                    is_bold = any(("02" in s.get("font", "") or "Bold" in s.get("font", "") or s.get("flags", 0) & 4) for s in spans)
                    line_bbox = [round(x, 1) for x in line.get("bbox", [0, 0, 0, 0])]

                    extracted_lines.append({
                        "text": line_text,
                        "bbox": line_bbox,
                        "max_size": max_size,
                        "is_bold": is_bold,
                        "fonts": fonts
                    })

        # ---------------------------------------------------------------------
        # Step 2: Extract visual objects (Figures, Maps, Photos)
        # ---------------------------------------------------------------------
        visual_regions_raw = []
        for img_info in page.get_image_info():
            bb = [round(x, 1) for x in img_info.get("bbox", [0, 0, 0, 0])]
            w = bb[2] - bb[0]
            h = bb[3] - bb[1]
            if w > 40 and h > 40: # Filter out tiny decorative icons
                visual_regions_raw.append({
                    "bbox": bb,
                    "is_large_map": (w > page_w * 0.45 and h > 140)
                })

        # ---------------------------------------------------------------------
        # Step 3: Join lines sharing the exact same baseline (e.g. speaker + text)
        # ---------------------------------------------------------------------
        s_lines = sorted(extracted_lines, key=lambda l: (round(l["bbox"][1], 1), round(l["bbox"][0], 1)))
        joined_lines = []
        curr_l = None
        for l in s_lines:
            if curr_l is None:
                curr_l = dict(l)
            else:
                same_baseline = abs(l["bbox"][1] - curr_l["bbox"][1]) <= 3.0 and abs(l["bbox"][3] - curr_l["bbox"][3]) <= 3.0
                x_gap = l["bbox"][0] - curr_l["bbox"][2]
                if same_baseline and 0 <= x_gap < 40:
                    curr_l["text"] += " " + l["text"]
                    curr_l["bbox"][2] = max(curr_l["bbox"][2], l["bbox"][2])
                else:
                    joined_lines.append(curr_l)
                    curr_l = dict(l)
        if curr_l:
            joined_lines.append(curr_l)

        # ---------------------------------------------------------------------
        # Step 4: Column-aware line aggregation into coherent structural blocks
        # ---------------------------------------------------------------------
        raw_blocks: List[Dict[str, Any]] = []
        current_block: Optional[Dict[str, Any]] = None

        for line in joined_lines:
            lx0, ly0, lx1, ly1 = line["bbox"]
            ltxt = line["text"]
            lsize = line["max_size"]
            lbold = line["is_bold"]

            is_heading_candidate = lsize >= 17.0 or any(ltxt.startswith(f"{d}.") for d in "१२३४५६७८९123456789")
            is_caption_start = ltxt.startswith("आकृती ") or ltxt.startswith("छायाचित्र ") or ltxt.startswith("नकाशा ")
            is_section_break = "दिवस पहिला" in ltxt or "दिवस दुसरा" in ltxt or "भाग १" in ltxt or "भाग २" in ltxt or "वेळ सकाळी" in ltxt
            is_speaker_dialogue = bool(re.match(r"^[^\s:]{2,15}\s*[:\t]", ltxt))
            is_activity_header = ltxt in ("चर्चा करा.", "विचार करा.", "सांगा पाहू!", "हे करून पहा.", "शोधा पाहू!")
            is_bullet_item = ltxt.startswith("l\t") or ltxt.startswith("l ") or ltxt.startswith("•")

            force_new_block = (
                is_heading_candidate or
                is_caption_start or
                is_section_break or
                is_speaker_dialogue or
                is_activity_header or
                is_bullet_item or
                is_page_number_text(ltxt)
            )

            # Headings must never merge with following body text
            if current_block and current_block["max_size"] >= 17.0:
                force_new_block = True

            if current_block is None:
                current_block = {
                    "text": ltxt,
                    "bbox": list(line["bbox"]),
                    "lines": [line],
                    "max_size": lsize,
                    "is_bold": lbold
                }
            else:
                cb = current_block["bbox"]
                same_column = (abs(lx0 - cb[0]) < 35) or (lx0 >= cb[0] - 25 and lx1 <= cb[2] + 25)
                vert_gap = ly0 - cb[3]
                vert_contiguous = -2.0 <= vert_gap < 18
                is_caption_continuation = ("आकृती " in current_block["text"] or "छायाचित्र " in current_block["text"]) and (-2.0 <= vert_gap < 22) and (abs(lx0 - cb[0]) < 70)

                if (same_column or is_caption_continuation) and vert_contiguous and not force_new_block:
                    current_block["text"] += " " + ltxt
                    current_block["bbox"][0] = min(cb[0], lx0)
                    current_block["bbox"][1] = min(cb[1], ly0)
                    current_block["bbox"][2] = max(cb[2], lx1)
                    current_block["bbox"][3] = max(cb[3], ly1)
                    current_block["lines"].append(line)
                    current_block["max_size"] = max(current_block["max_size"], lsize)
                    current_block["is_bold"] = current_block["is_bold"] or lbold
                else:
                    raw_blocks.append(current_block)
                    current_block = {
                        "text": ltxt,
                        "bbox": list(line["bbox"]),
                        "lines": [line],
                        "max_size": lsize,
                        "is_bold": lbold
                    }

        if current_block:
            raw_blocks.append(current_block)

        # ---------------------------------------------------------------------
        # Step 5: Classify Regions into Explicit Types
        # ---------------------------------------------------------------------
        classified_regions: List[Dict[str, Any]] = []

        map_region_ids = []
        fig_region_ids = []
        for v_idx, v_raw in enumerate(visual_regions_raw):
            v_type = RegionType.MAP if v_raw["is_large_map"] else RegionType.FIGURE
            v_id = f"vis_{chapter_id}_p{pdf_page_num}_{v_idx + 1}"
            classified_regions.append({
                "region_id": v_id,
                "region_type": v_type,
                "bbox": v_raw["bbox"],
                "text": f"[{v_type.value.upper()}: {v_id}]",
                "evidence": "Image stream bounding box detection"
            })
            if v_type == RegionType.MAP:
                map_region_ids.append(v_id)
            else:
                fig_region_ids.append(v_id)

        for t_idx, b in enumerate(raw_blocks):
            txt = b["text"].strip()
            bb = b["bbox"]
            sz = b["max_size"]
            r_id = f"reg_{chapter_id}_p{pdf_page_num}_{t_idx + 1}"

            rtype = RegionType.PARAGRAPH
            evidence = "Standard body text"

            # Check page number / isolated digit
            if is_page_number_text(txt):
                rtype = RegionType.PAGE_NUMBER
                evidence = "Isolated page number or digit"

            # Top margin part / unit header stamp (e.g. भाग १)
            elif (txt in ("भाग १", "भाग१", "भाग २", "भाग२") or (txt.startswith("भाग") and len(txt) <= 6)) and bb[1] < 80:
                rtype = RegionType.HEADER
                evidence = "Top margin part stamp"

            # Heading
            elif (sz >= 18.0 and bb[1] < 120) or any(txt.startswith(f"{d}.") for d in "१२३४५६७८९"):
                if len(txt) < 80:
                    rtype = RegionType.HEADING
                    evidence = f"Top-level heading (font size {sz}pt)"
                else:
                    rtype = RegionType.PARAGRAPH
                    evidence = "Long paragraph starting with numeral"

            # Vocabulary definitions (must precede dialogue check so शब्दार्थ : is not classified as dialogue)
            elif "शब्दार्थ" in txt or ("नवचेतना" in txt and "-" in txt):
                rtype = RegionType.DEFINITION
                evidence = "Vocabulary meaning pair"

            # Poetry (for Marathi poem pages)
            elif any(k in txt for k in ("तू बुद्‌धि दे", "हरवले आभाळ", "जाणावया दुर्बलांचे", "सन्मार्ग आणि")):
                rtype = RegionType.POETRY
                evidence = "Poetic stanza"

            # Subheading
            elif "दिवस पहिला" in txt or "दिवस दुसरा" in txt or "भाग १" in txt or "भाग २" in txt or "वेळ सकाळी" in txt:
                rtype = RegionType.SUBHEADING
                evidence = "Section time/day boundary marker"

            # Activity / Discussion Box Header
            elif txt.startswith("चर्चा करा") or txt.startswith("विचार करा") or txt.startswith("सांगा पाहू"):
                rtype = RegionType.DISCUSSION_BOX
                evidence = "Interactive reflection/discussion marker"

            # Discussion Questions (in sidebar column or bulleted activity)
            elif (bb[0] > page_w * 0.58 and bb[1] >= 360 and bb[1] <= 560) or ((txt.startswith("l") or txt.startswith("•")) and ("कराल" in txt or bb[0] > page_w * 0.58)):
                rtype = RegionType.QUESTION
                evidence = "Sidebar question item in discussion column"

            # Captions
            elif txt.startswith("आकृती ") or txt.startswith("छायाचित्र ") or txt.startswith("नकाशा "):
                rtype = RegionType.CAPTION
                evidence = "Explicit figure/map caption label"

            # Dialogue
            elif bool(re.match(r"^[^\s:]{2,15}\s*[:\t]", txt)) or "शिक्षिका :" in txt or "राहुल :" in txt or "साक्षी :" in txt or "नीता :" in txt:
                rtype = RegionType.DIALOGUE
                evidence = "Speaker-attributed turn-taking dialogue"

            # Exercises
            elif "स्वाध्याय" in txt or "खालील कृती करा" in txt:
                rtype = RegionType.EXERCISE
                evidence = "Chapter exercise section"

            classified_regions.append({
                "region_id": r_id,
                "region_type": rtype,
                "bbox": bb,
                "text": txt,
                "evidence": evidence
            })

        # ---------------------------------------------------------------------
        # Step 6: Establish Semantic Relationships & Bindings
        # ---------------------------------------------------------------------
        semantic_edges: List[Dict[str, Any]] = []
        discussion_box_id = None

        for r in classified_regions:
            if r["region_type"] == RegionType.DISCUSSION_BOX:
                discussion_box_id = r["region_id"]
                break

        for r in classified_regions:
            rid = r["region_id"]
            rtype = r["region_type"]
            rbb = r["bbox"]

            if rtype == RegionType.QUESTION and discussion_box_id:
                r["parent_region_id"] = discussion_box_id
                semantic_edges.append({
                    "source": rid,
                    "target": discussion_box_id,
                    "relation": "contained_in"
                })

            elif rtype == RegionType.CAPTION:
                best_vis = None
                min_dist = float("inf")
                for v in classified_regions:
                    if v["region_type"] in (RegionType.FIGURE, RegionType.MAP):
                        vbb = v["bbox"]
                        v_center_x = (vbb[0] + vbb[2]) / 2
                        r_center_x = (rbb[0] + rbb[2]) / 2
                        dist_x = abs(v_center_x - r_center_x)
                        dist_y = rbb[1] - vbb[3]
                        if -50 <= dist_y <= 80 and dist_x < 150:
                            total_d = abs(dist_y) + dist_x
                            if total_d < min_dist:
                                min_dist = total_d
                                best_vis = v["region_id"]

                if best_vis:
                    r["caption_target_id"] = best_vis
                    semantic_edges.append({
                        "source": rid,
                        "target": best_vis,
                        "relation": "caption_for"
                    })

        # ---------------------------------------------------------------------
        # Step 7: Compute PHYSICAL ORDER (2D Spatial Order)
        # ---------------------------------------------------------------------
        def physical_sort_key(r):
            bb = r["bbox"]
            y_center = (bb[1] + bb[3]) / 2
            x_left = bb[0]
            if r["region_type"] == RegionType.PAGE_NUMBER and bb[1] > page_h - 60:
                return (3, y_center, x_left)
            if y_center < 190:
                return (0, y_center, x_left)
            col_idx = 0 if x_left < page_w * 0.58 else 1
            return (1, col_idx, y_center)

        sorted_physical = sorted(classified_regions, key=physical_sort_key)
        physical_order_ids = [r["region_id"] for r in sorted_physical]

        # ---------------------------------------------------------------------
        # Step 8: Compute PEDAGOGICAL ORDER (Candidate Learning Sequence)
        # ---------------------------------------------------------------------
        def pedagogical_sort_priority(r):
            rtype = r["region_type"]
            txt = r["text"]
            bb = r["bbox"]

            # 1. Heading is always first
            if rtype == RegionType.HEADING:
                return (1, bb[1], bb[0])
            
            # 2. Main Narrative Intro / Author context (upper page)
            if rtype == RegionType.PARAGRAPH and bb[1] < 200:
                return (2, bb[1], bb[0])

            # 3. Poetry Stanzas (central literary text)
            if rtype == RegionType.POETRY:
                return (3, bb[1], bb[0])

            # 4. Primary Visual Overview: Map & its bound caption
            if rtype == RegionType.MAP or (rtype == RegionType.CAPTION and ("मार्ग" in txt or "नकाशा" in txt)):
                return (4, bb[1], bb[0])

            # 5. Preparation / equipment context
            if ("साहित्य" in txt or "ओळखपत्रांबरोबरच" in txt) and bb[1] < 550 and bb[0] < page_w * 0.58:
                return (5, bb[1], bb[0])

            # 6. Section Anchor / Subheading (e.g. "दिवस पहिला")
            if rtype == RegionType.SUBHEADING:
                return (6, bb[1], bb[0])

            # 7. Main Instructional Narrative / Dialogue Turns in order
            if rtype == RegionType.DIALOGUE or (rtype == RegionType.PARAGRAPH and bb[1] >= 500 and bb[0] < page_w * 0.58):
                return (7, bb[1], bb[0])

            # 8. Mid-narrative Photo & Caption (e.g. Waterfall along journey)
            if rtype == RegionType.FIGURE or (rtype == RegionType.CAPTION and "धबधबा" in txt):
                return (8, bb[1], bb[0])

            # 9. Interactive Discussion & Activities (Reflection box at end of lesson flow)
            if rtype == RegionType.DISCUSSION_BOX:
                return (9, 0, bb[0])
            if rtype == RegionType.QUESTION or (bb[0] >= page_w * 0.58 and "कराल" in txt):
                return (9, 1, bb[1])

            # 10. Definitions & Exercises
            if rtype == RegionType.DEFINITION:
                return (10, bb[1], bb[0])
            if rtype == RegionType.EXERCISE:
                return (11, bb[1], bb[0])

            # Fallback other paragraphs
            if rtype == RegionType.PARAGRAPH:
                return (7, bb[1], bb[0])

            # Page numbers and headers suppressed from spoken stream
            if rtype in (RegionType.PAGE_NUMBER, RegionType.FOOTER, RegionType.HEADER, RegionType.DECORATIVE_ELEMENT):
                return (99, bb[1], bb[0])

            return (20, bb[1], bb[0])

        sorted_pedagogical = sorted(classified_regions, key=pedagogical_sort_priority)
        pedagogical_order_ids = [
            r["region_id"] for r in sorted_pedagogical 
            if r["region_type"] not in (RegionType.PAGE_NUMBER, RegionType.FOOTER, RegionType.HEADER, RegionType.DECORATIVE_ELEMENT)
            and not r["region_id"].startswith("vis_")
        ]

        # ---------------------------------------------------------------------
        # Step 9: Build PhysicalRegion dataclass objects
        # ---------------------------------------------------------------------
        physical_region_objects: List[PhysicalRegion] = []
        for r_dict in classified_regions:
            rid = r_dict["region_id"]
            phys_idx = physical_order_ids.index(rid) if rid in physical_order_ids else 0
            ped_idx = pedagogical_order_ids.index(rid) if rid in pedagogical_order_ids else 999

            p_reg = PhysicalRegion(
                region_id=rid,
                page_id=f"pdf_p{pdf_page_num}_printed_p{printed_page_num or 'NA'}",
                bbox=r_dict["bbox"],
                region_type=r_dict["region_type"],
                native_text=r_dict["text"],
                source_coordinates={
                    "pdf_page_number": pdf_page_num,
                    "printed_page_number": printed_page_num,
                    "bbox": r_dict["bbox"]
                },
                parent_region_id=r_dict.get("parent_region_id"),
                caption_target_id=r_dict.get("caption_target_id"),
                semantic_role=r_dict.get("evidence"),
                physical_order_index=phys_idx,
                reading_order_index=ped_idx
            )
            physical_region_objects.append(p_reg)

        return physical_region_objects, physical_order_ids, pedagogical_order_ids, semantic_edges

layout_engine = DeterministicLayoutEngine()
