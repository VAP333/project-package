"""
AksharSetu — TTS Benchmark Suite: Sarvam vs IndicF5 (§14)

Benchmarks the two candidate engines across 6 educational test categories:
1. Canonical Paragraphs (textbook narrative)
2. Dialogue Turns (teacher vs student turns)
3. Questions (pedagogical questions with question intonation)
4. Explanations (measured teacher explanations)
5. Pronunciation Cases (complex Marathi conjuncts e.g. नळदुर्ग, पर्जन्यछायेचा)
6. Punctuation Cases (dandas, commas, pauses, colons)
"""

import time
from typing import Dict, List, Any
from voice.tts_service import tts_service, SpeechStylePlan
from voice.indicf5_provider import IndicF5TTSProvider

BENCHMARK_SAMPLES = [
    {
        "category": "canonical_paragraph",
        "label": "Geography Ch 1 Main Intro Paragraph",
        "text": "राहुलच्या वर्गातील विद्यार्थी आणि शाळेतील शिक्षक असे सर्वजण उस्मानाबाद जिल्ह्यातील नळदुर्ग ते रायगड जिल्ह्यातील अलिबाग येथे क्षेत्रभेटीसाठी निघाले आहेत.",
        "plan": SpeechStylePlan.for_canonical_reading(1.0)
    },
    {
        "category": "dialogue_turn",
        "label": "Teacher Turn (Day 1)",
        "text": "शिक्षिका : आता आपण नळदुर्ग परिसर सोडून सोलापूरच्या दिशेने जात आहोत. प्रवासात तुम्हांला रस्त्याच्या दोन्ही बाजूंना भूरूपे आणि वनस्पतींचे निरीक्षण करायचे आहे.",
        "plan": SpeechStylePlan(style="dialogue", intent="dialogue_teacher", pace=0.95, energy="warm")
    },
    {
        "category": "dialogue_turn",
        "label": "Student Turn (Rahul)",
        "text": "राहुल : होय मॅडम, येथे चढ-उतार असलेली जमीन दिसत असून कोरडी जमीन आणि बाभळीची झाडे जास्त दिसत आहेत.",
        "plan": SpeechStylePlan(style="dialogue", intent="dialogue_student", pace=1.05, energy="inquisitive")
    },
    {
        "category": "question",
        "label": "Interactive Reflection Question",
        "text": "चर्चा करा : तुम्ही या क्षेत्रभेटीत सहभागी होणार असाल, तर कशी पूर्वतयारी कराल आणि साहित्याची निवड कशी कराल?",
        "plan": SpeechStylePlan(style="canonical", intent="question", pace=1.0, pause_after_ms=450)
    },
    {
        "category": "explanation",
        "label": "Grounded Pedagogical Explanation",
        "text": "मराठवाड्यात पाऊस कमी असल्याने शुष्क व काटेरी वनस्पती आढळतात. प्रवासात जमिनीचा उतार आणि वनस्पतीचा प्रकार बदलतो.",
        "plan": SpeechStylePlan.for_teacher_explanation(1.0, ["मराठवाड्यात", "काटेरी वनस्पती"])
    },
    {
        "category": "pronunciation_case",
        "label": "Complex Devanagari Conjuncts & Place Names",
        "text": "नळदुर्ग, अलिबाग, पर्जन्यछायेचा प्रदेश, बेसाल्ट खडक आणि होकायंत्र.",
        "plan": SpeechStylePlan(style="canonical", intent="narration", pace=0.9)
    },
    {
        "category": "punctuation_case",
        "label": "Dandas, Breath Pauses and Punctuation Cadence",
        "text": "दिवस पहिला : वेळ सकाळी ६:०० । शिक्षिका : आता आपण निघत आहोत... सर्वांनी नोंदवही उघडावी !",
        "plan": SpeechStylePlan(style="canonical", intent="narration", pace=1.0)
    }
]

def run_tts_benchmark() -> Dict[str, Any]:
    """Runs identical benchmark suite across Sarvam Bulbul and IndicF5."""
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_test_cases": len(BENCHMARK_SAMPLES),
        "sarvam_results": [],
        "indicf5_results": [],
        "comparison_summary": {}
    }

    sarvam_total_time = 0.0
    indicf5_total_time = 0.0

    for sample in BENCHMARK_SAMPLES:
        text = sample["text"]
        plan = sample["plan"]

        # 1. Benchmark Sarvam
        t0 = time.perf_counter()
        s_res = tts_service.synthesize(text=text, plan=plan, provider_name="sarvam")
        s_lat = (time.perf_counter() - t0) * 1000
        sarvam_total_time += s_lat

        results["sarvam_results"].append({
            "category": sample["category"],
            "label": sample["label"],
            "status": s_res.get("status"),
            "latency_ms": round(s_lat, 2),
            "cached": s_res.get("cached", False),
            "speaker": s_res.get("speaker")
        })

        # 2. Benchmark IndicF5
        t1 = time.perf_counter()
        i_res = tts_service.synthesize(text=text, plan=plan, provider_name="indicf5")
        i_lat = (time.perf_counter() - t1) * 1000
        indicf5_total_time += i_lat

        results["indicf5_results"].append({
            "category": sample["category"],
            "label": sample["label"],
            "status": i_res.get("status"),
            "latency_ms": round(i_lat, 2),
            "is_experimental": True
        })

    results["comparison_summary"] = {
        "sarvam_avg_latency_ms": round(sarvam_total_time / len(BENCHMARK_SAMPLES), 2),
        "indicf5_avg_latency_ms": round(indicf5_total_time / len(BENCHMARK_SAMPLES), 2),
        "sarvam_status": "production_ready",
        "indicf5_status": "experimental_local_pipeline_active"
    }

    return results

if __name__ == "__main__":
    bench = run_tts_benchmark()
    print("=== AksharSetu TTS Benchmark Results ===")
    print(f"Sarvam Avg Latency: {bench['comparison_summary']['sarvam_avg_latency_ms']} ms")
    print(f"IndicF5 Avg Latency: {bench['comparison_summary']['indicf5_avg_latency_ms']} ms")
    for r in bench["sarvam_results"]:
        print(f"- [{r['category']}] {r['label']}: Sarvam {r['latency_ms']}ms")
