"""
AksharSetu — Class 8 History Granular Caching Engine (Phase 10)

Fixed-Textbook Preprocessing & Versioned Invalidation:
- Precomputes and caches expensive artifacts:
  - document parsing
  - chapter structure
  - learning graph
  - teaching graph
  - narration plan
  - speaking style
  - pronunciation
  - TTS audio
- Granular dependency-aware invalidation:
  - Pronunciation update -> invalidates affected narration/audio only.
  - TTS voice/model change -> invalidates TTS audio only.
  - Teaching graph update -> invalidates downstream narration/explanation/audio.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import hashlib
import json


class HistoryCacheLayer(str, Enum):
    DOCUMENT_PARSING = "document_parsing"
    CHAPTER_STRUCTURE = "chapter_structure"
    LEARNING_GRAPH = "learning_graph"
    TEACHING_GRAPH = "teaching_graph"
    NARRATION_PLAN = "narration_plan"
    SPEAKING_STYLE = "speaking_style"
    PRONUNCIATION = "pronunciation"
    TTS_AUDIO = "tts_audio"


@dataclass
class HistoryVersionLedger:
    schema_version: str = "v0.1"
    grammar_version: str = "v1.0"
    learning_graph_version: str = "v1.0"
    teaching_graph_version: str = "v1.0"
    narration_version: str = "v1.0"
    speaking_style_version: str = "v1.0"
    pronunciation_version: str = "v1.0"
    tts_provider: str = "sarvam"
    tts_model: str = "bulbul:v3"
    tts_voice: str = "shreya"
    document_hash: str = "AKS_HIST_PDF_HASH_V1"
    chapter_hashes: Dict[str, str] = field(default_factory=lambda: {
        f"CH_{i:02d}": f"CH_{i:02d}_HASH_V1" for i in range(1, 15)
    })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class HistoryArtifactCache:
    """
    Dependency-aware versioned caching engine for Class 8 History.
    """

    def __init__(self):
        self.ledger = HistoryVersionLedger()
        self._store: Dict[HistoryCacheLayer, Dict[str, Any]] = {
            layer: {} for layer in HistoryCacheLayer
        }

    def generate_cache_key(
        self,
        layer: HistoryCacheLayer,
        entity_id: str,
        extra_keys: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Constructs composite cache key incorporating relevant version dependencies.
        """
        ch_id = entity_id if entity_id.startswith("CH_") else "ALL"
        ch_hash = self.ledger.chapter_hashes.get(ch_id, "DEFAULT_HASH")

        parts = [
            f"layer={layer.value}",
            f"entity={entity_id}",
            f"doc_hash={self.ledger.document_hash}",
            f"ch_hash={ch_hash}",
            f"schema={self.ledger.schema_version}"
        ]

        if layer in (HistoryCacheLayer.TEACHING_GRAPH, HistoryCacheLayer.NARRATION_PLAN, HistoryCacheLayer.TTS_AUDIO):
            parts.append(f"teach_ver={self.ledger.teaching_graph_version}")

        if layer in (HistoryCacheLayer.NARRATION_PLAN, HistoryCacheLayer.TTS_AUDIO):
            parts.append(f"narr_ver={self.ledger.narration_version}")
            parts.append(f"style_ver={self.ledger.speaking_style_version}")
            parts.append(f"pron_ver={self.ledger.pronunciation_version}")

        if layer == HistoryCacheLayer.TTS_AUDIO:
            parts.append(f"provider={self.ledger.tts_provider}")
            parts.append(f"model={self.ledger.tts_model}")
            parts.append(f"voice={self.ledger.tts_voice}")

        if extra_keys:
            for k, v in sorted(extra_keys.items()):
                parts.append(f"{k}={v}")

        raw_str = "|".join(parts)
        h = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]
        return f"{layer.value}:{entity_id}:{h}"

    def get(self, layer: HistoryCacheLayer, entity_id: str, extra_keys: Optional[Dict[str, str]] = None) -> Optional[Any]:
        key = self.generate_cache_key(layer, entity_id, extra_keys)
        return self._store[layer].get(key)

    def put(self, layer: HistoryCacheLayer, entity_id: str, value: Any, extra_keys: Optional[Dict[str, str]] = None) -> str:
        key = self.generate_cache_key(layer, entity_id, extra_keys)
        self._store[layer][key] = value
        return key

    def has(self, layer: HistoryCacheLayer, entity_id: str, extra_keys: Optional[Dict[str, str]] = None) -> bool:
        key = self.generate_cache_key(layer, entity_id, extra_keys)
        return key in self._store[layer]

    # --- Granular Invalidation Methods ---

    def invalidate_pronunciation(self, chapter_id: Optional[str] = None):
        """
        Rule: Pronunciation change -> invalidate affected narration/audio only.
        Document parsing, chapter structure, and learning graph remain UNTOUCHED.
        """
        int_ver = int(self.ledger.pronunciation_version.replace("v", "").split(".")[0])
        self.ledger.pronunciation_version = f"v{int_ver + 1}.0"

        # Invalidate downstream layers
        if chapter_id:
            ch_upper = chapter_id.upper()
            self._store[HistoryCacheLayer.NARRATION_PLAN] = {
                k: v for k, v in self._store[HistoryCacheLayer.NARRATION_PLAN].items() if ch_upper not in k
            }
            self._store[HistoryCacheLayer.TTS_AUDIO] = {
                k: v for k, v in self._store[HistoryCacheLayer.TTS_AUDIO].items() if ch_upper not in k
            }
        else:
            self._store[HistoryCacheLayer.NARRATION_PLAN].clear()
            self._store[HistoryCacheLayer.TTS_AUDIO].clear()

    def invalidate_tts_voice(self, new_voice: str):
        """
        Rule: TTS voice change -> regenerate audio only.
        Document parsing, chapter structure, graphs, and narration plans remain UNTOUCHED.
        """
        self.ledger.tts_voice = new_voice
        self._store[HistoryCacheLayer.TTS_AUDIO].clear()

    def invalidate_teaching_graph(self, chapter_id: Optional[str] = None):
        """
        Rule: Teaching graph change -> invalidate downstream narration, explanation and audio.
        Document parsing, chapter structure, and learning graph remain UNTOUCHED.
        """
        int_ver = int(self.ledger.teaching_graph_version.replace("v", "").split(".")[0])
        self.ledger.teaching_graph_version = f"v{int_ver + 1}.0"

        if chapter_id:
            ch_upper = chapter_id.upper()
            self._store[HistoryCacheLayer.TEACHING_GRAPH] = {
                k: v for k, v in self._store[HistoryCacheLayer.TEACHING_GRAPH].items() if ch_upper not in k
            }
            self._store[HistoryCacheLayer.NARRATION_PLAN] = {
                k: v for k, v in self._store[HistoryCacheLayer.NARRATION_PLAN].items() if ch_upper not in k
            }
            self._store[HistoryCacheLayer.TTS_AUDIO] = {
                k: v for k, v in self._store[HistoryCacheLayer.TTS_AUDIO].items() if ch_upper not in k
            }
        else:
            self._store[HistoryCacheLayer.TEACHING_GRAPH].clear()
            self._store[HistoryCacheLayer.NARRATION_PLAN].clear()
            self._store[HistoryCacheLayer.TTS_AUDIO].clear()


history_cache = HistoryArtifactCache()
