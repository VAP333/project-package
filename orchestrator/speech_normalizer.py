"""
AksharSetu — TTS Speech Normalizer & Punctuation Sanitizer (§1, §2, §3)

CRITICAL INVARIANT:
Punctuation marks in canonical textbook text are CONTROL SIGNALS for prosody/pauses.
They are NEVER spoken words.
The TTS system must NEVER explicitly pronounce punctuation as:
"comma", "full stop", "question mark", "exclamation mark", "vertical bar", "pipe",
"colon", "bracket", "स्वल्पविराम", "पूर्णविराम", "प्रश्नचिन्ह", "उद्गारवाचक चिन्ह", "कंस", "उभी रेघ", etc.

Pipeline:
Canonical Text
    ↓
Punctuation / Prosody Analysis (extracts pause cues, question intonation, emphasis)
    ↓
TTS-Safe Speech Normalization (sanitizes text, transforms punctuation to acoustic pauses)
    ↓
Speech Output for TTS
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

# Literal punctuation word tokens that must NEVER appear in speech text sent to TTS
FORBIDDEN_PUNCTUATION_WORDS = [
    # English names
    r'\bcomma\b', r'\bfull\s*stop\b', r'\bperiod\b', r'\bquestion\s*mark\b',
    r'\bexclamation\s*mark\b', r'\bvertical\s*bar\b', r'\bpipe\b', r'\bcolon\b',
    r'\bsemicolon\b', r'\bbracket\b', r'\bparenthesis\b', r'\bhyphen\b', r'\bdash\b',
    r'\bslash\b', r'\bbackslash\b', r'\bquote\b', r'\bquotes\b',
    # Marathi names
    r'\bस्वल्पविराम\b', r'\bपूर्णविराम\b', r'\bप्रश्नचिन्ह\b', r'\bउद्गारवाचक\s*चिन्ह\b',
    r'\bउभी\s*रेघ\b', r'\bकंस\b', r'\bविरामचिन्ह\b', r'\bअल्पविराम\b', r'\bअवतरणचिन्ह\b'
]

@dataclass
class PunctuationProsodyAnalysis:
    is_question: bool = False
    is_exclamation: bool = False
    has_dialogue_colon: bool = False
    has_list_separators: bool = False
    pause_points: List[Dict[str, Any]] = field(default_factory=list)
    suggested_sentence_pause_ms: int = 250
    suggested_clause_pause_ms: int = 150

class SpeechNormalizer:
    """
    Sanitizes textbook text into a safe, natural speech representation
    where punctuation acts exclusively as prosodic/acoustic control cues,
    never as spoken lexical tokens.
    """

    def analyze_punctuation_prosody(self, text: str) -> PunctuationProsodyAnalysis:
        analysis = PunctuationProsodyAnalysis()
        clean = text.strip()

        # 1. Question Detection
        if clean.endswith("?") or "?" in clean or re.search(r'\b(का|कसे|कोणते|केव्हा|कुठे|सांगा)\s*\?', clean):
            analysis.is_question = True

        # 2. Exclamation / Expressive Emphasis
        if "!" in clean:
            analysis.is_exclamation = True

        # 3. Speaker Dialogue Colon (e.g. "शिक्षिका : ")
        if re.search(r'(शिक्षिका|शिक्षक|राहुल|साक्षी|नीता|विद्यार्थी)\s*[:\t]', clean):
            analysis.has_dialogue_colon = True

        # 4. List / Pipe / Tabular Separators
        if "|" in clean or "•" in clean:
            analysis.has_list_separators = True

        return analysis

    def normalize_for_tts(self, text: str) -> str:
        """
        Transforms canonical text into safe speech text:
        - Replaces tabular '|' with natural list pause commas (never verbalized as 'pipe').
        - Replaces dialogue colons with acoustic breath pauses.
        - Removes brackets and quotes without saying 'bracket' or 'quote'.
        - Preserves native Devanagari rhythm markers (। , ?) for neural TTS pitch/pause modulation.
        - Strips any accidental literal punctuation names.
        """
        t = text.strip()
        if not t:
            return ""

        # 1. First, strip any stray forbidden literal punctuation words if they were accidentally injected
        for pattern in FORBIDDEN_PUNCTUATION_WORDS:
            t = re.sub(pattern, '', t, flags=re.IGNORECASE)

        # 2. Handle Table & List Separator: Vertical Bar '|'
        # e.g. "| भूषणा | जलाशय | वनस्पती |" -> "भूषणा, जलाशय, वनस्पती"
        # Never vocalized as "vertical bar" or "pipe"
        t = re.sub(r'^\s*\|\s*', '', t) # leading pipe
        t = re.sub(r'\s*\|\s*$', '', t) # trailing pipe
        t = re.sub(r'\s*\|\s*', ', ', t) # internal pipes become natural list pauses

        # 3. Handle Bullets and Symbols (•, *, -, —, –)
        t = re.sub(r'^\s*[•\*\-–—]\s*', '', t) # leading bullets
        t = re.sub(r'\s*[•\*]\s*', ', ', t) # inline bullets become commas
        t = re.sub(r'\s*[-–—]{2,}\s*', ' ... ', t) # em-dash becomes thoughtful pause
        t = re.sub(r'\s+[-–—]\s+', ', ', t) # single hyphen between words becomes short pause

        # 4. Handle Parentheses and Brackets:
        # e.g. "(Field Visit)" or "[१]" -> soften to subtle pauses, never say "bracket" or "कंस"
        t = re.sub(r'[\(\[\{]\s*', ', ', t)
        t = re.sub(r'\s*[\)\]\}]', ', ', t)

        # 5. Handle Quotation Marks:
        # e.g. 'चर्चा करा' or "दिवस पहिला" -> remove quotes, do not speak "कोट" or "quote"
        t = re.sub(r'["\'«»“”‘’]', '', t)

        # 6. Clean Dialogue Speaker Attribution Colon:
        # e.g. "शिक्षिका : " -> "शिक्षिका, ... " (breath pause for neural TTS)
        t = re.sub(r'(^|\s)(शिक्षिका|राहुल|साक्षी|नीता|शिक्षक|कवी|विद्यार्थी)\s*[:\t]\s*', r'\1\2, ... ', t)

        # 7. Clean Other Colons (explanatory transition)
        # e.g. "वेळ सकाळी ६:००" -> "वेळ सकाळी ६:००" (time colon preserved), but "टीप :" -> "टीप, "
        t = re.sub(r'(?<!\d)\s*:\s*(?!\d)', ', ... ', t)

        # 8. Semicolons (;) -> medium pause comma
        t = re.sub(r'\s*;\s*', ', ', t)

        # 9. Clean multiple consecutive commas or spaces
        t = re.sub(r',\s*,+', ', ', t)
        t = re.sub(r'\s*,\s*', ', ', t)
        t = re.sub(r'\s{2,}', ' ', t)

        # 10. Normalize numbers, years, dates, and times into fluent Marathi words
        # Prevents raw digits from being read as isolated individual numbers (e.g. १९६० as "एक नऊ सहा शून्य")
        from orchestrator.marathi_number_normalizer import marathi_number_normalizer
        t = marathi_number_normalizer.normalize_text_numbers(t)

        # 11. Clean beginning of sentence punctuation
        t = re.sub(r'^[,\s.]+', '', t)

        # 12. Final sentence closure
        # Ensure clean prosodic finish with Devanagari Danda if question or exclamation mark not present
        if not re.search(r'[।.!?…]$', t):
            t = t.rstrip(', ') + '।'

        return t.strip()

speech_normalizer = SpeechNormalizer()
