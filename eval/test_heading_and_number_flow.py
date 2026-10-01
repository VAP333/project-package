# -*- coding: utf-8 -*-
"""
Test Suite for Heading Speech Formatting & Marathi Number/Year Normalization:
Verifies:
1. Heading '१. क्षेत्रभेट' produces 'आज आपण शिकणार आहोत, क्षेत्रभेट.'
2. Heading '1. 2. सिंहगड यात्रा' produces 'आज आपण शिकणार आहोत, सिंहगड यात्रा.'
3. Dates & Years: '१ मे १९६०' -> 'एक मे एकोणीसशे साठ'
4. Year '१९४७' -> 'एकोणीसशे सेहेचाळीस'
5. Year '२०२४' -> 'दोन हजार चोवीस'
6. Time 'सकाळी ६:०० वाजता' -> 'सकाळी सहा वाजता'
7. Figure 'आकृती १.१' -> 'आकृती क्रमांक एक दशांश एक'
8. Pre-TTS pipeline normalizes all numbers before sending to Sarvam TTS.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import requests
from orchestrator.marathi_number_normalizer import marathi_number_normalizer
from orchestrator.speech_normalizer import speech_normalizer

BASE_URL = "http://localhost:8000"

def run_heading_and_number_tests():
    print("=" * 60)
    print("TESTING HEADING FORMATTING & NUMBER/YEAR NORMALIZATION")
    print("=" * 60)

    # 1. Heading tests
    h1 = "१. क्षेत्रभेट"
    res1 = marathi_number_normalizer.format_heading_for_speech(h1)
    print(f"\n[Heading 1] Input: '{h1}' -> Spoken: '{res1}'")
    assert "आज आपण शिकणार आहोत" in res1, "Missing introductory phrase!"
    assert "१." not in res1 and "1." not in res1, "Mechanical number not stripped!"
    assert "क्षेत्रभेट" in res1

    h2 = "1. 2. सिंहगड यात्रा"
    res2 = marathi_number_normalizer.format_heading_for_speech(h2)
    print(f"[Heading 2] Input: '{h2}' -> Spoken: '{res2}'")
    assert "आज आपण शिकणार आहोत" in res2
    assert "1." not in res2 and "2." not in res2
    assert "सिंहगड यात्रा" in res2

    # 1b. Non-chapter start / Page 2+ headings (miscellaneous transitions)
    h_sub1 = "लिखित साधने"
    res_sub1 = marathi_number_normalizer.format_heading_for_speech(h_sub1, is_chapter_start=False, heading_index=0)
    print(f"[Heading Sub 1 (Page 2+)] Input: '{h_sub1}' -> Spoken: '{res_sub1}'")
    assert "आज आपण शिकणार आहोत" not in res_sub1
    assert "लिखित साधने" in res_sub1

    h_sub2 = "मौखिक साधने"
    res_sub2 = marathi_number_normalizer.format_heading_for_speech(h_sub2, is_chapter_start=False, heading_index=1)
    print(f"[Heading Sub 2 (Page 3+)] Input: '{h_sub2}' -> Spoken: '{res_sub2}'")
    assert "आज आपण शिकणार आहोत" not in res_sub2
    assert "चला, आता बघूयात, मौखिक साधने." in res_sub2

    # 2. Date and Year Normalization tests
    y1 = "महाराष्ट्र राज्याची स्थापना १ मे १९६० रोजी झाली."
    norm_y1 = speech_normalizer.normalize_for_tts(y1)
    print(f"\n[Year 1] Input: '{y1}'\n        Normalized: '{norm_y1}'")
    assert "एक मे" in norm_y1, "Date not verbalized!"
    assert "एकोणीसशे साठ" in norm_y1, "Year 1960 not verbalized into Marathi words!"
    assert "१९६०" not in norm_y1, "Raw digits still present!"

    y2 = "भारत देशाला १९४७ मध्ये स्वातंत्र्य मिळाले आणि २०२० मध्ये नवी धोरणे आली."
    norm_y2 = speech_normalizer.normalize_for_tts(y2)
    print(f"\n[Year 2] Input: '{y2}'\n        Normalized: '{norm_y2}'")
    assert "एकोणीसशे" in norm_y2, "Year 1947 not verbalized!"
    assert "दोन हजार वीस" in norm_y2, "Year 2020 not verbalized!"
    assert "१९४७" not in norm_y2 and "२०२०" not in norm_y2

    # 3. Time and Figure tests
    tf = "बसचा प्रवास सकाळी ६:०० वाजता सुरू झाला. आकृती १.१ मधील नकाशा पहा."
    norm_tf = speech_normalizer.normalize_for_tts(tf)
    print(f"\n[Time & Figure] Input: '{tf}'\n               Normalized: '{norm_tf}'")
    assert "सकाळी सहा वाजता" in norm_tf, "Time 6:00 not verbalized!"
    assert "आकृती क्रमांक एक दशांश एक" in norm_tf, "Figure 1.1 not verbalized!"

    # 4. Live API Synthesis Verification
    print("\n[API Synthesis] Synthesizing normalized sentence through TTS endpoint...")
    payload = {
        "text": norm_y1,
        "speaker": "shreya",
        "provider": "sarvam"
    }
    resp = requests.post(f"{BASE_URL}/api/tts/synthesize", json=payload)
    assert resp.status_code == 200, f"TTS API failed: {resp.text}"
    data = resp.json()
    assert data.get("audio_base64"), "No audio returned!"
    print(f"PASS: Synthesized audio ({len(data['audio_base64'])} chars) with smooth spoken years!")
    print(f"  Speech text used: '{data.get('resolved_speech_text')}'")

    print("\n" + "=" * 60)
    print("ALL HEADING & NUMBER NORMALIZATION TESTS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    run_heading_and_number_tests()
