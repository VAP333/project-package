-- AksharSetu Relational Database Schema (§2.1 of Implementation Guide)
-- Target: PostgreSQL (compatible with SQLite for local development)

CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR(64) PRIMARY KEY,
    edition VARCHAR(32) NOT NULL,
    book_title VARCHAR(255) NOT NULL,
    subject VARCHAR(64) NOT NULL,
    source_hash VARCHAR(64) NOT NULL UNIQUE,
    total_pages INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    provenance_metadata JSONB
);

CREATE TABLE IF NOT EXISTS pages (
    page_id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) REFERENCES documents(document_id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    source_hash VARCHAR(64) NOT NULL UNIQUE,
    width FLOAT NOT NULL,
    height FLOAT NOT NULL,
    is_scanned_fallback BOOLEAN DEFAULT FALSE,
    native_text TEXT,
    reading_order_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS regions (
    region_id VARCHAR(64) PRIMARY KEY,
    page_id VARCHAR(64) REFERENCES pages(page_id) ON DELETE CASCADE,
    source_hash VARCHAR(64) NOT NULL,
    region_type VARCHAR(32) NOT NULL,
    bbox_json JSONB NOT NULL,
    native_text TEXT NOT NULL,
    canonical_text TEXT,
    reading_order_idx INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS golden_corpus (
    record_id VARCHAR(64) PRIMARY KEY,
    region_id VARCHAR(64) REFERENCES regions(region_id),
    page_id VARCHAR(64) REFERENCES pages(page_id),
    document_id VARCHAR(64) REFERENCES documents(document_id),
    source_hash VARCHAR(64) NOT NULL,
    canonical_text TEXT NOT NULL,
    region_type VARCHAR(32) NOT NULL,
    coordinates_json JSONB NOT NULL,
    reading_order INTEGER NOT NULL,
    semantic_relations_json JSONB,
    learning_units_json JSONB,
    verification_status VARCHAR(32) NOT NULL DEFAULT 'TEACHER_OUTPUT',
    verification_source VARCHAR(64) NOT NULL,
    reviewer_notes TEXT,
    model_version VARCHAR(32) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS provenance_nodes (
    node_id VARCHAR(64) PRIMARY KEY,
    chain_id VARCHAR(64) NOT NULL,
    stage VARCHAR(32) NOT NULL,
    source_hash VARCHAR(64) NOT NULL,
    parent_id VARCHAR(64) REFERENCES provenance_nodes(node_id),
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS minor_consents (
    student_pseudonym VARCHAR(64) PRIMARY KEY,
    school_id VARCHAR(64) NOT NULL,
    consent_grantor VARCHAR(64) NOT NULL,
    consent_status VARCHAR(32) NOT NULL DEFAULT 'GRANTED',
    voice_allowed BOOLEAN DEFAULT TRUE,
    tutor_allowed BOOLEAN DEFAULT TRUE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);
