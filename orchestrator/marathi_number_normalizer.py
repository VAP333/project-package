# -*- coding: utf-8 -*-
"""
AksharSetu — Marathi Number, Date, Year & Heading Prosody Normalizer

Solves:
1. Dates and years pronounced as isolated digits (e.g. १९६० as "एक नऊ सहा शून्य" instead of "एकोणीसशे साठ").
2. Mechanical heading numbering (e.g. "१. क्षेत्रभेट" or "1. 2.") converted into warm, natural
   teacher introduction: "आज आपण शिकणार आहोत, [Title]..."
3. Time formats: "६:००" -> "सहा वाजता", "८:३०" -> "साडे आठ वाजता".
4. Decimal / Figure numbering: "१.१" -> "एक दशांश एक", "५०%" -> "पन्नास टक्के".
"""

import re
from typing import Dict, Optional

# Mapping from Devanagari digits to ASCII digits
DEVA_TO_ASCII = str.maketrans("०१२३४५६७८९", "0123456789")
ASCII_TO_DEVA = str.maketrans("0123456789", "०१२३४५६७८९")

# 0 to 100 in Marathi words
MARATHI_NUMS_0_TO_100: Dict[int, str] = {
    0: "शून्य", 1: "एक", 2: "दोन", 3: "तीन", 4: "चार", 5: "पाच",
    6: "सहा", 7: "सात", 8: "आठ", 9: "नऊ", 10: "दहा",
    11: "अकरा", 12: "बारा", 13: "तेरा", 14: "चौदा", 15: "पंधरा",
    16: "सोळा", 17: "सतरा", 18: "अठरा", 19: "एकोणीस", 20: "वीस",
    21: "एकवीस", 22: "बावीस", 23: "तेवीस", 24: "चोवीस", 25: "पंचवीस",
    26: "सव्वीस", 27: "सत्तावीस", 28: "अठ्ठावीस", 29: "एकोणतीस", 30: "तीस",
    31: "एकतीस", 32: "बत्तीस", 33: "तेहतीस", 34: "चौतीस", 35: "पस्तीस",
    36: "छत्तीस", 37: "सदतीस", 38: "अडतीस", 39: "एकेचाळीस", 40: "चाळीस",
    41: "एक्केचाळीस", 42: "बेचाळीस", 43: "त्रेचाळीस", 44: "चव्वेचाळीस", 45: "पंचेचाळीस",
    46: "सेहेचाळीस", 47: "सत्तेचाळीस", 48: "अठ्ठेचाळीस", 49: "एकोणपन्नास", 50: "पन्नास",
    51: "एक्कावन्न", 52: "बावन्न", 53: "त्रेपन्न", 54: "चौपन्न", 55: "पंचावन्न",
    56: "छप्पन्न", 57: "सत्तावन्न", 58: "अठ्ठावन्न", 59: "एकोणसाठ", 60: "साठ",
    61: "एकसष्ठ", 62: "बासष्ठ", 63: "त्रेसष्ठ", 64: "चौसष्ठ", 65: "पासष्ठ",
    66: "सहासष्ठ", 67: "सदुसष्ठ", 68: "अडुसष्ठ", 69: "एकोणसत्तर", 70: "सत्तर",
    71: "एकाहत्तर", 72: "बहात्तर", 73: "त्र्याहत्तर", 74: "चौऱ्याहत्तर", 75: "पंच्याहत्तर",
    76: "शहात्तर", 77: "सत्त्याहत्तर", 78: "अठ्ठ्याहत्तर", 79: "एकोणऐंशी", 80: "ऐंशी",
    81: "एक्याऐंशी", 82: "ब्याऐंशी", 83: "त्र्याऐंशी", 84: "चौऱ्याऐंशी", 85: "पंच्याऐंशी",
    86: "शहाऐंशी", 87: "सत्त्याऐंशी", 88: "अठ्ठ्याऐंशी", 89: "एकोणनव्वद", 90: "नव्वद",
    91: "एक्याण्णव", 92: "ब्याण्णव", 93: "त्र्याण्णव", 94: "चौऱ्याण्णव", 95: "पंच्याण्णव",
    96: "शहाण्णव", 97: "सत्त्याण्णव", 98: "अठ्ठ्याण्णव", 99: "नव्व्याण्णव", 100: "शंभर"
}

MARATHI_MONTHS = [
    "जानेवारी", "फेब्रुवारी", "मार्च", "एप्रिल", "मे", "जून",
    "जुलै", "ऑगस्ट", "सप्टेंबर", "ऑक्टोबर", "नोव्हेंबर", "डिसेंबर",
    "चैत्र", "वैशाख", "ज्येष्ठ", "आषाढ", "श्रावण", "भाद्रपद",
    "आश्विन", "कार्तिक", "मार्गशीर्ष", "पौष", "माघ", "फाल्गुन"
]

def int_to_marathi_words(num: int, is_year: bool = False) -> str:
    """Converts integer into natural spoken Marathi words."""
    if num in MARATHI_NUMS_0_TO_100:
        return MARATHI_NUMS_0_TO_100[num]

    # 4-Digit Years: 1000 - 2099
    if 1000 <= num <= 2099 and (is_year or 1800 <= num <= 2050):
        if 1800 <= num <= 1899:
            rem = num - 1800
            return f"अठराशे {MARATHI_NUMS_0_TO_100[rem]}".strip() if rem else "अठराशे"
        elif 1900 <= num <= 1999:
            rem = num - 1900
            return f"एकोणीसशे {MARATHI_NUMS_0_TO_100[rem]}".strip() if rem else "एकोणीसशे"
        elif 2000 <= num <= 2099:
            rem = num - 2000
            return f"दोन हजार {MARATHI_NUMS_0_TO_100[rem]}".strip() if rem else "दोन हजार"

    # Hundreds: 101 - 999
    if 100 < num < 1000:
        hundreds = num // 100
        rem = num % 100
        h_prefix = "एकशे" if hundreds == 1 else f"{MARATHI_NUMS_0_TO_100.get(hundreds, '')}शे"
        if rem == 0:
            return h_prefix
        return f"{h_prefix} {MARATHI_NUMS_0_TO_100.get(rem, '')}".strip()

    # Thousands: 1000 - 99999
    if 1000 <= num < 100000:
        thousands = num // 1000
        rem = num % 1000
        t_word = f"{MARATHI_NUMS_0_TO_100.get(thousands, str(thousands))} हजार"
        if rem == 0:
            return t_word
        return f"{t_word} {int_to_marathi_words(rem, is_year=False)}".strip()

    return str(num)

class MarathiNumberNormalizer:
    """
    Translates raw numbers, dates, times, decimals, and mechanical headings
    into fluent, pedagogical Marathi speech strings.
    """

    def normalize_text_numbers(self, text: str) -> str:
        """Full pass over text to verbalize numbers, years, and dates into Marathi."""
        if not text:
            return ""

        t = text

        # 1. Normalize Percentages: e.g. "५०%" or "50%" -> "पन्नास टक्के"
        t = re.sub(
            r'([०-९0-9]+)\s*%',
            lambda m: f"{self._num_str_to_words(m.group(1))} टक्के",
            t
        )

        # 2. Normalize Time: e.g. "६:००" or "06:00" -> "सहा वाजता", "८:३०" -> "साडे आठ वाजता"
        t = re.sub(
            r'(सकाळी|दुपारी|संध्याकाळी|रात्री)?\s*([०-९0-9]{1,2})\s*:\s*([०-९0-9]{2})\s*(वाजता)?',
            self._replace_time,
            t
        )

        # 3. Normalize Dates with Month: e.g. "१ मे १९६०" or "15 ऑगस्ट 1947"
        months_pat = "|".join(MARATHI_MONTHS)
        t = re.sub(
            rf'([०-९0-9]{{1,2}})\s*({months_pat})\s*([०-९0-9]{{4}})',
            lambda m: f"{self._num_str_to_words(m.group(1))} {m.group(2)} {self._num_str_to_words(m.group(3), is_year=True)}",
            t
        )
        t = re.sub(
            rf'({months_pat})\s*([०-९0-9]{{4}})',
            lambda m: f"{m.group(1)} {self._num_str_to_words(m.group(2), is_year=True)}",
            t
        )

        # 4. Normalize Explicit Year Mentions: e.g. "सन १९६०", "वर्ष १९४७", "१९६० मध्ये", "२०२४ सालात"
        t = re.sub(
            r'(सन|वर्ष|साली|सालात)\s*([०-९0-9]{4})',
            lambda m: f"{m.group(1)} {self._num_str_to_words(m.group(2), is_year=True)}",
            t
        )
        t = re.sub(
            r'([०-९0-9]{4})\s*(मध्ये|रोजी|पर्यंत|पासून|दरम्यान|साली)',
            lambda m: f"{self._num_str_to_words(m.group(1), is_year=True)} {m.group(2)}",
            t
        )

        # 5. Normalize Figure / Map Decimals: e.g. "आकृती १.१" -> "आकृती क्रमांक एक दशांश एक"
        t = re.sub(
            r'(आकृती|नकाशा|चित्र|तक्ता)\s*([०-९0-9]+)\.([०-९0-9]+)',
            lambda m: f"{m.group(1)} क्रमांक {self._num_str_to_words(m.group(2))} दशांश {self._num_str_to_words(m.group(3))}",
            t
        )

        # 6. Normalize General Decimals: e.g. "२.५" -> "दोन दशांश पाच"
        t = re.sub(
            r'([०-९0-9]+)\.([०-९0-9]+)(?!\w)',
            lambda m: f"{self._num_str_to_words(m.group(1))} दशांश {self._num_str_to_words(m.group(2))}",
            t
        )

        # 7. Normalize Standalone 4-digit years (1800-2099)
        t = re.sub(
            r'(?<![०-९0-9\.\-])(1[89][0-9]{2}|20[0-9]{2}|[१२][८९०][०-९]{2})(?![०-९0-9\.\-])',
            lambda m: self._num_str_to_words(m.group(1), is_year=True),
            t
        )

        # 8. Normalize remaining standalone integers: 0 to 99999
        t = re.sub(
            r'(?<![०-९0-9\.\-])([०-९0-9]{1,5})(?![०-९0-9\.\-])',
            lambda m: self._num_str_to_words(m.group(1), is_year=False),
            t
        )

        return t

    def format_heading_for_speech(self, raw_heading: str, is_chapter_start: bool = True, heading_index: int = 0) -> str:
        """
        Transforms mechanical heading titles into warm pedagogical introduction:
        - Chapter start (Page 1 main chapter heading): "आज आपण शिकणार आहोत, [Title]."
        - Page 2 and onwards / subsequent sub-headings: miscellaneous teacher transitions:
          "आता आपण बघूयात, [Title]." / "चला, आता बघूयात, [Title]." / "आता पुढील भाग पाहूयात, [Title]."
        """
        clean = raw_heading.strip()
        # Strip leading numbers, Roman numerals, punctuation: e.g. "1. ", "१. ", "1.1 ", "१.१ ", "1. 2. "
        clean = re.sub(r'^(?:[०-९0-9ivxLCDM\.\-–—\:\,\t\s]+)', '', clean)
        # Strip prefixes like "प्रकरण १", "पाठ १", "घटक २", "अध्याय १"
        clean = re.sub(r'^(?:प्रकरण|पाठ|घटक|अध्याय)\s*[०-९0-9ivxLCDM\.\-–—\:\,\t\s]+', '', clean, flags=re.IGNORECASE)
        clean = clean.strip().rstrip('.।:;')

        if not clean:
            clean = raw_heading.strip()

        if is_chapter_start:
            return f"आज आपण शिकणार आहोत, {clean}."

        transitions = [
            f"आता आपण बघूयात, {clean}.",
            f"चला, आता बघूयात, {clean}.",
            f"आता पुढील भाग पाहूयात, {clean}.",
            f"चला, आता समजून घेऊया, {clean}.",
            f"आता आपण पाहूया, {clean}."
        ]
        return transitions[heading_index % len(transitions)]

    def _num_str_to_words(self, num_str: str, is_year: bool = False) -> str:
        ascii_digits = num_str.translate(DEVA_TO_ASCII)
        try:
            val = int(ascii_digits)
            return int_to_marathi_words(val, is_year=is_year)
        except ValueError:
            return num_str

    def _replace_time(self, match: re.Match) -> str:
        prefix = match.group(1) or ""
        hour_str = match.group(2).translate(DEVA_TO_ASCII)
        min_str = match.group(3).translate(DEVA_TO_ASCII)
        try:
            h = int(hour_str)
            m = int(min_str)
            h_word = MARATHI_NUMS_0_TO_100.get(h, str(h))

            if m == 0:
                time_word = f"{h_word} वाजता"
            elif m == 30:
                time_word = f"साडे {h_word} वाजता" if h != 1 and h != 2 else ("दीड वाजता" if h == 1 else "अडीच वाजता")
            elif m == 15:
                time_word = f"सव्वा {h_word} वाजता"
            elif m == 45:
                next_h = MARATHI_NUMS_0_TO_100.get((h % 12) + 1, "")
                time_word = f"पावणे {next_h} वाजता"
            else:
                m_word = MARATHI_NUMS_0_TO_100.get(m, str(m))
                time_word = f"{h_word} वाजून {m_word} मिनिटे"

            if prefix:
                return f"{prefix} {time_word}".strip()
            return time_word
        except Exception:
            return match.group(0)

marathi_number_normalizer = MarathiNumberNormalizer()
