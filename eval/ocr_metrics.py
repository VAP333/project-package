"""
AksharSetu — OCR & Critical Token Metrics (§6.2 of Implementation Guide)

Implements:
1. Character Error Rate (CER) via Levenshtein edit distance
2. Word Error Rate (WER)
3. Critical-Token Accuracy (CTA) — strictly asserts numbers, units, formulas
"""

from typing import List, Tuple, Dict, Any
import unicodedata
from correction.critical_token_pipeline import CriticalTokenPipeline

def levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard dynamic-programming Levenshtein distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_cer(reference: str, hypothesis: str) -> float:
    """Character Error Rate = Levenshtein(ref, hyp) / len(ref)."""
    ref_norm = unicodedata.normalize("NFC", reference).strip()
    hyp_norm = unicodedata.normalize("NFC", hypothesis).strip()
    if not ref_norm:
        return 0.0 if not hyp_norm else 1.0
    dist = levenshtein_distance(ref_norm, hyp_norm)
    return round(min(1.0, dist / len(ref_norm)), 4)

def calculate_wer(reference: str, hypothesis: str) -> float:
    """Word Error Rate = Levenshtein on word tokens / total ref words."""
    ref_words = reference.strip().split()
    hyp_words = hypothesis.strip().split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    dist = levenshtein_distance(ref_words, hyp_words)
    return round(min(1.0, dist / len(ref_words)), 4)

def calculate_critical_token_accuracy(reference_tokens: List[str], hypothesis_tokens: List[str]) -> Dict[str, Any]:
    """Calculates accuracy on critical tokens (numbers, units, formulas)."""
    pipeline = CriticalTokenPipeline()
    total_critical = 0
    correct_critical = 0
    violations = []

    for ref_tok, hyp_tok in zip(reference_tokens, hypothesis_tokens):
        is_crit, ttype = pipeline.identify_critical_token(ref_tok)
        if is_crit:
            total_critical += 1
            if ref_tok == hyp_tok:
                correct_critical += 1
            else:
                violations.append({
                    "ref": ref_tok,
                    "hyp": hyp_tok,
                    "token_type": ttype
                })

    acc = (correct_critical / total_critical) if total_critical > 0 else 1.0
    return {
        "total_critical_tokens": total_critical,
        "correct_critical_tokens": correct_critical,
        "critical_token_accuracy": round(acc, 4),
        "violations": violations
    }
