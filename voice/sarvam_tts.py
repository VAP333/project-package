"""
AksharSetu — Sarvam AI Marathi TTS Integration
Model: bulbul:v3
Default speaker: shreya (friendly, natural Marathi narration)
Optimal default speed: 0.75x

HARDENING & PARAGRAPH CHUNKING (§1, §13):
1. Sarvam bulbul:v3 enforces a strict 500-char limit per input string.
2. Long paragraphs are automatically chunked into 2-3 sentence segments (<= 380 chars)
   at natural discourse boundaries ([।.?!]).
3. Synthesized WAV segments are seamlessly concatenated into a single unified continuous audio stream.
"""

import os
import re
import io
import wave
import json
import base64
import hashlib
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from orchestrator.speech_normalizer import speech_normalizer

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")  # Set via .env file — never hardcode
SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

# In-memory audio cache: hash(text, speed, speaker, temperature) -> base64 audio
_AUDIO_CACHE: Dict[str, str] = {}

def structure_marathi_prosody(text: str, is_tutor: bool = False) -> str:
    """
    Enriches Marathi text with natural prosody markers, breath pauses,
    and cadence cues for Sarvam bulbul:v3.
    Guarantees punctuation is treated as acoustic control, never spoken literally.
    """
    # 0. Normalize for speech first (pipes to commas, remove brackets/quotes, remove literal punctuation words)
    t = speech_normalizer.normalize_for_tts(text)
    if not t:
        return ""

    # 1. Natural speaker dialogue attribution pauses (e.g. "शिक्षिका : " -> "शिक्षिका, ... ")
    # The comma and ellipsis trigger neural TTS breath pause and natural pitch inflection
    t = re.sub(r'(^|\s)(शिक्षिका|राहुल|साक्षी|नीता|शिक्षक|कवी|विद्यार्थी)\s*[:\t]\s*', r'\1\2, ... ', t)

    # 2. Section and timeline markers (e.g. "दिवस पहिला : वेळ सकाळी ६:००" -> "दिवस पहिला, वेळ सकाळी ६:०० ... ")
    t = re.sub(r'(दिवस पहिला|दिवस दुसरा|दिवस तिसरा)\s*[:\t]\s*', r'\1, ... ', t)

    # 3. Chapter title pauses (e.g. "१. क्षेत्रभेट :" -> "१. क्षेत्रभेट ... ")
    t = re.sub(r'^([०१२३४५६७८९\d]+\.\s*[^:.]+)\s*:\s*', r'\1 ... ', t)

    # 4. Caption labels (e.g. "आकृती १.१ : क्षेत्रभेटीचा मार्ग" -> "आकृती १.१ ... क्षेत्रभेटीचा मार्ग")
    t = re.sub(r'(आकृती|छायाचित्र|नकाशा|तक्ता|सारणी)\s*([०१२३४५६७८९\d.]+)\s*[:\t\-–—]?\s*', r'\1 \2 ... ', t)

    # 5. Science Boxed Elements & Activity Headers (e.g. "करून पहा :", "थोडे आठवा :", "जरा डोके चालवा :")
    t = re.sub(
        r'(थोडे आठवा|सांगा पाहू|करून पहा|जरा डोके चालवा|माहीत आहे का तुम्हांला|हे नेहमी लक्षात ठेवा|'
        r'सोडवलेली उदाहरणे|सोडविलेली उदाहरणे|परिचय शास्त्रज्ञांचा|असे होऊन गेले|मागे वळून पाहताना|'
        r'इतिहासात डोकावताना|चर्चा करा|विचार करा|शोधा पाहू|स्वाध्याय)\s*[:\t.\-–—]?\s*',
        r'\1 ... ',
        t
    )

    # 6. Title speech introduction breath pause ("आज आपण शिकणार आहोत, [Title]" / "आज आपण बघणार आहोत, [Title]")
    t = re.sub(r'(आज आपण शिकणार आहोत|आज आपण बघणार आहोत|आता आपण बघूयात|चला, आता बघूयात|आता पुढील भाग पाहूयात|चला, आता समजून घेऊया|आता आपण पाहूया),\s*', r'\1, ... ', t)

    # 7. Clause cadence: add gentle breathing commas before heavy conjunctions if not already punctuated
    t = re.sub(r'(?<![।,?!.–—…])\s+(आणि|परंतु|तसेच|म्हणून|कारण)\s+', r', \1 ', t)

    # 8. Ensure clean sentence cadence closure
    if not re.search(r'[।.!?…]$', t):
        t += '।'

    return t

def chunk_text_for_sarvam(text: str, max_chars: int = 350) -> List[str]:
    """
    Chunks text into natural segments strictly <= max_chars (default 350, well under Sarvam's 500-char limit).
    Respects Marathi sentence boundaries ([।.?!]), clause boundaries (, ; : – —), and word boundaries.
    Guarantees no chunk EVER exceeds max_chars.
    """
    if not text or not text.strip():
        return []

    # 1. First split by sentence boundaries
    raw_sentences = re.split(r'([।.?!]\s*)', text)
    sentences = []
    i = 0
    while i < len(raw_sentences):
        sent = raw_sentences[i]
        sep = raw_sentences[i+1] if i+1 < len(raw_sentences) else ''
        full_s = (sent + sep).strip()
        if full_s:
            sentences.append(full_s)
        i += 2

    # 2. If any individual sentence is > max_chars, split by clauses/commas/words
    sub_units = []
    for s in sentences:
        if len(s) <= max_chars:
            sub_units.append(s)
        else:
            clauses = re.split(r'([,;:–—\t]\s*)', s)
            curr_clause = ''
            ci = 0
            while ci < len(clauses):
                c_part = clauses[ci]
                c_sep = clauses[ci+1] if ci+1 < len(clauses) else ''
                combined = c_part + c_sep
                if len(curr_clause) + len(combined) <= max_chars:
                    curr_clause += combined
                else:
                    if curr_clause.strip():
                        sub_units.append(curr_clause.strip())
                    if len(combined) > max_chars:
                        words = combined.split()
                        w_curr = ''
                        for w in words:
                            if len(w_curr) + len(w) + 1 <= max_chars:
                                w_curr += (' ' if w_curr else '') + w
                            else:
                                if w_curr.strip():
                                    sub_units.append(w_curr.strip())
                                w_curr = w
                        curr_clause = w_curr
                    else:
                        curr_clause = combined
                ci += 2
            if curr_clause.strip():
                sub_units.append(curr_clause.strip())

    # 3. Pack sub-units into chunks up to max_chars
    chunks = []
    curr = ''
    for unit in sub_units:
        if not unit:
            continue
        if len(curr) + len(unit) + 1 <= max_chars:
            curr += (' ' if curr else '') + unit
        else:
            if curr.strip():
                chunks.append(curr.strip())
            curr = unit
    if curr.strip():
        chunks.append(curr.strip())

    return chunks

def concatenate_wav_base64(b64_list: List[str]) -> str:
    """Concatenates multiple base64 WAV chunks into a single unified continuous WAV file."""
    if not b64_list:
        return ""
    if len(b64_list) == 1:
        return b64_list[0]

    output_io = io.BytesIO()
    first = True
    output_wave = None
    for b64 in b64_list:
        try:
            wav_bytes = base64.b64decode(b64)
            with wave.open(io.BytesIO(wav_bytes), 'rb') as infile:
                if first:
                    output_wave = wave.open(output_io, 'wb')
                    output_wave.setparams(infile.getparams())
                    first = False
                output_wave.writeframes(infile.readframes(infile.getnframes()))
        except Exception as e:
            print(f"[WAV Concat] Chunk error: {e}")
    if output_wave:
        output_wave.close()

    return base64.b64encode(output_io.getvalue()).decode('utf-8')


class SarvamTTSService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SARVAM_API_KEY", SARVAM_API_KEY)

    def _call_sarvam_api(
        self,
        chunk_text: str,
        pace: float = 1.0,
        speaker: str = "shreya",
        temperature: float = 0.68
    ) -> str:
        """Low-level single-request call to Sarvam AI."""
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }

        # Strict defensive guard under Sarvam 500-char limit
        safe_chunk = chunk_text.strip()
        if len(safe_chunk) > 420:
            safe_chunk = safe_chunk[:420]

        payload = {
            "inputs": [safe_chunk],
            "target_language_code": "mr-IN",
            "speaker": speaker,
            "pace": pace,
            "temperature": temperature,
            "model": "bulbul:v3"
        }

        req = urllib.request.Request(
            SARVAM_TTS_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        last_err = None
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if "audios" in data and len(data["audios"]) > 0:
                        return data["audios"][0]
                    raise ValueError("No audio returned from Sarvam API")
            except Exception as e:
                last_err = e
                print(f"[Sarvam API] Attempt {attempt + 1} error: {e}. Retrying if possible...")
                import time
                time.sleep(1.0)
        raise last_err

    def synthesize(
        self,
        text: str,
        pace: float = 1.0,
        speaker: str = "shreya",
        is_tutor: bool = False,
        temperature: float = 0.68
    ) -> Dict[str, Any]:
        """
        Synthesizes natural, modulated Marathi speech using Sarvam bulbul:v3.
        Supports full textbook paragraphs of arbitrary length via natural chunking
        and seamless WAV concatenation.
        """
        clean_text = structure_marathi_prosody(text.strip(), is_tutor)
        if not clean_text:
            return {"status": "error", "message": "Text is empty", "audio_base64": ""}

        cache_key = hashlib.md5(f"{clean_text}_{pace}_{speaker}_{temperature}".encode("utf-8")).hexdigest()
        if cache_key in _AUDIO_CACHE:
            return {
                "status": "success",
                "audio_base64": _AUDIO_CACHE[cache_key],
                "cached": True,
                "speaker": speaker,
                "pace": pace,
                "temperature": temperature
            }

        try:
            # Check length: if under 380 chars, synthesize in one request
            if len(clean_text) <= 380:
                audio_b64 = self._call_sarvam_api(clean_text, pace, speaker, temperature)
            else:
                # Paragraph-first chunking: split into natural sentence chunks <= 380 chars
                chunks = chunk_text_for_sarvam(clean_text, max_chars=380)
                from concurrent.futures import ThreadPoolExecutor

                # Identify which chunks need API fetch vs already cached
                chunk_audios = [None] * len(chunks)
                to_fetch_indices = []
                for idx, c in enumerate(chunks):
                    c_key = hashlib.md5(f"{c}_{pace}_{speaker}_{temperature}".encode("utf-8")).hexdigest()
                    if c_key in _AUDIO_CACHE:
                        chunk_audios[idx] = _AUDIO_CACHE[c_key]
                    else:
                        to_fetch_indices.append((idx, c, c_key))

                if to_fetch_indices:
                    def _fetch(item):
                        i, c_text, k = item
                        audio = self._call_sarvam_api(c_text, pace, speaker, temperature)
                        return i, k, audio

                    with ThreadPoolExecutor(max_workers=min(4, len(to_fetch_indices))) as executor:
                        results = executor.map(_fetch, to_fetch_indices)
                        for i, k, audio in results:
                            _AUDIO_CACHE[k] = audio
                            chunk_audios[i] = audio

                # Concatenate all WAV chunks into one unified seamless audio
                audio_b64 = concatenate_wav_base64([a for a in chunk_audios if a])

            _AUDIO_CACHE[cache_key] = audio_b64
            return {
                "status": "success",
                "audio_base64": audio_b64,
                "cached": False,
                "speaker": speaker,
                "pace": pace,
                "temperature": temperature
            }
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return {"status": "error", "code": e.code, "message": err_body, "audio_base64": ""}
        except Exception as e:
            return {"status": "error", "message": str(e), "audio_base64": ""}

sarvam_tts_service = SarvamTTSService()
