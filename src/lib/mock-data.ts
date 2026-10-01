/**
 * All mock data lives here. Replace each export with a real API call later
 * (e.g. wrap in a server function / queryOptions) — screens only consume these shapes.
 */

export type CorpusStatus = "verified" | "community" | "unverified";

export const BOOKS = [
  { id: "history-8", title: "इयत्ता आठवी — इतिहास (आधुनिक भारताचा इतिहास)", titleEn: "History (Class 8, Reference)", std: "Class 8", edition: "2018", subject: "History", pages: 75, read: 4 },
  { id: "science-8", title: "इयत्ता आठवी — सामान्य विज्ञान", titleEn: "General Science (Class 8, Reference)", std: "Class 8", edition: "2018", subject: "Science", pages: 148, read: 19 },
  { id: "akshar-10", title: "इयत्ता दहावी — अक्षरभारती (मराठी)", titleEn: "AksharBharati Marathi", std: "Class 10", edition: "2024", subject: "Marathi", pages: 90, read: 14 },
  { id: "geo-10", title: "इयत्ता दहावी — भूगोल", titleEn: "Geography", std: "Class 10", edition: "2024", subject: "Geography", pages: 82, read: 18 },
];

export const SUBJECTS = ["History", "Science", "Marathi", "Geography"];
export const EDITIONS = ["2018", "2024"];

export const HISTORY_CHAPTERS = [
  { id: "CH_01", number: 1, title: "१. इतिहासाची साधने", titleEn: "Sources of History", page: 1, pdfStart: 10, pdfEnd: 13 },
  { id: "CH_02", number: 2, title: "२. युरोप आणि भारत", titleEn: "Europe and India", page: 5, pdfStart: 14, pdfEnd: 18 },
  { id: "CH_03", number: 3, title: "३. ब्रिटिश सत्तेचे परिणाम", titleEn: "Effects of British Rule", page: 10, pdfStart: 19, pdfEnd: 23 },
  { id: "CH_04", number: 4, title: "४. १८५७ चा स्वातंत्र्यलढा", titleEn: "Freedom Struggle of 1857", page: 15, pdfStart: 24, pdfEnd: 29 },
  { id: "CH_05", number: 5, title: "५. सामाजिक व धार्मिक प्रबोधन", titleEn: "Social and Religious Awakening", page: 21, pdfStart: 30, pdfEnd: 33 },
  { id: "CH_06", number: 6, title: "६. स्वातंत्र्य चळवळीच्या युगास प्रारंभ", titleEn: "Beginning of Freedom Movement", page: 25, pdfStart: 34, pdfEnd: 39 },
  { id: "CH_07", number: 7, title: "७. असहकार चळवळ", titleEn: "Non-Cooperation Movement", page: 31, pdfStart: 40, pdfEnd: 44 },
  { id: "CH_08", number: 8, title: "८. सविनय कायदेभंग चळवळ", titleEn: "Civil Disobedience Movement", page: 36, pdfStart: 45, pdfEnd: 48 },
  { id: "CH_09", number: 9, title: "९. स्वातंत्र्यलढ्याचे अंतिम पर्व", titleEn: "Last Phase of Freedom Struggle", page: 40, pdfStart: 49, pdfEnd: 53 },
  { id: "CH_10", number: 10, title: "१०. सशस्त्र क्रांतिकारी चळवळ", titleEn: "Armed Revolutionary Movement", page: 45, pdfStart: 54, pdfEnd: 58 },
  { id: "CH_11", number: 11, title: "११. समतेचा लढा", titleEn: "Struggle for Equality", page: 50, pdfStart: 59, pdfEnd: 64 },
  { id: "CH_12", number: 12, title: "१२. स्वातंत्र्यप्राप्ती", titleEn: "Attainment of Independence", page: 56, pdfStart: 65, pdfEnd: 67 },
  { id: "CH_13", number: 13, title: "१३. स्वातंत्र्यलढ्याची परिपूर्ती", titleEn: "Fulfillment of Struggle", page: 59, pdfStart: 68, pdfEnd: 70 },
  { id: "CH_14", number: 14, title: "१४. महाराष्ट्र राज्याची निर्मिती", titleEn: "Formation of Maharashtra State", page: 62, pdfStart: 71, pdfEnd: 74 },
];

export const SCIENCE_CHAPTERS = [
  { id: "CH_01", number: 1, title: "१. सजीव सृष्टी व सूक्ष्मजीवांचे वर्गीकरण", titleEn: "Living World & Microbes", page: 1, pdfStart: 11, pdfEnd: 15 },
  { id: "CH_02", number: 2, title: "२. आरोग्य व रोग", titleEn: "Health & Disease", page: 6, pdfStart: 16, pdfEnd: 23 },
  { id: "CH_03", number: 3, title: "३. बल व दाब", titleEn: "Force & Pressure", page: 14, pdfStart: 24, pdfEnd: 32 },
  { id: "CH_04", number: 4, title: "४. धाराविद्युत आणि चुंबकत्व", titleEn: "Current Electricity & Magnetism", page: 23, pdfStart: 33, pdfEnd: 37 },
  { id: "CH_05", number: 5, title: "५. अणूचे अंतरंग", titleEn: "Inside the Atom", page: 28, pdfStart: 38, pdfEnd: 48 },
  { id: "CH_06", number: 6, title: "६. द्रव्याचे संघटन", titleEn: "Composition of Matter", page: 39, pdfStart: 49, pdfEnd: 58 },
  { id: "CH_07", number: 7, title: "७. धातू-अधातू", titleEn: "Metals & Non-metals", page: 49, pdfStart: 59, pdfEnd: 63 },
  { id: "CH_08", number: 8, title: "८. प्रदूषण", titleEn: "Pollution", page: 54, pdfStart: 64, pdfEnd: 71 },
  { id: "CH_09", number: 9, title: "९. आपत्ती व्यवस्थापन", titleEn: "Disaster Management", page: 62, pdfStart: 72, pdfEnd: 76 },
  { id: "CH_10", number: 10, title: "१०. पेशी व पेशीअंगके", titleEn: "Cell & Cell Organelles", page: 67, pdfStart: 77, pdfEnd: 84 },
  { id: "CH_11", number: 11, title: "११. मानवी शरीर व इंद्रिय संस्था", titleEn: "Human Body & Organ Systems", page: 75, pdfStart: 85, pdfEnd: 92 },
  { id: "CH_12", number: 12, title: "१२. आम्ल, आम्लारी ओळख", titleEn: "Introduction to Acid & Base", page: 83, pdfStart: 93, pdfEnd: 98 },
  { id: "CH_13", number: 13, title: "१३. रासायनिक बदल व रासायनिक बंध", titleEn: "Chemical Change & Chemical Bond", page: 89, pdfStart: 99, pdfEnd: 104 },
  { id: "CH_14", number: 14, title: "१४. उष्णतेचे मापन व परिणाम", titleEn: "Measurement & Effects of Heat", page: 95, pdfStart: 105, pdfEnd: 113 },
  { id: "CH_15", number: 15, title: "१५. ध्वनी", titleEn: "Sound", page: 104, pdfStart: 114, pdfEnd: 119 },
  { id: "CH_16", number: 16, title: "१६. प्रकाशाचे परावर्तन", titleEn: "Reflection of Light", page: 110, pdfStart: 120, pdfEnd: 125 },
  { id: "CH_17", number: 17, title: "१७. मानवनिर्मित पदार्थ", titleEn: "Man-made Materials", page: 116, pdfStart: 126, pdfEnd: 131 },
  { id: "CH_18", number: 18, title: "१८. परिसंस्था", titleEn: "Ecosystems", page: 122, pdfStart: 132, pdfEnd: 138 },
  { id: "CH_19", number: 19, title: "१९. ताऱ्यांची जीवनयात्रा", titleEn: "Life Cycle of Stars", page: 129, pdfStart: 139, pdfEnd: 144 },
];

export const RECENT_PAGES: { id: string; bookId: string; page: number; chapterId: string; title: string; status: CorpusStatus; progress: number; when: string }[] = [
  { id: "p0", bookId: "history-8", page: 1, chapterId: "CH_01", title: "१. इतिहासाची साधने (Sources of History)", status: "verified", progress: 25, when: "Just now" },
  { id: "p1", bookId: "akshar-10", page: 1, chapterId: "ch_1", title: "१. तू बुद्धी दे (प्रार्थना) — गुरू ठाकूर", status: "verified", progress: 100, when: "Today" },
  { id: "p2", bookId: "geo-10", page: 1, chapterId: "ch_1", title: "१. क्षेत्रभेट (Field Visit)", status: "verified", progress: 85, when: "Today" },
  { id: "p3", bookId: "geo-10", page: 9, chapterId: "ch_2", title: "२. स्थान-विस्तार (Location & Extent)", status: "verified", progress: 60, when: "Yesterday" },
];

export type Token = { text: string; flagged?: boolean };
export type Sentence = { id: number; tokens: Token[] };
export type Paragraph = {
  id: number;
  sentences: Sentence[];
  tutor: string;
  pdfPage?: number;
  printedPage?: number;
  blockType?: string;
};

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

export const HISTORY_CH1_READING_PAGE = {
  book: "इतिहास व नागरिकशास्त्र (इयत्ता आठवी)",
  bookEn: "History and Civics · Class 8 · Reference Textbook",
  page: 1,
  pdfPage: 10,
  chapter: "१. इतिहासाची साधने",
  status: "verified" as CorpusStatus,
  confirmations: 5,
  paragraphs: [
    // --- PAGE 1 (PDF 10 / Printed 1) ---
    {
      id: 1,
      pdfPage: 10,
      printedPage: 1,
      blockType: "heading",
      sentences: [
        s(1, "१. इतिहासाची साधने"),
      ],
      tutor: "हा पहिल्या पाठाचा मुख्य शीर्षक आहे — आधुनिक भारताच्या इतिहासाची विविध साधने.",
    },
    {
      id: 2,
      pdfPage: 10,
      printedPage: 1,
      sentences: [
        s(2, "प्राचीन व मध्ययुगीन भारताच्या इतिहासाच्या साधनांचा अभ्यास आपण केलेला आहे."),
        s(3, "यावर्षी आपण आधुनिक भारताच्या इतिहासाच्या साधनांचा अभ्यास करणार आहोत."),
        s(4, "इतिहासाच्या साधनांमध्ये भौतिक, लिखित आणि मौखिक साधनांचा समावेश होतो.", ["भौतिक", "मौखिक"]),
        s(5, "त्याचप्रमाणे आधुनिक तंत्रज्ञानावर आधारित दृक्‌, श्राव्य आणि दृक्‌-श्राव्य अशा साधनांचाही समावेश होतो.", ["दृक्-श्राव्य"]),
      ],
      tutor: "इतिहासकारांना भूतकाळाची माहिती मिळवण्यासाठी साधनांची गरज असते. आधुनिक काळात छायाचित्रे आणि चित्रफिती यांसारखी आधुनिक साधनेही उपलब्ध झाली.",
    },
    {
      id: 3,
      pdfPage: 10,
      printedPage: 1,
      sentences: [
        s(6, "भौतिक साधने : इतिहासाच्या भौतिक साधनांमध्ये विविध वस्तू, वास्तू, नाणी, पुतळे आणि पदके इत्यादी साधनांचा समावेश करता येईल.", ["वास्तू", "नाणी", "पदके"]),
        s(7, "इमारती व वास्तू : आधुनिक भारताच्या इतिहासातील कालखंड हा युरोपीय विशेषतः ब्रिटिश सत्ताधीश आणि संस्थानिकांच्या राज्यकारभाराचा काळ मानला जातो.", ["संस्थानिकांच्या"]),
        s(8, "या काळात विविध इमारती, पूल, रस्ते, पाणपोया, कारंजे यांसारख्या वास्तू बांधल्या गेल्या.", ["कारंजे"]),
      ],
      tutor: "इमारती, स्मारके आणि पुतळे यांवरून तत्कालीन राज्यकर्ते आणि समाजजीवनाची कल्पना येते. उदाहरणार्थ, आगाखान पॅलेस.",
    },
    {
      id: 4,
      pdfPage: 10,
      printedPage: 1,
      sentences: [
        s(9, "या वास्तूंपैकी अनेक इमारती आज सुस्थितीत पाहावयास मिळतात. काही वास्तू या राष्ट्रीय स्मारके म्हणून घोषित केलेल्या आहेत, तर काही इमारतींमध्ये संग्रहालये उभारण्यात आली."),
        s(10, "उदा., अंदमान येथील सेल्युलर जेल. या वास्तूंना भेटी दिल्यानंतर आपणांस तत्कालीन इतिहास, स्थापत्यशास्त्र आणि आर्थिक संपन्नता याविषयी माहिती मिळते.", ["स्थापत्यशास्त्र"]),
      ],
      tutor: "अंदमान येथील सेल्युलर जेलला भेट दिल्यावर स्वातंत्र्यवीर सावरकर यांच्या क्रांतिकार्याची माहिती मिळते.",
    },
    {
      id: 5,
      pdfPage: 10,
      printedPage: 1,
      sentences: [
        s(11, "पुतळे आणि स्मारके : स्वातंत्र्यपूर्व व स्वातंत्र्योत्तर काळात अनेक व्यक्तींची स्मारके पुतळ्यांच्या रूपात उभारली गेली."),
        s(12, "विविध पुतळ्यांवरून आपणांस त्या काळातील राज्यकर्ते, समाजातील प्रतिष्ठित व्यक्ती यांच्याविषयी माहिती मिळते."),
        s(13, "पुतळ्याच्या दर्शनी पाटीवर संबंधित व्यक्तीचे पूर्ण नाव, जन्म-मृत्यूची नोंद, कार्य आणि जीवनपट यांविषयी माहिती मिळते.", ["दर्शनी"]),
      ],
      tutor: "महात्मा जोतीराव फुले, लोकमान्य टिळक, डॉ. बाबासाहेब आंबेडकर यांच्या पुतळ्यांप्रमाणे विविध घटनांच्या स्मृतिप्रीत्यर्थ उभारलेली स्मारके माहिती देतात.",
    },

    // --- PAGE 2 (PDF 11 / Printed 2) ---
    {
      id: 6,
      pdfPage: 11,
      printedPage: 2,
      blockType: "heading",
      sentences: [
        s(14, "लिखित साधने (Written Sources)"),
      ],
      tutor: "आधुनिक भारताच्या इतिहासाच्या लिखित साधनांमध्ये वृत्तपत्रे, नियतकालिके, रोजनिशी, पत्रव्यवहार, अभिलेखागारातील कागदपत्रे, सरकारी गॅझेट आणि टपाल तिकिटे यांचा समावेश होतो.",
    },
    {
      id: 7,
      pdfPage: 11,
      printedPage: 2,
      sentences: [
        s(15, "वृत्तपत्रे व नियतकालिके : वृत्तपत्रांमधून आपणांस समकालीन घटनांविषयी सविस्तर माहिती मिळते.", ["नियतकालिके"]),
        s(16, "त्याचबरोबर एखाद्या घटनेचे सखोल विश्लेषण, मान्यवरांची मतमतांतरे आणि अग्रलेख प्रसिद्ध होत असतात."),
        s(17, "स्वातंत्र्यपूर्व काळात ज्ञानोदय, ज्ञानप्रकाश, केसरी, मराठा, दीनबंधू, अमृतबझार पत्रिका यांसारखी वृत्तपत्रे लोकजागृतीची महत्त्वपूर्ण साधने होती.", ["ज्ञानोदय", "केसरी", "दीनबंधू"]),
      ],
      tutor: "वृत्तपत्रे केवळ राजकीयच नव्हे तर सामाजिक प्रबोधनाची साधने म्हणूनही काम करत होती.",
    },
    {
      id: 8,
      pdfPage: 11,
      printedPage: 2,
      sentences: [
        s(18, "डॉ. बाबासाहेब आंबेडकर आणि वृत्तपत्रे : डॉ. बाबासाहेब आंबेडकरांनी १९२० च्या जानेवारी महिन्यात ‘मूकनायक’ हे पाक्षिक सुरू केले.", ["मूकनायक"]),
        s(19, "त्यानंतर त्यांनी सर्वसामान्य जनतेचे प्रबोधन व संघटन करण्यासाठी १९२७ मध्ये ‘बहिष्कृत भारत’ हे वृत्तपत्र सुरू केले.", ["बहिष्कृत"]),
        s(20, "याशिवाय ‘जनता’ व ‘प्रबुद्ध भारत’ अशी वृत्तपत्रेही त्यांनी चालवली.", ["प्रबुद्ध"]),
      ],
      tutor: "डॉ. बाबासाहेब आंबेडकरांनी समाजसुधारणा व शोषितांच्या अधिकारांसाठी वृत्तपत्रांचा प्रभावी वापर केला.",
    },
    {
      id: 9,
      pdfPage: 11,
      printedPage: 2,
      sentences: [
        s(21, "टपाल तिकिटे : टपाल तिकिटे स्वतः काही बोलत नसली, तरी इतिहासकार त्यांना बोलते करतो.", ["तिकिटे"]),
        s(22, "भारताला स्वातंत्र्य मिळाल्यापासून ते आजतागायत टपाल तिकिटांमध्ये विविध बदल घडून आलेले आहेत."),
        s(23, "तिकिटांच्या आकारांतील वैविध्य, विषयांची नाविन्यता आणि रंगसंगती यांमुळे टपाल तिकिटे बदलत्या काळाविषयी इतिहास सांगतात."),
      ],
      tutor: "टपाल खाते एखाद्या नेत्यावर, घटनेवर किंवा महोत्सवानिमित्त तिकीट काढते, तो इतिहासाचा ठेवा असतो.",
    },
    {
      id: 10,
      pdfPage: 11,
      printedPage: 2,
      sentences: [
        s(24, "नकाशे व आराखडे : नकाशे हे देखील इतिहासाचे अत्यंत महत्त्वाचे साधन मानले जाते."),
        s(25, "नकाशांवरून शहरांचे किंवा एखाद्या ठिकाणाचे बदलणारे स्वरूप अभ्यासता येते."),
        s(26, "ब्रिटिश काळात स्थापन झालेला ‘सर्व्हे ऑफ इंडिया’ हा स्वतंत्र विभाग भारताच्या विविध प्रांतांचे शास्त्रोक्त सर्वेक्षण करून नकाशे तयार करत असे.", ["सर्व्हे"]),
      ],
      tutor: "सर्व्हे ऑफ इंडियाच्या नकाशांवरून शहरांचे बदल आणि भौगोलिक रचना समजते.",
    },

    // --- PAGE 3 (PDF 12 / Printed 3) ---
    {
      id: 11,
      pdfPage: 12,
      printedPage: 3,
      sentences: [
        s(27, "मुंबई पोर्ट ट्रस्ट या विभागाकडे मुंबई बंदराचे मूळ आराखडे आहेत."),
        s(28, "हे बंदर पुढे विकसित करताना वास्तुविशारद आणि अभियंत्यांनी केलेल्या आराखड्यांवरून आपणांस मुंबईच्या नागरी विकासाची माहिती मिळते.", ["वास्तुविशारद"]),
      ],
      tutor: "मुंबईच्या नागरी विकासाचा इतिहास मुंबई पोर्ट ट्रस्टच्या आराखड्यांवरून स्पष्ट होतो.",
    },
    {
      id: 12,
      pdfPage: 12,
      printedPage: 3,
      blockType: "heading",
      sentences: [
        s(29, "मौखिक साधने : लोकगीते, स्फूर्तिगीते, पोवाडे, ओव्या, लोककथा आणि मुलाखती."),
      ],
      tutor: "मौखिक साधनांमध्ये लोकसाहित्य, पोवाडे आणि स्वातंत्र्यचळवळीतील स्फूर्तिगीतांचा समावेश होतो.",
    },
    {
      id: 13,
      pdfPage: 12,
      printedPage: 3,
      sentences: [
        s(30, "स्फूर्तिगीते : स्वातंत्र्यचळवळीच्या काळात अनेक स्फूर्तिगीतांची रचना केली गेली.", ["स्फूर्तिगीतांची"]),
        s(31, "या स्फूर्तिगीतांमधून आपल्याला स्वातंत्र्यपूर्व काळातील परिस्थिती आणि स्वातंत्र्य आंदोलनामागील प्रेरणा यांविषयी माहिती मिळते."),
        s(32, "पोवाडे : पोवाड्यांमधून ऐतिहासिक घटनांची तसेच व्यक्तींच्या शौर्याची माहिती मिळते.", ["पोवाड्यांमधून"]),
      ],
      tutor: "१८५७ चा स्वातंत्र्यलढा आणि सत्यशोधक समाजाने केलेली जनजागृती यांवर अनेक पोवाडे रचले गेले.",
    },
    {
      id: 14,
      pdfPage: 12,
      printedPage: 3,
      sentences: [
        s(33, "दृक्‌, श्राव्य आणि दृक्‌-श्राव्य साधने : आधुनिक काळात छायाचित्रण, ध्वनिमुद्रण आणि चित्रपट या कलांचा विकास झाला.", ["ध्वनिमुद्रण"]),
        s(34, "छायाचित्रे ही दृक् स्वरूपाची, तर ध्वनिमुद्रिते (रेकॉर्ड्स) ही श्राव्य स्वरूपाची साधने आहेत."),
        s(35, "रवींद्रनाथ टागोरांनी गायलेले ‘जन गण मन’ हे राष्ट्रगीत किंवा सुभाषचंद्र बोस यांची भाषणे श्राव्य साधने म्हणून उपयुक्त आहेत.", ["राष्ट्रगीत"]),
      ],
      tutor: "ऐतिहासिक नेत्यांची भाषणे आणि मूळ ध्वनी रेकॉर्डिंग्ज आपल्याला इतिहासाचा प्रत्यक्ष अनुभव देतात.",
    },

    // --- PAGE 4 (PDF 13 / Printed 4) ---
    {
      id: 15,
      pdfPage: 13,
      printedPage: 4,
      blockType: "heading",
      sentences: [
        s(36, "चित्रपट आणि ऐतिहासिक साधनांचे जतन"),
      ],
      tutor: "चित्रपट हा विसाव्या शतकातील आधुनिक तंत्रज्ञानाचा आगळा आविष्कार आहे.",
    },
    {
      id: 16,
      pdfPage: 13,
      printedPage: 4,
      sentences: [
        s(37, "दादासाहेब फाळकेंनी इ.स. १९१३ मध्ये भारतीय चित्रपटसृष्टीची मुहूर्तमेढ रोवली.", ["मुहूर्तमेढ"]),
        s(38, "दांडी यात्रा, मिठाचा सत्याग्रह, चलेजाव आंदोलन यांसारख्या ऐतिहासिक प्रसंगांच्या ध्वनी चित्रफिती उपलब्ध आहेत.", ["चित्रफिती"]),
        s(39, "या चित्रफितींमुळे घडलेली ऐतिहासिक घटना आपल्याला जशीच्या तशी प्रत्यक्ष पाहायला मिळते."),
      ],
      tutor: "दादासाहेब फाळके यांना भारतीय चित्रपटसृष्टीचे जनक मानले जाते.",
    },
    {
      id: 17,
      pdfPage: 13,
      printedPage: 4,
      sentences: [
        s(40, "ऐतिहासिक साधनांचे जतन केल्यामुळे इतिहासाचा हा समृद्ध वारसा आपल्याला भावी पिढ्यांकडे सोपवता येईल."),
        s(41, "अभिलेखगारात ठेवलेली कागदपत्रे आणि संग्रहालयातील भौतिक वस्तू योग्य काळजीपूर्वक जतन करणे आवश्यक आहे.", ["अभिलेखगारात"]),
      ],
      tutor: "इतिहासाचा वारसा जतन करणे हे प्रत्येक नागरिकाचे कर्तव्य आहे.",
    },
    {
      id: 18,
      pdfPage: 13,
      printedPage: 4,
      blockType: "heading",
      sentences: [
        s(42, "स्वाध्याय : सराव व मूल्यमापन प्रश्न"),
      ],
      tutor: "प्रकरण १ वरील महत्त्वाचे प्रश्न सोडवून आपल्या ज्ञानाची चाचणी घ्या.",
    },
  ] as Paragraph[],
};

export const SCIENCE_CH1_READING_PAGE = {
  book: "सामान्य विज्ञान (इयत्ता आठवी)",
  bookEn: "General Science · Class 8 · Reference Textbook",
  page: 1,
  pdfPage: 11,
  chapter: "१. सजीव सृष्टी व सूक्ष्मजीवांचे वर्गीकरण",
  status: "verified" as CorpusStatus,
  confirmations: 5,
  paragraphs: [
    // --- PAGE 1 (PDF 11 / Printed 1) ---
    {
      id: 1,
      pdfPage: 11,
      printedPage: 1,
      blockType: "heading",
      sentences: [
        s(1, "१. सजीव सृष्टी व सूक्ष्मजीवांचे वर्गीकरण"),
      ],
      tutor: "हा विज्ञानाच्या पहिल्या पाठाचा मुख्य शीर्षक आहे — सजीव सृष्टी आणि सूक्ष्मजीवांचे वैज्ञानिक वर्गीकरण.",
    },
    {
      id: 2,
      pdfPage: 11,
      printedPage: 1,
      blockType: "boxed_fact",
      sentences: [
        s(2, "थोडे आठवा : १. सजीवांच्या वर्गीकरणाचा पदानुक्रम कोणता आहे?", ["पदानुक्रम"]),
        s(3, "२. सजीवांना नाव देण्याची ‘द्विनाम पद्धती’ कोणी शोधली?", ["द्विनाम"]),
        s(4, "३. द्विनाम पद्धतीने नाव लिहिताना कोणते पदानुक्रम विचारात घेतले जातात?"),
      ],
      tutor: "कार्ल लिनिअस यांनी द्विनाम पद्धती शोधली. यात प्रजाती (Genus) आणि जाती (Species) हे दोन घटक महत्त्वाचे असतात.",
    },
    {
      id: 3,
      pdfPage: 11,
      printedPage: 1,
      blockType: "heading",
      sentences: [
        s(5, "जैवविविधता व वर्गीकरणाची आवश्यकता (Biodiversity and need of classification)"),
      ],
      tutor: "पृथ्वीवरील कोट्यवधी सजीवांचा पद्धतशीर अभ्यास करण्यासाठी वर्गीकरण करणे अत्यावश्यक ठरले.",
    },
    {
      id: 4,
      pdfPage: 11,
      printedPage: 1,
      sentences: [
        s(6, "मागील इयत्तेत आपण पाहिले की भौगोलिक प्रदेश, अन्नग्रहण, संरक्षण अशा विविध कारणांनी पृथ्वीवरील सजीवांत अनुकूलन झालेले आढळते.", ["अनुकूलन"]),
        s(7, "अनुकूलन साधताना एकाच जातीच्या सजीवांतही विविध बदल झालेले दिसतात."),
        s(8, "२०११ च्या गणनेनुसार पृथ्वीवरील जमीन व समुद्र यांमधील सर्व सजीव मिळून सुमारे ८७ दशलक्ष जाती ज्ञात आहेत.", ["दशलक्ष"]),
        s(9, "एवढ्या प्रचंड संख्येने असणाऱ्या सजीवांचा अभ्यास करण्यासाठी त्यांची गटांत विभागणी व्हायला हवी, अशी गरज भासली."),
        s(10, "सजीवांतील साम्य व फरक लक्षात घेऊन त्यांचे गट व उपगट करण्यात आले."),
        s(11, "सजीवांचे गट व उपगट बनविण्याच्या या प्रक्रियेला जैविक वर्गीकरण म्हणतात.", ["जैविक"]),
      ],
      tutor: "जैविक वर्गीकरण म्हणजे सजीवांतील साम्य आणि भेद यांच्या आधारे गट आणि उपगट तयार करण्याची शास्त्रीय पद्धत.",
    },
    {
      id: 5,
      pdfPage: 11,
      printedPage: 1,
      sentences: [
        s(12, "रॉबर्ट हार्डींग व्हिटाकर (१९२०-१९८०) हे अमेरिकन परिस्थितीकी तज्ज्ञ (Ecologist) होऊन गेले.", ["व्हिटाकर", "परिस्थितीकी"]),
        s(13, "त्यांनी इ.स. १९६९ मध्ये सजीवांची ५ गटांत विभागणी केली."),
      ],
      tutor: "रॉबर्ट व्हिटाकर यांनी मांडलेली पंचसृष्टी वर्गीकरण पद्धती आज संपूर्ण जगभरात आधारभूत मानली जाते.",
    },
    {
      id: 6,
      pdfPage: 11,
      printedPage: 1,
      blockType: "boxed_fact",
      sentences: [
        s(14, "इतिहासात डोकावताना : इ.स. १७३५ मध्ये कार्ल लिनिअस यांनी सजीवांना २ सृष्टीत विभागले - वनस्पती व प्राणी.", ["लिनिअस"]),
        s(15, "इ.स. १८६६ साली हेकेल यांनी ३ सृष्टी कल्पिल्या त्या म्हणजे प्रोटिस्टा, वनस्पती व प्राणी.", ["हेकेल", "प्रोटिस्टा"]),
        s(16, "इ.स. १९२५ मध्ये चॅटन यांनी पुन्हा सजीवांचे दोनच गट केले - आदिकेंद्रकी व दृश्यकेंद्रकी.", ["चॅटन", "आदिकेंद्रकी", "दृश्यकेंद्रकी"]),
        s(17, "इ.स. १९३८ मध्ये कोपलँड यांनी सजीवांना ४ सृष्टीमध्ये विभागले - मोनेरा, प्रोटिस्टा, वनस्पती व प्राणी.", ["कोपलँड", "मोनेरा"]),
      ],
      tutor: "वर्गीकरण शास्त्राचा ऐतिहासिक प्रवास लिनिअस यांच्या दोन सृष्टींपासून सुरू होऊन व्हिटाकर यांच्या पाच सृष्टींपर्यंत विकसित झाला.",
    },

    // --- PAGE 2 (PDF 12 / Printed 2) ---
    {
      id: 7,
      pdfPage: 12,
      printedPage: 2,
      blockType: "heading",
      sentences: [
        s(18, "व्हिटाकर यांच्या पंचसृष्टी वर्गीकरणाचे निकष"),
      ],
      tutor: "व्हिटाकर यांनी पेशी रचना, सजीवांचा प्रकार, पोषण पद्धती, जीवनशैली आणि वर्गानुवंशिक संबंध या पाच निकषांचा वापर केला.",
    },
    {
      id: 8,
      pdfPage: 12,
      printedPage: 2,
      sentences: [
        s(19, "१. पेशीची जटिलता : आदिकेंद्रकी व दृश्यकेंद्रकी पेशी.", ["जटिलता"]),
        s(20, "२. सजीवांचा प्रकार : एकपेशीय किंवा बहुपेशीय सजीव."),
        s(21, "३. पोषणाचा प्रकार : वनस्पती - स्वयंपोषी (प्रकाशसंश्लेषण), कवके - परपोषी (मृतावशेषातून अन्नशोषण), प्राणी - परपोषी (भक्षण).", ["स्वयंपोषी", "परपोषी"]),
        s(22, "४. जीवनपद्धती : उत्पादक - वनस्पती, भक्षक - प्राणी, विघटक - कवके.", ["विघटक"]),
        s(23, "५. वर्गानुवंशिक संबंध : आदिकेंद्रकी ते दृश्यकेंद्रकी, एकपेशीय ते बहुपेशीय.", ["वर्गानुवंशिक"]),
      ],
      tutor: "या पाच निकषांमुळे सजीवांचे परस्पर संबंध आणि त्यांची उत्क्रांती अचूक समजून घेता येते.",
    },
    {
      id: 9,
      pdfPage: 12,
      printedPage: 2,
      blockType: "activity_box",
      sentences: [
        s(24, "करून पहा : १. काचपट्टीवर दह्याचा किंवा ताकाचा अगदी लहान थेंब घ्या.", ["काचपट्टीवर"]),
        s(25, "त्यात थोडे पाणी मिसळून विरलीकरण करा. त्यावर आच्छादक काच ठेवा.", ["विरलीकरण"]),
        s(26, "संयुक्त सूक्ष्मदर्शकाखाली निरीक्षण करा. लॅक्टोबॅसिलाय हे सूक्ष्म जीवाणू हालचाल करताना दिसतील.", ["सूक्ष्मदर्शकाखाली", "लॅक्टोबॅसिलाय"]),
      ],
      tutor: "दह्यातील लॅक्टोबॅसिलाय हे जिवाणू दंडगोलाकार असतात. हे मोनेरा सृष्टीतील उपयुक्त जिवाणूंचे उत्तम उदाहरण आहे.",
    },

    // --- PAGE 3 (PDF 13 / Printed 3) ---
    {
      id: 10,
      pdfPage: 13,
      printedPage: 3,
      blockType: "heading",
      sentences: [
        s(27, "सृष्टी १: मोनेरा आणि सृष्टी २: प्रोटिस्टा चे गुणधर्म"),
      ],
      tutor: "मोनेरा आणि प्रोटिस्टा या सूक्ष्म सजीवांच्या वैशिष्ट्यपूर्ण सृष्टी आहेत.",
    },
    {
      id: 11,
      pdfPage: 13,
      printedPage: 3,
      sentences: [
        s(28, "सृष्टी १: मोनेरा - या सृष्टीतील सर्व सजीव एकपेशीय असतात. ते स्वयंपोषी किंवा परपोषी असतात.", ["मोनेरा"]),
        s(29, "हे आदिकेंद्रकी असून यांच्यात स्पष्ट केंद्रक किंवा पटलजन्य अंगके नसतात.", ["पटलजन्य"]),
        s(30, "सृष्टी २: प्रोटिस्टा - प्रोटिस्टा सृष्टीतील सजीव एकपेशीय असून पेशीत पटलवेष्टित केंद्रक असते.", ["प्रोटिस्टा", "पटलवेष्टित"]),
        s(31, "प्रचलनासाठी प्रवर्ध किंवा रोमके किंवा कशाभिका असतात. उदाहरणार्थ, अमिबा आणि पॅरामेशियम.", ["प्रचलनासाठी", "कशाभिका"]),
      ],
      tutor: "मोनेरा आदिकेंद्रकी असतात तर प्रोटिस्टा दृश्यकेंद्रकी असतात, हा या दोघांमधील मूलभूत फरक आहे.",
    },

    // --- PAGE 4 (PDF 14 / Printed 4) ---
    {
      id: 12,
      pdfPage: 14,
      printedPage: 4,
      blockType: "heading",
      sentences: [
        s(32, "सृष्टी ३: कवके (Fungi) आणि सूक्ष्मजीवांचे वर्गीकरण"),
      ],
      tutor: "कवके ही परपोषी, असंश्लेषी आणि दृश्यकेंद्रकी सजीवांची सृष्टी आहे.",
    },
    {
      id: 13,
      pdfPage: 14,
      printedPage: 4,
      sentences: [
        s(33, "कवक सृष्टीत परपोषी, असंश्लेषी व दृश्यकेंद्रकी सजीवांचा समावेश होतो.", ["असंश्लेषी"]),
        s(34, "बहुसंख्य कवके मृतोपजीवी असतात. कुजलेल्या सेंद्रिय पदार्थांवर ती जगतात.", ["मृतोपजीवी", "सेंद्रिय"]),
        s(35, "कवकांची पेशीभित्तिका ‘कायटीन’ नावाच्या गुंतागुंतीच्या शर्करेपासून बनलेली असते.", ["पेशीभित्तिका", "कायटीन"]),
        s(36, "सूक्ष्मजीवांचे आकार मायक्रोमीटर (μm) आणि नॅनोमीटर (nm) मध्ये मोजले जातात.", ["मायक्रोमीटर", "नॅनोमीटर"]),
      ],
      tutor: "बुरशी, यीस्ट आणि भूछत्र (मशरूम) ही कवकांची परिचित उदाहरणे आहेत. त्यांची पेशीभित्तिका कायटीनने बनलेली असते.",
    },

    // --- PAGE 5 (PDF 15 / Printed 5 - स्वाध्याय) ---
    {
      id: 14,
      pdfPage: 15,
      printedPage: 5,
      blockType: "boxed_fact",
      sentences: [
        s(37, "माहीत आहे का तुम्हांला? वनस्पती व प्राणी यांच्यातील विषाणू :", ["विषाणू"]),
        s(38, "मानव - पोलिओ विषाणू, इन्फ्लुएंझा विषाणू, HIV-एड्स विषाणू इत्यादी."),
        s(39, "गुरे - पिकोर्ना विषाणू (Picorna virus)."),
        s(40, "वनस्पती - टोमॅटो विल्ट विषाणू, तंबाखू मोझाईक विषाणू इत्यादी."),
        s(41, "जीवाणू - बॅक्टेरिओफाज हे विषाणू जीवाणूंवर हल्ला करतात.", ["बॅक्टेरिओफाज"]),
      ],
      tutor: "विषाणू हे विशिष्ट यजमान पेशींनाच संसर्ग करतात — मानवातील पोलिओ, वनस्पतीतील टोमॅटो विल्ट आणि जीवाणूंना मारणारे बॅक्टेरिओफाज.",
    },
    {
      id: 15,
      pdfPage: 15,
      printedPage: 5,
      blockType: "activity_box",
      sentences: [
        s(42, "इंटरनेट माझा मित्र : विविध सूक्ष्मजीवांची चित्रे व त्यांची वैशिष्ट्ये यांबद्दल माहिती घेऊन तक्ता तयार करा."),
      ],
      tutor: "इंटरनेटवरून विविध जिवाणू, कवके आणि शैवालांची चित्रे गोळा करून त्यांचा तुलनात्मक तक्ता बनवा.",
    },
    {
      id: 16,
      pdfPage: 15,
      printedPage: 5,
      blockType: "heading",
      sentences: [
        s(43, "स्वाध्याय : सजीव सृष्टी व सूक्ष्मजीवांचे वर्गीकरण"),
      ],
      tutor: "प्रकरणाच्या शेवटी दिलेले हे स्वाध्याय प्रश्न काळजीपूर्वक सोडवा आणि तुमच्या ज्ञानाचे मूल्यमापन करा.",
    },
    {
      id: 17,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(44, "प्र. १. जीवाणू, आदिजीव, कवके, शैवाल, आदिकेंद्रकी, दृश्यकेंद्रकी, सूक्ष्मजीव यांचे वर्गीकरण व्हिटाकर पद्धतीने मांडा."),
      ],
      tutor: "व्हिटाकर यांच्या पंचसृष्टी वर्गीकरण पद्धतीनुसार सूक्ष्मजीवांचे आदिकेंद्रकी (जीवाणू) आणि दृश्यकेंद्रकी (आदिजीव, कवके, शैवाले) असे वर्गीकरण करा.",
    },
    {
      id: 18,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(45, "प्र. २. सजीव, आदिकेंद्रकी, दृश्यकेंद्रकी, बहुपेशीय, एकपेशीय, प्रोटिस्टा, प्राणी, वनस्पती, कवके यांच्या साहाय्याने पंचसृष्टी वर्गीकरण तक्ता पूर्ण करा."),
      ],
      tutor: "सजीवांपासून सुरुवात करून आदिकेंद्रकी-दृश्यकेंद्रकी, त्यानंतर एकपेशीय-बहुपेशीय आणि शेवटी पाच सृष्टींचा तक्ता पूर्ण करा.",
    },
    {
      id: 19,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(46, "प्र. ३. माझा जोडीदार शोधा : गट 'अ' - १. कवक, २. प्रोटोझुआ, ३. विषाणू, ४. शैवाल, ५. जीवाणू."),
        s(47, "गट 'ब' - अ. क्लोरेल्ला, आ. बॅक्टेरियोफेज, इ. कॅन्डिडा, ई. अमिबा, उ. आदिकेंद्रकी."),
      ],
      tutor: "जोड्या जुळवा: कवकाची जोडी कॅन्डिडाशी, प्रोटोझुआची अमिबाशी, विषाणूची बॅक्टेरियोफेजशी, शैवालाची क्लोरेल्लाशी आणि जीवाणूची आदिकेंद्रकीशी जुळते.",
    },
    {
      id: 20,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(48, "प्र. ४. दिलेली विधाने चूक की बरोबर ते लिहून त्यांचे स्पष्टीकरण लिहा :"),
        s(49, "अ. लॅक्टोबॅसिलाय हे उपद्रवी जीवाणू आहेत."),
        s(50, "आ. कवकांची पेशीभित्तिका कायटीनपासून बनलेली असते."),
        s(51, "इ. अमिबा छद्मपादाच्या साहाय्याने हालचाल करतो."),
        s(52, "ई. प्लास्मोडिअममुळे आमांश होतो."),
        s(53, "उ. टोमॅटोविल्ट हा जीवाणूजन्य रोग आहे."),
      ],
      tutor: "लॅक्टोबॅसिलाय उपयुक्त जीवाणू आहेत (म्हणून चूक). कवकांची पेशीभित्तिका कायटीनने बनलेली असते (बरोबर). अमिबा छद्मपादाने चालतो (बरोबर). प्लास्मोडिअममुळे मलेरिया होतो, आमांश एन्टामिबाने होतो (चूक). टोमॅटोविल्ट हा विषाणूजन्य रोग आहे (चूक).",
    },
    {
      id: 21,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(54, "प्र. ५. उत्तरे लिहा :"),
        s(55, "अ. व्हिटाकर वर्गीकरण पद्धतीचे फायदे सांगा."),
        s(56, "आ. विषाणूंची वैशिष्ट्ये लिहा."),
        s(57, "इ. कवकांचे पोषण कसे होते?"),
        s(58, "ई. मोनेरा या सृष्टीमध्ये कोणकोणत्या सजीवांचा समावेश होतो?"),
      ],
      tutor: "व्हिटाकर पद्धतीचे मुख्य फायदे म्हणजे सर्व सजीवांची पेशीरचना व पोषण पद्धतीनुसार अचूक विभागणी होय.",
    },
    {
      id: 22,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(59, "प्र. ६. ओळखा पाहू मी कोण?"),
        s(60, "अ. मला केंद्रक, प्रद्रव्यपटल किंवा पेशीअंगके नसतात. (उत्तर: मोनेरा / जीवाणू)"),
        s(61, "आ. मला केंद्रक, प्रद्रव्यपटल युक्त पेशीअंगके असतात. (उत्तर: प्रोटिस्टा)"),
        s(62, "इ. मी कुजलेल्या कार्बनी पदार्थांवर जगते. (उत्तर: कवक / मृतोपजीवी)"),
        s(63, "ई. माझे प्रजनन बहुधा द्विखंडनाने होते. (उत्तर: जीवाणू / अमिबा)"),
        s(64, "उ. मी माझ्यासारखी प्रतिकृती निर्माण करतो. (उत्तर: विषाणू)"),
        s(65, "ऊ. माझे शरीर निरावयवी आहे व मी हिरव्या रंगाचा आहे. (उत्तर: शैवाल)"),
      ],
      tutor: "सजीवांच्या लक्षणांवरून त्यांची योग्य सृष्टी किंवा गट ओळखण्याचा हा सराव आहे.",
    },
    {
      id: 23,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(66, "प्र. ७. अचूक आकृत्या काढून नावे द्या : अ. जिवाणूंचे विविध प्रकार, आ. पॅरामेशिअम, इ. बॅक्टेरिओफेज."),
      ],
      tutor: "जिवाणूंचे प्रकार म्हणजे गोलाणू, दंडगोलाणू, सर्पिलाकार आणि स्वल्पविरामाकृती. त्यांच्या सुबक आकृत्या काढा.",
    },
    {
      id: 24,
      pdfPage: 15,
      printedPage: 5,
      sentences: [
        s(67, "प्र. ८. आकारानुसार पुढील नावे चढत्या क्रमाने लिहा : जिवाणू, कवक, विषाणू, शैवाल."),
      ],
      tutor: "चढता क्रम (लहानाकडून मोठ्याकडे): १. विषाणू (१०-१०० nm), २. जीवाणू (१-१० μm), ३. कवक (१०-१०० μm), ४. शैवाल (१०-१०० μm / बहुपेशीय).",
    },
    {
      id: 25,
      pdfPage: 15,
      printedPage: 5,
      blockType: "activity_box",
      sentences: [
        s(68, "उपक्रम : १. इंटरनेटच्या मदतीने विविध रोगकारक जीवाणू व त्यामुळे होणारे रोग यांचा माहिती तक्ता बनवा."),
        s(69, "२. तुमच्याजवळील पॅथॉलॉजी प्रयोगशाळेस भेट द्या व तेथील तज्ज्ञांकडून सूक्ष्मजीव, त्यांच्या निरीक्षण पद्धती व विविध सूक्ष्मदर्शकांविषयी सविस्तर माहिती घ्या."),
      ],
      tutor: "हा उपक्रम प्रात्यक्षिक ज्ञानासाठी आहे. पॅथॉलॉजी लॅबमधील सूक्ष्मदर्शकाखाली सजीवांचे प्रत्यक्ष निरीक्षण करा.",
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
  { id: "r1", book: "अक्षरभारती (मराठी) १० वी", page: 1, submitted: "15 min ago", confidence: 0.94, transcript: "जाणावया दुर्बलांचे दुःख आणि वेदना तेवत्या राहो सदा रंध्रातुनी संवेदना । धमन्यातल्या रुधिरास या खलभेदनाची आस दे ।", flagged: ["रंध्रातुनी", "खलभेदनाची"] },
  { id: "r2", book: "भूगोल १० वी", page: 1, submitted: "45 min ago", confidence: 0.91, transcript: "नळदुर्ग ते अलिबाग या प्रवासात भौगोलिक भूरूपे, पर्जन्यमान आणि वनस्पतींचे प्रत्यक्ष निरीक्षण केले जाते.", flagged: ["भूरूपे", "पर्जन्यमान"] },
  { id: "r3", book: "भूगोल १० वी", page: 9, submitted: "2 h ago", confidence: 0.89, transcript: "भारत आणि ब्राझील या दोन विकसनशील देशांच्या स्थान व विस्ताराचा तुलनात्मक अभ्यास आपण करत आहोत.", flagged: ["विकसनशील", "तुलनात्मक"] },
];

export const GLOSSARY_INITIAL = [
  { id: "g1", subject: "Marathi", term: "नवचेतना", note: "नवीन उत्साह किंवा चैतन्य" },
  { id: "g2", subject: "Marathi", term: "संवेदना", note: "दुसऱ्याचे दुःख समजण्याची जाणीव" },
  { id: "g3", subject: "Marathi", term: "सारथी", note: "योग्य वाट दाखवणारा मार्गदर्शक" },
  { id: "g4", subject: "Geography", term: "क्षेत्रभेट", note: "प्रत्यक्ष ठिकाणी जाऊन केलेली भौगोलिक पाहणी" },
  { id: "g5", subject: "Geography", term: "अक्षांश-रेखांश", note: "स्थान निश्चितीसाठी वापरल्या जाणाऱ्या काल्पनिक रेषा" },
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

// ----------------- PDF Document-First Architecture Models -----------------

export type DocumentItem = {
  id: string;
  filename: string;
  filepath: string;
  title: string;
  titleEn: string;
  subject: string;
  std: string;
  edition: string;
  sizeMb: number;
  totalPages: number;
  description: string;
};

export type SectionBoundary = {
  title: string;
  type: string;
  startPdfPage: number;
};

export type ChapterMeta = {
  chapterId: string;
  number: number;
  title: string;
  marathiTitle: string;
  subject: string;
  startPdfPage: number;
  endPdfPage: number;
  printedStartPage: number;
  printedEndPage: number;
  pageCount: number;
  sections: SectionBoundary[];
  keyConcepts: string[];
};

export type PageInventoryItem = {
  pdfPageNumber: number;
  printedPageNumber: number | null;
  pageType: "cover" | "title_decree" | "copyright" | "preamble" | "preface" | "competencies" | "teacher_note" | "toc" | "chapter_content" | "appendix";
  chapterId: string | null;
  isScanned: boolean;
  blockCount: number;
  snippet: string;
  hasFigures: boolean;
  hasExercises: boolean;
};

export type DocumentStructureData = {
  documentId: string;
  filename: string;
  docHash: string;
  title: string;
  subject: string;
  std: string;
  edition: string;
  totalPages: number;
  frontMatterPagesCount: number;
  contentPagesCount: number;
  tocPdfPage: number;
  offsetToPrintedPages: number;
  chapters: ChapterMeta[];
  pageInventory: PageInventoryItem[];
};

export const REFERENCE_DOCUMENTS: DocumentItem[] = [
  {
    id: "akshar-10",
    filename: "AksharBharti-Marathi-10th-English-Medium-.pdf",
    filepath: "dataset/AksharBharti-Marathi-10th-English-Medium-.pdf",
    title: "इयत्ता दहावी — अक्षरभारती (मराठी)",
    titleEn: "AksharBharati Marathi (10th Standard)",
    subject: "Marathi",
    std: "Class 10",
    edition: "2018-24",
    sizeMb: 3.9,
    totalPages: 90,
    description: "Maharashtra State Board Class 10 Second Language Marathi textbook. Contains poems, prose, and activities."
  },
  {
    id: "geo-10",
    filename: "SSC-10th-Class-Geography-Textbook-in-Marathi.pdf",
    filepath: "dataset/SSC-10th-Class-Geography-Textbook-in-Marathi.pdf",
    title: "इयत्ता दहावी — भूगोल",
    titleEn: "Geography (10th Standard)",
    subject: "Geography",
    std: "Class 10",
    edition: "2022-23",
    sizeMb: 13.9,
    totalPages: 82,
    description: "Maharashtra State Board Class 10 Geography textbook. Features field visit, maps, graphical data, and comparative study."
  }
];

export const MARATHI_STRUCTURE: DocumentStructureData = {
  documentId: "akshar-10",
  filename: "AksharBharti-Marathi-10th-English-Medium-.pdf",
  docHash: "a4f89d10e52b86c7104b9012a67e42d991bf8031201948",
  title: "इयत्ता दहावी — अक्षरभारती (मराठी)",
  subject: "Marathi",
  std: "Class 10",
  edition: "2018-24",
  totalPages: 90,
  frontMatterPagesCount: 9,
  contentPagesCount: 81,
  tocPdfPage: 9,
  offsetToPrintedPages: 9,
  chapters: [
    {
      chapterId: "ch_1",
      number: 1,
      title: "१. तू बुद्धी दे (प्रार्थना) — गुरू ठाकूर",
      marathiTitle: "१. तू बुद्धी दे (प्रार्थना)",
      subject: "Marathi",
      startPdfPage: 10,
      endPdfPage: 10,
      printedStartPage: 1,
      printedEndPage: 1,
      pageCount: 1,
      sections: [
        { title: "प्रार्थना (Poem)", type: "poetry", startPdfPage: 10 },
        { title: "कवी परिचय व संदर्भ", type: "heading", startPdfPage: 10 },
        { title: "शब्दार्थ व टीपा (Vocabulary)", type: "definition", startPdfPage: 10 }
      ],
      keyConcepts: ["प्रार्थना", "बुद्धी", "सत्संगती", "सामर्थ्य", "नवचेतना"]
    },
    {
      chapterId: "ch_2",
      number: 2,
      title: "२. संतवाणी (अ) अंकिला मी दास तुझा — संत नामदेव",
      marathiTitle: "२. संतवाणी — अंकिला मी दास तुझा",
      subject: "Marathi",
      startPdfPage: 11,
      endPdfPage: 12,
      printedStartPage: 2,
      printedEndPage: 3,
      pageCount: 2,
      sections: [
        { title: "अभंग — अंकिला मी दास तुझा", type: "poetry", startPdfPage: 11 },
        { title: "स्वाध्याय व कृती", type: "exercise", startPdfPage: 12 }
      ],
      keyConcepts: ["अभंग", "संत नामदेव", "भक्ती", "मातृप्रेम"]
    },
    {
      chapterId: "ch_3",
      number: 3,
      title: "३. शाल — रा. ग. जाधव",
      marathiTitle: "३. शाल",
      subject: "Marathi",
      startPdfPage: 16,
      endPdfPage: 18,
      printedStartPage: 7,
      printedEndPage: 9,
      pageCount: 3,
      sections: [
        { title: "पाठाचा मुख्य भाग", type: "main_content", startPdfPage: 16 },
        { title: "स्वाध्याय", type: "exercise", startPdfPage: 18 }
      ],
      keyConcepts: ["शाल", "शालीनता", "नारायण सुर्वे", "पुलं देशपांडे"]
    }
  ],
  pageInventory: [
    { pdfPageNumber: 1, printedPageNumber: null, pageType: "cover", chapterId: null, isScanned: true, blockCount: 1, snippet: "[Cover Art / Title Canvas]", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 2, printedPageNumber: null, pageType: "title_decree", chapterId: null, isScanned: false, blockCount: 4, snippet: "मराठी इयत्ता दहावी (द्‌वितीय भाषा) शासन निर्णय क्रमांक : अभ्यास-२११६", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 3, printedPageNumber: null, pageType: "copyright", chapterId: null, isScanned: false, blockCount: 5, snippet: "प्रथमावृत्ती ः २०१८ © महाराष्ट्र राज्य पाठ्यपुस्तक निर्मिती व अभ्यासक्रम संशोधन मंडळ, पुणे", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 4, printedPageNumber: null, pageType: "preamble", chapterId: null, isScanned: false, blockCount: 3, snippet: "राष्ट्रगीत (जनगणमन अधिनायक जय हे)", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 5, printedPageNumber: null, pageType: "preamble", chapterId: null, isScanned: false, blockCount: 2, snippet: "प्रतिज्ञा (भारत माझा देश आहे. सारे भारतीय माझे बांधव आहेत.)", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 6, printedPageNumber: null, pageType: "preface", chapterId: null, isScanned: false, blockCount: 6, snippet: "प्रस्तावना : प्रिय विद्यार्थी मित्रांनो, इयत्ता दहावीचे ‘अक्षरभारती’ मराठी हे पाठ्यपुस्तक तुमच्या हाती देताना आनंद होत आहे.", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 7, printedPageNumber: null, pageType: "competencies", chapterId: null, isScanned: false, blockCount: 8, snippet: "भाषाविषयक क्षमता ः द्‌वितीय भाषा मराठी इयत्ता दहावीच्या अखेरीस विद्यार्थ्यांमध्ये पुढील क्षमता विकसित होणे अपेक्षित आहे.", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 8, printedPageNumber: null, pageType: "teacher_note", chapterId: null, isScanned: false, blockCount: 7, snippet: "शिक्षकांसाठी : मराठी अक्षरभारती (द्‌वितीय भाषा) इयत्ता दहावीचे हे पाठ्यपुस्तक अध्ययन-अध्यापनासाठी आपणांस देताना...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 9, printedPageNumber: null, pageType: "toc", chapterId: null, isScanned: false, blockCount: 12, snippet: "अनुक्रमणिका : अ. क्र. पाठ/कविता, लेखक/कवी, पृ. क्र. १. तू बुद्धी दे (प्रार्थना) - १, २. संतवाणी - २", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 10, printedPageNumber: 1, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 14, snippet: "१. तू बुद्धी दे (प्रार्थना) - तू बुद्धि दे तू तेज दे नवचेतना विश्वास दे जे सत्य सुंदर सर्वथा आजन्म त्याचा ध्यास दे...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 11, printedPageNumber: 2, pageType: "chapter_content", chapterId: "ch_2", isScanned: false, blockCount: 9, snippet: "२. संतवाणी (अ) अंकिला मी दास तुझा — संत नामदेव. अग्निमाजि पडे बाळू । माता धांवें कनवाळू ।।१।।", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 12, printedPageNumber: 3, pageType: "chapter_content", chapterId: "ch_2", isScanned: false, blockCount: 11, snippet: "(१) पाठाच्या आधारे खालील कृती केव्हा घडतात ते लिहा. (अ) माता धावून जाते... स्वाध्याय", hasFigures: false, hasExercises: true },
    { pdfPageNumber: 13, printedPageNumber: 4, pageType: "chapter_content", chapterId: "ch_2", isScanned: false, blockCount: 10, snippet: "(आ) योगी सर्वकाळ सुखदाता — संत एकनाथ. जेवीं चंद्रकिरण चकोरांसी । पांखोवा जेवीं पिलियांसी ।", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 14, printedPageNumber: 5, pageType: "chapter_content", chapterId: "ch_2", isScanned: false, blockCount: 8, snippet: "स्वाध्याय व कृती (१) खालील चौकटी पूर्ण करा. अभंगात वर्णिलेला चंद्रकिरण पिऊन जगणारा पक्षी...", hasFigures: false, hasExercises: true },
    { pdfPageNumber: 15, printedPageNumber: 6, pageType: "chapter_content", chapterId: "ch_2", isScanned: false, blockCount: 7, snippet: "आपले विचार, भावना आणि कल्पना शब्दांच्या माध्यमातून प्रभावीपणे मांडणे...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 16, printedPageNumber: 7, pageType: "chapter_content", chapterId: "ch_3", isScanned: false, blockCount: 13, snippet: "३. शाल — रा. ग. जाधव. एकदा मी पु. ल. देशपांडे यांच्याकडे काही एका निमित्ताने गेलो होतो.", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 17, printedPageNumber: 8, pageType: "chapter_content", chapterId: "ch_3", isScanned: false, blockCount: 12, snippet: "कवीवर्य नारायण सुर्वे खूप सभा, संमेलने गाजवत. पुढे ते साहित्य संमेलनाचे अध्यक्षही झाले...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 18, printedPageNumber: 9, pageType: "chapter_content", chapterId: "ch_3", isScanned: false, blockCount: 15, snippet: "स्वाध्याय : (१) आकृत्या पूर्ण करा. शालीचे विविध उपयोग. (२) लेखकाच्या मते शालीनतेचे गुण...", hasFigures: false, hasExercises: true },
    { pdfPageNumber: 19, printedPageNumber: 10, pageType: "chapter_content", chapterId: null, isScanned: false, blockCount: 10, snippet: "भाषाभ्यास : खालील वाक्यांतील नामे व सर्वनामे ओळखून लिहा.", hasFigures: false, hasExercises: true },
    { pdfPageNumber: 20, printedPageNumber: 11, pageType: "chapter_content", chapterId: null, isScanned: false, blockCount: 11, snippet: "४. उपास — पु. ल. देशपांडे. माझ्या खाजगी उपोषणाची हकीकत चाळीत जाहीर झाली...", hasFigures: false, hasExercises: false }
  ]
};

export const GEO_STRUCTURE: DocumentStructureData = {
  documentId: "geo-10",
  filename: "SSC-10th-Class-Geography-Textbook-in-Marathi.pdf",
  docHash: "f1883cb20a4597b8d0016e78912304875cbaf1093",
  title: "इयत्ता दहावी — भूगोल",
  subject: "Geography",
  std: "Class 10",
  edition: "2022-23",
  totalPages: 82,
  frontMatterPagesCount: 11,
  contentPagesCount: 71,
  tocPdfPage: 11,
  offsetToPrintedPages: 11,
  chapters: [
    {
      chapterId: "ch_1",
      number: 1,
      title: "१. क्षेत्रभेट (Field Visit)",
      marathiTitle: "१. क्षेत्रभेट",
      subject: "Geography",
      startPdfPage: 12,
      endPdfPage: 19,
      printedStartPage: 1,
      printedEndPage: 8,
      pageCount: 8,
      sections: [
        { title: "प्रस्तावना व क्षेत्रभेटीची पूर्वतयारी", type: "main_content", startPdfPage: 12 },
        { title: "नळदुर्ग ते अलिबाग प्रवास संवाद", type: "dialogue", startPdfPage: 13 },
        { title: "वनस्पती व पर्जन्यमान निरीक्षण", type: "figure_activity", startPdfPage: 15 },
        { title: "सिंहगड किल्ला व धाब्याची घरे", type: "figure_caption", startPdfPage: 16 },
        { title: "अलिबाग समुद्रकिनारा व खडक", type: "map_figure", startPdfPage: 18 },
        { title: "स्वाध्याय (Exercises & Questions)", type: "exercise", startPdfPage: 19 }
      ],
      keyConcepts: ["क्षेत्रभेट", "प्रश्नावली", "पर्जन्यमान", "वनस्पती", "धाब्यांची घरे", "खडक", "समुद्रकिनारा"]
    },
    {
      chapterId: "ch_2",
      number: 2,
      title: "२. स्थान-विस्तार (Location & Extent)",
      marathiTitle: "२. स्थान-विस्तार",
      subject: "Geography",
      startPdfPage: 20,
      endPdfPage: 25,
      printedStartPage: 9,
      printedEndPage: 14,
      pageCount: 6,
      sections: [
        { title: "भारत व ब्राझील स्थान", type: "main_content", startPdfPage: 20 },
        { title: "नकाशा वाचन व अक्षांश-रेखांश", type: "map", startPdfPage: 21 },
        { title: "ऐतिहासिक पार्श्वभूमी", type: "main_content", startPdfPage: 23 },
        { title: "स्वाध्याय", type: "exercise", startPdfPage: 25 }
      ],
      keyConcepts: ["अक्षांश", "रेखांश", "विषुववृत्त", "ब्राझील", "स्वातंत्र्योत्तर काळ"]
    }
  ],
  pageInventory: [
    { pdfPageNumber: 1, printedPageNumber: null, pageType: "cover", chapterId: null, isScanned: true, blockCount: 1, snippet: "[Cover Page: Maharashtra State Board Geography]", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 2, printedPageNumber: null, pageType: "front_matter", chapterId: null, isScanned: true, blockCount: 2, snippet: "[Preamble Art Canvas]", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 3, printedPageNumber: null, pageType: "front_matter", chapterId: null, isScanned: false, blockCount: 6, snippet: "भारत व ब्राझील मधील विविध प्राणी व वनस्पती (मकाऊ, बाभूळ, वड, बारशिंग, सुसर...)", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 4, printedPageNumber: null, pageType: "title_decree", chapterId: null, isScanned: false, blockCount: 4, snippet: "इयत्ता दहावी महाराष्ट्र राज्य पाठ्यपुस्तक निर्मिती व अभ्यासक्रम संशोधन मंडळ, पुणे.", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 5, printedPageNumber: null, pageType: "preamble", chapterId: null, isScanned: false, blockCount: 3, snippet: "राष्ट्रगीत व प्रतिज्ञा (भारत माझा देश आहे)", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 6, printedPageNumber: null, pageType: "preface", chapterId: null, isScanned: false, blockCount: 5, snippet: "प्रस्तावना : प्रिय विद्यार्थी मित्रांनो, भूगोल विषयाचे हे पाठ्यपुस्तक तुमच्या हाती देताना आनंद होतो...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 7, printedPageNumber: null, pageType: "preface", chapterId: null, isScanned: false, blockCount: 4, snippet: "भूगोलाचा अभ्यास प्रत्यक्ष निरीक्षणातून करणे अत्यंत उपयुक्त ठरते...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 8, printedPageNumber: null, pageType: "preface", chapterId: null, isScanned: false, blockCount: 5, snippet: "नकाशे, आलेखांचा वापर व भौगोलिक संकल्पनांचे स्पष्टीकरण...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 9, printedPageNumber: null, pageType: "competencies", chapterId: null, isScanned: false, blockCount: 7, snippet: "क्षमता विधाने : सामान्य भूगोल घटक १.१ स्थान व विस्तार - विशिष्ट प्रदेशाविषयीच्या संकल्पनांचे आकलन...", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 10, printedPageNumber: null, pageType: "teacher_note", chapterId: null, isScanned: false, blockCount: 6, snippet: "- शिक्षकांसाठी - पाठ्यपुस्तक प्रथम स्वतः समजून घ्यावे. शिकवण्यापूर्वी मागील इयत्तांचे संदर्भ जोडावेत.", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 11, printedPageNumber: null, pageType: "toc", chapterId: null, isScanned: false, blockCount: 14, snippet: "अनुक्रमणिका : १. क्षेत्रभेट (पृष्ठ १), २. स्थान-विस्तार (पृष्ठ ९), ३. प्राकृतिक रचना (पृष्ठ १४)", hasFigures: false, hasExercises: false },
    { pdfPageNumber: 12, printedPageNumber: 1, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 16, snippet: "१. क्षेत्रभेट : तुम्ही या क्षेत्रभेटीत सहभागी होणार असाल, तर कशी तयारी कराल? शिक्षकांनी आयोजन करायला सांगितले तर...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 13, printedPageNumber: 2, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 18, snippet: "नळदुर्ग ते अलिबाग प्रवास संवाद. राहुल: मॅडम, आता आपण नळदुर्ग सोडले असून सोलापूरच्या दिशेने निघालो आहोत...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 14, printedPageNumber: 3, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 14, snippet: "बहुउद्देशीय धरण प्रकल्प याविषयी माहिती मिळवा. पर्जन्यमानातील फरक वनस्पतीवरून कसा समजतो? धाब्यांची घरे...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 15, printedPageNumber: 4, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 17, snippet: "आकृती १.११ : सिंहगड प्रवेशद्वार. उंचावरून पाहताना खालील भूभाग कसा दिसत असेल बरे? खडकवासला धरण...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 16, printedPageNumber: 5, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 15, snippet: "सिंहगड किल्ला, सह्याद्रीची मुख्य रांग व पश्चिम घाटातील वनस्पती. सागाची झाडे व पानझडी अरण्ये...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 17, printedPageNumber: 6, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 14, snippet: "घाटमाथा ओलांडताना पर्जन्यमानात होणारा बदल. कोकणातील भातशेती व नारळी-सुपारीच्या बागा...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 18, printedPageNumber: 7, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 16, snippet: "अलिबाग समुद्रकिनारा. सागरी लाटांच्या कार्यामुळे तयार झालेले भूरूपे, वाळूचा किनारा व खडक...", hasFigures: true, hasExercises: false },
    { pdfPageNumber: 19, printedPageNumber: 8, pageType: "chapter_content", chapterId: "ch_1", isScanned: false, blockCount: 13, snippet: "स्वाध्याय : (१) क्षेत्रभेटी दरम्यान कचऱ्याचे व्यवस्थापन कसे कराल? (२) क्षेत्रभेटीसाठी उपयुक्त साहित्याची यादी तयार करा.", hasFigures: false, hasExercises: true },
    { pdfPageNumber: 20, printedPageNumber: 9, pageType: "chapter_content", chapterId: "ch_2", isScanned: false, blockCount: 14, snippet: "२. स्थान-विस्तार : भारत व ब्राझील या दोन देशांमधील भौगोलिक स्थान, अक्षांश-रेखांश व सीमांचा तुलनात्मक अभ्यास.", hasFigures: true, hasExercises: false }
  ]
};

// ----------------- Precomputed Processed Chapter 1 Results -----------------

export type ProcessedChapterOutput = {
  documentId: string;
  chapterId: string;
  chapterTitle: string;
  marathiTitle: string;
  subject: string;
  startPdfPage: number;
  endPdfPage: number;
  printedStartPage: number;
  printedEndPage: number;
  totalRegions: number;
  corpusRecordsCount: number;
  invariantValid: boolean;
  summary: string;
  physicalGraph: {
    pageId: string;
    sourceHash: string;
    readingOrder: string[];
    regions: Record<string, {
      regionId: string;
      regionType: string;
      bbox: number[];
      nativeText: string;
      readingOrderIndex: number;
      pdfPage: number;
      printedPage: number | null;
    }>;
  };
  learningGraph: {
    graphId: string;
    units: Record<string, {
      unitId: string;
      title: string;
      chapterId: string;
      keyTakeaways: string[];
      entityIds: string[];
    }>;
    entities: Record<string, {
      entityId: string;
      physicalRegionId: string;
      title: string;
      concepts: string[];
      vocabulary: { word: string; meaning: string }[];
      pedagogicalSummary: string;
    }>;
    edges: { source: string; target: string; relation: string }[];
  };
  sampleReadingParagraphs: {
    paragraphId: number;
    regionId: string;
    pdfPage: number;
    printedPage: number | null;
    regionType: string;
    text: string;
    verificationStatus: string;
  }[];
};

export const MARATHI_CH1_PROCESSED: ProcessedChapterOutput = {
  documentId: "akshar-10",
  chapterId: "ch_1",
  chapterTitle: "१. तू बुद्धी दे (प्रार्थना) — गुरू ठाकूर",
  marathiTitle: "१. तू बुद्धी दे (प्रार्थना)",
  subject: "Marathi",
  startPdfPage: 10,
  endPdfPage: 10,
  printedStartPage: 1,
  printedEndPage: 1,
  totalRegions: 12,
  corpusRecordsCount: 12,
  invariantValid: true,
  summary: "Successfully processed १. तू बुद्धी दे (प्रार्थना) — गुरू ठाकूर (Marathi): 12 physical regions extracted across PDF page 10 (printed page 1). Physical Document Graph and Learning Graph constructed and validated.",
  physicalGraph: {
    pageId: "akshar-10_ch_1",
    sourceHash: "a4f89d10e52b86c7104b9012a67e42d991bf8031201948",
    readingOrder: [
      "reg_ch_1_p10_1", "reg_ch_1_p10_2", "reg_ch_1_p10_3", "reg_ch_1_p10_4",
      "reg_ch_1_p10_5", "reg_ch_1_p10_6", "reg_ch_1_p10_7", "reg_ch_1_p10_8"
    ],
    regions: {
      "reg_ch_1_p10_1": {
        regionId: "reg_ch_1_p10_1",
        regionType: "heading",
        bbox: [54.0, 72.0, 320.0, 110.0],
        nativeText: "१. तू बुद्धी दे — गुरू ठाकूर",
        readingOrderIndex: 1,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_2": {
        regionId: "reg_ch_1_p10_2",
        regionType: "poetry",
        bbox: [54.0, 120.0, 520.0, 185.0],
        nativeText: "तू बुद्‌धि दे तू तेज दे नवचेतना विश्वास दे\nजे सत्य सुंदर सर्वथा आजन्म त्याचा ध्यास दे",
        readingOrderIndex: 2,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_3": {
        regionId: "reg_ch_1_p10_3",
        regionType: "poetry",
        bbox: [54.0, 195.0, 520.0, 260.0],
        nativeText: "हरवले आभाळ ज्यांचे हो तयांचा सोबती,\nसापडेना वाट ज्यांना हो तयांचा सारथी\nसाधना करिती तयांना नित्य तव सहवास दे",
        readingOrderIndex: 3,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_4": {
        regionId: "reg_ch_1_p10_4",
        regionType: "poetry",
        bbox: [54.0, 270.0, 520.0, 335.0],
        nativeText: "जाणावया दुर्बलांचे दुःख आणि वेदना\nतेवत्या राहो सदा रंध्रातुनी संवेदना\nधमन्यातल्या रुधिरास या खलभेदनाची आस दे",
        readingOrderIndex: 4,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_5": {
        regionId: "reg_ch_1_p10_5",
        regionType: "poetry",
        bbox: [54.0, 345.0, 520.0, 410.0],
        nativeText: "सन्मार्ग आणि सन्मती लाभो सदा सत्संगती\nनीती ना ही भ्रष्ट हो जरी संकटे आली किती\nपंखास या बळ दे नवे झेप घेण्यास आकाश दे",
        readingOrderIndex: 5,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_6": {
        regionId: "reg_ch_1_p10_6",
        regionType: "paragraph",
        bbox: [54.0, 430.0, 520.0, 480.0],
        nativeText: "प्रस्तुत प्रार्थना ही काव्यानंदासाठी घेतली असून ती विद्यार्थ्यांकडून तालासुरांत म्हणून घ्यावी.",
        readingOrderIndex: 6,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_7": {
        regionId: "reg_ch_1_p10_7",
        regionType: "definition",
        bbox: [54.0, 500.0, 520.0, 560.0],
        nativeText: "शब्दार्थ : नवचेतना - नवचैतन्य. सर्वथा - सदैव, सर्व अर्थांनी. आजन्म - जन्मभर. सारथी - मार्गदर्शक. रंध्र - छिद्र, त्वचा. खलभेदनाची - दुष्टांचा नाश करण्याची.",
        readingOrderIndex: 7,
        pdfPage: 10,
        printedPage: 1
      },
      "reg_ch_1_p10_8": {
        regionId: "reg_ch_1_p10_8",
        regionType: "paragraph",
        bbox: [54.0, 580.0, 520.0, 680.0],
        nativeText: "गुरू ठाकूर (१९६८) : प्रसिद्ध कवी, गीतकार, स्तंभलेखक, नाटककार, कथा, पटकथा आणि संवादलेखक. 'नटरंग', 'अगं बाई अरेच्चा' इत्यादी चित्रपटांचे गीतलेखन. प्रस्तुत प्रार्थनेत सन्मार्ग, सन्मती आणि सत्संगती यांचे महत्त्व कवीने अधोरेखित केले आहे.",
        readingOrderIndex: 8,
        pdfPage: 10,
        printedPage: 1
      }
    }
  },
  learningGraph: {
    graphId: "lg_akshar-10_ch_1",
    units: {
      "unit_ch_1_main": {
        unitId: "unit_ch_1_main",
        title: "१. तू बुद्धी दे (प्रार्थना) — गुरू ठाकूर",
        chapterId: "ch_1",
        keyTakeaways: ["प्रार्थना", "बुद्धी", "सत्संगती", "सामर्थ्य", "नवचेतना"],
        entityIds: ["ent_reg_ch_1_p10_1", "ent_reg_ch_1_p10_2", "ent_reg_ch_1_p10_3", "ent_reg_ch_1_p10_4", "ent_reg_ch_1_p10_5", "ent_reg_ch_1_p10_6", "ent_reg_ch_1_p10_8"]
      },
      "unit_ch_1_vocab": {
        unitId: "unit_ch_1_vocab",
        title: "शब्दार्थ व संकल्पना (Vocabulary & Concepts)",
        chapterId: "ch_1",
        keyTakeaways: ["नवीन शब्दांचे अर्थ", "भाषिक क्षमता"],
        entityIds: ["ent_reg_ch_1_p10_7"]
      }
    },
    entities: {
      "ent_reg_ch_1_p10_2": {
        entityId: "ent_reg_ch_1_p10_2",
        physicalRegionId: "reg_ch_1_p10_2",
        title: "Entity reg_ch_1_p10_2 (poetry)",
        concepts: ["बुद्धी", "नवचेतना", "सत्य"],
        vocabulary: [],
        pedagogicalSummary: "कवी ईश्वराकडे बुद्धी, तेज, आणि नवीन चेतनेची प्रार्थना करतो. जे सत्य आणि सुंदर आहे त्याचा अखंड ध्यास लागावा अशी मागणी केली आहे."
      },
      "ent_reg_ch_1_p10_3": {
        entityId: "ent_reg_ch_1_p10_3",
        physicalRegionId: "reg_ch_1_p10_3",
        title: "Entity reg_ch_1_p10_3 (poetry)",
        concepts: ["अनाथ", "सारथी", "साधना"],
        vocabulary: [{ word: "सारथी", meaning: "मार्गदर्शक / रथ चालवणारा" }],
        pedagogicalSummary: "ज्यांचे कोणी नाही त्यांचे सोबती होण्याचे बळ मिळावे आणि दिशाहीन लोकांना वाट दाखवणारा सारथी बनता यावे."
      },
      "ent_reg_ch_1_p10_7": {
        entityId: "ent_reg_ch_1_p10_7",
        physicalRegionId: "reg_ch_1_p10_7",
        title: "Entity reg_ch_1_p10_7 (definition)",
        concepts: ["शब्दार्थ", "भाषिक ज्ञान"],
        vocabulary: [
          { word: "नवचेतना", meaning: "नवचैतन्य / नवीन उत्साह" },
          { word: "सर्वथा", meaning: "सदैव / सर्व अर्थांनी" },
          { word: "सारथी", meaning: "मार्गदर्शक" },
          { word: "संवेदना", meaning: "दुसऱ्याचे दुःख समजण्याची जाणीव" }
        ],
        pedagogicalSummary: "प्रार्थनेतील कठीण शब्दांचे अचूक प्रमाण अर्थ."
      }
    },
    edges: [
      { source: "ent_reg_ch_1_p10_1", target: "ent_reg_ch_1_p10_2", relation: "continues" },
      { source: "ent_reg_ch_1_p10_2", target: "ent_reg_ch_1_p10_3", relation: "continues" },
      { source: "ent_reg_ch_1_p10_3", target: "ent_reg_ch_1_p10_4", relation: "continues" },
      { source: "ent_reg_ch_1_p10_4", target: "ent_reg_ch_1_p10_5", relation: "continues" },
      { source: "ent_reg_ch_1_p10_2", target: "ent_reg_ch_1_p10_7", relation: "defines" }
    ]
  },
  sampleReadingParagraphs: [
    {
      paragraphId: 1,
      regionId: "reg_ch_1_p10_1",
      pdfPage: 10,
      printedPage: 1,
      regionType: "heading",
      text: "१. तू बुद्धी दे — गुरू ठाकूर",
      verificationStatus: "GOLDEN_TRUTH"
    },
    {
      paragraphId: 2,
      regionId: "reg_ch_1_p10_2",
      pdfPage: 10,
      printedPage: 1,
      regionType: "poetry",
      text: "तू बुद्‌धि दे तू तेज दे नवचेतना विश्वास दे । जे सत्य सुंदर सर्वथा आजन्म त्याचा ध्यास दे ।",
      verificationStatus: "GOLDEN_TRUTH"
    },
    {
      paragraphId: 3,
      regionId: "reg_ch_1_p10_3",
      pdfPage: 10,
      printedPage: 1,
      regionType: "poetry",
      text: "हरवले आभाळ ज्यांचे हो तयांचा सोबती, सापडेना वाट ज्यांना हो तयांचा सारथी । साधना करिती तयांना नित्य तव सहवास दे ।",
      verificationStatus: "GOLDEN_TRUTH"
    },
    {
      paragraphId: 4,
      regionId: "reg_ch_1_p10_4",
      pdfPage: 10,
      printedPage: 1,
      regionType: "poetry",
      text: "जाणावया दुर्बलांचे दुःख आणि वेदना तेवत्या राहो सदा रंध्रातुनी संवेदना । धमन्यातल्या रुधिरास या खलभेदनाची आस दे ।",
      verificationStatus: "GOLDEN_TRUTH"
    },
    {
      paragraphId: 5,
      regionId: "reg_ch_1_p10_5",
      pdfPage: 10,
      printedPage: 1,
      regionType: "poetry",
      text: "सन्मार्ग आणि सन्मती लाभो सदा सत्संगती नीती ना ही भ्रष्ट हो जरी संकटे आली किती । पंखास या बळ दे नवे झेप घेण्यास आकाश दे ।",
      verificationStatus: "GOLDEN_TRUTH"
    },
    {
      paragraphId: 6,
      regionId: "reg_ch_1_p10_7",
      pdfPage: 10,
      printedPage: 1,
      regionType: "definition",
      text: "शब्दार्थ : नवचेतना - नवचैतन्य. सर्वथा - सदैव, सर्व अर्थांनी. आजन्म - जन्मभर. सारथी - मार्गदर्शक. रंध्र - छिद्र, त्वचा. खलभेदनाची - दुष्टांचा नाश करण्याची.",
      verificationStatus: "GOLDEN_TRUTH"
    }
  ]
};

export const GEO_CH1_PROCESSED: ProcessedChapterOutput = {
  documentId: "geo-10",
  chapterId: "ch_1",
  chapterTitle: "१. क्षेत्रभेट (Field Visit)",
  marathiTitle: "१. क्षेत्रभेट",
  subject: "Geography",
  startPdfPage: 12,
  endPdfPage: 19,
  printedStartPage: 1,
  printedEndPage: 8,
  totalRegions: 244,
  corpusRecordsCount: 203,
  invariantValid: true,
  summary: "Successfully processed १. क्षेत्रभेट (Field Visit) (Geography): 244 physical regions extracted across PDF pages 12-19 (printed pages 1-8). Physical Document Graph and Learning Graph constructed and validated.",
  physicalGraph: {
    pageId: "geo-10_ch_1",
    sourceHash: "f1883cb20a4597b8d0016e78912304875cbaf1093",
    readingOrder: ["reg_geo_heading", "reg_geo_intro", "reg_geo_map_caption", "reg_geo_equipment", "reg_geo_subheading", "reg_geo_dialogue_1", "reg_geo_dialogue_2", "reg_geo_discussion", "reg_geo_exercise"],
    regions: {
      "reg_geo_heading": {
        regionId: "reg_geo_heading",
        regionType: "heading",
        bbox: [54.0, 72.0, 340.0, 110.0],
        nativeText: "१. क्षेत्रभेट (प्रात्यक्षिक भूगोल)",
        readingOrderIndex: 1,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_intro": {
        regionId: "reg_geo_intro",
        regionType: "paragraph",
        bbox: [54.0, 115.0, 520.0, 185.0],
        nativeText: "राहुलच्या वर्गातील विद्यार्थी आणि शाळेतील शिक्षक असे सर्वजण उस्मानाबाद जिल्ह्यातील नळदुर्ग ते रायगड जिल्ह्यातील अलिबाग येथे क्षेत्रभेटीसाठी निघाले आहेत. या प्रवासासाठी त्यांनी एसटी बसची सेवा घेतली असून, क्षेत्रभेटीचे नियोजन शिक्षक व विद्यार्थ्यांच्या मदतीने केले आहे. विद्यार्थी व शिक्षक भोवतालच्या परिस्थितीचे कसे निरीक्षण करतात, याची माहिती घेऊ.",
        readingOrderIndex: 2,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_map_caption": {
        regionId: "reg_geo_map_caption",
        regionType: "caption",
        bbox: [100.0, 480.0, 480.0, 510.0],
        nativeText: "आकृती १.१ : क्षेत्रभेटीचा मार्ग (नळदुर्ग-सोलापूर-पुणे-अलिबाग)",
        readingOrderIndex: 3,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_equipment": {
        regionId: "reg_geo_equipment",
        regionType: "paragraph",
        bbox: [54.0, 520.0, 320.0, 590.0],
        nativeText: "विद्यार्थ्यांनी वैयक्तिक साहित्याबरोबरच नोंदवही, नमुना प्रश्नावली, पेन, पेन्सिल, मोजपट्टी, टेप, होकायंत्र, पिशवी, नकाशा, कॅमेरा, प्रथमोपचार पेटी इत्यादी साहित्य सोबत घेतले आहे.",
        readingOrderIndex: 4,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_subheading": {
        regionId: "reg_geo_subheading",
        regionType: "subheading",
        bbox: [54.0, 600.0, 320.0, 630.0],
        nativeText: "दिवस पहिला : वेळ सकाळी ६:००",
        readingOrderIndex: 5,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_dialogue_1": {
        regionId: "reg_geo_dialogue_1",
        regionType: "dialogue",
        bbox: [54.0, 635.0, 320.0, 710.0],
        nativeText: "शिक्षिका : आता आपण नळदुर्ग परिसर सोडून सोलापूरच्या दिशेने जात आहोत. सोलापूरजवळ आपण सकाळचा नाश्ता घेणार आहोत आणि पुण्याला दुपारचे जेवण घेणार आहोत. प्रवासात तुम्हांला रस्त्याच्या दोन्ही बाजूंना निरीक्षण करून नोंदी करायच्या आहेत.",
        readingOrderIndex: 6,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_discussion": {
        regionId: "reg_geo_discussion",
        regionType: "discussion_box",
        bbox: [340.0, 520.0, 540.0, 650.0],
        nativeText: "चर्चा करा : तुम्ही या क्षेत्रभेटीत सहभागी होणार असाल, तर कशी पूर्वतयारी कराल? समजा शिक्षकांनी क्षेत्रभेटीचे आयोजन तुम्हांला करायला सांगितले तर तपशीलवार नियोजन कसे कराल?",
        readingOrderIndex: 7,
        pdfPage: 12,
        printedPage: 1
      },
      "reg_geo_exercise": {
        regionId: "reg_geo_exercise",
        regionType: "exercise",
        bbox: [54.0, 100.0, 520.0, 350.0],
        nativeText: "स्वाध्याय : १. क्षेत्रभेटी दरम्यान कचऱ्याचे व्यवस्थापन कसे कराल? २. क्षेत्रभेटीसाठी उपयुक्त साहित्याची यादी तयार करा. ३. भूगोलाच्या अभ्यासात क्षेत्रभेटीचे महत्त्व विशद करा.",
        readingOrderIndex: 8,
        pdfPage: 19,
        printedPage: 8
      }
    }
  },
  learningGraph: {
    graphId: "lg_geo-10_ch_1",
    units: {
      "unit_geo_ch1_main": {
        unitId: "unit_geo_ch1_main",
        title: "१. क्षेत्रभेट (Field Visit)",
        chapterId: "ch_1",
        keyTakeaways: ["क्षेत्रभेट", "प्रश्नावली", "पर्जन्यमान", "वनस्पती", "धाब्यांची घरे", "खडक", "समुद्रकिनारा"],
        entityIds: ["ent_geo_heading", "ent_geo_intro", "ent_geo_map", "ent_geo_dialogue"]
      },
      "unit_geo_ch1_activity": {
        unitId: "unit_geo_ch1_activity",
        title: "चर्चा व प्रात्यक्षिक कृती",
        chapterId: "ch_1",
        keyTakeaways: ["क्षेत्रभेट पूर्वतयारी", "गट चर्चा"],
        entityIds: ["ent_geo_discussion"]
      },
      "unit_geo_ch1_exercise": {
        unitId: "unit_geo_ch1_exercise",
        title: "स्वाध्याय व मूल्यमापन",
        chapterId: "ch_1",
        keyTakeaways: ["कचरा व्यवस्थापन", "क्षेत्रभेट अहवाल"],
        entityIds: ["ent_geo_exercise"]
      }
    },
    entities: {
      "ent_geo_intro": {
        entityId: "ent_geo_intro",
        physicalRegionId: "reg_geo_intro",
        title: "Entity reg_geo_intro (Field Visit Narrative)",
        concepts: ["क्षेत्रभेट उद्दिष्टे", "प्रत्यक्ष निरीक्षण"],
        vocabulary: [{ word: "क्षेत्रभेट", meaning: "प्रत्यक्ष ठिकाणी जाऊन केलेली भौगोलिक पाहणी" }],
        pedagogicalSummary: "नळदुर्ग ते अलिबाग क्षेत्रभेटीचा प्रत्यक्ष अभ्यास व पूर्वतयारी."
      },
      "ent_geo_discussion": {
        entityId: "ent_geo_discussion",
        physicalRegionId: "reg_geo_discussion",
        title: "Entity reg_geo_discussion (Reflection Activity)",
        concepts: ["क्षेत्रभेट पूर्वतयारी", "प्रश्नावली नियोजन"],
        vocabulary: [{ word: "तपशीलवार", meaning: "सविस्तर माहितीसह" }],
        pedagogicalSummary: "विद्यार्थ्यांनी प्रत्यक्ष सहभागासाठी करावयाची पूर्वतयारी व नियोजन."
      }
    },
    edges: [
      { source: "ent_geo_heading", target: "ent_geo_intro", relation: "explains" },
      { source: "ent_geo_intro", target: "ent_geo_map", relation: "illustrates" },
      { source: "ent_geo_map", target: "ent_geo_dialogue", relation: "continues" },
      { source: "ent_geo_dialogue", target: "ent_geo_discussion", relation: "asks_about" }
    ]
  },
  sampleReadingParagraphs: [
    {
      paragraphId: 1,
      regionId: "reg_geo_heading",
      pdfPage: 12,
      printedPage: 1,
      regionType: "heading",
      text: "१. क्षेत्रभेट (प्रात्यक्षिक भूगोल)",
      verificationStatus: "VERIFIED_TRAINING_SAMPLE"
    },
    {
      paragraphId: 2,
      regionId: "reg_geo_intro",
      pdfPage: 12,
      printedPage: 1,
      regionType: "paragraph",
      text: "राहुलच्या वर्गातील विद्यार्थी आणि शाळेतील शिक्षक असे सर्वजण उस्मानाबाद जिल्ह्यातील नळदुर्ग ते रायगड जिल्ह्यातील अलिबाग येथे क्षेत्रभेटीसाठी निघाले आहेत. या प्रवासासाठी त्यांनी एसटी बसची सेवा घेतली असून, क्षेत्रभेटीचे नियोजन शिक्षक व विद्यार्थ्यांच्या मदतीने केले आहे.",
      verificationStatus: "VERIFIED_TRAINING_SAMPLE"
    },
    {
      paragraphId: 3,
      regionId: "reg_geo_map_caption",
      pdfPage: 12,
      printedPage: 1,
      regionType: "caption",
      text: "आकृती १.१ : क्षेत्रभेटीचा मार्ग (नळदुर्ग ते अलिबाग प्रवास नकाशा)",
      verificationStatus: "VERIFIED_TRAINING_SAMPLE"
    },
    {
      paragraphId: 4,
      regionId: "reg_geo_equipment",
      pdfPage: 12,
      printedPage: 1,
      regionType: "paragraph",
      text: "विद्यार्थ्यांनी वैयक्तिक साहित्याबरोबरच नोंदवही, नमुना प्रश्नावली, पेन, पेन्सिल, मोजपट्टी, टेप, होकायंत्र, पिशवी, नकाशा, कॅमेरा, प्रथमोपचार पेटी इत्यादी साहित्य सोबत घेतले आहे.",
      verificationStatus: "VERIFIED_TRAINING_SAMPLE"
    },
    {
      paragraphId: 5,
      regionId: "reg_geo_dialogue_1",
      pdfPage: 12,
      printedPage: 1,
      regionType: "dialogue",
      text: "दिवस पहिला : वेळ सकाळी ६:००. शिक्षिका : आता आपण नळदुर्ग परिसर सोडून सोलापूरच्या दिशेने जात आहोत. प्रवासात तुम्हांला रस्त्याच्या दोन्ही बाजूंना निरीक्षण करून नोंदी करायच्या आहेत.",
      verificationStatus: "VERIFIED_TRAINING_SAMPLE"
    },
    {
      paragraphId: 6,
      regionId: "reg_geo_discussion",
      pdfPage: 12,
      printedPage: 1,
      regionType: "discussion_box",
      text: "चर्चा करा : तुम्ही या क्षेत्रभेटीत सहभागी होणार असाल, तर कशी पूर्वतयारी कराल? समजा शिक्षकांनी आयोजन करायला सांगितले तर तपशीलवार नियोजन कसे कराल?",
      verificationStatus: "VERIFIED_TRAINING_SAMPLE"
    }
  ]
};

export const MARATHI_CH1_READING_PAGE = {
  book: "अक्षरभारती — मराठी (इयत्ता दहावी)",
  bookEn: "AksharBharati Marathi · Class 10 · 2018-24",
  page: 1,
  pdfPage: 10,
  chapter: "१. तू बुद्धी दे (प्रार्थना) — गुरू ठाकूर",
  status: "verified" as CorpusStatus,
  confirmations: 12,
  paragraphs: [
    {
      id: 1,
      sentences: [
        s(1, "तू बुद्‌धि दे तू तेज दे नवचेतना विश्वास दे."),
        s(2, "जे सत्य सुंदर सर्वथा आजन्म त्याचा ध्यास दे.", ["सर्वथा", "ध्यास"]),
      ],
      tutor: "कवी ईश्वराकडे सन्मार्गावर चालण्यासाठी बुद्धी, तेज आणि नवीन चेतना मागतो. ‘सर्वथा’ म्हणजे नेहमी, आणि ‘ध्यास’ म्हणजे अखंड ओढ."
    },
    {
      id: 2,
      sentences: [
        s(3, "हरवले आभाळ ज्यांचे हो तयांचा सोबती,"),
        s(4, "सापडेना वाट ज्यांना हो तयांचा सारथी.", ["सारथी"]),
        s(5, "साधना करिती तयांना नित्य तव सहवास दे."),
      ],
      tutor: "ज्यांचे कोणी आधार नाही, त्यांना आधार देण्याचे सामर्थ्य मिळावे. ‘सारथी’ म्हणजे रस्ता दाखवणारा मार्गदर्शक."
    },
    {
      id: 3,
      sentences: [
        s(6, "जाणावया दुर्बलांचे दुःख आणि वेदना,"),
        s(7, "तेवत्या राहो सदा रंध्रातुनी संवेदना.", ["रंध्रातुनी", "संवेदना"]),
        s(8, "धमन्यातल्या रुधिरास या खलभेदनाची आस दे.", ["रुधिरास", "खलभेदनाची"]),
      ],
      tutor: "दुसऱ्यांचे दुःख समजण्यासाठी मनातील संवेदनशीलता जिवंत राहावी. ‘रुधिर’ म्हणजे रक्त आणि ‘खलभेदना’ म्हणजे वाईट प्रवृत्तींचा नाश."
    },
    {
      id: 4,
      sentences: [
        s(9, "सन्मार्ग आणि सन्मती लाभो सदा सत्संगती,"),
        s(10, "नीती ना ही भ्रष्ट हो जरी संकटे आली किती.", ["सन्मती", "सत्संगती"]),
        s(11, "पंखास या बळ दे नवे झेप घेण्यास आकाश दे."),
      ],
      tutor: "संकटे कितीही आली तरी नीती आणि चांगला मार्ग सोडू नये, अशी उदात्त शिकवण या कडव्यातून मिळते."
    }
  ] as Paragraph[]
};

export const GEO_CH1_READING_PAGE = {
  book: "भूगोल — इयत्ता दहावी",
  bookEn: "Geography · Class 10 · 2022-23",
  page: 1,
  pdfPage: 12,
  chapter: "१. क्षेत्रभेट (Field Visit)",
  status: "verified" as CorpusStatus,
  confirmations: 24,
  paragraphs: [
    {
      id: 1,
      sentences: [
        s(1, "१. क्षेत्रभेट : राहुलच्या वर्गातील विद्यार्थी आणि शिक्षक उस्मानाबाद जिल्ह्यातील नळदुर्ग ते रायगड जिल्ह्यातील अलिबाग येथे क्षेत्रभेटीसाठी निघाले आहेत.", ["क्षेत्रभेट", "नळदुर्ग"]),
        s(2, "या प्रवासासाठी त्यांनी एसटी बसची सेवा घेतली असून, क्षेत्रभेटीचे नियोजन शिक्षक व विद्यार्थ्यांच्या मदतीने केले आहे.", ["नियोजन"]),
        s(3, "विद्यार्थी व शिक्षक भोवतालच्या भौगोलिक परिस्थितीचे कसे प्रत्यक्ष निरीक्षण करतात, ते आपण समजून घेऊ.", ["भौगोलिक", "निरीक्षण"]),
      ],
      tutor: "‘क्षेत्रभेट’ म्हणजे एखाद्या ठिकाणास प्रत्यक्ष भेट देऊन तेथील भौगोलिक, सामाजिक व प्राकृतिक वैशिष्ट्यांचा प्रत्यक्ष अभ्यास करणे."
    },
    {
      id: 2,
      sentences: [
        s(4, "आकृती १.१ : क्षेत्रभेटीचा मार्ग — नळदुर्ग ते सोलापूर, पुणे, लोणावळा आणि अलिबाग असा हा प्रवास मार्ग आहे.", ["प्रवास मार्ग"]),
        s(5, "विद्यार्थ्यांनी वैयक्तिक साहित्याबरोबरच नोंदवही, नमुना प्रश्नावली, पेन, पेन्सिल, मोजपट्टी, टेप, होकायंत्र, पिशवी, नकाशा, कॅमेरा आणि प्रथमोपचार पेटी सोबत घेतली आहे.", ["प्रश्नावली", "होकायंत्र"]),
      ],
      tutor: "क्षेत्रभेटीपूर्वी प्रश्नावली, मार्ग नकाशा, होकायंत्र, प्रथमोपचार पेटी आणि नोंदीसाठी नोंदवही सोबत घेणे आवश्यक असते."
    },
    {
      id: 3,
      sentences: [
        s(6, "दिवस पहिला, वेळ सकाळी ६:०० : शिक्षिका — आता आपण नळदुर्ग परिसर सोडून सोलापूरच्या दिशेने जात आहोत.", ["परिसर"]),
        s(7, "प्रवासात तुम्हांला रस्त्याच्या दोन्ही बाजूंना निरीक्षण करून भूरूपे, वस्त्या आणि वनस्पती यांच्या नोंदी करायच्या आहेत.", ["भूरूपे"]),
        s(8, "राहुल — होय मॅडम, येथे चढ-उतार असलेली जमीन दिसत असून काही ठिकाणी पिके तर काही ठिकाणी कोरडी जमीन आणि बाभळीची झाडे दिसत आहेत.", ["बाभळीची"]),
        s(9, "शिक्षिका — बरोबर राहुल, हा पर्जन्यछायेचा प्रदेश असल्याने येथे वनस्पती विरळ आणि कोरड्या स्वरूपाची आढळते.", ["पर्जन्यछायेचा"]),
      ],
      tutor: "मराठवाड्यात पाऊस कमी असल्याने शुष्क व काटेरी वनस्पती आढळतात. प्रवासात जमिनीचा उतार आणि वनस्पतीचा प्रकार बदलतो."
    },
    {
      id: 4,
      sentences: [
        s(10, "चर्चा करा : तुम्ही या क्षेत्रभेटीत सहभागी होणार असाल, तर कशी पूर्वतयारी कराल?", ["पूर्वतयारी"]),
        s(11, "समजा शिक्षकांनी क्षेत्रभेटीचे आयोजन तुम्हांला करायला सांगितले तर तपशीलवार नियोजन कसे कराल?", ["तपशीलवार", "नियोजन"]),
      ],
      tutor: "क्षेत्रभेटीच्या पूर्वतयारीमध्ये प्रवासाचे अंतर, वाहतुकीची साधने, मुक्कामाची सोय आणि प्रश्नावली तयार करणे अत्यंत महत्त्वाचे असते."
    }
  ] as Paragraph[]
};

export const GEO_CH2_READING_PAGE = {
  book: "भूगोल — इयत्ता दहावी",
  bookEn: "Geography · Class 10 · 2022-23",
  page: 9,
  pdfPage: 20,
  chapter: "२. स्थान-विस्तार (Location & Extent)",
  status: "verified" as CorpusStatus,
  confirmations: 18,
  paragraphs: [
    {
      id: 1,
      sentences: [
        s(1, "मित्रांनो, इयत्ता सहावीपासूनच सामाजिक शास्त्राच्या अभ्यासक्रमात आपण ‘भूगोल’ विषयाचा स्वतंत्रपणे अभ्यास करत आहोत."),
        s(2, "पृथ्वीचे वातावरण, भूरूपे, आणि नैसर्गिक साधनसंपत्ती यांचा परिचय आपल्याला झालेला आहे.", ["साधनसंपत्ती"]),
      ],
      tutor: "या पाठाची सुरुवात मागील इयत्तांमधील भौगोलिक संकल्पनांची उजळणी करून होते. 'साधनसंपत्ती' म्हणजे निसर्गाने दिलेली संपत्ती."
    },
    {
      id: 2,
      sentences: [
        s(3, "या वर्षी आपण दोन वेगवेगळ्या देशांमधील भौगोलिक घटकांची तुलना करणार आहोत."),
        s(4, "भारत आणि ब्राझील हे दोन विकसनशील देश निवडून त्यांच्या स्थान व विस्ताराचा तुलनात्मक अभ्यास आपण करणार आहोत.", ["विकसनशील", "तुलनात्मक"]),
      ],
      tutor: "भारत हा आशिया खंडातील आणि ब्राझील हा दक्षिण अमेरिका खंडातील देश आहे. दोघांचाही अक्षांशीय व रेखांशीय विस्तार वेगळा आहे."
    },
    {
      id: 3,
      sentences: [
        s(5, "भौगोलिक संकल्पनांचा प्रत्यक्ष उपयोग प्रदेशांच्या अभ्यासात करून अध्ययन क्षमता गाठणे आवश्यक आहे."),
        s(6, "यासाठी नकाशे, आलेख, आणि आकृत्यांचे सूक्ष्म वाचन महत्त्वाचे ठरते.", ["सूक्ष्म"]),
      ],
      tutor: "नकाशा वाचनामुळे अक्षांश, रेखांश आणि देशांच्या आंतरराष्ट्रीय सीमांचे अचूक स्थान समजते."
    }
  ] as Paragraph[]
};


