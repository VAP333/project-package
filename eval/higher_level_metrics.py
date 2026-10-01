"""
AksharSetu — Higher Level Accessibility & Layout Metrics (§6.3 of Implementation Guide)

Includes:
1. Safe-Page Rate: % of pages readable without an unsafe substantive error (Headline Accessibility Metric)
2. Reading-Order Accuracy
3. Region Classification Accuracy
"""

from typing import List, Dict, Any, Tuple

def calculate_reading_order_accuracy(gold_order: List[str], pred_order: List[str]) -> float:
    """
    Computes pairwise relative order accuracy between gold sequence and predicted sequence.
    """
    if len(gold_order) <= 1:
        return 1.0

    # Common elements only
    common = [rid for rid in gold_order if rid in pred_order]
    if len(common) <= 1:
        return 1.0

    pos_pred = {rid: i for i, rid in enumerate(pred_order)}
    concordant = 0
    total_pairs = 0

    for i in range(len(common)):
        for j in range(i + 1, len(common)):
            total_pairs += 1
            if pos_pred[common[i]] < pos_pred[common[j]]:
                concordant += 1

    return round(concordant / total_pairs, 4) if total_pairs > 0 else 1.0

def calculate_safe_page_rate(page_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    SAFE-PAGE RATE (§6.3):
    Headline accessibility metric. A page is considered 'safe' if and only if:
    1. Critical Token Accuracy == 1.0 (zero corrupted numerals, units, formulas)
    2. Character Error Rate <= 0.05 (95%+ character fidelity)
    3. Reading Order Accuracy >= 0.90
    """
    if not page_evaluations:
        return {"total_pages": 0, "safe_pages": 0, "safe_page_rate": 0.0}

    safe_count = 0
    breakdown = []

    for pe in page_evaluations:
        cer = pe.get("cer", 0.0)
        cta = pe.get("critical_token_accuracy", 1.0)
        roa = pe.get("reading_order_accuracy", 1.0)

        is_safe = (cta == 1.0) and (cer <= 0.05) and (roa >= 0.90)
        if is_safe:
            safe_count += 1

        breakdown.append({
            "page_id": pe.get("page_id", "unknown"),
            "is_safe": is_safe,
            "cer": cer,
            "critical_token_accuracy": cta,
            "reading_order_accuracy": roa
        })

    rate = safe_count / len(page_evaluations)
    return {
        "total_pages": len(page_evaluations),
        "safe_pages": safe_count,
        "safe_page_rate": round(rate, 4),
        "safe_page_percentage": f"{round(rate * 100, 1)}%",
        "evaluations": breakdown
    }
