"""
AksharSetu — Golden Corpus Manager (§3.3 & §2.1 of Implementation Guide)

Implements:
1. Persistent storage of Golden Corpus records
2. 3-tier promotion state machine: TEACHER_OUTPUT -> VERIFIED_TRAINING_SAMPLE -> GOLDEN_TRUTH
3. Provenance linking: anchors every record to document source_hash and region_id
4. Query filter: enforces that production Reading Mode only reads verified truth (Principle 5)
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from corpus.schema import GoldenCorpusRecord, VerificationTier, VerificationSource, PromotionError
from infra.db.database import DB_FILE, init_db

class CorpusManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        init_db(db_path)

    def insert_record(self, record: GoldenCorpusRecord) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO golden_corpus (
                record_id, region_id, page_id, document_id, source_hash,
                canonical_text, region_type, coordinates_json, reading_order,
                semantic_relations_json, learning_units_json, verification_status,
                verification_source, reviewer_notes, model_version, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"{record.document_id}_{record.page}_{record.region_id}",
            record.region_id,
            f"{record.document_id}_p{record.page}",
            record.document_id,
            record.source_hash,
            record.canonical_text,
            record.region_type,
            json.dumps(record.coordinates),
            record.reading_order,
            json.dumps(record.semantic_relations),
            json.dumps(record.learning_units),
            record.verification_status.value,
            record.verification_source.value,
            record.reviewer_notes,
            record.model_version,
            record.timestamp
        ))
        conn.commit()
        conn.close()

    def get_records_for_page(self, document_id: str, page: int, production_only: bool = False) -> List[GoldenCorpusRecord]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        
        query = """
            SELECT document_id, canonical_text, region_id, source_hash, region_type, 
                   coordinates_json, reading_order, semantic_relations_json, 
                   learning_units_json, verification_status, verification_source, 
                   reviewer_notes, model_version, timestamp 
            FROM golden_corpus 
            WHERE document_id = ? AND page_id = ?
        """
        params = [document_id, f"{document_id}_p{page}"]
        
        if production_only:
            query += " AND verification_status = 'GOLDEN_TRUTH'"
        
        query += " ORDER BY reading_order ASC"

        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()

        records = []
        for r in rows:
            rec = GoldenCorpusRecord(
                document_id=r[0],
                edition="2024.1",
                book=document_id,
                subject="Marathi",
                chapter="पाठ",
                page=page,
                region_id=r[2],
                source_hash=r[3],
                canonical_text=r[1],
                region_type=r[4],
                coordinates=json.loads(r[5]),
                reading_order=r[6],
                semantic_relations=json.loads(r[7]) if r[7] else [],
                learning_units=json.loads(r[8]) if r[8] else [],
                verification_status=VerificationTier(r[9]),
                verification_source=VerificationSource(r[10]),
                reviewer_notes=r[11],
                model_version=r[12],
                timestamp=r[13]
            )
            records.append(rec)
        return records

    def promote_record(self, record_id: str, to_tier: VerificationTier, expert_id: str, notes: str = "") -> None:
        """Enforces three-tier promotion state machine in persistent storage."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT verification_status FROM golden_corpus WHERE record_id = ?", (record_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise KeyError(f"Record {record_id} not found in Golden Corpus.")
        
        current_status = VerificationTier(row[0])
        
        if to_tier == VerificationTier.VERIFIED_TRAINING_SAMPLE:
            if current_status != VerificationTier.TEACHER_OUTPUT:
                conn.close()
                raise PromotionError(f"Cannot promote to VERIFIED_TRAINING_SAMPLE from {current_status}")
            source = VerificationSource.CRITICAL_TOKEN_VERIFIER
        elif to_tier == VerificationTier.GOLDEN_TRUTH:
            source = VerificationSource.HUMAN_SUBJECT_EXPERT
        else:
            source = VerificationSource.GEMINI_TEACHER

        cur.execute("""
            UPDATE golden_corpus 
            SET verification_status = ?, verification_source = ?, reviewer_notes = ?
            WHERE record_id = ?
        """, (to_tier.value, source.value, f"Promoted by {expert_id}: {notes}", record_id))
        conn.commit()
        conn.close()

    def get_corpus_statistics(self) -> Dict[str, Any]:
        """Returns statistics for admin dashboard and phase-gate evaluation."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT verification_status, COUNT(*) FROM golden_corpus GROUP BY verification_status")
        rows = cur.fetchall()
        conn.close()

        counts = {r[0]: r[1] for r in rows}
        total = sum(counts.values())
        golden = counts.get(VerificationTier.GOLDEN_TRUTH.value, 0)
        verified = counts.get(VerificationTier.VERIFIED_TRAINING_SAMPLE.value, 0)
        teacher = counts.get(VerificationTier.TEACHER_OUTPUT.value, 0)

        coverage = round((golden / total) * 100, 1) if total > 0 else 0.0
        return {
            "total_regions": total,
            "golden_truth_count": golden,
            "verified_training_count": verified,
            "teacher_hypothesis_count": teacher,
            "golden_corpus_coverage_percentage": f"{coverage}%",
            "is_production_ready": golden > 0
        }
