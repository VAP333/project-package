/**
 * All mock data lives here. Replace each export with a real API call later
 * (e.g. wrap in a server function / queryOptions) — screens only consume these shapes.
 */

export type CorpusStatus = "verified" | "community" | "unverified";

export const BOOKS = [
  { id: "bal-8", title: "बालभारती — मराठी", titleEn: "Balbharati Marathi", std: "Class 8", edition: "2024", subject: "Marathi", pages: 142, read: 58 },
  { id: "itihas-8", title: "इतिहास व नागरिकशास्त्र", titleEn: "History & Civics", std: "Class 8", edition: "2023", subject: "History", pages: 96, read: 21 },
  { id: "vidnyan-8", title: "सामान्य विज्ञान", titleEn: "General Science", std: "Class 8", edition: "2024", subject: "Science", pages: 168, read: 74 },
  { id: "bhugol-8", title: "भूगोल", titleEn: "Geography", std: "Class 8", edition: "2022", subject: "Geography", pages: 88, read: 9 },
];

export const SUBJECTS = ["Marathi", "History", "Science", "Geography", "Mathematics"];
export const EDITIONS = ["2024", "2023", "2022"];

export const RECENT_PAGES: { id: string; bookId: string; page: number; title: string; status: CorpusStatus; progress: number; when: string }[] = [
  { id: "p1", bookId: "bal-8", page: 34, title: "पाठ ५ — माझी शाळा", status: "verified", progress: 100, when: "Today" },
  { id: "p2", bookId: "vidnyan-8", page: 61, title: "प्रकाशाचे परावर्तन", status: "community", progress: 72, when: "Yesterday" },
  { id: "p3", bookId: "itihas-8", page: 12, title: "स्वातंत्र्यलढा", status: "unverified", progress: 40, when: "2 days ago" },
  { id: "p4", bookId: "bal-8", page: 35, title: "पाठ ५ — (पुढे)", status: "verified", progress: 15, when: "3 days ago" },
  { id: "p5", bookId: "bhugol-8", page: 7, title: "नकाशा वाचन", status: "community", progress: 100, when: "Last week" },
];

export type Token = { text: string; flagged?: boolean };
export type Sentence = { id: number; tokens: Token[] };
export type Paragraph = { id: number; sentences: Sentence[]; tutor: string };

const s = (id: number, str: string, flagged: string[] = []): Sentence => ({
  id,
  tokens: str.split(" ").map((w) => ({ text: w, flagged: flagged.includes(w) })),
});

export const READING_PAGE = {
  book: "बालभारती — मराठी (इयत्ता आठवी)",
  bookEn: "Balbharati Marathi · Class 8 · 2024",
  page: 34,
  chapter: "पाठ ५ — माझी शाळा",
  status: "community" as CorpusStatus,
  confirmations: 3,
  paragraphs: [
    {
      id: 1,
      sentences: [
        s(1, "माझी शाळा गावाच्या टोकाला एका टेकडीवर आहे."),
        s(2, "शाळेभोवती आंबा, चिंच आणि वडाची मोठी झाडे आहेत.", ["चिंच"]),
        s(3, "सकाळी प्रार्थनेच्या वेळी सगळा परिसर शांत असतो."),
      ],
      tutor:
        "या परिच्छेदात लेखक आपल्या शाळेचे स्थान आणि निसर्गरम्य परिसर वर्णन करतो. ‘टेकडी’ म्हणजे लहान डोंगर.",
    },
    {
      id: 2,
      sentences: [
        s(4, "आमचे गुरुजी रोज नवीन गोष्ट सांगतात."),
        s(5, "त्यांच्या गोष्टींमधून आम्हाला प्रामाणिकपणा आणि परिश्रमाचे महत्त्व समजते.", ["परिश्रमाचे"]),
        s(6, "मधल्या सुट्टीत आम्ही मैदानावर कबड्डी खेळतो."),
      ],
      tutor:
        "‘परिश्रम’ म्हणजे कष्ट किंवा मेहनत. गुरुजी गोष्टींमधून मूल्ये शिकवतात, हा या भागाचा मुख्य मुद्दा आहे.",
    },
    {
      id: 3,
      sentences: [
        s(7, "शाळेचे ग्रंथालय मला सर्वात जास्त आवडते."),
        s(8, "तिथे बसून पुस्तके वाचताना वेळ कसा जातो ते कळतच नाही."),
      ],
      tutor: "लेखकाला वाचनाची आवड आहे. ‘वेळ कसा जातो ते कळत नाही’ हा वाक्प्रचार तल्लीनता दर्शवतो.",
    },
  ] as Paragraph[],
};

export const VOICE_COMMANDS = [
  { say: "वाचा / Play", does: "Start reading aloud" },
  { say: "थांबा / Pause", does: "Pause reading" },
  { say: "पुन्हा / Repeat", does: "Repeat current sentence" },
  { say: "पुढे / Next", does: "Next paragraph" },
  { say: "मागे / Back", does: "Previous paragraph" },
  { say: "हळू / Slower", does: "Decrease speed" },
  { say: "समजावून सांगा / Explain", does: "Switch to Tutor Mode" },
];

export const REVIEW_QUEUE = [
  { id: "r1", book: "सामान्य विज्ञान", page: 61, submitted: "12 min ago", confidence: 0.86, transcript: "प्रकाश एखाद्या गुळगुळीत पृष्ठभागावर पडल्यावर तो परत फिरतो, यालाच परावर्तन म्हणतात.", flagged: ["गुळगुळीत", "परावर्तन"] },
  { id: "r2", book: "इतिहास व नागरिकशास्त्र", page: 12, submitted: "40 min ago", confidence: 0.71, transcript: "१८५७ च्या उठावाला भारताचे पहिले स्वातंत्र्ययुद्ध असे म्हटले जाते.", flagged: ["उठावाला", "स्वातंत्र्ययुद्ध"] },
  { id: "r3", book: "बालभारती — मराठी", page: 88, submitted: "2 h ago", confidence: 0.93, transcript: "पावसाळ्यात डोंगरदऱ्यांतून धबधबे कोसळू लागतात.", flagged: ["डोंगरदऱ्यांतून"] },
];

export const GLOSSARY_INITIAL = [
  { id: "g1", subject: "Science", term: "परावर्तन", note: "Reflection" },
  { id: "g2", subject: "Science", term: "प्रकाशसंश्लेषण", note: "Photosynthesis" },
  { id: "g3", subject: "History", term: "स्वातंत्र्ययुद्ध", note: "War of independence" },
  { id: "g4", subject: "Marathi", term: "परिश्रम", note: "Hard work" },
  { id: "g5", subject: "Geography", term: "अक्षांश", note: "Latitude" },
];

export const METRICS = {
  pagesProcessed: 18432,
  pagesDelta: "+6.2%",
  coverage: 64,
  correctionAccuracy: 97.8,
  unresolvedRate: 1.9,
  trend: [
    { week: "W1", cer: 4.8, wer: 11.2, unresolved: 3.4, pages: 1100 },
    { week: "W2", cer: 4.3, wer: 10.1, unresolved: 3.1, pages: 1240 },
    { week: "W3", cer: 3.9, wer: 9.4, unresolved: 2.8, pages: 1380 },
    { week: "W4", cer: 3.6, wer: 8.7, unresolved: 2.5, pages: 1450 },
    { week: "W5", cer: 3.2, wer: 7.9, unresolved: 2.3, pages: 1590 },
    { week: "W6", cer: 2.9, wer: 7.1, unresolved: 2.1, pages: 1720 },
    { week: "W7", cer: 2.7, wer: 6.6, unresolved: 1.9, pages: 1810 },
  ],
  bySubject: [
    { subject: "Marathi", coverage: 82 },
    { subject: "Science", coverage: 67 },
    { subject: "History", coverage: 58 },
    { subject: "Geography", coverage: 44 },
    { subject: "Maths", coverage: 31 },
  ],
  health: [
    { name: "OCR pipeline", ok: true, detail: "p95 1.8s" },
    { name: "Correction model", ok: true, detail: "p95 0.6s" },
    { name: "Speech synthesis", ok: true, detail: "p95 0.9s" },
    { name: "Review queue", ok: false, detail: "38 pending > 24h" },
  ],
};
