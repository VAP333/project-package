"""
AksharSetu — Provenance Chain Scaffold (§2.1 of Implementation Guide)
Enforces: PDF -> page -> region -> text -> verification -> Golden Corpus entry -> learning graph -> tutor answer.
Queryable and cryptographically anchored to source_hash.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json

@dataclass
class ProvenanceNode:
    node_id: str
    stage: str # "pdf", "page", "region", "text", "verification", "golden_corpus", "learning_graph", "tutor_answer"
    source_hash: str
    parent_id: Optional[str]
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProvenanceChain:
    chain_id: str
    nodes: Dict[str, ProvenanceNode] = field(default_factory=dict)
    root_pdf_id: Optional[str] = None

    def add_node(self, node_id: str, stage: str, source_hash: str, parent_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> ProvenanceNode:
        if parent_id and parent_id not in self.nodes:
            raise ValueError(f"Parent node {parent_id} does not exist in provenance chain {self.chain_id}")
        
        node = ProvenanceNode(
            node_id=node_id,
            stage=stage,
            source_hash=source_hash,
            parent_id=parent_id,
            metadata=metadata or {}
        )
        self.nodes[node_id] = node
        if stage == "pdf" and not self.root_pdf_id:
            self.root_pdf_id = node_id
        return node

    def trace_lineage(self, leaf_node_id: str) -> List[ProvenanceNode]:
        """Traces lineage from leaf back to the root PDF document."""
        if leaf_node_id not in self.nodes:
            raise KeyError(f"Node {leaf_node_id} not found in chain")
        
        lineage = []
        curr: Optional[ProvenanceNode] = self.nodes[leaf_node_id]
        while curr:
            lineage.append(curr)
            curr = self.nodes.get(curr.parent_id) if curr.parent_id else None
        return list(reversed(lineage))

    def verify_integrity(self, leaf_node_id: str) -> bool:
        """Verifies that the lineage chain back to PDF is unbroken."""
        lineage = self.trace_lineage(leaf_node_id)
        if not lineage:
            return False
        return lineage[0].stage == "pdf"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain_id": self.chain_id,
            "root_pdf_id": self.root_pdf_id,
            "nodes": {k: asdict(v) for k, v in self.nodes.items()}
        }
