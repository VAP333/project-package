"""
AksharSetu — Model E: Marathi NLP Layer / MahaBERT Adapter (Phase 5 — GATED)
DO NOT ACTIVATE UNTIL PHASE 3 GATE CLEARS (Principle 7 & §5.2).
Uses L3Cube/MahaNLP & MahaBERT for contextual candidate ranking & Marathi NER.
"""

from eval.phase_gate_checks import PhaseGateChecker

class ModelEMarathiNLPAdapter:
    def __init__(self, bypass_gate: bool = False):
        if not bypass_gate:
            gate_status = PhaseGateChecker.check_phase_3_gate(safe_page_rate=0.0, cer=1.0, cta=0.0)
            if not gate_status["passed"]:
                raise PermissionError(
                    "Phase 3 gate has not cleared yet. Per Principle 7 & §5.2 of the Implementation Guide, "
                    "Model E (MahaBERT / Marathi NLP Layer) is strictly gated on Phase 3 completion."
                )
