"""
AksharSetu — Cost Tracker & Modeling Engine (§7 of Implementation Guide)

Tracks:
1. Teacher pipeline bootstrap cost (~one-time per page): input tokens + output tokens
2. Tutor Mode inference cost (per student-interaction, recurring indefinitely)
3. Pricing tiers dynamically pegged to the pinned Gemini Flash model
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import json
import os

# Gemini 2.5 Flash / Flash-tier reference pricing per 1M tokens (USD)
FLASH_PRICING = {
    "input_per_million": 0.075,   # $0.075 / 1M tokens (text/image)
    "output_per_million": 0.30,   # $0.30 / 1M tokens
}

@dataclass
class PageCostRecord:
    page_id: str
    workload_type: str # "teacher_bootstrap" or "tutor_inference"
    model_name: str
    prompt_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CostTracker:
    def __init__(self, ledger_file: str = "./data/cost_ledger.json"):
        self.ledger_file = ledger_file
        self.records: List[PageCostRecord] = []
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for r in data:
                        self.records.append(PageCostRecord(**r))
            except Exception:
                pass

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.ledger_file) or ".", exist_ok=True)
        with open(self.ledger_file, "w", encoding="utf-8") as f:
            json.dump([asdict(r) for r in self.records], f, indent=2)

    def calculate_cost(self, prompt_tokens: int, output_tokens: int) -> float:
        in_cost = (prompt_tokens / 1_000_000.0) * FLASH_PRICING["input_per_million"]
        out_cost = (output_tokens / 1_000_000.0) * FLASH_PRICING["output_per_million"]
        return round(in_cost + out_cost, 6)

    def record_usage(self, page_id: str, workload: str, model_name: str, prompt_tokens: int, output_tokens: int) -> PageCostRecord:
        cost = self.calculate_cost(prompt_tokens, output_tokens)
        record = PageCostRecord(
            page_id=page_id,
            workload_type=workload,
            model_name=model_name,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
            estimated_cost_usd=cost
        )
        self.records.append(record)
        self._save()
        return record

    def get_summary(self) -> Dict[str, Any]:
        bootstrap_cost = sum(r.estimated_cost_usd for r in self.records if r.workload_type == "teacher_bootstrap")
        tutor_cost = sum(r.estimated_cost_usd for r in self.records if r.workload_type == "tutor_inference")
        total_pages = len({r.page_id for r in self.records})
        return {
            "total_pages_annotated": total_pages,
            "bootstrap_cost_usd": round(bootstrap_cost, 4),
            "tutor_inference_cost_usd": round(tutor_cost, 4),
            "total_cost_usd": round(bootstrap_cost + tutor_cost, 4),
            "average_cost_per_page_usd": round(bootstrap_cost / total_pages, 6) if total_pages else 0.0,
            "pricing_reference": FLASH_PRICING
        }
