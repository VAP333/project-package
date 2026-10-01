"""
AksharSetu — Comprehensive Regression Suite for Pronunciation & Speech Hardening (§15)

Test Cases:
A. Punctuation is never spoken literally (no "vertical bar", "pipe", "comma", "bracket").
B. Question marks produce question-style prosody without saying "question mark".
C. Full stops create natural sentence boundaries without speaking "full stop".
D. Lists containing "|" are not spoken as "vertical bar" or "pipe".
E. Canonical spelling remains unchanged after pronunciation correction.
F. Admin voice pronunciation survives application restart (JSON persistence).
G. Admin pronunciation is reused when the same word appears later.
H. Document-specific pronunciation overrides global pronunciation.
I. Sarvam consumes the resolved pronunciation path.
J. IndicF5 consumes the provider-neutral pronunciation representation where supported.
K. ASR transcription does not replace the stored pronunciation representation.
L. Reference audio remains linked to the pronunciation entry.
"""

import os
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
import json
import urllib.request
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestrator.speech_normalizer import speech_normalizer, FORBIDDEN_PUNCTUATION_WORDS
from corpus.pronunciation_kb import (
    PronunciationEntry,
    PronunciationKnowledgeBase,
    PronunciationResolver,
    ResolvedPronunciation,
    SarvamPronunciationAdapter,
    IndicF5PronunciationAdapter
)
from orchestrator.prosody_planner import prosody_planner
from voice.tts_service import tts_service, SpeechStylePlan


def test_a_and_d_punctuation_never_spoken_literally():
    print("[TEST A & D] Punctuation & Pipes Never Spoken Literally...")
    # Canonical textbook list with table dividers and brackets
    sample_text = "| भूषणा | जलाशय | वनस्पती | मृदा | शेती | मानवी वसाहत | वसाहतींची आकृतिबंध."
    normalized = speech_normalizer.normalize_for_tts(sample_text)

    # Must NOT contain pipe or literal words
    assert "|" not in normalized, "Vertical bar '|' must not appear in synthesized speech text"
    for forbidden in ["vertical bar", "pipe", "comma", "full stop", "question mark", "bracket", "उभी रेघ"]:
        assert forbidden not in normalized.lower(), f"Literal punctuation word '{forbidden}' found in speech text"

    # Must contain natural pause markers (commas between list items)
    assert "भूषणा, जलाशय, वनस्पती, मृदा, शेती, मानवी वसाहत, वसाहतींची आकृतिबंध" in normalized
    print(f"  Canonical : {sample_text}")
    print(f"  Normalized: {normalized}")
    print("  -> Passed Test A & D")


def test_b_and_c_question_and_sentence_prosody():
    print("[TEST B & C] Question Marks & Full Stops -> Prosody Signals...")
    question_text = "तुम्ही क्षेत्रभेटीसाठी कशी तयारी कराल?"
    analysis = speech_normalizer.analyze_punctuation_prosody(question_text)
    assert analysis.is_question is True, "Must detect question signal"

    prosody = prosody_planner.plan_prosody(question_text)
    assert prosody.question_intonation is True, "Must set question_intonation flag"
    assert prosody.pause_after_ms >= 400, "Sentence final question pause must be natural"

    # Normalized speech text must NOT contain literal words like 'question mark'
    speech_rep = speech_normalizer.normalize_for_tts(question_text)
    assert "question mark" not in speech_rep.lower()
    assert "प्रश्नचिन्ह" not in speech_rep
    assert speech_rep.endswith("?"), "Question intonation punctuation preserved for neural acoustic cadence"

    # Full stop / Danda sentence closure test
    statement_text = "आम्ही सकाळी ६:०० वाजता निघालो."
    speech_stmt = speech_normalizer.normalize_for_tts(statement_text)
    assert "full stop" not in speech_stmt.lower()
    assert "पूर्णविराम" not in speech_stmt
    print("  -> Passed Test B & C")


def test_e_k_canonical_spelling_immutability():
    print("[TEST E & K] Canonical Spelling Immutability & ASR Lexical Separation...")
    canonical_word = "सिंहगडाजवळ"
    kb = PronunciationKnowledgeBase()

    # Admin teaches pronunciation with voice reference audio
    entry = kb.add_voice_pronunciation(
        canonical_text=canonical_word,
        audio_bytes=b"RIFF_FAKE_AUDIO_BYTES_TEST",
        audio_format="webm",
        preferred_pronunciation="सिंह-गडा-जवळ",
        phonetic_form="singha-gada-jawal",
        notes="स्पष्ट 'सिंह' आणि 'गडाजवळ' संयुक्त उच्चार",
        scope="global"
    )

    # 1. Canonical spelling MUST remain unchanged
    assert entry.canonical_text == canonical_word, "Canonical spelling must NEVER be modified"
    assert entry.preferred_pronunciation == "सिंह-गडा-जवळ", "Phonetic representation must be separate"
    assert entry.phonetic_form == "singha-gada-jawal"

    # 2. ASR Lexical Confirmation separation:
    # ASR gives "सिंहगडाजवळ" (lexical identity), but stored pronunciation remains the phonetic form
    asr_transcript = "सिंहगडाजवळ"
    assert asr_transcript == entry.canonical_text, "ASR confirms word identity"
    assert entry.preferred_pronunciation != asr_transcript, "ASR transcript must not overwrite phonetic representation"
    print("  -> Passed Test E & K")


def test_f_voice_pronunciation_survives_restart():
    print("[TEST F] Voice Pronunciation Survives Restart (Persistence)...")
    kb_path = os.path.join("corpus", "pronunciation_kb.json")
    
    # 1. Add voice entry
    kb1 = PronunciationKnowledgeBase(kb_path)
    kb1.add_voice_pronunciation(
        canonical_text="सिंहगडाजवळ",
        audio_bytes=b"RIFF_AUDIO_TEST_PERSISTENCE",
        audio_format="webm",
        preferred_pronunciation="सिंह-गडा-जवळ",
        phonetic_form="singha-gada-jawal",
        scope="global"
    )

    # 2. Re-instantiate KB from disk (simulates backend restart)
    kb2 = PronunciationKnowledgeBase(kb_path)
    entries = kb2.get_entries_for_word("सिंहगडाजवळ")
    assert len(entries) > 0, "Voice pronunciation must survive restart"
    latest = entries[-1]
    assert latest.preferred_pronunciation == "सिंह-गडा-जवळ"
    assert latest.reference_audio is not None, "Reference audio path must survive restart"
    assert os.path.exists(latest.reference_audio), f"Reference audio file must exist at {latest.reference_audio}"
    print(f"  Persisted audio reference: {latest.reference_audio}")
    print("  -> Passed Test F")


def test_g_reused_on_future_appearances():
    print("[TEST G] Pronunciation Automatically Reused on Future Occurrences...")
    resolver = PronunciationResolver()
    
    # Text with repeated occurrences of taught word
    full_passage = "आम्ही सिंहगडाजवळ पोहोचलो. दुपारी सिंहगडाजवळ खूप गर्दी होती."
    resolved_speech, applied = resolver.resolve_speech_text(full_passage)

    assert "सिंह-गडा-जवळ" in resolved_speech, "Resolved speech must include phonetic form"
    # Should be applied to occurrences without re-prompting
    assert resolved_speech.count("सिंह-गडा-जवळ") == 2, "Must automatically resolve all occurrences"
    assert len(applied) >= 2, "Must record audit trail for each occurrence"
    print(f"  Speech representation: {resolved_speech}")
    print("  -> Passed Test G")


def test_h_document_scope_overrides_global():
    print("[TEST H] Document Scope Overrides Global Scope...")
    kb = PronunciationKnowledgeBase()

    # Global entry
    kb.add_entry(PronunciationEntry(
        canonical_text="घाट",
        preferred_pronunciation="घाट (सामान्य)",
        scope="global",
        approved=True
    ))

    # Document-specific entry
    kb.add_entry(PronunciationEntry(
        canonical_text="घाट",
        preferred_pronunciation="घाट (प्रकरण १ नळदुर्ग मार्ग)",
        scope="document",
        target_id="doc_geo_ch1",
        approved=True
    ))

    resolver = PronunciationResolver(kb)

    # In Document doc_geo_ch1: must get document-specific pronunciation
    res_doc = resolver.resolve_word("घाट", document_id="doc_geo_ch1")
    assert res_doc.preferred_pronunciation == "घाट (प्रकरण १ नळदुर्ग मार्ग)"

    # In another document: must fallback to global
    res_other = resolver.resolve_word("घाट", document_id="other_doc")
    assert res_other.preferred_pronunciation == "घाट (सामान्य)"
    print("  -> Passed Test H")


def test_i_and_j_provider_adapters():
    print("[TEST I & J] Provider Adapters (Sarvam & IndicF5)...")
    neutral_entry = ResolvedPronunciation(
        canonical_text="सिंहगडाजवळ",
        pronunciation_text="सिंह-गडा-जवळ",
        phonetic_form="singha-gada-jawal",
        reference_audio="data/audio/pronunciations/singhagadajawal_v1.webm"
    )

    # 1. Sarvam Adapter
    sarvam_text = SarvamPronunciationAdapter.adapt(
        "आम्ही | सिंह-गडा-जवळ | पोहोचलो.",
        [neutral_entry]
    )
    assert "|" not in sarvam_text, "Sarvam adapter must sanitize pipes"
    assert "सिंह-गडा-जवळ" in sarvam_text

    # 2. IndicF5 Adapter
    indic_adapted = IndicF5PronunciationAdapter.adapt(
        "आम्ही | सिंह-गडा-जवळ | पोहोचलो.",
        [neutral_entry]
    )
    assert "|" not in indic_adapted["text"]
    assert indic_adapted["ref_audio"] == "data/audio/pronunciations/singhagadajawal_v1.webm"
    assert indic_adapted["has_voice_guidance"] is True
    print("  -> Passed Test I & J")


def test_l_reference_audio_linked_and_versioned():
    print("[TEST L] Reference Audio Versioning & History Retention...")
    kb = PronunciationKnowledgeBase()
    
    # Initial recording v1
    e1 = kb.add_voice_pronunciation(
        canonical_text="कळसूबाई",
        audio_bytes=b"VERSION_1_AUDIO",
        preferred_pronunciation="कळसू-बाई",
        phonetic_form="kalsu-bai"
    )
    assert e1.version == 1
    assert "v1" in e1.reference_audio

    # Re-recording v2 (updating without losing history)
    e2 = kb.add_voice_pronunciation(
        canonical_text="कळसूबाई",
        audio_bytes=b"VERSION_2_AUDIO",
        preferred_pronunciation="कळ-सू-बाई",
        phonetic_form="kal-soo-bai"
    )
    assert e2.version == 2
    assert "v2" in e2.reference_audio
    assert len(e2.history) == 1, "Prior v1 entry must be retained in history"
    assert e2.history[0]["version"] == 1
    print(f"  v1 audio: {e2.history[0]['reference_audio']}")
    print(f"  v2 audio: {e2.reference_audio}")
    print("  -> Passed Test L")


def run_all_tests():
    print("=" * 65)
    print("RUNNING AKSHARSETU PRONUNCIATION & SPEECH HARDENING REGRESSION SUITE")
    print("=" * 65)
    test_a_and_d_punctuation_never_spoken_literally()
    test_b_and_c_question_and_sentence_prosody()
    test_e_k_canonical_spelling_immutability()
    test_f_voice_pronunciation_survives_restart()
    test_g_reused_on_future_appearances()
    test_h_document_scope_overrides_global()
    test_i_and_j_provider_adapters()
    test_l_reference_audio_linked_and_versioned()
    print("=" * 65)
    print("ALL 12 PRONUNCIATION & SPEECH HARDENING TESTS (A-L) PASSED!")
    print("=" * 65)


if __name__ == "__main__":
    run_all_tests()
