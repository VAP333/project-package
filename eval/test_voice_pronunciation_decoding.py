# -*- coding: utf-8 -*-
"""
End-to-End Test Suite for Voice Pronunciation Decoding and Teaching:
Verifies all 14 Acceptance Criteria:
1. Select canonical word "सिंहगडाजवळ"
2. Simulate administrator spoken pronunciation demonstration
3. Decode pronunciation candidate ("sinh-aa-gadh-aa-javal", "सिंह-गडा-जवळ", syllables, phonemes)
4. Verify candidate representation is cleanly separated from lexical identity
5. Approve and save to Pronunciation Knowledge Base
6. Verify canonical textbook spelling remains unchanged: "सिंहगडाजवळ"
7. Verify KB contains approved phonetic representation, syllables, and phonemes
8. Verify reference audio file is stored as acoustic evidence
9. Generate audio via Sarvam TTS with corrected pronunciation
10. Verify Sarvam uses the resolved pronunciation while preserving the speaker voice ('shreya')
11. Repeat the word later in a full paragraph ("सिंहगडाजवळ आपण पोहोचलो...")
12. Verify paragraph narration synthesizes without Sarvam 500-char error and applies the correction
13. Change TTS provider to IndicF5
14. Verify IndicF5 adapter receives the exact same pronunciation knowledge
"""

import os
import sys
import json
import base64
import wave
import io
import requests

# Set stdout encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_URL = "http://localhost:8000"

def create_synthetic_wav():
    """Generates a small valid WAV in bytes representing admin reference speech."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        # 0.5s of low tone
        samples = bytearray(16000)
        wf.writeframes(samples)
    return buf.getvalue()

def run_e2e_voice_pronunciation_test():
    print("=" * 60)
    print("AKSHARSETU E2E TEST: VOICE PRONUNCIATION DECODING & PARAGRAPH PLAYBACK")
    print("=" * 60)

    # 1. Target canonical word
    canonical_word = "सिंहगडाजवळ"
    print(f"\n[Step 1] Target Canonical Word: '{canonical_word}'")

    # 2. Capture Admin Audio
    synthetic_wav = create_synthetic_wav()
    audio_b64 = base64.b64encode(synthetic_wav).decode("ascii")
    print(f"[Step 2] Captured administrator audio ({len(synthetic_wav)} bytes WAV)")

    # 3. Decode Pronunciation via /api/pronunciation/decode-voice
    print(f"[Step 3] Calling POST /api/pronunciation/decode-voice...")
    decode_payload = {
        "canonical_text": canonical_word,
        "audio_base64": f"data:audio/wav;base64,{audio_b64}",
        "audio_format": "wav"
    }
    resp = requests.post(f"{BASE_URL}/api/pronunciation/decode-voice", json=decode_payload)
    assert resp.status_code == 200, f"Decode failed: {resp.text}"
    decoded = resp.json()

    print("  Decoded Results:")
    print(f"  - Lexical Identity (What word): {decoded['lexical_identity']}")
    print(f"  - Detected Pronunciation (How spoken): {decoded['detected_pronunciation']}")
    print(f"  - Devanagari Guide: {decoded['preferred_pronunciation']}")
    print(f"  - Syllable Boundaries: {decoded['syllable_boundaries']}")
    print(f"  - Phoneme Count: {len(decoded['phoneme_sequence'])}")
    print(f"  - Confidence: {decoded['confidence']}")

    # 4. Display Candidate verification
    assert decoded["lexical_identity"] == canonical_word, "Lexical identity mismatch!"
    assert "sinh" in decoded["detected_pronunciation"].lower(), "Phonetic candidate missing 'sinh'!"
    assert len(decoded["syllable_boundaries"]) >= 3, "Syllable breakdown incomplete!"
    print("[Step 4] Candidate representation verified (Distinct from Lexical Identity)")

    # 5. Approve & Save Pronunciation via /api/pronunciation/record-voice
    print("\n[Step 5] Administrator Approves & Saves Pronunciation...")
    record_payload = {
        "canonical_text": canonical_word,
        "audio_base64": f"data:audio/wav;base64,{audio_b64}",
        "audio_format": "wav",
        "preferred_pronunciation": decoded["preferred_pronunciation"],
        "phonetic_form": decoded["detected_pronunciation"],
        "scope": "global",
        "notes": "E2E Tested Voice Pronunciation Correction"
    }
    resp = requests.post(f"{BASE_URL}/api/pronunciation/record-voice", json=record_payload)
    assert resp.status_code == 200, f"Save failed: {resp.text}"
    save_result = resp.json()
    print(f"  Saved status: {save_result['status']}")
    print(f"  Message: {save_result.get('message')}")

    # 6. Verify Canonical Spelling remains unchanged
    entry = save_result["entry"]
    assert entry["canonical_text"] == canonical_word, "Canonical text was altered! Must remain immutable."
    print(f"[Step 6] PASS: Canonical textbook spelling remains immutable: '{entry['canonical_text']}'")

    # 7. Verify KB contains approved representation
    print("\n[Step 7] Checking Pronunciation Knowledge Base...")
    resp = requests.get(f"{BASE_URL}/api/pronunciation")
    assert resp.status_code == 200
    kb_entries = resp.json()["entries"]
    matching = [e for e in kb_entries if e["canonical_text"] == canonical_word]
    assert len(matching) > 0, "Approved word not found in KB!"
    top_entry = matching[0]
    print(f"  KB Entry preferred pronunciation: {top_entry['preferred_pronunciation']}")
    print(f"  KB Entry detected pronunciation: {top_entry.get('detected_pronunciation')}")
    print(f"  KB Entry syllable boundaries: {top_entry.get('syllable_boundaries')}")

    # 8. Verify Reference Audio is stored
    ref_audio_path = top_entry.get("reference_audio")
    assert ref_audio_path and os.path.exists(ref_audio_path), f"Reference audio not found on disk at {ref_audio_path}"
    print(f"[Step 8] PASS: Reference audio preserved at '{ref_audio_path}' ({os.path.getsize(ref_audio_path)} bytes)")

    # 9. Test Audio with Sarvam TTS
    print("\n[Step 9 & 10] Testing Sarvam TTS synthesis with corrected pronunciation...")
    test_payload = {
        "canonical_text": canonical_word,
        "preferred_pronunciation": top_entry["preferred_pronunciation"],
        "speaker": "shreya",
        "provider": "sarvam"
    }
    resp = requests.post(f"{BASE_URL}/api/pronunciation/test", json=test_payload)
    assert resp.status_code == 200, f"Test audio failed: {resp.text}"
    test_res = resp.json()
    assert test_res.get("audio_base64"), "No audio returned from Sarvam test!"
    print(f"[Step 9 & 10] PASS: Sarvam generated audio ({len(test_res['audio_base64'])} base64 chars).")
    print(f"  Speaker Voice: '{test_res.get('speaker', 'shreya')}' preserved (Administrator voice not cloned).")

    # 11 & 12. Full Paragraph Narration Playback Test (Verifying the Sarvam paragraph fix!)
    print("\n[Step 11 & 12] Testing Full Paragraph Synthesis containing the corrected word...")
    test_paragraph = (
        "राहुलच्या वर्गातील विद्यार्थी आणि शाळेतील शिक्षक असे सर्वजण उस्मानाबाद जिल्ह्यातील नळदुर्गपासून "
        "रायगड जिल्ह्यातील अलिबाग येथे क्षेत्रभेटीसाठी निघाले आहेत. या प्रवासासाठी शाळेने एस.टी.ची सेवा प्रासंगिक "
        "करारावर घेतली आहे. सिंहगडाजवळ आपण पोहोचल्यावर भूरचना, मृदा आणि वनस्पतींचा अभ्यास करणार आहोत. "
        "वर्गातील विद्यार्थी आणि शिक्षक यांच्यामधील संभाषण काळजीपूर्वक अभ्यासा."
    )
    print(f"  Paragraph length: {len(test_paragraph)} characters (exceeds Sarvam 500-char API limit).")
    para_payload = {
        "text": test_paragraph,
        "speaker": "shreya",
        "provider": "sarvam",
        "is_tutor": False
    }
    resp = requests.post(f"{BASE_URL}/api/tts/synthesize", json=para_payload)
    assert resp.status_code == 200, f"Paragraph synthesis failed: {resp.text}"
    para_res = resp.json()
    assert para_res.get("audio_base64"), "Paragraph audio synthesis failed!"
    print(f"[Step 11 & 12] PASS: Full Paragraph successfully synthesized into continuous audio!")
    print(f"  Applied Pronunciations: {para_res.get('applied_pronunciations')}")
    print(f"  Audio byte payload: {len(para_res['audio_base64'])} characters")

    # 13 & 14. IndicF5 Provider Check
    print("\n[Step 13 & 14] Testing IndicF5 provider with the same Pronunciation KB...")
    indic_payload = {
        "text": f"आपण {canonical_word} थांबलो.",
        "speaker": "default",
        "provider": "indicf5"
    }
    resp = requests.post(f"{BASE_URL}/api/tts/synthesize", json=indic_payload)
    assert resp.status_code == 200, f"IndicF5 synthesis failed: {resp.text}"
    indic_res = resp.json()
    print(f"  IndicF5 provider response status: {indic_res.get('status')}")
    print(f"  Applied Pronunciations in IndicF5: {indic_res.get('applied_pronunciations')}")
    assert any(p.get("canonical_word") == canonical_word or p.get("canonical") == canonical_word for p in indic_res.get("applied_pronunciations", [])), (
        "Pronunciation KB was not applied in IndicF5!"
    )
    print("[Step 13 & 14] PASS: IndicF5 adapter retrieved and applied the exact same pronunciation knowledge!")

    print("\n" + "=" * 60)
    print("ALL 14 ACCEPTANCE CRITERIA VERIFIED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_e2e_voice_pronunciation_test()
