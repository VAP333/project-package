"""
AksharSetu — Document Hashing & Provenance Root (§2.1 of Implementation Guide)
Computes source_hash for every ingested PDF document, page, and region.
Ensures that all downstream structures are cryptographically anchored to original PDF geometry.
"""

import hashlib
import json
from typing import Dict, Any, List, Union

def hash_bytes(data: bytes) -> str:
    """Computes SHA-256 hex digest for arbitrary bytes."""
    return hashlib.sha256(data).hexdigest()

def hash_file(filepath: str) -> str:
    """Computes SHA-256 hex digest of a file in chunks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_page_source_hash(doc_hash: str, page_number: int, native_text: str, geometry: List[Dict[str, Any]]) -> str:
    """
    Computes deterministic source_hash for a single page.
    Combines:
    - doc_hash (parent document SHA-256)
    - page_number
    - native extracted text
    - canonical geometry list (bboxes, coordinates)
    """
    canonical_geo = json.dumps(geometry, sort_keys=True)
    payload = f"{doc_hash}:{page_number}:{native_text.strip()}:{canonical_geo}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def compute_region_hash(page_source_hash: str, region_id: str, bbox: List[float], native_text: str) -> str:
    """
    Computes deterministic hash for an individual region within a page.
    """
    payload = f"{page_source_hash}:{region_id}:{bbox}:{native_text.strip()}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
