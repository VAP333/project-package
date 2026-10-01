"""
AksharSetu — Pedagogical Planner & Structured Tutor Mode (§0, Part 3 & Part 4)

SEPARATES:
1. WHAT THE TEACHER SAYS (grounded, subject-aware pedagogical content)
2. HOW THE TEACHER SAYS IT (speech style, prosody, pacing, audio segmentation)
3. CANONICAL TEXT FROM AI EXPLANATION (canonical textbook text is NEVER mutated)

Audio Segmentation:
Represents Tutor Mode as distinct speech segments:
[
  { "type": "canonical", "text": "...", "prosody_style": "canonical_reading" },
  { "type": "transition", "text": "...", "prosody_style": "teacher_transition" },
  { "type": "explanation", "text": "...", "prosody_style": "teacher_explanation" }
]
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import re

@dataclass
class SpeechSegment:
    type: str # "canonical" | "transition" | "explanation"
    text: str
    prosody_style: str = "canonical_reading" # "canonical_reading" | "teacher_transition" | "teacher_explanation"
    pace: float = 1.0
    pause_before_ms: int = 0
    pause_after_ms: int = 250
    emphasis_terms: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TutorResponse:
    response_type: str # "explanation" | "clarify_concept" | "question_hint" | "vocabulary"
    teaching_intent: str # "clarify_concept" | "connect_real_world" | "guide_observation" | "encourage_reflection"
    canonical_text: str # Original unmutated textbook line
    transition: str # Natural transition into explanation
    explanation: str # Simple, grounded pedagogical explanation
    prosody_style: str = "teacher_explanation"
    pause_after: bool = True
    emphasis_terms: List[str] = field(default_factory=list)
    source_region_ids: List[str] = field(default_factory=list)
    learning_unit_id: str = ""
    subject: str = "Geography"
    segments: List[SpeechSegment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PedagogicalPlanner:
    """
    Subject-Aware Pedagogical Planner.
    Grounded in:
    - current textbook content
    - current chapter & learning unit
    - current region
    - subject/genre strategies
    """
    def __init__(self):
        # Subject transition phrases (natural Marathi teacher cadence)
        self.transitions = {
            "geography": "इथे मुख्य मुद्दा असा आहे की, भौगोलिक परिस्थिती समजून घेऊया.",
            "marathi": "या ओळीचा भावार्थ आणि कवीची भावना समजून घेऊया.",
            "science": "यामागील वैज्ञानिक तत्त्व आणि कारण समजून घेऊया.",
            "mathematics": "या पायरीचा गणितीय अर्थ आणि पद्धत पाहूया.",
            "exercise": "या प्रश्नाचे उत्तर शोधण्यासाठी मुख्य मुद्दा लक्षात घ्या."
        }

    def plan_tutor_response(
        self,
        canonical_text: str,
        subject: str = "Geography",
        region_type: str = "paragraph",
        concept: str = "",
        learning_unit_id: str = "",
        source_region_ids: Optional[List[str]] = None,
        custom_explanation: Optional[str] = None
    ) -> TutorResponse:
        """
        Creates a structured, grounded teacher response with 3 separate audio segments.
        Ensures canonical text is never overwritten.
        """
        subj_key = subject.lower()
        reg_ids = source_region_ids or []

        # Determine teaching intent and subject strategy
        if region_type in ("exercise", "question", "discussion_box"):
            intent = "encourage_reflection"
            trans = "या प्रश्नाचा किंवा कृतीचा विचार करताना मुख्य मुद्दा लक्षात घ्या."
            resp_type = "question_hint"
            prosody = "teacher_guidance"
        elif region_type == "caption":
            intent = "guide_observation"
            trans = "या आकृतीचे किंवा नकाशाचे काळजीपूर्वक निरीक्षण करा."
            resp_type = "explanation"
            prosody = "teacher_observation"
        elif region_type == "dialogue":
            intent = "clarify_concept"
            trans = "या संवादातून शिक्षिका व विद्यार्थ्यांमधील महत्त्वाचा मुद्दा समजून घेऊया."
            resp_type = "explanation"
            prosody = "teacher_explanation"
        elif "marathi" in subj_key or region_type == "poetry":
            intent = "clarify_concept"
            trans = "या ओळीचा भावार्थ सोप्या भाषेत समजून घेऊया."
            resp_type = "explanation"
            prosody = "teacher_explanation"
        else:
            intent = "clarify_concept"
            trans = self.transitions.get(subj_key, "इथे मुख्य मुद्दा असा आहे की, हे समजून घेऊया.")
            resp_type = "explanation"
            prosody = "teacher_explanation"

        # Generate grounded explanation if not explicitly provided
        if custom_explanation:
            explanation = custom_explanation
        else:
            explanation = self._generate_grounded_pedagogic_text(
                canonical_text=canonical_text,
                subject=subject,
                region_type=region_type,
                concept=concept
            )

        # Extract emphasis terms
        emphasis_terms = self._extract_emphasis_terms(canonical_text, explanation)

        # Create 3 distinct speech segments:
        # 1. Canonical textbook segment (exact text, standard pace)
        # 2. Teacher transition segment (smooth conversational prompt)
        # 3. Grounded explanation segment (measured teacher pace, warm modulation)
        segments = [
            SpeechSegment(
                type="canonical",
                text=canonical_text.strip(),
                prosody_style="canonical_reading",
                pace=1.0,
                pause_before_ms=0,
                pause_after_ms=300,
                emphasis_terms=[]
            ),
            SpeechSegment(
                type="transition",
                text=trans.strip(),
                prosody_style="teacher_transition",
                pace=1.0,
                pause_before_ms=250,
                pause_after_ms=350,
                emphasis_terms=[]
            ),
            SpeechSegment(
                type="explanation",
                text=explanation.strip(),
                prosody_style=prosody,
                pace=0.95, # slightly more measured and clear for teacher explanation
                pause_before_ms=200,
                pause_after_ms=500,
                emphasis_terms=emphasis_terms
            )
        ]

        return TutorResponse(
            response_type=resp_type,
            teaching_intent=intent,
            canonical_text=canonical_text.strip(),
            transition=trans,
            explanation=explanation.strip(),
            prosody_style=prosody,
            pause_after=True,
            emphasis_terms=emphasis_terms,
            source_region_ids=reg_ids,
            learning_unit_id=learning_unit_id,
            subject=subject,
            segments=segments
        )

    def _generate_grounded_pedagogic_text(
        self,
        canonical_text: str,
        subject: str,
        region_type: str,
        concept: str
    ) -> str:
        """Subject-aware pedagogical grounding generator."""
        clean = canonical_text.strip()
        subj = subject.lower()

        if "geography" in subj:
            # Geography: concept -> place/process -> visual/diagram -> real-world connection
            if "नळदुर्ग" in clean or "अलिबाग" in clean:
                return "क्षेत्रभेटीमध्ये प्रत्यक्ष प्रवासादरम्यान भूरूपे, वनस्पती आणि वस्त्यांमधील बदल प्रत्यक्ष डोळ्यांनी पाहणे हा मुख्य हेतू असतो. नळदुर्ग ते अलिबाग प्रवासात पर्जन्यमान आणि हवामानातील बदल स्पष्ट जाणवतो."
            elif "आकृती" in clean or "नकाशा" in clean:
                return "नकाशा वाचनामुळे आपण कोणत्या मार्गाने जात आहोत आणि वाटेत कोणती गावे, डोंगर किंवा नद्या लागणार आहेत, याची पूर्वकल्पना येते."
            elif "साहित्य" in clean or "नोंदवही" in clean:
                return "क्षेत्रभेटीत अचूक निरीक्षणासाठी दिशा दाखवणारे होकायंत्र, अंतरासाठी टेप आणि माहिती नोंदवण्यासाठी प्रश्नावली सोबत ठेवणे अत्यंत गरजेचे असते."
            elif "सिंहगड" in clean or "किल्ला" in clean:
                return "सिंहगड हा ऐतिहासिक किल्ला असून तो दख्खनच्या पठारावरील एका उंचावर आहे. येथे बेसाल्ट खडकाचे स्तर आणि सह्याद्री पर्वताची रचना प्रत्यक्ष अभ्यासता येते."
            elif "खडक" in clean or "बेसाल्ट" in clean:
                return "महाराष्ट्राच्या पठारी भागात ज्वालामुखीच्या लाव्हारसापासून तयार झालेला अग्निजन्य बेसाल्ट खडक मोठ्या प्रमाणावर आढळतो."
            elif "पर्जन्य" in clean or "पाऊस" in clean or "बाभळी" in clean:
                return "उस्मानाबाद व सोलापूर परिसर पर्जन्यछायेच्या भागात येत असल्याने तिथे कोरडी हवा आणि काटेरी बाभळीची झाडे जास्त दिसतात."
            elif "समुद्र" in clean or "अलिबाग" in clean or "लाटा" in clean:
                return "अलिबाग हे कोकणातील समुद्रकिनाऱ्यावरील ठिकाण आहे. इथे समुद्राच्या लाटांमुळे तयार झालेली भूरूपे आणि आद्र हवामान अनुभवता येते."
            elif region_type in ("exercise", "discussion_box", "question"):
                return "या प्रश्नाचे उत्तर लिहिताना आपल्या परिसरातील प्रत्यक्ष अनुभव आणि प्रवासाच्या पूर्वतयारीचे टप्पे क्रमाने मांडा."
            else:
                return f"या परिच्छेदात {concept or 'भौगोलिक घटकांचे'} प्रत्यक्ष निरीक्षण कसे करावे हे समजावून सांगितले आहे. स्थानिक पर्यावरणाचा मानवी जीवनावर होणारा परिणाम इथे लक्षात घ्यावा."

        elif "marathi" in subj:
            # Poetry/Prose: line/stanza -> meaning -> difficult words -> emotion/theme -> interpretation
            if "तू बुद्धी दे" in clean or "तेज दे" in clean:
                return "कवी ईश्वराकडे सन्मार्गावर चालण्यासाठी बुद्धी, तेज आणि अखंड विश्वास मागतो. ‘सर्वथा’ म्हणजे सर्व प्रकारे, आणि ‘ध्यास’ म्हणजे एकाग्र ओढ."
            elif "हरवले आभाळ" in clean or "सारथी" in clean:
                return "ज्यांना जीवनात कोणाचाही आधार नाही, अशा निराधार लोकांना मदत करण्याची वृत्ती आपल्यात निर्माण व्हावी, अशी प्रार्थना कवी करतो. ‘सारथी’ म्हणजे योग्य मार्ग दाखवणारा."
            elif "जाणावया" in clean or "संवेदना" in clean:
                return "दुसऱ्यांचे दुःख समजून घेण्याची कणव मनात सदैव जिवंत राहावी आणि अन्यायाविरुद्ध लढण्याची शक्ती रक्तामध्ये असावी, असा या ओळींचा अर्थ आहे."
            elif "सन्मार्ग" in clean or "सत्संगती" in clean:
                return "जीवनात कितीही संकटे आली तरी चांगला मार्ग आणि नीतिमत्ता ढळू नये, यासाठी कवी ईश्वराकडे आत्मिक बळ मागतो."
            else:
                return f"हा भाग ‘{concept or 'पाठाचा मुख्य संदेश'}’ स्पष्ट करतो. भाषेचे सौंदर्य आणि मूल्यांची शिकवण यावर लक्ष केंद्रित करा."

        return f"हा भाग ‘{concept or 'अभ्यास घटक'}’ स्पष्ट करतो. मूळ मजकुरातील संकल्पना समजून घेऊन वाचन सुरू ठेवा."

    def _extract_emphasis_terms(self, canonical_text: str, explanation: str) -> List[str]:
        terms = []
        candidates = ["क्षेत्रभेट", "नळदुर्ग", "अलिबाग", "होकायंत्र", "बेसाल्ट", "पर्जन्यछाया", "सिंहगड", "बुद्धी", "तेज", "संवेदना", "सारथी", "सन्मार्ग"]
        for c in candidates:
            if c in canonical_text or c in explanation:
                terms.append(c)
        return terms[:4]

pedagogical_planner = PedagogicalPlanner()
