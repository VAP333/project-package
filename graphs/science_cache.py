"""
AksharSetu — Class 8 Science Cache Layer (Phase 10)

Granular Invalidation Caching across layers:
1. MANIFEST (static document manifest)
2. CHAPTER_STRUCTURE (chapter metadata & learning units)
3. PHYSICAL_GRAPH (extracted regions and page topology)
4. LEARNING_GRAPH (concepts, entities, relationships)
5. TEACHING_GRAPH (scaffolding and instructional prompts)
6. NARRATION_PLAN (planned narration sequences)
7. PRONUNCIATION_LEXICON (pronunciation entries)
8. READER_PAYLOAD (synthesized Reader UI structures)
"""

from enum import Enum
from typing import Dict, Any, Optional


class ScienceCacheLayer(str, Enum):
    MANIFEST = "manifest"
    CHAPTER_STRUCTURE = "chapter_structure"
    PHYSICAL_GRAPH = "physical_graph"
    LEARNING_GRAPH = "learning_graph"
    TEACHING_GRAPH = "teaching_graph"
    NARRATION_PLAN = "narration_plan"
    PRONUNCIATION_LEXICON = "pronunciation_lexicon"
    READER_PAYLOAD = "reader_payload"


class ScienceCache:
    """In-memory cache with granular layer-based invalidation."""

    def __init__(self):
        self._stores: Dict[ScienceCacheLayer, Dict[str, Any]] = {
            layer: {} for layer in ScienceCacheLayer
        }

    def get(self, layer: ScienceCacheLayer, key: str) -> Optional[Any]:
        return self._stores[layer].get(key)

    def put(self, layer: ScienceCacheLayer, key: str, value: Any):
        self._stores[layer][key] = value

    def invalidate_layer(self, layer: ScienceCacheLayer):
        self._stores[layer].clear()

    def invalidate_all(self):
        for layer in ScienceCacheLayer:
            self._stores[layer].clear()


science_cache = ScienceCache()
