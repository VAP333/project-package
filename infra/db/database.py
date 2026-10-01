"""
AksharSetu — Database Connection & Storage Manager (§2.1 of Implementation Guide)
Supports SQLite (local dev) and PostgreSQL (production).
"""

import os
import sqlite3
import json
from typing import Dict, Any, List, Optional

DB_FILE = "./data/aksharsetu.db"

def init_db(db_path: str = DB_FILE) -> None:
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # SQLite schema
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS documents (
        document_id TEXT PRIMARY KEY,
        edition TEXT NOT NULL,
        book_title TEXT NOT NULL,
        subject TEXT NOT NULL,
        source_hash TEXT NOT NULL UNIQUE,
        total_pages INTEGER NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        provenance_metadata TEXT
    );

    CREATE TABLE IF NOT EXISTS pages (
        page_id TEXT PRIMARY KEY,
        document_id TEXT,
        page_number INTEGER NOT NULL,
        source_hash TEXT NOT NULL UNIQUE,
        width REAL NOT NULL,
        height REAL NOT NULL,
        is_scanned_fallback INTEGER DEFAULT 0,
        native_text TEXT,
        reading_order_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(document_id) REFERENCES documents(document_id)
    );

    CREATE TABLE IF NOT EXISTS regions (
        region_id TEXT PRIMARY KEY,
        page_id TEXT,
        source_hash TEXT NOT NULL,
        region_type TEXT NOT NULL,
        bbox_json TEXT NOT NULL,
        native_text TEXT NOT NULL,
        canonical_text TEXT,
        reading_order_idx INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(page_id) REFERENCES pages(page_id)
    );

    CREATE TABLE IF NOT EXISTS golden_corpus (
        record_id TEXT PRIMARY KEY,
        region_id TEXT,
        page_id TEXT,
        document_id TEXT,
        source_hash TEXT NOT NULL,
        canonical_text TEXT NOT NULL,
        region_type TEXT NOT NULL,
        coordinates_json TEXT NOT NULL,
        reading_order INTEGER NOT NULL,
        semantic_relations_json TEXT,
        learning_units_json TEXT,
        verification_status TEXT DEFAULT 'TEACHER_OUTPUT',
        verification_source TEXT NOT NULL,
        reviewer_notes TEXT,
        model_version TEXT NOT NULL,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS provenance_nodes (
        node_id TEXT PRIMARY KEY,
        chain_id TEXT NOT NULL,
        stage TEXT NOT NULL,
        source_hash TEXT NOT NULL,
        parent_id TEXT,
        metadata_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at", DB_FILE)
