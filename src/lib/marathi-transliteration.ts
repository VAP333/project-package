// -*- coding: utf-8 -*-
/**
 * AksharSetu — Enhanced Marathi Phonetic Transliteration & Diacritic (Matra) Engine
 */

export interface MatraTablet {
  id: string;
  sign: string;
  sample: string;
  label: string;
  name_en: string;
  roman: string;
  category: "vowel_matra" | "anusvara" | "halant" | "special" | "independent_vowel";
  independentChar: string;
  tooltip: string;
}

export const COMMON_MATRA_TABLETS: MatraTablet[] = [
  {
    id: "anusvara",
    sign: "ं",
    sample: "सं",
    label: "अनुस्वार (ं)",
    name_en: "Anusvara",
    roman: "n / m",
    category: "anusvara",
    independentChar: "अं",
    tooltip: "अनुस्वार — नासिक्य उच्चार (उदा. सं, कं, कां)"
  },
  {
    id: "matra_aa",
    sign: "ा",
    sample: "सा",
    label: "कान्हा (ा)",
    name_en: "Matra Aa",
    roman: "aa",
    category: "vowel_matra",
    independentChar: "आ",
    tooltip: "कान्हा (दीर्घ आ) — उदा. सा, का, मा"
  },
  {
    id: "matra_i",
    sign: "ि",
    sample: "सि",
    label: "पहिली वेलांटी (ि)",
    name_en: "Hrasva I",
    roman: "i",
    category: "vowel_matra",
    independentChar: "इ",
    tooltip: "पहिली वेलांटी (ऱ्हस्व इ) — उदा. कि, दि, सि"
  },
  {
    id: "matra_ee",
    sign: "ी",
    sample: "सी",
    label: "दुसरी वेलांटी (ी)",
    name_en: "Deergha II",
    roman: "ee",
    category: "vowel_matra",
    independentChar: "ई",
    tooltip: "दुसरी वेलांटी (दीर्घ ई) — उदा. की, ली, सी"
  },
  {
    id: "matra_u",
    sign: "ु",
    sample: "सु",
    label: "पहिला उकार (ु)",
    name_en: "Hrasva U",
    roman: "u",
    category: "vowel_matra",
    independentChar: "उ",
    tooltip: "पहिला उकार (ऱ्हस्व उ) — उदा. कु, मु, सु"
  },
  {
    id: "matra_oo",
    sign: "ू",
    sample: "सू",
    label: "दुसरा उकार (ू)",
    name_en: "Deergha UU",
    roman: "oo",
    category: "vowel_matra",
    independentChar: "ऊ",
    tooltip: "दुसरा उकार (दीर्घ ऊ) — उदा. कू, भू, सू"
  },
  {
    id: "matra_e",
    sign: "े",
    sample: "से",
    label: "एक मात्रा (े)",
    name_en: "Matra E",
    roman: "e",
    category: "vowel_matra",
    independentChar: "ए",
    tooltip: "एक मात्रा — उदा. के, ते, से"
  },
  {
    id: "matra_ai",
    sign: "ै",
    sample: "सै",
    label: "दोन मात्रे (ै)",
    name_en: "Matra Ai",
    roman: "ai",
    category: "vowel_matra",
    independentChar: "ऐ",
    tooltip: "दोन मात्रे — उदा. कै, मै, सै"
  },
  {
    id: "matra_o",
    sign: "ो",
    sample: "सो",
    label: "एक कान्हा एक मात्रा (ो)",
    name_en: "Matra O",
    roman: "o",
    category: "vowel_matra",
    independentChar: "ओ",
    tooltip: "एक कान्हा एक मात्रा — उदा. को, तो, सो"
  },
  {
    id: "matra_au",
    sign: "ौ",
    sample: "सौ",
    label: "एक कान्हा दोन मात्रे (ौ)",
    name_en: "Matra Au",
    roman: "au",
    category: "vowel_matra",
    independentChar: "औ",
    tooltip: "एक कान्हा दोन मात्रे — उदा. कौ, नौ, सौ"
  },
  {
    id: "matra_candra_e",
    sign: "ॅ",
    sample: "कॅ",
    label: "चंद्र (ॅ)",
    name_en: "Candra E",
    roman: "ae",
    category: "vowel_matra",
    independentChar: "ॲ",
    tooltip: "चंद्र (इंग्रजी उच्चार) — उदा. कॅ, बॅ, मॅ"
  },
  {
    id: "matra_candra_o",
    sign: "ॉ",
    sample: "कॉ",
    label: "चंद्र-ओ (ॉ)",
    name_en: "Candra O",
    roman: "aw / o",
    category: "vowel_matra",
    independentChar: "ऑ",
    tooltip: "चंद्र-ओ (इंग्रजी 'ॉ' उच्चार) — उदा. कॉ, हॉ, डॉ"
  },
  {
    id: "halant",
    sign: "्",
    sample: "क्",
    label: "हलंत (्)",
    name_en: "Virama",
    roman: "virama",
    category: "halant",
    independentChar: "",
    tooltip: "हलंत — जोडाक्षरासाठी व्यंजन अर्धे करणे (उदा. क्, स्, त्)"
  },
  {
    id: "reph",
    sign: "र्",
    sample: "सर्व",
    label: "रफार (र्)",
    name_en: "Reph",
    roman: "r-",
    category: "special",
    independentChar: "र",
    tooltip: "रफार — अक्षरावरील अर्धा र (उदा. गर्व, सर्व)"
  },
  {
    id: "hyphen",
    sign: "-",
    sample: "सम-कालीन",
    label: "हायफन (-)",
    name_en: "Syllable Break",
    roman: "-",
    category: "special",
    independentChar: "-",
    tooltip: "हायफन — TTS उच्चार सुलभ करण्यासाठी अक्षर अवयव वेगळा करणे"
  },
  {
    id: "visarga",
    sign: "ः",
    sample: "तः",
    label: "विसर्ग (ः)",
    name_en: "Visarga",
    roman: "h",
    category: "special",
    independentChar: "अः",
    tooltip: "विसर्ग — कंठ्य ह-कार उच्चार (उदा. स्वतः, दुःख)"
  }
];

const IS_CONSONANT_REGEX = /[\u0915-\u0939\u0958-\u095F\u0933]/;
const IS_VOWEL_MATRA_REGEX = /[\u093E-\u094C\u0944\u0949\u0962\u0963]/;

/**
 * Smartly inserts a Matra / Diacritic at the user's cursor position adhering to accepted Marathi conventions.
 */
export function insertMatraSmartly(
  currentText: string,
  cursorPos: number,
  tablet: MatraTablet
): { newText: string; newCursor: number; notification?: string } {
  const text = currentText || "";
  const pos = Math.max(0, Math.min(cursorPos, text.length));

  const pre = text.slice(0, pos);
  const post = text.slice(pos);
  const prevChar = pre.length > 0 ? pre[pre.length - 1] : "";

  // 1. Hyphen (-) Insertion
  if (tablet.id === "hyphen") {
    if (prevChar === "-" || post.startsWith("-")) {
      return { newText: text, newCursor: pos, notification: "हायफन आधीच जोडलेला आहे." };
    }
    const newText = pre + "-" + post;
    return { newText, newCursor: pos + 1 };
  }

  // 2. Anusvara (ं) Insertion
  if (tablet.id === "anusvara") {
    if (prevChar === "ं") {
      return { newText: text, newCursor: pos, notification: "अनुस्वार आधीच जोडलेला आहे." };
    }
    if (prevChar === "्") {
      return { newText: text, newCursor: pos, notification: "हलंत अक्षरावर थेट अनुस्वार जोडता येत नाही." };
    }
    if (!prevChar || prevChar === " " || prevChar === "-") {
      const newText = pre + "अं" + post;
      return { newText, newCursor: pos + 2, notification: "सुरुवातीला स्वतंत्र 'अं' जोडले." };
    }
    const newText = pre + "ं" + post;
    return { newText, newCursor: pos + 1 };
  }

  // 3. Halant (्) Insertion
  if (tablet.id === "halant") {
    if (prevChar === "्") {
      return { newText: text, newCursor: pos, notification: "हलंत आधीच जोडलेले आहे." };
    }
    if (!prevChar || prevChar === " " || prevChar === "-") {
      return { newText: text, newCursor: pos, notification: "हलंत हे व्यंजनानंतरच जोडले जाते." };
    }
    if (IS_VOWEL_MATRA_REGEX.test(prevChar)) {
      const newText = pre.slice(0, -1) + "्" + post;
      return { newText, newCursor: pos, notification: "मात्रा बदलून हलंत जोडले." };
    }
    const newText = pre + "्" + post;
    return { newText, newCursor: pos + 1 };
  }

  // 4. Reph (र्) Insertion
  if (tablet.id === "reph") {
    const newText = pre + "र्" + post;
    return { newText, newCursor: pos + 2, notification: "रफार जोडला." };
  }

  // 5. Visarga (ः) Insertion
  if (tablet.id === "visarga") {
    if (prevChar === "ः") {
      return { newText: text, newCursor: pos, notification: "विसर्ग आधीच जोडलेला आहे." };
    }
    if (!prevChar || prevChar === " " || prevChar === "-") {
      const newText = pre + "अः" + post;
      return { newText, newCursor: pos + 2, notification: "स्वतंत्र 'अः' जोडले." };
    }
    const newText = pre + "ः" + post;
    return { newText, newCursor: pos + 1 };
  }

  // 6. Vowel Matras (ा, ि, ी, ु, ू, े, ै, ो, ौ, ॅ, ॉ)
  if (tablet.category === "vowel_matra") {
    // If cursor is at start of input, or after space or hyphen:
    if (!prevChar || prevChar === " " || prevChar === "-") {
      const indep = tablet.independentChar;
      const newText = pre + indep + post;
      return {
        newText,
        newCursor: pos + indep.length,
        notification: `सुरुवातीला स्वतंत्र स्वर '${indep}' जोडला.`
      };
    }

    // If preceding character is Halant (्): replace halant with matra (e.g. क् + ा = का)
    if (prevChar === "्") {
      const newText = pre.slice(0, -1) + tablet.sign + post;
      return { newText, newCursor: pos, notification: "हलंत काढून मात्रा जोडली." };
    }

    // If preceding character is an existing vowel matra: replace it cleanly! (e.g. से + ी = सी)
    if (IS_VOWEL_MATRA_REGEX.test(prevChar)) {
      const newText = pre.slice(0, -1) + tablet.sign + post;
      return { newText, newCursor: pos, notification: "आधीची मात्रा बदलली." };
    }

    // If preceding character is Anusvara (ं): in Devanagari, matra must precede anusvara (e.g. सं + ा = सां)
    if (prevChar === "ं") {
      const charBeforeAnusvara = pre.length > 1 ? pre[pre.length - 2] : "";
      if (IS_VOWEL_MATRA_REGEX.test(charBeforeAnusvara)) {
        const newText = pre.slice(0, -2) + tablet.sign + "ं" + post;
        return { newText, newCursor: pos, notification: "मात्रा अद्ययावत केली." };
      }
      const newText = pre.slice(0, -1) + tablet.sign + "ं" + post;
      return { newText, newCursor: pos + 1 };
    }

    // Preceding character is a consonant or independent vowel (अ + ा = आ)
    if (prevChar === "अ" && tablet.sign === "ा") {
      const newText = pre.slice(0, -1) + "आ" + post;
      return { newText, newCursor: pos, notification: "'अ' चा 'आ' केला." };
    }

    const newText = pre + tablet.sign + post;
    return { newText, newCursor: pos + tablet.sign.length };
  }

  // Fallback direct insert
  return { newText: pre + tablet.sign + post, newCursor: pos + tablet.sign.length };
}

// ============================================================================
// Phonetic Transliteration Engine: Romanized <-> Devanagari
// ============================================================================

// Common Marathi phonetic patterns
const SPECIAL_PHONETIC_WORDS: Record<string, string> = {
  "sinh": "सिंह",
  "sinha": "सिंह",
  "nat": "नट",
  "rang": "रंग",
  "gadh": "गड",
  "gad": "गड",
  "durga": "दुर्ग",
  "durg": "दुर्ग",
  "baag": "बाग",
  "bag": "बाग"
};

const MULTI_CONSONANTS: Array<[string, string]> = [
  ["ksha", "क्ष"], ["ksh", "क्ष"], ["x", "क्ष"],
  ["dnya", "ज्ञ"], ["gya", "ज्ञ"], ["jnya", "ज्ञ"],
  ["chha", "छा"], ["chh", "छ"],
  ["kha", "खा"], ["kh", "ख"],
  ["gha", "घा"], ["gh", "घ"],
  ["cha", "चा"], ["ch", "च"],
  ["jha", "झा"], ["jh", "झ"], ["z", "झ"],
  ["tha", "था"], ["th", "थ"], ["Th", "ठ"],
  ["dha", "धा"], ["dh", "ध"], ["Dh", "ढ"],
  ["pha", "फा"], ["ph", "फ"], ["f", "फ"],
  ["bha", "भा"], ["bh", "भ"],
  ["shh", "ष"], ["Sh", "ष"], ["sh", "श"],
  ["rh", "ऱ्ह"], ["lh", "ल्ह"], ["wh", "व्ह"], ["mh", "म्ह"],
  ["ld", "ळ"], ["L", "ळ"]
];

const SINGLE_CONSONANTS: Array<[string, string]> = [
  ["k", "क"], ["g", "ग"], ["j", "ज"],
  ["T", "ट"], ["t", "त"],
  ["D", "ड"], ["d", "द"],
  ["N", "ण"], ["n", "न"],
  ["p", "प"], ["b", "ब"], ["m", "म"],
  ["y", "य"], ["r", "र"], ["l", "ल"],
  ["v", "व"], ["w", "व"],
  ["s", "स"], ["h", "ह"]
];

const VOWEL_MATRAS_LIST: Array<[string, string]> = [
  ["aa", "ा"], ["A", "ा"],
  ["ee", "ी"], ["ii", "ी"], ["I", "ी"],
  ["oo", "ू"], ["uu", "ू"], ["U", "ू"],
  ["ai", "ै"], ["au", "ौ"], ["ou", "ौ"],
  ["ae", "ॅ"], ["aw", "ॉ"],
  ["e", "े"], ["E", "े"],
  ["i", "ि"], ["u", "ु"],
  ["o", "ो"], ["O", "ो"],
  ["a", ""]
];

const INDEP_VOWELS: Array<[string, string]> = [
  ["aa", "आ"], ["A", "आ"],
  ["ee", "ई"], ["ii", "ई"], ["I", "ई"],
  ["oo", "ऊ"], ["uu", "ऊ"], ["U", "ऊ"],
  ["ai", "ऐ"], ["au", "औ"], ["ou", "औ"],
  ["ae", "ॲ"], ["aw", "ऑ"],
  ["e", "ए"], ["E", "ए"],
  ["i", "इ"], ["u", "उ"],
  ["o", "ओ"], ["O", "ओ"],
  ["am", "अं"], ["an", "अं"],
  ["ah", "अः"], ["aha", "अः"],
  ["a", "अ"]
];

/**
 * Converts a Romanized phonetic token into Devanagari.
 * Preserves hyphens (e.g. "sama-kaalee-n" -> "सम-कालीन").
 */
export function romanToDevanagari(roman: string): string {
  if (!roman) return "";

  // Split by hyphen to preserve exact user syllable structure
  const segments = roman.split("-");
  const convertedSegments: string[] = [];

  for (let sIdx = 0; sIdx < segments.length; sIdx++) {
    const rawSeg = segments[sIdx].trim();
    if (!rawSeg) {
      convertedSegments.push("");
      continue;
    }

    // Special single-letter consonant segment like "-n" at end of "sama-kaalee-n"
    if (rawSeg.toLowerCase() === "n" && sIdx > 0) {
      // If previous segment ended with vowel matra, attach directly
      if (convertedSegments.length > 0 && IS_VOWEL_MATRA_REGEX.test(convertedSegments[convertedSegments.length - 1].slice(-1))) {
        convertedSegments[convertedSegments.length - 1] += "न";
        continue;
      }
      convertedSegments.push("न");
      continue;
    }
    if (rawSeg.toLowerCase() === "m" && sIdx > 0) {
      if (convertedSegments.length > 0 && IS_VOWEL_MATRA_REGEX.test(convertedSegments[convertedSegments.length - 1].slice(-1))) {
        convertedSegments[convertedSegments.length - 1] += "म";
        continue;
      }
      convertedSegments.push("म");
      continue;
    }

    convertedSegments.push(convertSegmentToDevanagari(rawSeg));
  }

  return convertedSegments.filter((s, idx) => s !== "" || idx === 0).join("-");
}

function convertSegmentToDevanagari(input: string): string {
  let str = input.trim();
  if (!str) return "";

  const lower = str.toLowerCase();
  if (SPECIAL_PHONETIC_WORDS[lower]) {
    return SPECIAL_PHONETIC_WORDS[lower];
  }

  let result = "";
  let i = 0;

  while (i < str.length) {
    const remaining = str.slice(i);

    // Check for 'ng' -> 'ंग' (e.g. rang -> रंग)
    if (remaining.toLowerCase().startsWith("ng") && (i === str.length - 2 || !/[aeiou]/i.test(str[i+2]))) {
      result += "ंग";
      i += 2;
      continue;
    }

    // Check for Anusvara: 'am' or 'an' before consonant or at end of syllable
    if (i > 0 && (remaining.startsWith("m") || remaining.startsWith("n"))) {
      const nextChar = remaining.length > 1 ? remaining[1] : "";
      if (
        nextChar === "" ||
        (!["a", "e", "i", "o", "u"].includes(nextChar.toLowerCase()) && nextChar !== "h")
      ) {
        if (remaining.length === 1) {
          result += remaining === "n" ? "न" : "म";
          i += 1;
          continue;
        }
      }
    }

    // Independent Vowels at segment start
    if (i === 0 || result.endsWith(" ") || result.endsWith("-")) {
      let matchedVowel = false;
      for (const [rom, indep] of INDEP_VOWELS) {
        if (remaining.toLowerCase().startsWith(rom)) {
          result += indep;
          i += rom.length;
          matchedVowel = true;
          break;
        }
      }
      if (matchedVowel) continue;
    }

    // Consonants
    let matchedConsonant: string | null = null;
    let consLen = 0;

    // Check retroflex L / ld specifically (case-sensitive)
    if (remaining.startsWith("ld") || remaining.startsWith("Ld")) {
      matchedConsonant = "ळ";
      consLen = 2;
    } else if (remaining.startsWith("L")) {
      matchedConsonant = "ळ";
      consLen = 1;
    } else {
      for (const [rom, deva] of MULTI_CONSONANTS) {
        if (rom === "L" || rom === "ld") continue;
        if (remaining.toLowerCase().startsWith(rom.toLowerCase())) {
          matchedConsonant = deva;
          consLen = rom.length;
          break;
        }
      }
    }

    if (!matchedConsonant) {
      for (const [rom, deva] of SINGLE_CONSONANTS) {
        if (remaining.startsWith(rom) || remaining.toLowerCase().startsWith(rom)) {
          // If word is 'nat', 't' in 'nat' should be 'ट'
          if (rom === "t" && (lower.startsWith("nat") || lower.startsWith("pat") || lower.startsWith("mot"))) {
            matchedConsonant = "ट";
          } else {
            matchedConsonant = deva;
          }
          consLen = rom.length;
          break;
        }
      }
    }

    if (matchedConsonant) {
      i += consLen;
      const afterConsonant = str.slice(i);

      let matchedMatra = false;
      for (const [vRom, vMatra] of VOWEL_MATRAS_LIST) {
        if (afterConsonant.toLowerCase().startsWith(vRom)) {
          result += matchedConsonant + vMatra;
          i += vRom.length;
          matchedMatra = true;
          break;
        }
      }

      if (!matchedMatra) {
        if (i < str.length && /[a-zA-Z]/.test(str[i])) {
          result += matchedConsonant + "्";
        } else {
          result += matchedConsonant;
        }
      }
      continue;
    }

    result += str[i];
    i++;
  }

  return result;
}

/**
 * Converts a Devanagari syllable guide into clean Romanized phonetics.
 */
export function devanagariToRoman(deva: string): string {
  if (!deva) return "";

  const segments = deva.split("-");
  const romanSegments = segments.map((seg) => convertSegmentToRoman(seg));
  return romanSegments.join("-");
}

function convertSegmentToRoman(input: string): string {
  let str = input.trim();
  if (!str) return "";

  const DEVA_CONSONANTS: Record<string, string> = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh',
    'ष': 'sh', 'स': 's', 'ह': 'h', 'ळ': 'l', 'क्ष': 'ksh', 'ज्ञ': 'dny'
  };

  const DEVA_INDEP_VOWELS: Record<string, string> = {
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo',
    'ऋ': 'ru', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'ॲ': 'ae', 'ऑ': 'aw', 'अं': 'am', 'अः': 'aha'
  };

  const DEVA_MATRAS: Record<string, string> = {
    'ा': 'aa', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo',
    'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
    'ॅ': 'ae', 'ॉ': 'aw', 'ृ': 'ru'
  };

  let out = "";
  const chars = Array.from(str);

  for (let i = 0; i < chars.length; i++) {
    const c = chars[i];
    const next = i + 1 < chars.length ? chars[i + 1] : "";

    if (DEVA_INDEP_VOWELS[c]) {
      out += DEVA_INDEP_VOWELS[c];
    } else if (DEVA_CONSONANTS[c]) {
      out += DEVA_CONSONANTS[c];
      if (next === "्") {
        i++;
      } else if (DEVA_MATRAS[next]) {
        out += DEVA_MATRAS[next];
        i++;
      } else {
        if (i < chars.length - 1 && chars[i + 1] !== " " && chars[i + 1] !== "-") {
          out += "a";
        }
      }
    } else if (DEVA_MATRAS[c]) {
      out += DEVA_MATRAS[c];
    } else if (c === "ं") {
      out += "n";
    } else if (c === "ः") {
      out += "h";
    } else if (c === "्") {
      // skip
    } else {
      out += c;
    }
  }

  return out;
}
