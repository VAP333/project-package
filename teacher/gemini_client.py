"""
AksharSetu — High-Reliability REST Gemini Teacher Pipeline Client (§4 of Implementation Guide)

NON-NEGOTIABLE ARCHITECTURAL RULES:
1. Pinned model name is NEVER hardcoded in code; it is fetched from VersionLedger.
2. Structured JSON output is a HYPOTHESIS, never auto-promoted to Golden Corpus truth.
3. No confidence fusion, ever (Principle 3). Teacher supervises during training, not inference voting.
4. Input and output token usage is recorded for cost tracking (§7).
5. Uses direct HTTPS REST with automatic 429 quota backoff and retry.
"""

import os
import sys
import json
import re
import time
import base64
from typing import Dict, Any, Optional
import requests
from dotenv import load_dotenv

load_dotenv()
from versioning.version_ledger import VersionLedger
from teacher.prompts.annotation_prompt import TEACHER_SYSTEM_INSTRUCTION, build_teacher_user_prompt

class GeminiTeacherClient:
    def __init__(self, api_key: Optional[str] = None, cache_dir: str = "./data/teacher_cache"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required to initialize GeminiTeacherClient.")
        self.model_name = VersionLedger.get_teacher_model()
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, page_id: str) -> str:
        return os.path.join(self.cache_dir, f"{page_id}.json")

    def annotate_page(self, page_image_path: str, page_id: str, native_text_hint: str = "", max_retries: int = 4, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Sends page image + native text evidence to Gemini teacher model over HTTPS REST.
        Returns parsed structured annotation hypothesis. Caches results by page_id.
        """
        cache_path = self._get_cache_path(page_id)
        if not force_refresh and os.path.exists(cache_path):
            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    cached_data["from_cache"] = True
                    return cached_data
            except Exception:
                pass

        user_prompt = build_teacher_user_prompt(page_id, native_text_hint)
        
        # Read and base64-encode page canvas
        with open(page_image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        
        payload = {
            "system_instruction": {
                "parts": [{"text": TEACHER_SYSTEM_INSTRUCTION}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": user_prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": img_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        }

        last_error = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=payload, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise ValueError(f"No candidates returned: {data}")
                    raw_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                    usage_meta = data.get("usageMetadata", {})
                    
                    # Parse JSON hypothesis
                    try:
                        parsed = json.loads(raw_text)
                    except json.JSONDecodeError:
                        match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
                        if match:
                            parsed = json.loads(match.group(1))
                        else:
                            raise ValueError(f"Teacher output could not be parsed as JSON: {raw_text[:200]}...")

                    result_envelope = {
                        "is_hypothesis": True,
                        "verification_tier": "TEACHER_OUTPUT",
                        "page_id": page_id,
                        "teacher_model": self.model_name,
                        "prompt_version": VersionLedger.get_current().prompt_version,
                        "annotations": parsed,
                        "usage": {
                            "prompt_token_count": usage_meta.get("promptTokenCount", 0),
                            "candidates_token_count": usage_meta.get("candidatesTokenCount", 0),
                            "total_token_count": usage_meta.get("totalTokenCount", 0)
                        },
                        "raw_response_text": raw_text
                    }
                    try:
                        with open(cache_path, "w", encoding="utf-8") as f:
                            json.dump(result_envelope, f, indent=2, ensure_ascii=False)
                    except Exception:
                        pass
                    return result_envelope
                elif resp.status_code == 429:
                    # Rate limit / Quota exceeded
                    err_json = resp.json().get("error", {})
                    delay = 15
                    for detail in err_json.get("details", []):
                        if "retryDelay" in detail:
                            delay_str = detail["retryDelay"].replace("s", "")
                            try:
                                delay = int(float(delay_str)) + 2
                            except Exception:
                                pass
                    print(f"[Gemini Teacher] 429 Quota reached. Backing off for {delay}s (attempt {attempt+1}/{max_retries})...", flush=True)
                    time.sleep(delay)
                elif resp.status_code == 503:
                    print(f"[Gemini Teacher] 503 High Demand. Backing off for 15s (attempt {attempt+1}/{max_retries})...", flush=True)
                    time.sleep(15)
                else:
                    raise RuntimeError(f"Gemini API returned error {resp.status_code}: {resp.text}")
            except Exception as e:
                last_error = e
                if "429" in str(e) or "503" in str(e):
                    time.sleep(15)
                else:
                    raise e
        
        raise RuntimeError(f"Gemini Teacher failed after {max_retries} attempts: {last_error}")
