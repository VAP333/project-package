"""
AksharSetu — Model C: Reading-Order Prediction (Phase 5 — GATED)
DO NOT ACTIVATE UNTIL PHASE 3 GATE CLEARS (Principle 7 & §5.2).
"""

from eval.phase_gate_checks import PhaseGateChecker

class ModelCReadingOrderPredictor:
    def __init__(self, bypass_gate: bool = False):
        if not bypass_gate:
            # Enforce gate invariant
            gate_status = PhaseGateChecker.check_phase_3_gate(safe_page_rate=0.0, cer=1.0, cta=0.0)
            if not gate_status["passed"]:
                raise PermissionError(
                    "Phase 3 gate has not cleared yet. Per Principle 7 & §5.2 of the Implementation Guide, "
                    "Model C (Reading-Order Prediction) is strictly gated on Phase 3 completion."
                )

    def predict_reading_order(self, regions: list) -> list:
        # Sort top-to-bottom, left-to-right as baseline
        return sorted(regions, key=lambda r: (r.bbox[1], r.bbox[0]))
