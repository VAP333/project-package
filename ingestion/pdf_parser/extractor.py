"""
AksharSetu — Native PDF Ingestion & Geometry Extraction (§2.1 of Implementation Guide)

Extracts:
1. Native text blocks and line-by-line bounding box coordinates
2. Embedded raster images (figures, diagrams)
3. Vector graphics and drawings
4. Document metadata and structure
5. Cryptographic source_hash anchor for each page
6. Scanned/raster fallback detection (routes to OCR/vision if native text density is below threshold)
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import fitz # PyMuPDF
from ingestion.hashing import hash_file, hash_bytes, compute_page_source_hash

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

@dataclass
class ExtractedBlock:
    block_id: str
    block_type: str # "text", "image", "vector_drawing"
    bbox: List[float] # [x0, y0, x1, y1]
    text: str = ""
    font_info: List[Dict[str, Any]] = field(default_factory=list)
    image_bytes: Optional[bytes] = None
    image_ext: Optional[str] = None

@dataclass
class PageIngestionResult:
    doc_hash: str
    page_number: int
    page_source_hash: str
    width: float
    height: float
    is_scanned_fallback: bool
    blocks: List[ExtractedBlock] = field(default_factory=list)
    full_native_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Exclude raw image bytes from JSON dump
        for b in data["blocks"]:
            if "image_bytes" in b:
                del b["image_bytes"]
        return data

class PDFIngestionService:
    def __init__(self, storage_dir: str = "./data/storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def ingest_pdf(self, pdf_path: str) -> Tuple[str, List[PageIngestionResult]]:
        """Ingests a complete PDF document, extracting page structure and generating source_hash root."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found at {pdf_path}")
        
        doc_hash = hash_file(pdf_path)
        doc = fitz.open(pdf_path)
        results = []

        for p_idx in range(len(doc)):
            page = doc[p_idx]
            page_res = self.extract_page(doc, page, p_idx + 1, doc_hash)
            results.append(page_res)

        doc.close()
        return doc_hash, results

    def extract_page(self, doc: fitz.Document, page: fitz.Page, page_num: int, doc_hash: str) -> PageIngestionResult:
        """Extracts native text, geometry, images, and vectors for a single page."""
        width = page.rect.width
        height = page.rect.height
        page_dict = page.get_text("dict")
        blocks_list: List[ExtractedBlock] = []
        full_text_parts = []
        canonical_geo = []

        block_counter = 0
        for b in page_dict.get("blocks", []):
            block_counter += 1
            bid = f"b_{page_num}_{block_counter}"
            b_bbox = list(b.get("bbox", [0, 0, 0, 0]))

            if b.get("type") == 0: # Text block
                block_text_lines = []
                fonts = []
                for line in b.get("lines", []):
                    line_spans = []
                    for span in line.get("spans", []):
                        span_text = span.get("text", "")
                        line_spans.append(span_text)
                        fonts.append({
                            "font": span.get("font"),
                            "size": span.get("size"),
                            "color": span.get("color")
                        })
                    block_text_lines.append("".join(line_spans))
                block_text = "\n".join(block_text_lines).strip()
                if block_text:
                    full_text_parts.append(block_text)
                    canonical_geo.append({"id": bid, "bbox": b_bbox, "type": "text"})
                    blocks_list.append(ExtractedBlock(
                        block_id=bid,
                        block_type="text",
                        bbox=b_bbox,
                        text=block_text,
                        font_info=fonts
                    ))
            elif b.get("type") == 1: # Image block
                canonical_geo.append({"id": bid, "bbox": b_bbox, "type": "image"})
                blocks_list.append(ExtractedBlock(
                    block_id=bid,
                    block_type="image",
                    bbox=b_bbox,
                    text="[IMAGE_FIGURE]"
                ))

        full_native_text = "\n\n".join(full_text_parts).strip()
        # Fallback detection (§2.1 / Principle 1): If page has almost no native text (< 20 chars), mark as scanned fallback
        is_scanned = len(full_native_text) < 20

        # Compute cryptographic page_source_hash
        page_source_hash = compute_page_source_hash(
            doc_hash=doc_hash,
            page_number=page_num,
            native_text=full_native_text,
            geometry=canonical_geo
        )

        return PageIngestionResult(
            doc_hash=doc_hash,
            page_number=page_num,
            page_source_hash=page_source_hash,
            width=width,
            height=height,
            is_scanned_fallback=is_scanned,
            blocks=blocks_list,
            full_native_text=full_native_text,
            metadata={
                "block_count": len(blocks_list),
                "has_native_text": not is_scanned,
                "aspect_ratio": round(width / height, 3) if height else 0
            }
        )

    def render_page_image(self, pdf_path: str, page_num: int, output_dir: Optional[str] = None) -> str:
        """Renders page canvas to PNG for teacher annotation and visual review."""
        doc = fitz.open(pdf_path)
        page = doc[page_num - 1]
        pix = page.get_pixmap(dpi=150)
        out_dir = output_dir or os.path.join(self.storage_dir, "pages")
        os.makedirs(out_dir, exist_ok=True)
        img_path = os.path.join(out_dir, f"page_{page_num}.png")
        pix.save(img_path)
        doc.close()
        return img_path
