import { createFileRoute } from "@tanstack/react-router";
import {
  Play,
  Pause,
  Repeat,
  SkipBack,
  SkipForward,
  Sparkles,
  BookOpenCheck,
  Mic,
  MicOff,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  Volume2,
  Layers,
  MapPin,
  MessageSquare,
  BookOpen,
  Edit3,
  ExternalLink,
  Check,
  Info,
  Square,
  Send,
  HelpCircle,
  Radio
} from "lucide-react";
import { toast } from "sonner";
import { useEffect, useMemo, useState, useRef, useCallback } from "react";
import { READING_PAGE, HISTORY_CH1_READING_PAGE, SCIENCE_CH1_READING_PAGE, MARATHI_CH1_READING_PAGE, GEO_CH1_READING_PAGE, GEO_CH2_READING_PAGE, VOICE_COMMANDS, HISTORY_CHAPTERS, SCIENCE_CHAPTERS } from "@/lib/mock-data";
import {
  COMMON_MATRA_TABLETS,
  insertMatraSmartly,
  romanToDevanagari,
  devanagariToRoman,
  type MatraTablet
} from "@/lib/marathi-transliteration";
import { useVoiceAssistant, getVAResponse, type VACommand, type VAResult } from "@/lib/voice-assistant";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { Page, Card, CorpusChip } from "@/components/app-shell";

export const Route = createFileRoute("/read")({
  validateSearch: (search: Record<string, unknown>) => ({
    doc: (search.doc as string) || "geo-10",
    chapter: (search.chapter as string) || "ch_1",
    page: Number(search.page) || 1,
  }),
  head: () => ({
    meta: [
      { title: "Reading — AksharSetu" },
      { name: "description", content: "Paragraph-first Marathi textbook reading with structured dialogue, supporting visuals, and pronunciation correction." },
      { property: "og:title", content: "Reading — AksharSetu" },
      { property: "og:description", content: "Human-like textbook narration with teacher dialogue and persistent pronunciation knowledge." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: Reader,
});

const SPEEDS = [0.75, 1, 1.25, 1.5];

// Play pleasant audible chime for Tutor Mode (§0 Principle 2)
function playAudibleCue() {
  if (typeof window === "undefined") return;
  try {
    const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    if (!AudioContextClass) return;
    const ctx = new AudioContextClass();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = "sine";
    osc.frequency.setValueAtTime(587.33, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(880, ctx.currentTime + 0.15);
    gain.gain.setValueAtTime(0.2, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
    osc.start();
    osc.stop(ctx.currentTime + 0.35);
  } catch (err) {
    console.debug("Audio cue notice:", err);
  }
}

interface DialogueTurn {
  turn_id: string;
  speaker: string;
  speaker_role: "teacher" | "student" | "narrator";
  text: string;
  order: number;
  voice_profile: string;
  prosody_style: string;
}

interface SupportingMaterial {
  material_id: string;
  material_type: string;
  title: string;
  caption_text: string;
  explanation?: string;
  auto_narrate?: boolean;
}

interface SemanticBlock {
  id: string;
  block_id: string;
  block_type: string;
  primary_content: boolean;
  canonical_text: string;
  pdf_page: number;
  printed_page?: number;
  sentences: Array<{
    id: number;
    text: string;
    tokens: Array<{ text: string; flagged?: boolean }>;
    para_id: string;
    pdf_page: number;
    printed_page?: number;
  }>;
  dialogue_turns: DialogueTurn[];
  supporting_visuals: SupportingMaterial[];
  tutor?: string;
  tutor_explanation?: string;
  tutor_plan?: any;
  narration_plan?: any;
}

interface ChapterPageData {
  page_id: string;
  pdf_page: number;
  printed_page?: number;
  paragraphs: SemanticBlock[];
  total_blocks?: number;
  total_regions?: number;
}

interface ChapterPayload {
  chapter: {
    chapter_id: string;
    document_id: string;
    title: string;
    subject: string;
    pdf_start_page: number;
    pdf_end_page: number;
    printed_start_page: number;
    printed_end_page: number;
    total_pages: number;
    total_physical_regions: number;
  };
  manifest?: any;
  pages: ChapterPageData[];
  spoken_sequence: Array<any>;
}

function Reader() {
  const search = Route.useSearch();
  const [selectedBookKey, setSelectedBookKey] = useState<string>(() => {
    if (search.doc === "history-8" || search.doc === "history" || search.doc === "AKS_HISTORY_CLASS8_HISTORY") {
      const ch = search.chapter ? String(search.chapter).toLowerCase() : "ch_01";
      const num = ch.replace(/[^0-9]/g, "");
      return `history-8-ch${parseInt(num || "1")}`;
    }
    if (search.doc === "geo-10" && search.chapter === "ch_2") return "geo-10-ch2";
    if (search.doc === "akshar-10") return "akshar-10";
    if (search.doc === "geo-10") return "geo-10";
    if (search.doc === "science-8" || search.doc === "science" || search.doc === "sci") {
      const match = search.chapter ? search.chapter.match(/\d+/) : null;
      const chNum = match ? match[0] : "1";
      return `science-8-ch${chNum}`;
    }
    return "history-8-ch1"; // Class 8 History Ch 1 Master Reference default
  });

  const [remoteChapter, setRemoteChapter] = useState<ChapterPayload | null>(null);
  const [loadingChapter, setLoadingChapter] = useState(false);

  // Active reading position: active block and active sentence
  const [activeBlockIndex, setActiveBlockIndex] = useState(0);
  const [activeSentenceId, setActiveSentenceId] = useState<number | null>(null);
  const [activeTurnId, setActiveTurnId] = useState<string | null>(null);
  const [tutorSegmentIndex, setTutorSegmentIndex] = useState<0 | 1 | 2>(0);
  const [isCompleted, setIsCompleted] = useState(false);

  // Playback state
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [speaker, setSpeaker] = useState<string>("shreya");
  const [ttsProvider, setTtsProvider] = useState<string>("sarvam");
  const [modulation, setModulation] = useState<number>(0.72);
  const [tutor, setTutor] = useState(false);
  const [cmdOpen, setCmdOpen] = useState(false);
  const [loadingAudio, setLoadingAudio] = useState(false);

  // Word Selection & Pronunciation Admin Dialog State
  const [selectedWord, setSelectedWord] = useState<{ word: string; entry?: any } | null>(null);
  const [adminModalOpen, setAdminModalOpen] = useState(false);
  const [adminWordForm, setAdminWordForm] = useState({
    canonical_text: "",
    preferred_pronunciation: "",
    phonetic_form: "",
    scope: "global",
    notes: ""
  });
  const [savingPron, setSavingPron] = useState(false);
  const [testingPron, setTestingPron] = useState(false);

  // ─── Voice Assistant State ───────────────────────────────────────────────
  const [vaEnabled, setVaEnabled] = useState(true); // Always-on by default
  const [vaResponseMsg, setVaResponseMsg] = useState<string | null>(null);
  const vaResponseTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Voice-Based Pronunciation Teaching State
  const [isRecordingVoice, setIsRecordingVoice] = useState(false);
  const [isDecodingVoice, setIsDecodingVoice] = useState(false);
  const [isEditingPronunciation, setIsEditingPronunciation] = useState(false);
  const [isPlayingTestAudio, setIsPlayingTestAudio] = useState(false);
  const [decodedPronunciation, setDecodedPronunciation] = useState<{
    canonical_text: string;
    lexical_identity: string;
    spoken_transcript?: string;
    is_canonical_match?: boolean;
    detected_pronunciation: string;
    preferred_pronunciation: string;
    phonetic_form: string;
    syllable_boundaries: string[];
    phoneme_sequence: string[];
    confidence: number;
    acoustic_metrics?: any;
  } | null>(null);
  const [recordedAudioBlob, setRecordedAudioBlob] = useState<Blob | null>(null);
  const [recordedAudioUrl, setRecordedAudioUrl] = useState<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const testAudioRef = useRef<HTMLAudioElement | null>(null);
  const devaInputRef = useRef<HTMLInputElement>(null);

  // RAG Visual Explanation Modal
  const [visualModal, setVisualModal] = useState<SupportingMaterial | null>(null);

  // Grounded Tutor Q&A Interactive Assistant (§18)
  const [tutorInput, setTutorInput] = useState("");
  const [tutorQueryLoading, setTutorQueryLoading] = useState(false);
  const [tutorQnAResult, setTutorQnAResult] = useState<any | null>(null);

  const handleAskTutorQuestion = async (queryText: string) => {
    if (!queryText.trim()) return;
    setTutorQueryLoading(true);
    try {
      const isHistory = selectedBookKey.startsWith("history-8") || selectedBookKey.startsWith("hist");
      const isScience = selectedBookKey.startsWith("science-8") || selectedBookKey.startsWith("sci");
      let chId = "CH_01";
      if (isHistory || isScience) {
        const match = selectedBookKey.match(/ch_?(\d+)/i);
        const chNum = match ? parseInt(match[1]) : 1;
        chId = `CH_${chNum.toString().padStart(2, "0")}`;
      }

      const tutorUrl = isScience ? "/api/science/tutor" : "/api/history/tutor";
      const res = await fetch(tutorUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: queryText,
          chapter_id: chId,
          block_id: currentBlock?.id || `${chId}_LU_01`
        })
      });
      if (res.ok) {
        const data = await res.json();
        setTutorQnAResult(data);
        playAudibleCue();
        toast.success("शिक्षकांचे स्पष्टीकरण तयार आहे!");
      } else {
        toast.error("स्पष्टीकरण मिळवण्यात अडचण आली.");
      }
    } catch (e) {
      console.error(e);
      toast.error("नेटवर्क त्रुटी.");
    } finally {
      setTutorQueryLoading(false);
    }
  };

  // Load Chapter Data from API
  useEffect(() => {
    let isSubscribed = true;
    const isHistory = selectedBookKey.startsWith("history-8") || selectedBookKey.startsWith("hist");
    const isScience = selectedBookKey.startsWith("science-8") || selectedBookKey.startsWith("sci");
    let docId = "geo-10";
    let chapterId = "ch_1";
    let fetchUrl = `/api/chapters/${chapterId}/reader?doc_id=${docId}`;

    if (isScience) {
      docId = "AKS_SCIENCE_CLASS8_SCIENCE";
      const match = selectedBookKey.match(/ch_?(\d+)/i);
      const chNum = match ? parseInt(match[1]) : 1;
      chapterId = `CH_${chNum.toString().padStart(2, "0")}`;
      fetchUrl = `/api/science/chapters/${chapterId}/reader`;
    } else if (isHistory) {
      docId = "AKS_HISTORY_CLASS8_HISTORY";
      const match = selectedBookKey.match(/ch_?(\d+)/i);
      const chNum = match ? parseInt(match[1]) : 1;
      chapterId = `CH_${chNum.toString().padStart(2, "0")}`;
      fetchUrl = `/api/history/chapters/${chapterId}/reader`;
    } else if (selectedBookKey.startsWith("akshar")) {
      docId = "akshar-10";
      chapterId = "ch_1";
      fetchUrl = `/api/chapters/${chapterId}/reader?doc_id=${docId}`;
    } else if (selectedBookKey === "geo-10-ch2") {
      docId = "geo-10";
      chapterId = "ch_2";
      fetchUrl = `/api/chapters/${chapterId}/reader?doc_id=${docId}`;
    }

    setLoadingChapter(true);
    fetch(fetchUrl)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load chapter manifest");
        return res.json();
      })
      .then((data: ChapterPayload) => {
        if (isSubscribed && data?.pages?.length > 0) {
          setRemoteChapter(data);
        }
        setLoadingChapter(false);
      })
      .catch((err) => {
        console.warn("Reader API notice:", err);
        if (isSubscribed) setLoadingChapter(false);
      });

    return () => {
      isSubscribed = false;
    };
  }, [selectedBookKey]);

  // Unified Chapter Model
  const { chapterMeta, pages, allBlocks, spokenSequence } = useMemo(() => {
    if (remoteChapter && remoteChapter.pages.length > 0) {
      const blocks = remoteChapter.pages.flatMap((pg) => pg.paragraphs);
      return {
        chapterMeta: remoteChapter.chapter,
        pages: remoteChapter.pages,
        allBlocks: blocks,
        spokenSequence: remoteChapter.spoken_sequence || [],
      };
    }

    // Default fallback
    const isHistory = selectedBookKey.startsWith("hist") || selectedBookKey.startsWith("history-8");
    const isScience = selectedBookKey.startsWith("sci") || selectedBookKey.startsWith("science-8");
    const fallbackBase = isScience
      ? SCIENCE_CH1_READING_PAGE
      : isHistory
      ? HISTORY_CH1_READING_PAGE
      : selectedBookKey === "akshar-10"
      ? MARATHI_CH1_READING_PAGE
      : GEO_CH1_READING_PAGE || READING_PAGE;

    const pdfStart = isScience ? 11 : isHistory ? 10 : selectedBookKey === "akshar-10" ? 10 : 12;
    const pdfEnd = isScience ? 15 : isHistory ? 13 : selectedBookKey === "akshar-10" ? 10 : 19;
    const printedStart = 1;
    const printedEnd = isScience ? 5 : isHistory ? 4 : selectedBookKey === "akshar-10" ? 1 : 8;

    const safeParagraphs = fallbackBase?.paragraphs || READING_PAGE.paragraphs || [];

    const fallbackBlocks: SemanticBlock[] = safeParagraphs.map((p, pIdx) => {
      const bPdfPage = (p as any).pdfPage || pdfStart;
      const bPrintedPage = (p as any).printedPage || (bPdfPage - pdfStart + printedStart);
      const bType = (p as any).blockType || (pIdx === 0 ? "heading" : "paragraph");
      return {
        id: String(p.id),
        block_id: String(p.id),
        block_type: bType,
        primary_content: true,
        canonical_text: p.sentences.map((s) => s.tokens.map((t) => t.text).join(" ")).join(" "),
        pdf_page: bPdfPage,
        printed_page: bPrintedPage,
        sentences: p.sentences.map((s) => ({
          id: s.id,
          text: s.tokens.map((t) => t.text).join(" "),
          tokens: s.tokens,
          para_id: String(p.id),
          pdf_page: bPdfPage,
          printed_page: bPrintedPage,
        })),
        dialogue_turns: [],
        supporting_visuals: pIdx === 1 ? [
          {
            material_id: "map_fallback_1",
            material_type: isScience ? "diagram" : "map",
            title: isScience ? "आकृती १.१ : पंचसृष्टी वर्गीकरण पद्धती" : isHistory ? "आगाखान पॅलेस (पुणे) ऐतिहासिक स्मारक" : "आकृती १.१ : क्षेत्रभेटीचा मार्ग",
            caption_text: isScience ? "व्हिटाकर यांची पंचसृष्टी वर्गीकरण पद्धती" : isHistory ? "गांधी स्मारक संग्रहालय, आगाखान पॅलेस, पुणे" : "नळदुर्ग ते सोलापूर, पुणे आणि अलिबाग प्रवास नकाशा",
            explanation: isScience ? "ही आकृती मोनेरा, प्रोटिस्टा, कवके, वनस्पती आणि प्राणी या पाच सृष्टींमधील संबंध दर्शवते." : isHistory ? "या वास्तूमध्ये महात्मा गांधींच्या वापरातील वस्तू व कागदपत्रे जतन केलेली आहेत." : "हा नकाशा नळदुर्ग ते अलिबाग प्रवासाचा मार्ग आणि भूरूपे दर्शवतो.",
            auto_narrate: false
          }
        ] : [],
        tutor: p.tutor,
        tutor_plan: {
          transition: "या ओळीचा मुख्य मुद्दा समजून घेऊया.",
          explanation: p.tutor
        }
      };
    });

    // Build pages from fallbackBlocks grouped by pdf_page
    const pageMap = new Map<number, SemanticBlock[]>();
    fallbackBlocks.forEach((b) => {
      const pg = b.pdf_page || pdfStart;
      if (!pageMap.has(pg)) pageMap.set(pg, []);
      pageMap.get(pg)!.push(b);
    });

    const fallbackPages = Array.from(pageMap.entries())
      .sort(([pA], [pB]) => pA - pB)
      .map(([pdfPg, blocks]) => ({
        page_id: `page_${pdfPg}`,
        pdf_page: pdfPg,
        printed_page: blocks[0]?.printed_page || (pdfPg - pdfStart + printedStart),
        paragraphs: blocks,
        total_blocks: blocks.length,
        total_regions: blocks.length,
      }));

    return {
      chapterMeta: {
        chapter_id: isScience ? "CH_01" : isHistory ? "CH_01" : "ch_1",
        document_id: isScience ? "AKS_SCIENCE_CLASS8_SCIENCE" : isHistory ? "AKS_HISTORY_CLASS8_HISTORY" : selectedBookKey.startsWith("akshar") ? "akshar-10" : "geo-10",
        title: isScience ? "१. सजीव सृष्टी व सूक्ष्मजीवांचे वर्गीकरण (Living World & Microbes)" : isHistory ? "१. इतिहासाची साधने (Sources of History)" : selectedBookKey === "akshar-10" ? "१. तू बुद्धी दे (प्रार्थना)" : "१. क्षेत्रभेट (Field Visit)",
        subject: isScience ? "Science" : isHistory ? "History" : selectedBookKey === "akshar-10" ? "Marathi" : "Geography",
        pdf_start_page: pdfStart,
        pdf_end_page: pdfEnd,
        printed_start_page: printedStart,
        printed_end_page: printedEnd,
        total_pages: fallbackPages.length > 0 ? fallbackPages.length : (pdfEnd - pdfStart + 1),
        total_physical_regions: 244,
      },
      pages: fallbackPages.length > 0 ? fallbackPages : [
        {
          page_id: `page_${pdfStart}`,
          pdf_page: pdfStart,
          printed_page: printedStart,
          paragraphs: fallbackBlocks,
        }
      ],
      allBlocks: fallbackBlocks,
      spokenSequence: fallbackBlocks.flatMap((b) => b.sentences),
    };
  }, [remoteChapter, selectedBookKey]);

  // Active Block and Page
  const currentBlock: SemanticBlock = allBlocks[activeBlockIndex] || allBlocks[0] || {
    id: "0",
    block_id: "0",
    block_type: "paragraph",
    primary_content: true,
    canonical_text: "",
    pdf_page: chapterMeta.pdf_start_page,
    sentences: [],
    dialogue_turns: [],
    supporting_visuals: []
  };

  const activePdfPage = currentBlock.pdf_page || chapterMeta.pdf_start_page;
  const activePageData = pages.find((pg) => pg.pdf_page === activePdfPage) || pages[0] || {
    page_id: "page_10",
    pdf_page: chapterMeta.pdf_start_page || 10,
    printed_page: chapterMeta.printed_start_page || 1,
    paragraphs: allBlocks,
  };

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioCacheRef = useRef<Map<string, string>>(new Map());
  const inFlightPrefetch = useRef<Set<string>>(new Set());
  const pauseTimerRef = useRef<any>(null);

  // Audio fetcher
  const getAudio = useCallback(
    async (text: string, style: string, isTutorText: boolean, pace: number): Promise<string | null> => {
      const cacheKey = `${ttsProvider}_${speaker}_${pace}_${style}_${text}`;
      if (audioCacheRef.current.has(cacheKey)) {
        return audioCacheRef.current.get(cacheKey)!;
      }
      if (inFlightPrefetch.current.has(cacheKey)) return null;

      inFlightPrefetch.current.add(cacheKey);
      try {
        const res = await fetch("/api/tts/synthesize", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            text,
            pace,
            speaker,
            provider: ttsProvider,
            is_tutor: isTutorText,
            style,
            temperature: modulation,
            document_id: chapterMeta.document_id,
            subject: chapterMeta.subject
          }),
        });
        const data = await res.json();
        inFlightPrefetch.current.delete(cacheKey);
        if (data.audio_base64) {
          audioCacheRef.current.set(cacheKey, data.audio_base64);
          return data.audio_base64;
        }
      } catch (err) {
        inFlightPrefetch.current.delete(cacheKey);
      }
      return null;
    },
    [ttsProvider, speaker, modulation, chapterMeta]
  );

  // Playback execution for current semantic block (Paragraph or Dialogue)
  useEffect(() => {
    if (pauseTimerRef.current) {
      clearTimeout(pauseTimerRef.current);
      pauseTimerRef.current = null;
    }

    if (!playing || isCompleted) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      setLoadingAudio(false);
      return;
    }

    if (!currentBlock) return;

    let isCancelled = false;

    // A. Handle Dialogue Block Playback
    if (currentBlock.block_type === "dialogue_block" && currentBlock.dialogue_turns.length > 0) {
      const turns = currentBlock.dialogue_turns;
      const curTurnIdx = turns.findIndex((t) => t.turn_id === activeTurnId);
      const targetTurn = curTurnIdx === -1 ? turns[0] : turns[curTurnIdx];
      setActiveTurnId(targetTurn.turn_id);

      let textToSpeak = targetTurn.text;
      let style = targetTurn.prosody_style || "dialogue_teacher";
      let turnPace = targetTurn.speaker_role === "student" ? Math.min(1.15, speed * 1.05) : speed;

      if (tutor && tutorSegmentIndex > 0) {
        textToSpeak = tutorSegmentIndex === 1
          ? "या संवादातून शिक्षिका व विद्यार्थ्यांमधील मुख्य मुद्दा समजून घेऊया."
          : (currentBlock.tutor_plan?.explanation || currentBlock.tutor || "हा संवाद प्रत्यक्ष भौगोलिक निरीक्षणाचा आहे.");
        style = "teacher";
        turnPace = Math.max(0.75, speed * 0.95);
      }

      setLoadingAudio(true);
      getAudio(textToSpeak, style, tutor && tutorSegmentIndex > 0, turnPace).then((b64) => {
        if (isCancelled) return;
        setLoadingAudio(false);
        if (b64) {
          if (audioRef.current) audioRef.current.pause();
          const audio = new Audio("data:audio/wav;base64," + b64);
          audioRef.current = audio;
          audio.onended = () => {
            if (!playing || isCancelled) return;
            if (tutor && tutorSegmentIndex === 0) {
              playAudibleCue();
              setTutorSegmentIndex(1);
            } else if (tutor && tutorSegmentIndex === 1) {
              setTutorSegmentIndex(2);
            } else {
              setTutorSegmentIndex(0);
              // Next dialogue turn with 350ms pause
              pauseTimerRef.current = setTimeout(() => {
                if (!playing || isCancelled) return;
                const nextIdx = curTurnIdx + 1;
                if (nextIdx < turns.length) {
                  setActiveTurnId(turns[nextIdx].turn_id);
                } else {
                  // Dialogue block complete: advance to next block
                  setActiveTurnId(null);
                  if (activeBlockIndex < allBlocks.length - 1) {
                    setActiveBlockIndex((prev) => prev + 1);
                  } else {
                    setPlaying(false);
                    setIsCompleted(true);
                  }
                }
              }, 350);
            }
          };
          audio.play().catch(console.debug);
        }
      });

      return () => {
        isCancelled = true;
        if (audioRef.current) audioRef.current.pause();
      };
    }

    // B. Handle Standard Paragraph Block Playback
    // Paragraph-First Narration: narrate full text or natural coherent chunks
    let textToSpeak = currentBlock.canonical_text;
    let style = currentBlock.block_type === "heading" ? "heading" : "narration";
    let blockPace = speed;

    // Smooth Pedagogical Heading Introduction (§User Request: "आज आपण शिकणार आहोत [Title]..." only for chapter start; miscellaneous for Page 2+)
    const formatHeadingIntro = (rawHeading: string, blockIdx: number, bPrintedPage?: number, bType?: string) => {
      let cleanHeading = rawHeading
        .replace(/^(?:[०-९0-9ivxLCDM\.\-–—\:\,\t\s]+)/, '')
        .replace(/^(?:प्रकरण|पाठ|घटक|अध्याय)\s*[०-९0-9ivxLCDM\.\-–—\:\,\t\s]+/i, '')
        .replace(/[।.!?…]+$/, '')
        .trim();
      if (!cleanHeading) cleanHeading = rawHeading.trim();

      // Defensive guard: A heading must be a concise title, never a multi-line paragraph
      if (cleanHeading.length > 80) {
        const firstSentence = cleanHeading.split(/[\n।?!.]/)[0]?.trim();
        cleanHeading = firstSentence && firstSentence.length <= 80 ? firstSentence : cleanHeading.slice(0, 80).trim();
      }

      // "आज आपण बघणार आहोत" applies to the chapter start (Page 1 main chapter heading)
      const isChapterStart = (blockIdx === 0) || (bType === "chapter_title" && (!bPrintedPage || bPrintedPage === 1));
      if (isChapterStart) {
        return `आज आपण बघणार आहोत, ${cleanHeading}.`;
      }

      // For Page 2 and onwards, or subsequent sub-headings: miscellaneous natural teacher transitions
      const transitions = [
        `आता आपण बघूयात, ${cleanHeading}.`,
        `चला, आता बघूयात, ${cleanHeading}.`,
        `आता पुढील भाग पाहूयात, ${cleanHeading}.`,
        `चला, आता समजून घेऊया, ${cleanHeading}.`,
        `आता आपण पाहूया, ${cleanHeading}.`
      ];
      return transitions[Math.abs(blockIdx) % transitions.length];
    };

    if (currentBlock.block_type === "heading" || currentBlock.block_type === "chapter_title") {
      textToSpeak = formatHeadingIntro(currentBlock.canonical_text, activeBlockIndex, currentBlock.printed_page, currentBlock.block_type);
    }

    if (tutor) {
      if (tutorSegmentIndex === 0) {
        // In tutor mode, read the smooth heading first, or canonical text
        if (currentBlock.block_type === "heading" || currentBlock.block_type === "chapter_title") {
          textToSpeak = formatHeadingIntro(currentBlock.canonical_text, activeBlockIndex, currentBlock.printed_page, currentBlock.block_type);
        } else {
          textToSpeak = currentBlock.canonical_text;
        }
        style = "canonical";
      } else if (tutorSegmentIndex === 1) {
        textToSpeak = currentBlock.tutor_plan?.transition || "या परिच्छेदाचा मुख्य मुद्दा समजून घेऊया.";
        style = "transition";
      } else {
        textToSpeak = currentBlock.tutor_plan?.explanation || currentBlock.tutor || "हा भाग काळजीपूर्वक समजून घ्या.";
        style = "teacher";
        blockPace = Math.max(0.75, speed * 0.95);
      }
    }

    setLoadingAudio(true);
    getAudio(textToSpeak, style, tutor && tutorSegmentIndex > 0, blockPace).then((b64) => {
      if (isCancelled) return;
      setLoadingAudio(false);
      if (b64) {
        if (audioRef.current) audioRef.current.pause();
        const audio = new Audio("data:audio/wav;base64," + b64);
        audioRef.current = audio;

        audio.onended = () => {
          if (!playing || isCancelled) return;
          if (tutor && tutorSegmentIndex === 0) {
            playAudibleCue();
            setTutorSegmentIndex(1);
          } else if (tutor && tutorSegmentIndex === 1) {
            setTutorSegmentIndex(2);
          } else {
            setTutorSegmentIndex(0);
            pauseTimerRef.current = setTimeout(() => {
              if (!playing || isCancelled) return;
              if (activeBlockIndex < allBlocks.length - 1) {
                setActiveBlockIndex((prev) => prev + 1);
              } else {
                setPlaying(false);
                setIsCompleted(true);
              }
            }, 300);
          }
        };

        audio.play().catch(console.debug);
      }
    });

    return () => {
      isCancelled = true;
      if (audioRef.current) audioRef.current.pause();
    };
  }, [playing, activeBlockIndex, activeTurnId, tutorSegmentIndex, tutor, speed, speaker, modulation, ttsProvider, isCompleted, allBlocks, currentBlock, getAudio]);

  // Jump to specific paragraph block
  const playBlock = (blockIdx: number) => {
    setActiveBlockIndex(blockIdx);
    setActiveTurnId(null);
    setTutorSegmentIndex(0);
    setIsCompleted(false);
    setPlaying(true);
  };

  // Current page index among available pages
  const currentPageIndex = Math.max(
    0,
    pages.findIndex((pg) => pg.pdf_page === activePdfPage)
  );
  const hasPrevPage = currentPageIndex > 0;
  const hasNextPage = currentPageIndex < pages.length - 1;

  // Jump to specific page
  const jumpToPage = (pdfPageNum: number) => {
    // 1. Try to find the exact first block on that pdf page
    let targetIdx = allBlocks.findIndex((b) => b.pdf_page === pdfPageNum);

    // 2. If not found directly, find first block of that page from pages list
    if (targetIdx === -1) {
      const pageObj = pages.find((p) => p.pdf_page === pdfPageNum);
      if (pageObj && pageObj.paragraphs && pageObj.paragraphs.length > 0) {
        targetIdx = allBlocks.findIndex((b) => b.id === pageObj.paragraphs[0].id);
      }
    }

    // 3. Fallback: closest available block
    if (targetIdx === -1 && allBlocks.length > 0) {
      let minDiff = Infinity;
      let closestIdx = 0;
      allBlocks.forEach((b, idx) => {
        const diff = Math.abs((b.pdf_page || 0) - pdfPageNum);
        if (diff < minDiff) {
          minDiff = diff;
          closestIdx = idx;
        }
      });
      targetIdx = closestIdx;
    }

    if (targetIdx !== -1) {
      setActiveBlockIndex(targetIdx);
      setActiveTurnId(null);
      setTutorSegmentIndex(0);
      setIsCompleted(false);
    }
  };

  const jumpToPageIndex = (pageIdx: number) => {
    if (pageIdx >= 0 && pageIdx < pages.length) {
      const targetPage = pages[pageIdx];
      if (targetPage) {
        jumpToPage(targetPage.pdf_page);
      }
    }
  };

  // Word click popover handler
  const handleWordClick = async (word: string) => {
    const cleanWord = word.trim().replace(/[,।?!.–—;:'"]/g, "");
    if (!cleanWord) return;

    try {
      const res = await fetch("/api/pronunciation");
      const data = await res.json();
      const existing = (data.entries || []).find((e: any) => e.canonical_text === cleanWord);
      setSelectedWord({ word: cleanWord, entry: existing });
    } catch {
      setSelectedWord({ word: cleanWord });
    }
  };

  // Open Admin Pronunciation Modal
  const openAdminEdit = (word: string, entry?: any, autoRecord: boolean = false) => {
    const initialDeva = entry?.preferred_pronunciation || word;
    const initialRoman = entry?.phonetic_form || devanagariToRoman(initialDeva);
    setAdminWordForm({
      canonical_text: word,
      preferred_pronunciation: initialDeva,
      phonetic_form: initialRoman,
      scope: entry?.scope || "global",
      notes: entry?.notes || ""
    });
    setRecordedAudioBlob(null);
    setRecordedAudioUrl(entry?.reference_audio ? `/api/pronunciation/audio/${entry.reference_audio.split(/[/\\]/).pop()}` : null);
    if (entry?.detected_pronunciation || entry?.phonetic_form) {
      setDecodedPronunciation({
        canonical_text: word,
        lexical_identity: word,
        detected_pronunciation: entry.detected_pronunciation || entry.phonetic_form || "",
        preferred_pronunciation: entry.preferred_pronunciation || word,
        phonetic_form: entry.phonetic_form || "",
        syllable_boundaries: entry.syllable_boundaries || (entry.preferred_pronunciation ? entry.preferred_pronunciation.split("-") : [word]),
        phoneme_sequence: entry.phoneme_sequence || [],
        confidence: 1.0,
        acoustic_metrics: entry.acoustic_metrics
      });
      setIsEditingPronunciation(false);
    } else {
      setDecodedPronunciation(null);
      setIsEditingPronunciation(true);
    }
    setAdminModalOpen(true);
    if (autoRecord) {
      setTimeout(() => startRecordingVoice(word), 300);
    }
  };

  // Real-time bidirectional synchronization handlers
  const handleDevaChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    const syncedRoman = devanagariToRoman(val);
    setAdminWordForm((prev) => ({
      ...prev,
      preferred_pronunciation: val,
      phonetic_form: syncedRoman
    }));
  };

  const handleRomanChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    const syncedDeva = romanToDevanagari(val);
    setAdminWordForm((prev) => ({
      ...prev,
      phonetic_form: val,
      preferred_pronunciation: syncedDeva
    }));
  };

  const handleInsertMatraTablet = (tablet: MatraTablet) => {
    const inputEl = devaInputRef.current;
    const currentText = adminWordForm.preferred_pronunciation || "";
    const cursorPos = inputEl ? inputEl.selectionStart ?? currentText.length : currentText.length;

    const { newText, newCursor, notification } = insertMatraSmartly(currentText, cursorPos, tablet);

    if (notification) {
      toast.info(notification, { duration: 2500 });
    }

    const syncedRoman = devanagariToRoman(newText);
    setAdminWordForm((prev) => ({
      ...prev,
      preferred_pronunciation: newText,
      phonetic_form: syncedRoman
    }));

    setTimeout(() => {
      if (inputEl) {
        inputEl.focus();
        inputEl.setSelectionRange(newCursor, newCursor);
      }
    }, 10);
  };

  // Decode Voice Pronunciation Acoustic Analysis Pipeline (§5, §6)
  const decodeVoiceAudio = async (audioBlob: Blob, targetWord: string) => {
    setIsDecodingVoice(true);
    try {
      const reader = new FileReader();
      reader.readAsDataURL(audioBlob);
      reader.onloadend = async () => {
        try {
          const base64Audio = reader.result as string;
          const res = await fetch("/api/pronunciation/decode-voice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              canonical_text: targetWord,
              audio_base64: base64Audio,
              audio_format: "webm"
            })
          });
          const data = await res.json();
          if (res.ok && data.status === "success") {
            setDecodedPronunciation({
              canonical_text: data.canonical_text,
              lexical_identity: data.lexical_identity,
              spoken_transcript: data.spoken_transcript || data.canonical_text,
              is_canonical_match: data.is_canonical_match ?? true,
              detected_pronunciation: data.detected_pronunciation,
              preferred_pronunciation: data.preferred_pronunciation,
              phonetic_form: data.phonetic_form,
              syllable_boundaries: data.syllable_boundaries || [],
              phoneme_sequence: data.phoneme_sequence || [],
              confidence: data.confidence || 0.95,
              acoustic_metrics: data.acoustic_metrics
            });
            setAdminWordForm((prev) => ({
              ...prev,
              preferred_pronunciation: data.preferred_pronunciation || prev.preferred_pronunciation,
              phonetic_form: data.detected_pronunciation || prev.phonetic_form
            }));
            setIsEditingPronunciation(false);
            if (data.is_canonical_match === false) {
              toast.info(`दुरुस्त उच्चार ओळखला: '${data.spoken_transcript}' (मार्गदर्शक: ${data.preferred_pronunciation})`);
            } else {
              toast.success(`उच्चार ओळखला: '${data.spoken_transcript || data.preferred_pronunciation}' (${data.detected_pronunciation})`);
            }
          } else {
            toast.error(data.detail || "उच्चार विश्लेषण अयशस्वी.");
          }
        } catch (e) {
          console.error("Decode voice error:", e);
          toast.error("उच्चार विश्लेषण करताना त्रुटी आली.");
        } finally {
          setIsDecodingVoice(false);
        }
      };
    } catch (err) {
      console.error("Error reading audio:", err);
      setIsDecodingVoice(false);
    }
  };

  // Start Voice-Based Pronunciation Teaching Recording (§5, §6)
  const startRecordingVoice = async (wordOverride?: string) => {
    const targetWord = wordOverride || adminWordForm.canonical_text;
    try {
      if (typeof navigator !== "undefined" && navigator.mediaDevices?.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data);
          }
        };

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
          setRecordedAudioBlob(audioBlob);
          setRecordedAudioUrl(URL.createObjectURL(audioBlob));
          stream.getTracks().forEach((track) => track.stop());
          decodeVoiceAudio(audioBlob, targetWord);
        };

        mediaRecorder.start();
        setIsRecordingVoice(true);
      } else {
        throw new Error("getUserMedia not supported");
      }
    } catch (err) {
      console.warn("Microphone hardware fallback:", err);
      // Simulated audio recording for environments without mic hardware
      setIsRecordingVoice(true);
      setTimeout(() => {
        setIsRecordingVoice(false);
        const dummyBlob = new Blob(["RIFF....WAVEfmt....data...."], { type: "audio/webm" });
        setRecordedAudioBlob(dummyBlob);
        setRecordedAudioUrl(URL.createObjectURL(dummyBlob));
        toast.info("चाचणी उच्चार रेकॉर्डिंग पूर्ण झाले (Reference Audio Captured).");
        decodeVoiceAudio(dummyBlob, targetWord);
      }, 1200);
    }
  };

  // Stop Voice Recording
  const stopRecordingVoice = () => {
    if (mediaRecorderRef.current && isRecordingVoice) {
      mediaRecorderRef.current.stop();
      setIsRecordingVoice(false);
    } else {
      setIsRecordingVoice(false);
    }
  };

  // Save Admin Pronunciation (Voice Reference + Decoded Phonetic Representation)
  const handleSavePronunciation = async () => {
    setSavingPron(true);
    try {
      if (recordedAudioBlob) {
        // 1. Voice-based pronunciation teaching workflow (§5, §6, §7)
        const reader = new FileReader();
        reader.readAsDataURL(recordedAudioBlob);
        reader.onloadend = async () => {
          try {
            const base64Audio = reader.result as string;
            const res = await fetch("/api/pronunciation/record-voice", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                canonical_text: adminWordForm.canonical_text,
                audio_base64: base64Audio,
                preferred_pronunciation: adminWordForm.preferred_pronunciation,
                phonetic_form: adminWordForm.phonetic_form,
                notes: adminWordForm.notes,
                scope: adminWordForm.scope
              })
            });
            const data = await res.json();
            if (res.ok) {
              audioCacheRef.current.clear();
              toast.success(
                data.message || `उच्चार यशस्वीरित्या मंजूर झाला! निवडलेल्या व्याप्तीमध्ये (${adminWordForm.scope}) हा उच्चार आपोआप लागू होईल.`
              );
              setAdminModalOpen(false);
              setSelectedWord(null);
              setRecordedAudioBlob(null);
              setRecordedAudioUrl(null);
            } else {
              toast.error(data.detail || "उच्चार सेव्ह करताना त्रुटी आली.");
            }
          } finally {
            setSavingPron(false);
          }
        };
      } else {
        // 2. Standard Phonetic guide save
        const res = await fetch("/api/pronunciation", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(adminWordForm)
        });
        const data = await res.json();
        if (res.ok) {
          audioCacheRef.current.clear();
          toast.success(`'${adminWordForm.canonical_text}' चा उच्चार सेव्ह झाला!`);
          setAdminModalOpen(false);
          setSelectedWord(null);
        } else {
          toast.error(data.detail || "उच्चार सेव्ह करताना त्रुटी आली.");
        }
        setSavingPron(false);
      }
    } catch (err) {
      console.error(err);
      toast.error("उच्चार सेव्ह करताना त्रुटी आली.");
      setSavingPron(false);
    }
  };

  // Test Pronunciation Audio
  const handleTestPronunciation = async (overrideText?: string) => {
    setTestingPron(true);
    try {
      const textToTest = (overrideText || adminWordForm.preferred_pronunciation || adminWordForm.canonical_text || "").trim();
      if (!textToTest) {
        toast.warning("उच्चार करण्यासाठी शब्द उपलब्ध नाही.");
        return;
      }

      const payload = {
        ...adminWordForm,
        preferred_pronunciation: textToTest
      };

      toast.info(`'${textToTest}' ध्वनी चाचणी लोड होत आहे...`);
      const res = await fetch("/api/pronunciation/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.status === "success" && data.audio_base64) {
        if (testAudioRef.current) {
          testAudioRef.current.pause();
          testAudioRef.current = null;
        }
        const audio = new Audio("data:audio/wav;base64," + data.audio_base64);
        testAudioRef.current = audio;
        setIsPlayingTestAudio(true);
        audio.onended = () => setIsPlayingTestAudio(false);
        audio.onerror = () => {
          setIsPlayingTestAudio(false);
          toast.error("ऑडिओ प्ले करताना त्रुटी आली.");
        };
        await audio.play();
        toast.success(`'${textToTest}' उच्चार ऐकवला जात आहे!`);
      } else {
        toast.error(data.message || data.detail || "ऑडिओ तयार करताना त्रुटी आली.");
      }
    } catch (err: any) {
      console.error("Test pronunciation error:", err);
      toast.error(`ऑडिओ चाचणी अयशस्वी: ${err?.message || "नेटवर्क त्रुटी"}`);
    } finally {
      setTestingPron(false);
    }
  };

  const ctrl = "grid h-12 w-12 place-items-center rounded-full transition hover:bg-accent cursor-pointer";

  // ─── TTS speak helper for VA responses ──────────────────────────────────────
  const speakVAResponse = useCallback(
    (text: string) => {
      setVaResponseMsg(text);
      if (vaResponseTimerRef.current) clearTimeout(vaResponseTimerRef.current);
      // Speak using TTS
      fetch("/api/tts/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, speaker, provider: ttsProvider, style: "teacher", pace: 1.05 })
      })
        .then((r) => r.json())
        .then((d) => {
          if (d.audio_base64) {
            // Stop current reading audio before speaking response
            if (audioRef.current) {
              audioRef.current.pause();
            }
            const a = new Audio("data:audio/wav;base64," + d.audio_base64);
            a.play().catch(console.debug);
          }
        })
        .catch(console.debug);
      vaResponseTimerRef.current = setTimeout(() => setVaResponseMsg(null), 5000);
    },
    [speaker, ttsProvider]
  );

  // ─── Voice Assistant Command Handler ────────────────────────────────────────
  const handleVACommand = useCallback(
    (result: VAResult) => {
      const response = getVAResponse(result.command);
      speakVAResponse(response);

      switch (result.command) {
        case "play":
          if (isCompleted) {
            setActiveBlockIndex(0);
            setIsCompleted(false);
          }
          setPlaying(true);
          break;

        case "pause":
        case "stop":
          setPlaying(false);
          break;

        case "repeat":
          setTutorSegmentIndex(0);
          setActiveTurnId(null);
          setIsCompleted(false);
          setPlaying(true);
          break;

        case "explain":
          setTutor(true);
          setTutorSegmentIndex(1);
          setIsCompleted(false);
          setPlaying(true);
          break;

        case "go_slow":
          setSpeed((s) => {
            const idx = SPEEDS.indexOf(s);
            return idx > 0 ? SPEEDS[idx - 1] : SPEEDS[0];
          });
          audioCacheRef.current.clear();
          break;

        case "go_fast":
          setSpeed((s) => {
            const idx = SPEEDS.indexOf(s);
            return idx < SPEEDS.length - 1 ? SPEEDS[idx + 1] : SPEEDS[SPEEDS.length - 1];
          });
          audioCacheRef.current.clear();
          break;

        case "normal_speed":
          setSpeed(1);
          audioCacheRef.current.clear();
          break;

        case "next_block":
          setActiveBlockIndex((prev) => {
            const next = Math.min(prev + 1, allBlocks.length - 1);
            return next;
          });
          setActiveTurnId(null);
          setTutorSegmentIndex(0);
          break;

        case "prev_block":
          setActiveBlockIndex((prev) => Math.max(prev - 1, 0));
          setActiveTurnId(null);
          setTutorSegmentIndex(0);
          break;

        case "next_page":
          if (hasNextPage) {
            jumpToPageIndex(currentPageIndex + 1);
            window.scrollTo({ top: 0, behavior: "smooth" });
          } else {
            speakVAResponse("हे शेवटचे पान आहे.");
          }
          break;

        case "prev_page":
          if (hasPrevPage) {
            jumpToPageIndex(currentPageIndex - 1);
            window.scrollTo({ top: 0, behavior: "smooth" });
          } else {
            speakVAResponse("हे पहिले पान आहे.");
          }
          break;

        case "tutor_on":
          setTutor(true);
          setTutorSegmentIndex(0);
          break;

        case "tutor_off":
          setTutor(false);
          setTutorSegmentIndex(0);
          break;

        case "restart":
          setActiveBlockIndex(0);
          setActiveTurnId(null);
          setTutorSegmentIndex(0);
          setIsCompleted(false);
          setPlaying(true);
          window.scrollTo({ top: 0, behavior: "smooth" });
          break;

        case "go_to_page": {
          const pageNum = parseInt(result.payload || "1", 10);
          const targetPage = pages.find((p) => (p.printed_page || 0) === pageNum || p.pdf_page === pageNum + 9);
          if (targetPage) {
            jumpToPage(targetPage.pdf_page);
            window.scrollTo({ top: 0, behavior: "smooth" });
          } else {
            speakVAResponse(`पान ${pageNum} उपलब्ध नाही.`);
          }
          break;
        }

        case "ask_question":
          if (result.payload) {
            setTutorInput(result.payload);
            handleAskTutorQuestion(result.payload);
            // Scroll to tutor section
            setTimeout(() => {
              document.getElementById("va-tutor-section")?.scrollIntoView({ behavior: "smooth" });
            }, 500);
          }
          break;

        case "help":
          toast.info("Voice commands: वाचा, थांबा, पुन्हा सांग, समजावून सांग, हळू बोल, जलद बोल, पुढे जा, मागे जा, पुढील पान, मागील पान", { duration: 7000 });
          break;

        case "sleep":
          toast.info("'Hey AksharSetu' म्हणा परत सुरू करण्यासाठी.");
          break;

        default:
          break;
      }
    },
    [allBlocks, isCompleted, hasNextPage, hasPrevPage, currentPageIndex, pages, jumpToPageIndex, jumpToPage, speakVAResponse]
  );

  const handleVAWakeWord = useCallback(() => {
    // No-op: always-on mode, no wake word needed
  }, []);

  const { vaState, rawTranscript, errorMsg: vaError, activate: vaActivate } = useVoiceAssistant({
    enabled: vaEnabled,
    lang: "hi-IN",
    onCommand: handleVACommand,
    onWakeWord: handleVAWakeWord,
  });

  return (
    <TooltipProvider delayDuration={150}>
      <Page
        title={chapterMeta.title}
        intro={`${chapterMeta.subject} · Printed Page ${activePageData.printed_page || (activePageData.pdf_page ? activePageData.pdf_page - 9 : 1)} (PDF p. ${activePageData.pdf_page || 10}) · Total ${pages.length || 1} Pages`}
      >
        {/* Navigation & Controls Toolbar */}
        <div className="-mt-4 mb-6 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-3">
            <CorpusChip status="verified" />
            <span className="text-sm text-muted-foreground">
              {pages.length > 1 ? `Page ${pages.findIndex((p) => p.pdf_page === activePdfPage) + 1} of ${pages.length}` : "Verified Textbook"}
            </span>

            {/* Textbook Switcher */}
            <select
              value={selectedBookKey}
              onChange={(e) => {
                setSelectedBookKey(e.target.value);
                setActiveBlockIndex(0);
                setActiveTurnId(null);
                setPlaying(false);
                setIsCompleted(false);
              }}
              className="rounded-lg border bg-card px-2.5 py-1 text-xs font-semibold text-foreground focus-visible:border-primary cursor-pointer"
              aria-label="Switch textbook chapter"
            >
              <optgroup label="🔬 इयत्ता आठवी — सामान्य विज्ञान (General Science Reference)">
                {SCIENCE_CHAPTERS.map((ch) => (
                  <option key={ch.id} value={`science-8-ch${ch.number}`}>
                    विज्ञान {ch.title} ({ch.titleEn})
                  </option>
                ))}
              </optgroup>
              <optgroup label="🌟 इयत्ता आठवी — इतिहास (History Reference Implementation)">
                {HISTORY_CHAPTERS.map((ch) => (
                  <option key={ch.id} value={`history-8-ch${ch.number}`}>
                    इतिहास {ch.title} ({ch.titleEn})
                  </option>
                ))}
              </optgroup>
              <optgroup label="इतर पाठ्यपुस्तके (Other Subjects)">
                <option value="geo-10">भूगोल १० वी · Ch 1 (क्षेत्रभेट · Complete 8 Pages)</option>
                <option value="geo-10-ch2">भूगोल १० वी · Ch 2 (स्थान-विस्तार)</option>
                <option value="akshar-10">अक्षरभारती १० वी · Ch 1 (प्रार्थना · तू बुद्धी दे)</option>
              </optgroup>
            </select>

            {/* Page Jump Selector */}
            {pages.length > 1 && (
              <div className="flex items-center gap-1 rounded-lg border bg-card px-2 py-0.5 text-xs font-semibold">
                <span className="text-muted-foreground">पान:</span>
                <select
                  value={activePdfPage}
                  onChange={(e) => jumpToPage(Number(e.target.value))}
                  className="bg-transparent font-bold text-primary focus:outline-none cursor-pointer"
                  aria-label="Jump to chapter page"
                >
                  {pages.map((p, idx) => (
                    <option key={p.pdf_page} value={p.pdf_page}>
                      पृष्ठ {p.printed_page || idx + 1} (PDF {p.pdf_page})
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Pluggable TTS Provider (§13, §14) */}
            <select
              value={ttsProvider}
              onChange={(e) => {
                setTtsProvider(e.target.value);
                audioCacheRef.current.clear();
              }}
              className="rounded-lg border bg-card px-2 py-1 text-xs font-semibold text-foreground cursor-pointer"
              aria-label="TTS Engine Provider"
              title="TTS Engine Provider"
            >
              <option value="sarvam">⚡ Sarvam AI (bulbul:v3)</option>
              <option value="indicf5">🔬 IndicF5 (Experimental Local Engine)</option>
            </select>

            {/* Narrator Voice */}
            <select
              value={speaker}
              onChange={(e) => {
                setSpeaker(e.target.value);
                audioCacheRef.current.clear();
              }}
              className="rounded-lg border bg-card px-2.5 py-1 text-xs font-semibold text-foreground cursor-pointer"
              aria-label="Select narrator voice"
              title="वाचक आवाज (Narrator Voice)"
            >
              <option value="shreya">🎙️ श्रेया (Shreya · शिक्षक स्वर)</option>
              <option value="ritu">🎙️ रितू (Ritu · Clear)</option>
              <option value="priya">🎙️ प्रिया (Priya · Melodic)</option>
              <option value="shubh">🎙️ शुभ (Shubh · विद्यार्थी स्वर)</option>
            </select>
          </div>

          {/* Mode Switcher */}
          <div role="radiogroup" aria-label="Mode" className="flex rounded-xl border bg-card p-1">
            <button
              role="radio"
              aria-checked={!tutor}
              onClick={() => {
                setTutor(false);
                setTutorSegmentIndex(0);
              }}
              className={cn("flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold transition cursor-pointer", !tutor && "bg-primary text-primary-foreground")}
            >
              <BookOpenCheck className="h-4 w-4" aria-hidden /> Reading
            </button>
            <button
              role="radio"
              aria-checked={tutor}
              onClick={() => {
                setTutor(true);
                setTutorSegmentIndex(0);
              }}
              className={cn("flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-semibold transition cursor-pointer", tutor && "bg-tutor text-primary-foreground")}
            >
              <Sparkles className="h-4 w-4" aria-hidden /> Tutor
            </button>
          </div>

          {/* Voice Assistant Toggle */}
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => {
                  if (!vaEnabled) {
                    setVaEnabled(true);
                    toast.success("🎙️ Voice Assistant चालू! बोला — वाचा, थांबा, पुन्हा सांग...", { duration: 3000 });
                  } else {
                    setVaEnabled(false);
                    toast.info("Voice Assistant बंद.");
                  }
                }}
                className={cn(
                  "relative flex items-center gap-1.5 rounded-xl border px-3 py-2 text-sm font-bold transition cursor-pointer shadow-xs",
                  vaEnabled
                    ? "border-emerald-400 bg-emerald-500 text-white"
                    : "border-muted-foreground/30 bg-card text-foreground hover:bg-muted"
                )}
                aria-label={vaEnabled ? "Voice Assistant बंद करा" : "Voice Assistant चालू करा"}
              >
                {vaEnabled && <span className="absolute inset-0 rounded-xl bg-emerald-400 animate-ping opacity-20" />}
                {vaEnabled ? <Mic className="h-4 w-4 relative z-10" /> : <MicOff className="h-4 w-4" />}
                <span className="hidden sm:inline relative z-10">
                  {vaEnabled ? "🎙 ऐकत आहे" : "Voice Off"}
                </span>
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs max-w-xs p-2">
              <p className="font-bold">Voice Assistant {vaEnabled ? "चालू — ऐकत आहे" : "बंद"}</p>
              <p className="text-muted-foreground mt-0.5">
                {vaEnabled
                  ? "बोला: वाचा, थांबा, पुन्हा सांग, समजावून सांग, हळू बोल, जलद बोल, पुढे जा, पुढील पान..."
                  : "क्लिक करा — Voice Assistant चालू करण्यासाठी"}
              </p>
            </TooltipContent>
          </Tooltip>
        </div>

        {/* Page Traversal Banner */}
        {pages.length > 1 && (
          <div className="mb-4 flex items-center justify-between rounded-xl border border-muted bg-muted/30 px-4 py-2 text-xs font-medium text-muted-foreground">
            <div className="flex items-center gap-2">
              <Layers className="h-4 w-4 text-primary" />
              <span>
                अध्याय १ · पृष्ठ {activePageData.printed_page || currentPageIndex + 1} of {pages.length} · {(activePageData.paragraphs || []).length} अर्थपूर्ण घटक (Semantic Blocks)
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <button
                disabled={!hasPrevPage}
                onClick={() => jumpToPageIndex(currentPageIndex - 1)}
                className="flex items-center gap-1 rounded-lg border bg-card px-2.5 py-1 font-semibold text-foreground hover:bg-accent disabled:opacity-30 cursor-pointer transition shadow-2xs"
                title="मागील पानावर जा"
              >
                <ChevronLeft className="h-3.5 w-3.5" /> मागील पान
              </button>
              <button
                disabled={!hasNextPage}
                onClick={() => jumpToPageIndex(currentPageIndex + 1)}
                className="flex items-center gap-1 rounded-lg bg-primary px-3 py-1 font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-30 cursor-pointer transition shadow-2xs"
                title="पुढील पानावर जा"
              >
                पुढील पान <ChevronRight className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* Accessible Learning Units Navigation Strip */}
        {remoteChapter?.manifest?.learning_units && remoteChapter.manifest.learning_units.length > 0 && (
          <nav aria-label="Learning Units" className="mb-5 rounded-2xl border bg-card/60 p-3 shadow-xs">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2 pb-1.5 border-b">
              <span className="text-xs font-bold text-primary flex items-center gap-1.5">
                <BookOpen className="h-4 w-4" />
                अध्ययन घटक (Learning Units · {remoteChapter.manifest.learning_units.length})
              </span>
              <span className="text-xs text-muted-foreground">{chapterMeta.title}</span>
            </div>
            <div className="flex flex-wrap gap-1.5" role="tablist" aria-label="Learning units list">
              {remoteChapter.manifest.learning_units.map((unitTitle: string, uIdx: number) => {
                const matchingIdx = allBlocks.findIndex((b) => b.canonical_text.includes(unitTitle) || (b.tutor && b.tutor.includes(unitTitle)));
                const isSelected = matchingIdx !== -1 && activeBlockIndex >= matchingIdx;
                return (
                  <button
                    key={uIdx}
                    role="tab"
                    aria-selected={isSelected}
                    onClick={() => {
                      const targetIdx = matchingIdx !== -1 ? matchingIdx : 0;
                      playBlock(targetIdx);
                      toast.info(`अध्ययन घटक: ${unitTitle}`);
                    }}
                    className={cn(
                      "rounded-lg border px-2.5 py-1 text-xs font-medium transition cursor-pointer text-left",
                      isSelected
                        ? "bg-primary text-primary-foreground border-primary shadow-xs"
                        : "bg-background hover:bg-muted text-foreground"
                    )}
                  >
                    {uIdx + 1}. {unitTitle}
                  </button>
                );
              })}
            </div>
          </nav>
        )}

        {/* Chapter Completion State */}
        {isCompleted ? (
          <section className="my-8 rounded-3xl border-2 border-primary/30 bg-primary/5 p-8 text-center shadow-soft">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h2 className="mt-4 text-2xl font-bold text-foreground">अभ्यासक्रम पूर्ण झाला! (Chapter Completed)</h2>
            <p className="deva mt-2 text-muted-foreground">
              {chapterMeta.title} मधील सर्व {pages.length} पृष्ठे आणि घटक पूर्ण वाचून झाले आहेत.
            </p>
            <div className="mt-6 flex justify-center gap-3">
              <button
                onClick={() => {
                  setActiveBlockIndex(0);
                  setActiveTurnId(null);
                  setIsCompleted(false);
                  setPlaying(true);
                }}
                className="rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow transition hover:opacity-90 cursor-pointer"
              >
                पुन्हा सुरु करा (Start Over)
              </button>
              <button
                onClick={() => {
                  setSelectedBookKey("akshar-10");
                  setActiveBlockIndex(0);
                  setActiveTurnId(null);
                  setIsCompleted(false);
                }}
                className="rounded-xl border bg-card px-5 py-2.5 text-sm font-semibold transition hover:bg-accent cursor-pointer"
              >
                पुढील पाठ (Next Textbook)
              </button>
            </div>
          </section>
        ) : (
          /* Main Semantic Blocks List */
          <article className="space-y-6" aria-label="Textbook content">
            {(activePageData?.paragraphs || []).map((block, bIdx) => {
              const isActiveBlock = currentBlock.id === block.id;

              // -------------------------------------------------------------
              // 1. DIALOGUE BLOCK RENDERING (§5)
              // -------------------------------------------------------------
              if (block.block_type === "dialogue_block" && block.dialogue_turns.length > 0) {
                return (
                  <section
                    key={block.id}
                    className={cn(
                      "rounded-2xl border bg-card p-5 shadow-soft transition-all space-y-4",
                      isActiveBlock && "border-primary/50 ring-1 ring-primary/20 shadow-md"
                    )}
                  >
                    <div className="flex items-center justify-between border-b pb-2">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4 text-primary" />
                        <span className="text-xs font-bold text-primary uppercase tracking-wide">
                          संभाषण (Textbook Conversation) · {block.dialogue_turns.length} संवाद टप्पे
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => playBlock(allBlocks.findIndex((b) => b.id === block.id))}
                          className="flex items-center gap-1 rounded-lg bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary hover:bg-primary/20 transition cursor-pointer"
                        >
                          <Play className="h-3.5 w-3.5" /> संभाषण ऐका (Play Conversation)
                        </button>
                        <button
                          onClick={() => {
                            setActiveBlockIndex(allBlocks.findIndex((b) => b.id === block.id));
                            setTutor(true);
                            setTutorSegmentIndex(1);
                            setPlaying(true);
                          }}
                          className="flex items-center gap-1 rounded-lg bg-tutor/10 px-2.5 py-1 text-xs font-semibold text-tutor hover:bg-tutor/20 transition cursor-pointer"
                        >
                          <Sparkles className="h-3.5 w-3.5" /> स्पष्टीकरण
                        </button>
                      </div>
                    </div>

                    {/* Dialogue Turns */}
                    <div className="space-y-3 pt-1">
                      {block.dialogue_turns.map((turn) => {
                        const isTeacher = turn.speaker_role === "teacher";
                        const isSpeakingTurn = isActiveBlock && activeTurnId === turn.turn_id;
                        return (
                          <div
                            key={turn.turn_id}
                            className={cn(
                              "flex gap-3 p-3 rounded-xl transition-all",
                              isTeacher ? "bg-muted/40 border-l-4 border-l-primary" : "bg-card border border-muted/60 ml-4",
                              isSpeakingTurn && "bg-highlight/40 ring-1 ring-primary/30"
                            )}
                          >
                            <div className="mt-0.5 shrink-0">
                              <span
                                className={cn(
                                  "inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold",
                                  isTeacher ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
                                )}
                              >
                                {isTeacher ? "👩‍🏫 शिक्षिका" : `🎒 ${turn.speaker}`}
                              </span>
                            </div>
                            <div className="deva text-lg leading-relaxed flex-1">
                              {turn.text.split(" ").map((w, wIdx) => (
                                <span
                                  key={wIdx}
                                  onClick={() => handleWordClick(w)}
                                  className="cursor-pointer hover:underline hover:text-primary transition-colors px-0.5 rounded"
                                  title="उच्चार व दुरुस्तीसाठी क्लिक करा"
                                >
                                  {w}{" "}
                                </span>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Tutor Explanation Card for Dialogue */}
                    {tutor && block.tutor_explanation && isActiveBlock && (
                      <aside className="rounded-xl border border-dashed border-tutor/60 bg-tutor-soft p-4 mt-2">
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-tutor px-2.5 py-0.5 text-xs font-semibold text-primary-foreground">
                          <Sparkles className="h-3 w-3" /> शिक्षक स्पष्टीकरण (Dialogue Pedagogy)
                        </span>
                        <p className="deva mt-2 text-base text-tutor-foreground">
                          {block.tutor_explanation}
                        </p>
                      </aside>
                    )}
                  </section>
                );
              }

              // -------------------------------------------------------------
              // 2. STANDARD PARAGRAPH / PROSE / HEADING RENDERING (§1, §17)
              // -------------------------------------------------------------
              return (
                <section
                  key={block.id}
                  className={cn(
                    "rounded-2xl border bg-card p-5 shadow-soft transition-all space-y-3",
                    isActiveBlock && "border-primary/50 ring-1 ring-primary/20 shadow-md",
                    block.block_type === "heading" && "bg-muted/20 border-primary/30"
                  )}
                >
                  {/* Block Header Toolbar */}
                  <div className="flex items-center justify-between text-xs text-muted-foreground border-b pb-2">
                    <span className="font-semibold capitalize">
                      {block.block_type === "heading" ? "📌 मुख्य शीर्षक (Heading)" :
                       block.block_type === "subheading" ? "⏱️ वेळ व टप्पा (Subheading)" :
                       block.block_type === "discussion" ? "💭 चर्चा व विचार करा (Discussion)" :
                       block.block_type === "poetry_stanza" ? "🎵 काव्य कडवे (Stanza)" :
                       block.block_type === "definition" ? "📖 शब्दार्थ (Vocabulary)" :
                       `परिच्छेद ${bIdx + 1}`}
                    </span>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => playBlock(allBlocks.findIndex((b) => b.id === block.id))}
                        className="flex items-center gap-1 rounded-lg bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary hover:bg-primary/20 transition cursor-pointer"
                        title="Play this complete paragraph naturally"
                      >
                        <Play className="h-3.5 w-3.5" /> परिच्छेद वाचा (Read Paragraph)
                      </button>
                      <button
                        onClick={() => {
                          setActiveBlockIndex(allBlocks.findIndex((b) => b.id === block.id));
                          setTutor(true);
                          setTutorSegmentIndex(1);
                          setPlaying(true);
                        }}
                        className="flex items-center gap-1 rounded-lg bg-tutor/10 px-2.5 py-1 text-xs font-semibold text-tutor hover:bg-tutor/20 transition cursor-pointer"
                        title="Explain this concept in simple Marathi"
                      >
                        <Sparkles className="h-3.5 w-3.5" /> समजावून सांगा
                      </button>
                    </div>
                  </div>

                  {/* Paragraph Body with Clickable Words for Pronunciation */}
                  <p
                    className={cn(
                      "deva text-xl leading-relaxed text-foreground",
                      block.block_type === "heading" && "text-2xl font-bold text-primary",
                      block.block_type === "subheading" && "text-lg font-semibold text-muted-foreground italic"
                    )}
                  >
                    {block.canonical_text.split(" ").map((w, wIdx) => {
                      const isHighlighted = isActiveBlock && playing && (!tutor || tutorSegmentIndex === 0);
                      return (
                        <span
                          key={wIdx}
                          onClick={() => handleWordClick(w)}
                          className={cn(
                            "cursor-pointer hover:bg-accent/60 rounded px-0.5 transition-colors",
                            isHighlighted && "bg-highlight/30 font-medium"
                          )}
                          title="उच्चार तपासण्यासाठी व दुरुस्तीसाठी क्लिक करा"
                        >
                          {w}{" "}
                        </span>
                      );
                    })}
                  </p>

                  {/* ------------------------------------------------------------- */}
                  {/* 3. SUPPORTING VISUALS / MAPS (§3, §4) */}
                  {/* Visually attached without interrupting primary text flow */}
                  {/* ------------------------------------------------------------- */}
                  {block.supporting_visuals && block.supporting_visuals.length > 0 && (
                    <div className="pt-2 space-y-2">
                      {block.supporting_visuals.map((vis) => (
                        <div
                          key={vis.material_id}
                          className="flex items-center justify-between rounded-xl border border-primary/20 bg-primary/5 p-3 text-xs"
                        >
                          <div className="flex items-center gap-2.5">
                            <div className="rounded-lg bg-primary/10 p-2 text-primary">
                              <MapPin className="h-4 w-4" />
                            </div>
                            <div>
                              <p className="font-bold text-foreground deva text-sm">{vis.title}</p>
                              <p className="text-muted-foreground deva">{vis.caption_text}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => setVisualModal(vis)}
                            className="flex items-center gap-1 rounded-lg border bg-card px-3 py-1.5 font-semibold text-primary hover:bg-accent transition cursor-pointer"
                          >
                            <ExternalLink className="h-3.5 w-3.5" /> नकाशा विश्लेषण (Explain Map)
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Tutor Explanation Card */}
                  {tutor && block.tutor_explanation && isActiveBlock && (
                    <aside className="rounded-xl border border-dashed border-tutor/60 bg-tutor-soft p-4 mt-2">
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-tutor px-2.5 py-0.5 text-xs font-semibold text-primary-foreground">
                        <Sparkles className="h-3 w-3" /> शिक्षक स्पष्टीकरण (Pedagogical Explanation)
                      </span>
                      <p className="deva mt-2 text-base text-tutor-foreground">
                        {block.tutor_explanation}
                      </p>
                    </aside>
                  )}
                </section>
              );
            })}
          </article>
        )}

        {/* ------------------------------------------------------------- */}
        {/* BOTTOM PAGE NAVIGATION BAR                                    */}
        {/* Allows seamless flipping to next/previous page while reading  */}
        {/* ------------------------------------------------------------- */}
        {pages.length > 1 && (
          <nav aria-label="Page navigation" className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl border bg-card/80 p-4 shadow-sm backdrop-blur">
            <button
              disabled={!hasPrevPage}
              onClick={() => {
                jumpToPageIndex(currentPageIndex - 1);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="flex items-center gap-2 rounded-xl border bg-background px-4 py-2 text-sm font-semibold hover:bg-accent disabled:opacity-30 cursor-pointer transition"
            >
              <ChevronLeft className="h-4 w-4" /> मागील पान {hasPrevPage && `(पृष्ठ ${pages[currentPageIndex - 1]?.printed_page || currentPageIndex})`}
            </button>

            <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
              <span>पृष्ठ {activePageData.printed_page || currentPageIndex + 1} / {pages.length}</span>
              <span className="text-muted-foreground/60">·</span>
              <span className="font-mono text-primary font-bold">PDF पान {activePdfPage}</span>
            </div>

            <button
              disabled={!hasNextPage}
              onClick={() => {
                jumpToPageIndex(currentPageIndex + 1);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 disabled:opacity-30 cursor-pointer transition shadow-xs"
            >
              पुढील पान {hasNextPage && `(पृष्ठ ${pages[currentPageIndex + 1]?.printed_page || currentPageIndex + 2})`} <ChevronRight className="h-4 w-4" />
            </button>
          </nav>
        )}

        {/* ------------------------------------------------------------- */}
        {/* GROUNDED AI TUTOR INTERACTIVE Q&A (§18)                       */}
        {/* Strictly bounded to current chapter, learning unit & pages    */}
        {/* ------------------------------------------------------------- */}
        <section id="va-tutor-section" className="mt-8 rounded-2xl border-2 border-primary/30 bg-gradient-to-br from-card via-card to-primary/5 p-6 shadow-sm">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between border-b pb-4">
            <div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-bold text-primary">
                <Sparkles className="h-3.5 w-3.5" aria-hidden /> GROUNDED AI TUTOR · शिक्षक मार्गदर्शन
              </span>
              <h3 className="deva mt-1 text-xl font-bold text-foreground">
                पाठ्यपुस्तकावर आधारित प्रश्न विचारा (Grounded Tutor Q&A)
              </h3>
              <p className="text-xs text-muted-foreground">
                Questions are strictly retrieved and grounded from Chapter {chapterMeta.title} with explicit provenance.
              </p>
            </div>
            <span className="rounded bg-muted px-2 py-1 text-xs font-mono text-muted-foreground">
              Audible Cue Enabled
            </span>
          </div>

          {/* Quick Suggestions */}
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-xs font-semibold text-muted-foreground self-center mr-1">उदाहरणे:</span>
            {[
              "भौतिक साधने म्हणजे काय?",
              "लिखित साधनांची उदाहरणे कोणती?",
              "मौखिक साधनांमध्ये कशाचा समावेश होतो?"
            ].map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => {
                  setTutorInput(q);
                  handleAskTutorQuestion(q);
                }}
                className="rounded-lg border bg-card px-3 py-1 text-xs text-foreground font-medium transition hover:border-primary/50 hover:bg-accent cursor-pointer"
              >
                {q}
              </button>
            ))}
          </div>

          {/* Question Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleAskTutorQuestion(tutorInput);
            }}
            className="mt-4 flex gap-2"
          >
            <input
              type="text"
              value={tutorInput}
              onChange={(e) => setTutorInput(e.target.value)}
              placeholder="प्रकरणानुसार प्रश्न विचारा (उदा. भौतिक साधने म्हणजे काय?)..."
              className="flex-1 rounded-xl border bg-background px-4 py-2.5 text-sm text-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
            />
            <button
              type="submit"
              disabled={tutorQueryLoading || !tutorInput.trim()}
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow transition hover:opacity-90 disabled:opacity-50 cursor-pointer"
            >
              {tutorQueryLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
              विचारा (Ask)
            </button>
          </form>

          {/* Tutor Result with Explicit Provenance */}
          {tutorQnAResult && (
            <div className="mt-5 space-y-4 rounded-xl border border-primary/30 bg-card p-5 animate-in fade-in-50 duration-200">
              {/* Provenance Pill */}
              <div className="flex flex-wrap items-center justify-between gap-2 border-b pb-3">
                <span className="inline-flex items-center gap-1.5 text-xs font-bold text-primary">
                  <ShieldCheck className="h-4 w-4" /> Based on: {tutorQnAResult.chapter_title} · Learning Unit: {tutorQnAResult.learning_unit_title}
                </span>
                <span className="text-[11px] font-mono text-muted-foreground bg-muted px-2 py-0.5 rounded">
                  Source Status: {tutorQnAResult.provenance?.source_status || "SOURCE_VERIFIED"}
                </span>
              </div>

              {/* 1. Canonical Reference */}
              <div className="space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-muted-foreground">
                  १. मूळ पाठ्यपुस्तक संदर्भ (Canonical Grounding)
                </span>
                <p className="deva text-base font-medium text-foreground bg-muted/30 p-3 rounded-lg border">
                  {tutorQnAResult.canonical_reference}
                </p>
              </div>

              {/* 2. Pedagogical Transition & Explanation */}
              <div className="space-y-1">
                <span className="text-[11px] font-bold uppercase tracking-wider text-tutor">
                  २. शिक्षकांचे स्पष्टीकरण (Pedagogical Explanation)
                </span>
                <p className="deva text-base text-tutor-foreground bg-tutor-soft p-3 rounded-lg border border-dashed border-tutor/40">
                  {tutorQnAResult.pedagogical_explanation}
                </p>
              </div>

              {/* Audio Listen Button */}
              <div className="flex items-center justify-between pt-1">
                <button
                  type="button"
                  onClick={() => {
                    const textToSpeak = `${tutorQnAResult.canonical_reference}. आता स्पष्टीकरण ऐका: ${tutorQnAResult.pedagogical_explanation}`;
                    fetch("/api/tts/synthesize", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        text: textToSpeak,
                        is_tutor: true,
                        speaker,
                        provider: ttsProvider,
                        style: "explanatory_teacher"
                      })
                    })
                      .then((r) => r.json())
                      .then((d) => {
                        if (d.audio_base64) {
                          playAudibleCue();
                          const a = new Audio("data:audio/wav;base64," + d.audio_base64);
                          a.play();
                        }
                      });
                  }}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-tutor/10 px-3 py-1.5 text-xs font-semibold text-tutor hover:bg-tutor/20 transition cursor-pointer"
                >
                  <Volume2 className="h-4 w-4" /> स्पष्टीकरण ऐका (Listen to Explanation)
                </button>

                <span className="text-[11px] text-muted-foreground">
                  Audible Chime Played · Grounded RAG
                </span>
              </div>
            </div>
          )}
        </section>

        {/* Voice Commands Section */}
        <section className="mt-8 rounded-2xl border bg-card">
          <button
            className="flex w-full items-center justify-between p-4 font-semibold cursor-pointer"
            aria-expanded={cmdOpen}
            onClick={() => setCmdOpen(!cmdOpen)}
          >
            <span className="flex items-center gap-2">
              <Mic className="h-5 w-5 text-primary" aria-hidden /> Voice commands & Pronunciation Guide
            </span>
            <ChevronDown className={cn("h-5 w-5 transition", cmdOpen && "rotate-180")} aria-hidden />
          </button>
          {cmdOpen && (
            <ul className="grid gap-2 border-t p-4 sm:grid-cols-2">
              {VOICE_COMMANDS.map((c) => (
                <li key={c.say} className="flex justify-between gap-3 rounded-xl bg-muted px-3 py-2 text-sm">
                  <span className="deva font-semibold">“{c.say}”</span>
                  <span className="text-muted-foreground">{c.does}</span>
                </li>
              ))}
              <li className="text-sm text-muted-foreground sm:col-span-2">
                टीप: कोणत्याही शब्दावर क्लिक करून त्याचा फोनॅटिक उच्चार तपासता व दुरुस्त करता येतो.
              </li>
            </ul>
          )}
        </section>
      </Page>

      {/* Floating Bottom Audio Player Bar */}
      <div className="fixed inset-x-0 bottom-4 z-40 px-3">
        <div className="glass mx-auto flex max-w-2xl items-center gap-1 rounded-3xl px-3 py-2" role="region" aria-label="Audio player">
          <button
            className={ctrl}
            onClick={() => {
              if (activeBlockIndex > 0) setActiveBlockIndex((prev) => prev - 1);
            }}
            aria-label="Previous paragraph"
          >
            <SkipBack className="h-5 w-5" />
          </button>
          <button
            className="grid h-14 w-14 place-items-center rounded-full bg-primary text-primary-foreground shadow-soft transition hover:opacity-90 cursor-pointer"
            onClick={() => {
              if (isCompleted) {
                setActiveBlockIndex(0);
                setIsCompleted(false);
              }
              setPlaying(!playing);
            }}
            aria-label={playing ? "Pause" : "Play"}
          >
            {playing ? <Pause className="h-6 w-6" /> : <Play className="ml-0.5 h-6 w-6" />}
          </button>
          <button
            className={ctrl}
            onClick={() => {
              if (activeBlockIndex < allBlocks.length - 1) setActiveBlockIndex((prev) => prev + 1);
            }}
            aria-label="Next paragraph"
          >
            <SkipForward className="h-5 w-5" />
          </button>
          <button
            className={ctrl}
            onClick={() => {
              setTutorSegmentIndex(0);
              setPlaying(true);
            }}
            aria-label="Replay current paragraph"
          >
            <Repeat className="h-5 w-5" />
          </button>

          <div className="mx-2 hidden flex-1 sm:block" aria-hidden>
            <div className="h-1.5 rounded-full bg-muted">
              <div
                className="h-full rounded-full bg-primary transition-all"
                style={{ width: `${((activeBlockIndex + 1) / Math.max(1, allBlocks.length)) * 100}%` }}
              />
            </div>
            <p className="mt-1 text-xs text-muted-foreground truncate">
              घटक {activeBlockIndex + 1} of {allBlocks.length} · {currentBlock.block_type}
            </p>
          </div>

          <button
            className="ml-auto rounded-full border px-3 py-2 text-sm font-bold hover:bg-accent sm:ml-0 cursor-pointer"
            onClick={() => setSpeed(SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length])}
            aria-label={`Playback speed ${speed}x`}
          >
            {speed}×
          </button>
        </div>
      </div>

      {/* ─── Floating Voice Assistant Overlay (Always-On) ──────────────────── */}
      {vaEnabled && (
        <div className="fixed bottom-24 right-4 z-50 flex flex-col items-end gap-2">
          {/* Live interim transcript bubble — shows what you're saying */}
          {rawTranscript && (vaState === "listening" || vaState === "processing") && (
            <div className="max-w-[260px] rounded-2xl bg-black/85 backdrop-blur-sm px-4 py-2 text-sm text-white shadow-2xl animate-in slide-in-from-right-2 duration-150">
              <span className="text-[10px] text-white/50 block mb-0.5 uppercase tracking-wide">बोला...</span>
              <p className="font-medium leading-snug">{rawTranscript}</p>
            </div>
          )}

          {/* AksharSetu response bubble */}
          {vaResponseMsg && (
            <div className="max-w-[260px] rounded-2xl bg-primary px-4 py-2.5 text-sm text-primary-foreground shadow-2xl animate-in slide-in-from-right-2 duration-150">
              <span className="text-[10px] text-primary-foreground/60 block mb-0.5 uppercase tracking-wide">AksharSetu:</span>
              <p className="font-semibold leading-snug deva">{vaResponseMsg}</p>
            </div>
          )}

          {/* Mic orb — color/animation changes per state */}
          <div className="relative flex flex-col items-center gap-1">
            <button
              onClick={() => setVaEnabled(false)}
              title="Voice Assistant बंद करा"
              className={cn(
                "relative flex h-14 w-14 items-center justify-center rounded-full shadow-2xl border-2 transition-all duration-150 cursor-pointer select-none",
                vaState === "listening"
                  ? "bg-emerald-500 border-emerald-300 text-white"
                  : vaState === "processing"
                  ? "bg-amber-500 border-amber-300 text-white"
                  : vaState === "responding"
                  ? "bg-primary border-primary/60 text-primary-foreground scale-105"
                  : "bg-red-600 border-red-400 text-white"
              )}
            >
              {/* Soft always-on pulse ring for listening */}
              {vaState === "listening" && (
                <span className="absolute inset-0 rounded-full bg-emerald-400 animate-ping opacity-30" />
              )}
              {/* Fast pulse for processing */}
              {vaState === "processing" && (
                <span className="absolute inset-0 rounded-full bg-amber-300 animate-ping opacity-50" />
              )}
              <Mic className="h-6 w-6 relative z-10" />
            </button>

            {/* State pill */}
            <span className={cn(
              "text-[10px] font-bold px-2.5 py-0.5 rounded-full shadow-sm whitespace-nowrap",
              vaState === "listening" ? "bg-emerald-500 text-white" :
              vaState === "processing" ? "bg-amber-500 text-white" :
              vaState === "responding" ? "bg-primary text-primary-foreground" :
              "bg-red-500 text-white"
            )}>
              {vaState === "listening" ? "🎙 ऐकत आहे" :
               vaState === "processing" ? "⚙️ समजत आहे..." :
               vaState === "responding" ? "💬 बोलत आहे..." :
               "⚠️ Error"}
            </span>
          </div>
        </div>
      )}

      {/* Compact VA off button */}
      {!vaEnabled && (
        <button
          onClick={() => setVaEnabled(true)}
          title="Voice Assistant चालू करा"
          className="fixed bottom-24 right-4 z-50 flex h-12 w-12 items-center justify-center rounded-full border border-muted-foreground/20 bg-card text-muted-foreground shadow-lg hover:bg-emerald-50 hover:border-emerald-400 hover:text-emerald-600 transition cursor-pointer"
        >
          <MicOff className="h-5 w-5" />
        </button>
      )}

      {/* ------------------------------------------------------------- */}
      {/* WORD PRONUNCIATION POPOVER & ADMIN CORRECTION MODAL (§7, §8) */}
      {/* ------------------------------------------------------------- */}
      {selectedWord && (
        <Dialog open={!!selectedWord && !adminModalOpen} onOpenChange={() => setSelectedWord(null)}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="deva text-xl flex items-center justify-between">
                <span>शब्द उच्चार (Word Pronunciation)</span>
                {selectedWord.entry?.approved && (
                  <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full font-sans font-bold flex items-center gap-1">
                    <Check className="h-3 w-3" /> Approved Pronunciation
                  </span>
                )}
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4 py-2">
              <div className="rounded-xl bg-muted/40 p-4 border">
                <p className="text-xs text-muted-foreground">मूळ पाठ्यपुस्तक शब्द (Canonical Spelling):</p>
                <p className="deva text-3xl font-bold text-foreground mt-1">{selectedWord.word}</p>
                {selectedWord.entry ? (
                  <div className="mt-3 space-y-1 text-sm bg-muted/30 p-2.5 rounded-lg border">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-muted-foreground">मान्य फोनॅटिक उच्चार:</span>
                      <span className="text-[11px] font-bold text-green-600 bg-green-500/10 px-2 py-0.5 rounded-full">
                        ज्ञानकोशात मंजूर (v{selectedWord.entry.version || 1})
                      </span>
                    </div>
                    <p className="deva font-bold text-primary text-xl mt-1">{selectedWord.entry.preferred_pronunciation}</p>
                    {selectedWord.entry.phonetic_form && (
                      <p className="text-xs text-muted-foreground">IPA / Roman: {selectedWord.entry.phonetic_form}</p>
                    )}
                    {selectedWord.entry.notes && (
                      <p className="text-xs text-muted-foreground mt-1">टीप: {selectedWord.entry.notes}</p>
                    )}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground mt-2 italic bg-muted/20 p-2 rounded">
                    हा शब्द मानक उच्चार नियमांनुसार वाचला जातो. नवा उच्चार शिकवण्यासाठी किंवा दुरुस्तीसाठी खालील पर्याय वापरा.
                  </p>
                )}
              </div>
            </div>

            <DialogFooter className="flex flex-wrap gap-2 sm:justify-between">
              <button
                onClick={() => {
                  fetch("/api/tts/synthesize", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      text: selectedWord.entry?.preferred_pronunciation || selectedWord.word,
                      speaker,
                      provider: ttsProvider
                    })
                  })
                    .then((r) => r.json())
                    .then((d) => {
                      if (d.audio_base64) {
                        const a = new Audio("data:audio/wav;base64," + d.audio_base64);
                        a.play();
                      }
                    });
                }}
                className="flex items-center gap-1.5 rounded-xl border bg-card px-3.5 py-2 text-sm font-semibold hover:bg-accent transition cursor-pointer"
              >
                <Volume2 className="h-4 w-4" /> उच्चार ऐका (Listen)
              </button>
              <div className="flex gap-2">
                <button
                  onClick={() => openAdminEdit(selectedWord.word, selectedWord.entry, true)}
                  className="flex items-center gap-1.5 rounded-xl border border-primary/40 bg-primary/10 px-3.5 py-2 text-sm font-semibold text-primary hover:bg-primary/20 transition cursor-pointer"
                  title="Speak the correct pronunciation to teach the model"
                >
                  <Mic className="h-4 w-4" /> उच्चार शिकवा (Record Voice)
                </button>
                <button
                  onClick={() => openAdminEdit(selectedWord.word, selectedWord.entry, false)}
                  className="flex items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 transition cursor-pointer"
                >
                  <Edit3 className="h-4 w-4" /> संपादित करा (Edit)
                </button>
              </div>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {/* Admin Edit / Voice Pronunciation Teaching Dialog (§5, §6, §7, §8, §11) */}
      <Dialog open={adminModalOpen} onOpenChange={setAdminModalOpen}>
        <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="deva text-xl flex items-center justify-between">
              <span className="flex items-center gap-2">
                <Edit3 className="h-5 w-5 text-primary" />
                <span>उच्चार शिकवा (Teach Pronunciation)</span>
              </span>
              <span className="text-xs font-mono bg-primary/10 text-primary px-2.5 py-0.5 rounded-full">
                अपरिवर्तनीय मूळ मजकूर
              </span>
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-4 py-2 text-sm">
            <p className="text-xs text-muted-foreground">
              पाठ्यपुस्तकातील मूळ शब्द कधीही बदलला जात नाही. उच्चार मॉडेल व टीटीएससाठी ज्ञानकोशात ध्वनीशास्त्रीय मार्गदर्शक म्हणून जतन होतो.
            </p>

            {/* 1. Canonical Word (Always Unchanged) */}
            <div className="rounded-xl border bg-muted/40 p-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-muted-foreground uppercase tracking-wide">
                  पाठ्यपुस्तक मूळ शब्द (Canonical Word)
                </span>
                <span className="text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md">
                  कायम अपरिवर्तनीय
                </span>
              </div>
              <div className="mt-1 text-2xl font-bold deva text-foreground tracking-wide">
                {adminWordForm.canonical_text}
              </div>
            </div>

            {/* 2. Spoken Voice Recording Section */}
            <div className="rounded-xl border border-primary/30 bg-primary/5 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-primary uppercase tracking-wide flex items-center gap-1.5">
                    <Mic className="h-3.5 w-3.5" /> प्रशासक ध्वनी रेकॉर्डिंग (Admin Voice)
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    शब्दाचा स्वाभाविक उच्चार बोला. सिस्टीम ध्वनी विश्लेषण करून उच्चार डीकोड करेल.
                  </p>
                </div>
                {isRecordingVoice ? (
                  <button
                    onClick={stopRecordingVoice}
                    className="flex items-center gap-1.5 rounded-full bg-destructive px-3.5 py-1.5 text-xs font-bold text-destructive-foreground animate-pulse cursor-pointer shadow-md"
                  >
                    <Square className="h-3.5 w-3.5 fill-current" /> थांबा (Stop)
                  </button>
                ) : (
                  <button
                    onClick={() => startRecordingVoice()}
                    className="flex items-center gap-1.5 rounded-full bg-primary px-3.5 py-1.5 text-xs font-bold text-primary-foreground hover:opacity-90 transition cursor-pointer shadow-sm"
                  >
                    <Mic className="h-3.5 w-3.5" /> {recordedAudioBlob ? "🎙 पुन्हा बोला (Record Again)" : "🎙 उच्चार बोला (Speak)"}
                  </button>
                )}
              </div>

              {/* Decoding Progress */}
              {isDecodingVoice && (
                <div className="p-3 rounded-lg bg-card border border-primary/20 flex items-center gap-2.5 text-xs text-primary font-medium animate-pulse">
                  <div className="h-3.5 w-3.5 rounded-full border-2 border-primary border-t-transparent animate-spin" />
                  ध्वनीशास्त्र विश्लेषण व उच्चार डीकोडिंग चालू आहे (Decoding pronunciation acoustics)...
                </div>
              )}

              {/* Reference Audio Player */}
              {recordedAudioUrl && !isDecodingVoice && (
                <div className="flex flex-wrap items-center gap-3 pt-1 border-t border-primary/10">
                  <audio controls src={recordedAudioUrl} className="h-8 max-w-[260px]" />
                  <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-500/10 px-2.5 py-1 rounded-full flex items-center gap-1">
                    <Check className="h-3 w-3" /> संदर्भ ऑडिओ पुरावा उपलब्ध
                  </span>
                </div>
              )}
            </div>

            {/* 3. Detected Pronunciation Card & Real ASR Voice Feedback */}
            {decodedPronunciation && (
              <div className="rounded-xl border border-primary/30 bg-card p-4 space-y-3 shadow-xs">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-muted-foreground uppercase tracking-wide flex items-center gap-1">
                    <Sparkles className="h-3.5 w-3.5 text-primary" /> आवाज विश्लेषण (Voice Acoustic Analysis)
                  </span>
                  <span className={`text-[11px] font-mono px-2 py-0.5 rounded-md font-semibold ${
                    decodedPronunciation.is_canonical_match !== false
                      ? "bg-emerald-500/10 text-emerald-600 border border-emerald-500/20"
                      : "bg-amber-500/10 text-amber-700 border border-amber-500/20"
                  }`}>
                    {decodedPronunciation.is_canonical_match !== false ? "✓ उच्चार ओळखला" : "⚡ दुरुस्त उच्चार ओळखला"}
                  </span>
                </div>

                <div className="p-3 rounded-lg bg-primary/5 border border-primary/20 space-y-2">
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">रेकॉर्ड केलेले शब्द (Recognized Speech):</p>
                      <span className="deva text-xl font-bold text-foreground">
                        {decodedPronunciation.spoken_transcript || adminWordForm.canonical_text}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-medium text-muted-foreground">रोमन रूप (Phonetic):</p>
                      <span className="font-mono text-sm font-bold text-primary">
                        {decodedPronunciation.detected_pronunciation}
                      </span>
                    </div>
                  </div>

                  {/* Syllable Boundaries */}
                  {decodedPronunciation.syllable_boundaries?.length > 0 && (
                    <div className="pt-1.5 border-t border-primary/10">
                      <span className="text-[11px] font-semibold text-muted-foreground">अक्षर घटक (Syllable Boundaries):</span>
                      <div className="flex flex-wrap gap-1.5 mt-1">
                        {decodedPronunciation.syllable_boundaries.map((syl, idx) => (
                          <span key={idx} className="px-2.5 py-0.5 text-xs bg-card text-foreground border border-primary/20 rounded-md font-bold deva shadow-2xs">
                            {syl}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* 4. Pronunciation Guide & TTS Configuration (Always directly visible & editable) */}
            <div className="space-y-4 rounded-xl border p-4 bg-muted/20">
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="text-xs font-bold text-foreground">
                    फोनॅटिक उच्चार मार्गदर्शक (TTS Pronunciation Guide):
                  </label>
                  <span className="text-[11px] text-muted-foreground font-normal">हायफन (-) सह अक्षरे जोडा</span>
                </div>

                {/* Commonly Used Matras & Diacritics Tablets Bar */}
                <div className="mb-2 p-2.5 rounded-lg border border-primary/20 bg-card/70 backdrop-blur-xs">
                  <div className="flex items-center justify-between mb-1.5 px-0.5">
                    <span className="text-[11px] font-bold text-primary flex items-center gap-1">
                      <span>✨</span> मात्रा व उच्चार पाट्या (Matra Tablets):
                    </span>
                    <span className="text-[10px] text-muted-foreground">
                      कर्सरच्या जागी जोडण्यासाठी टॅप करा (Tap to insert at cursor)
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {COMMON_MATRA_TABLETS.map((tablet) => (
                      <Tooltip key={tablet.id}>
                        <TooltipTrigger asChild>
                          <button
                            type="button"
                            onMouseDown={(e) => e.preventDefault()}
                            onClick={() => handleInsertMatraTablet(tablet)}
                            className="inline-flex items-center gap-1.5 px-2 py-1 text-xs font-semibold rounded-md border border-primary/25 bg-background hover:bg-primary/10 hover:border-primary active:scale-95 transition shadow-2xs cursor-pointer select-none text-foreground"
                          >
                            <span className="text-sm font-bold text-primary deva">
                              {tablet.sign === "-" ? "हायफन (-)" : tablet.sample}
                            </span>
                            <span className="text-[10px] text-muted-foreground font-medium">
                              {tablet.name_en}
                            </span>
                          </button>
                        </TooltipTrigger>
                        <TooltipContent side="top" className="text-xs max-w-xs p-2">
                          <p className="font-bold text-primary">{tablet.label}</p>
                          <p className="text-muted-foreground mt-0.5">{tablet.tooltip}</p>
                        </TooltipContent>
                      </Tooltip>
                    ))}
                  </div>
                </div>

                <div className="relative mt-1">
                  <input
                    ref={devaInputRef}
                    value={adminWordForm.preferred_pronunciation}
                    onChange={handleDevaChange}
                    placeholder="उदा. नट-रंग किंवा सिंह-गडा-जवळ"
                    className="w-full rounded-lg border bg-card px-3.5 py-2 text-lg font-bold text-primary deva focus:outline-none focus:ring-2 focus:ring-primary shadow-xs"
                  />
                </div>
                <p className="text-[11px] text-muted-foreground mt-1 leading-relaxed">
                  हा उच्चार Sarvam TTS द्वारे बोलला जाईल. हायफनने अक्षर अवयव वेगळे केल्यास आवाजाचा आघात अचूक येतो.
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-semibold text-muted-foreground">
                    रोमन ध्वनी रूप (Phonetic Romanized Form):
                  </label>
                  <span className="text-[10px] text-primary/80 font-medium">
                    ⚡ मराठी उच्चाराशी थेट जोडलेले (Real-time 2-way sync)
                  </span>
                </div>
                <input
                  value={adminWordForm.phonetic_form}
                  onChange={handleRomanChange}
                  placeholder="उदा. sama-kaalee-n किंवा nat-rang"
                  className="w-full rounded-lg border bg-card px-3 py-1.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              <div className="grid grid-cols-2 gap-3 pt-1">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground">लागू व्याप्ती (Scope):</label>
                  <select
                    value={adminWordForm.scope}
                    onChange={(e) => setAdminWordForm({ ...adminWordForm, scope: e.target.value })}
                    className="w-full mt-1 rounded-lg border bg-card px-2.5 py-1.5 text-sm cursor-pointer"
                  >
                    <option value="global">🌍 Global (सर्व पुस्तकांसाठी)</option>
                    <option value="subject">📚 Subject (भूगोल विषयासाठी)</option>
                    <option value="textbook">📘 Textbook (इयत्ता १० भूगोल)</option>
                    <option value="document">📖 Document (या प्रकरणापुरते)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-semibold text-muted-foreground">टीप / संदर्भ (Notes):</label>
                  <input
                    value={adminWordForm.notes}
                    onChange={(e) => setAdminWordForm({ ...adminWordForm, notes: e.target.value })}
                    placeholder="उदा. स्पष्ट उच्चार आघात"
                    className="w-full mt-1 rounded-lg border bg-card px-3 py-1.5 text-sm"
                  />
                </div>
              </div>
            </div>
          </div>

          <DialogFooter className="flex flex-wrap gap-2 sm:justify-between pt-3 border-t">
            {/* Audio Test Controls */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => handleTestPronunciation()}
                disabled={testingPron || isDecodingVoice}
                className={`flex items-center gap-1.5 rounded-xl border px-4 py-2 text-sm font-bold transition cursor-pointer shadow-xs ${
                  isPlayingTestAudio
                    ? "border-primary bg-primary text-primary-foreground animate-pulse"
                    : "border-primary/40 bg-card text-primary hover:bg-primary/10"
                }`}
                title="दुरुस्त केलेल्या उच्चाराची Sarvam TTS द्वारे ध्वनी चाचणी ऐका"
              >
                <Volume2 className={`h-4 w-4 ${isPlayingTestAudio ? "animate-bounce" : ""}`} />
                {testingPron ? "तयार होत आहे..." : isPlayingTestAudio ? "🔊 ऑडिओ वाजत आहे..." : "▶ चाचणी ऐका (Test Audio)"}
              </button>

              <button
                onClick={() => handleTestPronunciation(adminWordForm.canonical_text)}
                disabled={testingPron || isDecodingVoice}
                className="flex items-center gap-1 rounded-xl border border-muted-foreground/20 bg-muted/40 px-3 py-2 text-xs font-medium hover:bg-muted transition cursor-pointer text-muted-foreground"
                title="तुलनेसाठी मूळ पाठ्यपुस्तक शब्दाचा उच्चार ऐका"
              >
                मूळ शब्द ऐका
              </button>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => startRecordingVoice()}
                disabled={isRecordingVoice || isDecodingVoice}
                className="flex items-center gap-1.5 rounded-xl border bg-card px-3.5 py-2 text-sm font-semibold hover:bg-accent cursor-pointer"
              >
                <Mic className="h-4 w-4 text-primary" /> 🎙 पुन्हा बोला
              </button>

              <button
                onClick={handleSavePronunciation}
                disabled={savingPron || isDecodingVoice}
                className="flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 transition cursor-pointer shadow-sm"
              >
                <Check className="h-4 w-4" /> {savingPron ? "सेव्ह होत आहे..." : "✓ सेव्ह व मंजूर करा"}
              </button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Supporting Visual / Map Explanation Modal */}
      {visualModal && (
        <Dialog open={!!visualModal} onOpenChange={() => setVisualModal(null)}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="deva text-xl flex items-center gap-2">
                <MapPin className="h-5 w-5 text-primary" />
                <span>{visualModal.title}</span>
              </DialogTitle>
            </DialogHeader>

            <div className="space-y-4 py-2 text-sm">
              <div className="rounded-xl bg-primary/5 p-4 border border-primary/20">
                <p className="text-xs font-semibold text-primary uppercase tracking-wide">नकाशा तपशील (Map Details)</p>
                <p className="deva font-bold text-base text-foreground mt-1">{visualModal.caption_text}</p>
                <p className="deva text-muted-foreground mt-2 leading-relaxed">
                  {visualModal.explanation || "क्षेत्रभेटीच्या मार्गामध्ये नळदुर्ग, सोलापूर, पुणे आणि अलिबाग या प्रमुख ठिकाणांचा प्रवास दाखवला आहे."}
                </p>
              </div>
              <p className="text-xs text-muted-foreground italic">
                RAG Context: हा नकाशा मुख्य मजकुरात व्यत्यय न आणता शैक्षणिक संदर्भासाठी संलग्न ठेवण्यात आला आहे.
              </p>
            </div>

            <DialogFooter>
              <button
                onClick={() => {
                  fetch("/api/tts/synthesize", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                      text: `${visualModal.title} । ${visualModal.explanation}`,
                      speaker,
                      is_tutor: true,
                      style: "teacher"
                    })
                  })
                    .then((r) => r.json())
                    .then((d) => {
                      if (d.audio_base64) {
                        const a = new Audio("data:audio/wav;base64," + d.audio_base64);
                        a.play();
                      }
                    });
                }}
                className="flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground hover:opacity-90 cursor-pointer"
              >
                <Volume2 className="h-4 w-4" /> नकाशा स्पष्टीकरण ऐका (Listen to Map Analysis)
              </button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </TooltipProvider>
  );
}
