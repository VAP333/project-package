"""
AksharSetu — Critical Token Protection & Correction Pipeline (§5.4 & Principle 4)

Pipeline Order:
raw OCR -> normalization -> dictionary -> subject glossary ->
Devanagari rules -> character similarity -> edit distance ->
MahaBERT context -> verified candidate

ARCHITECTURAL LAW (Principle 4):
Critical tokens are non-overridable by language plausibility.
Numbers, units, dates, formulas, percentages, scientific notation,
chemical expressions, names, chapter/question numbers MUST pass an
independent verification path.
A language model 'correcting' '50 kg' to '500 kg' because it's more fluent
is a critical failure.
"""

import re
import sys
import unicodedata

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field

# Devanagari to ASCII numeral mapping
DEVA_TO_ASCII_DIGITS = {
    '०': '0', '१': '1', '२': '2', '३': '3', '४': '4',
    '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'
}
ASCII_TO_DEVA_DIGITS = {v: k for k, v in DEVA_TO_ASCII_DIGITS.items()}

# Common Marathi educational units and critical patterns
KNOWN_UNITS = {
    "kg", "g", "mg", "km", "m", "cm", "mm", "s", "sec", "hr", "min", "l", "ml", "n", "j", "w", "v",
    "किग्रॅ", "किलो", "ग्रॅम", "मिली", "किमी", "मीटर", "सेमी", "मिमी", "सेकंद", "तास", "मिनिट", "लीटर",
    "न्यूटन", "ज्यूल", "वॉट", "व्होल्ट", "अंश", "टक्के", "%"
}

@dataclass
class TokenVerificationResult:
    original_raw: str
    verified_text: str
    is_critical_token: bool
    token_type: str # "number", "unit", "quantity", "formula", "date", "chapter_marker", "general_text"
    confidence: float
    overridden_by_fluency: bool = False
    flagged_for_review: bool = False
    notes: str = ""

class CriticalTokenPipeline:
    def __init__(self, subject_glossary: Optional[Dict[str, str]] = None):
        self.glossary = subject_glossary or {}
        # Precompile patterns for critical token detection
        # 1. Quantities with units: e.g. 50 kg, ५० किग्रॅ, 25%, १०० मीटर
        self.re_quantity = re.compile(
            r'^([0-9०-९]+(?:\.[0-9०-९]+)?)\s*([a-zA-Z%°℃]+|किग्रॅ|किलो|ग्रॅम|किमी|मीटर|सेमी|मिमी|सेकंद|तास|मिनिट|लीटर|टक्के)?$'
        )
        # 2. Pure numbers (Devanagari or ASCII)
        self.re_number = re.compile(r'^[0-9०-९]+(?:\.[0-9०-९]+)?$')
        # 3. Chapter / Question markers
        self.re_marker = re.compile(r'^(पाठ|धडा|प्रश्न|स्वाध्याय|प्रकरण|भाग)\s*([0-9०-९]+|[IVXLCDM]+)', re.IGNORECASE)
        # 4. Chemical / math expressions (e.g. H2O, CO2, NaCl, x^2 + y^2 = r^2)
        self.re_formula = re.compile(r'^[A-Z][a-z]?[0-9]*[A-Z][a-z]?[0-9]*|[a-zA-Z0-9\+\-\*\/\=\^\(\)]{3,}$')

    def normalize_devanagari(self, text: str) -> str:
        """Unicode NFC normalization and standard whitespace cleanup."""
        return unicodedata.normalize('NFC', text).strip()

    def identify_critical_token(self, token: str) -> Tuple[bool, str]:
        """Identifies if a token belongs to a protected class that can never be overridden by fluency."""
        token_norm = self.normalize_devanagari(token)
        if self.re_quantity.match(token_norm):
            return True, "quantity"
        if self.re_number.match(token_norm):
            return True, "number"
        if self.re_marker.match(token_norm):
            return True, "chapter_marker"
        if self.re_formula.match(token_norm) and any(c.isupper() for c in token_norm):
            return True, "formula"
        if token_norm in KNOWN_UNITS:
            return True, "unit"
        return False, "general_text"

    def verify_token(self, source_raw: str, candidate_proposal: str, source_evidence_confidence: float = 0.95) -> TokenVerificationResult:
        """
        Executes critical verification.
        GUARANTEE: If source_raw is a critical token (e.g. '50 kg'), candidate_proposal (e.g. '500 kg')
        is STRICTLY REJECTED if it alters numerals or critical values, regardless of candidate confidence.
        """
        raw_norm = self.normalize_devanagari(source_raw)
        cand_norm = self.normalize_devanagari(candidate_proposal)
        is_crit, token_type = self.identify_critical_token(raw_norm)

        if not is_crit:
            # General text: allow glossary lookup, dictionary corrections, or candidate
            if raw_norm in self.glossary:
                return TokenVerificationResult(
                    original_raw=source_raw,
                    verified_text=self.glossary[raw_norm],
                    is_critical_token=False,
                    token_type="glossary_term",
                    confidence=1.0,
                    notes="Matched verified subject glossary"
                )
            return TokenVerificationResult(
                original_raw=source_raw,
                verified_text=cand_norm if cand_norm else raw_norm,
                is_critical_token=False,
                token_type=token_type,
                confidence=source_evidence_confidence
            )

        # CRITICAL TOKEN PATH: Enforce source fidelity
        # Extract numerical digits from both raw and candidate
        raw_digits = "".join([DEVA_TO_ASCII_DIGITS.get(c, c) for c in raw_norm if c in DEVA_TO_ASCII_DIGITS or c.isdigit()])
        cand_digits = "".join([DEVA_TO_ASCII_DIGITS.get(c, c) for c in cand_norm if c in DEVA_TO_ASCII_DIGITS or c.isdigit()])

        if raw_digits and cand_digits and raw_digits != cand_digits:
            # FLUENCY OVERRIDE DETECTED AND BLOCKED!
            # Principle 4: A model altering 50 to 500 must be rejected with an audit flag.
            return TokenVerificationResult(
                original_raw=source_raw,
                verified_text=raw_norm, # Source evidence preserved
                is_critical_token=True,
                token_type=token_type,
                confidence=1.0,
                overridden_by_fluency=False,
                flagged_for_review=True,
                notes=f"CRITICAL GUARD ACTIVATED: Blocked fluency modification of digits from '{raw_digits}' to '{cand_digits}'."
            )

        # If digits match or unit normalization is minor, keep verified source
        return TokenVerificationResult(
            original_raw=source_raw,
            verified_text=raw_norm,
            is_critical_token=True,
            token_type=token_type,
            confidence=source_evidence_confidence,
            notes="Critical token verified against source evidence."
        )

    def process_sentence(self, tokens: List[str], candidates: Optional[List[str]] = None) -> List[TokenVerificationResult]:
        candidates = candidates or tokens
        results = []
        for raw, cand in zip(tokens, candidates):
            results.append(self.verify_token(raw, cand))
        return results

def run_regression_tests():
    """Validates Principle 4 non-overridability invariants."""
    pipeline = CriticalTokenPipeline()
    
    # Test 1: The canonical 50 kg -> 500 kg failure mode
    res1 = pipeline.verify_token("50 kg", "500 kg")
    assert res1.verified_text == "50 kg", f"Failed: Expected '50 kg', got '{res1.verified_text}'"
    assert "CRITICAL GUARD ACTIVATED" in res1.notes
    print("[PASS] Test 1: '50 kg' -> '500 kg' hallucination blocked.")

    # Test 2: Devanagari numeral protection: ५० किग्रॅ -> ५०० किग्रॅ
    res2 = pipeline.verify_token("५० किग्रॅ", "५०० किग्रॅ")
    assert res2.verified_text == "५० किग्रॅ", f"Failed: Expected '५० किग्रॅ', got '{res2.verified_text}'"
    assert "CRITICAL GUARD ACTIVATED" in res2.notes
    print("[PASS] Test 2: '५० किग्रॅ' -> '५०० किग्रॅ' blocked.")

    # Test 3: Chemical formula preservation
    res3 = pipeline.verify_token("H2O", "H2SO4")
    assert res3.verified_text == "H2O"
    print("[PASS] Test 3: Chemical formula 'H2O' protected.")

    # Test 4: Chapter marker protection
    res4 = pipeline.verify_token("पाठ ५", "पाठ ६")
    assert res4.verified_text == "पाठ ५"
    print("[PASS] Test 4: Chapter marker 'पाठ ५' protected.")
    print("All Critical Token Pipeline regression tests passed successfully!")

if __name__ == "__main__":
    run_regression_tests()
