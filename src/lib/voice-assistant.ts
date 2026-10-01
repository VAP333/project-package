// -*- coding: utf-8 -*-
/**
 * AksharSetu Voice Assistant Engine
 * ===================================
 * Wake word: "Hey AksharSetu" / "अक्षरसेतू"
 * Always-on continuous speech recognition (Web Speech API).
 * Command grammar supports Marathi + English commands for all reader functions.
 */

import { useEffect, useRef, useState, useCallback } from "react";

// ─── Types ────────────────────────────────────────────────────────────────────

export type VAState =
  | "idle"       // Sleeping — wake word detection ON
  | "listening"  // Awake — full command listening
  | "processing" // Parsing transcript
  | "responding" // Speaking back
  | "error";

export type VACommand =
  | "play"
  | "pause"
  | "repeat"
  | "next_block"
  | "prev_block"
  | "next_page"
  | "prev_page"
  | "go_slow"
  | "go_fast"
  | "normal_speed"
  | "tutor_on"
  | "tutor_off"
  | "explain"
  | "stop"
  | "restart"
  | "ask_question"
  | "go_to_page"
  | "sleep"
  | "help";

export interface VAResult {
  command: VACommand;
  payload?: string;
  confidence: number;
  rawTranscript: string;
}

export interface VAConfig {
  lang?: string;
  onStateChange?: (state: VAState) => void;
  onResult?: (result: VAResult) => void;
  onRawTranscript?: (text: string, isFinal: boolean) => void;
  onError?: (msg: string) => void;
  onWakeWord?: () => void;
}

// ─── Wake Phrase Variants ─────────────────────────────────────────────────────

const WAKE_PATTERNS = [
  "hey akshar setu",
  "hey aksharsetu",
  "akshar setu",
  "aksharsetu",
  "hey akshar",
  "अक्षरसेतू",
  "हे अक्षरसेतू",
  "ओ अक्षरसेतू",
  "o akshar setu",
];

// ─── Command Grammar ─────────────────────────────────────────────────────────

interface RuleSet {
  patterns: string[];
  command: VACommand;
}

const COMMAND_RULES: RuleSet[] = [
  { patterns: ["सुरू करा", "वाचा", "play", "start", "resume", "सुरू", "चालू", "वाचणे सुरू", "ऐकायचंय"], command: "play" },
  { patterns: ["थांबा", "pause", "रोखा", "stop reading", "थांब", "रुका", "विराम"], command: "pause" },
  { patterns: ["पुन्हा सांग", "पुन्हा वाचा", "repeat", "again", "एकदा परत", "पुन्हा", "repeat this", "परत सांग", "पुन्हा ऐकायचं", "फिर से"], command: "repeat" },
  { patterns: ["समजावून सांग", "explain", "स्पष्टीकरण", "समजावून", "explain this", "सांग नीट", "explain again", "पुन्हा समजावून", "समजत नाही"], command: "explain" },
  { patterns: ["हळू बोल", "हळू", "slow down", "go slow", "slower", "आस्ते", "slowly", "धीरे"], command: "go_slow" },
  { patterns: ["जलद बोल", "जलद", "speed up", "go fast", "faster", "लवकर", "fast", "जल्दी"], command: "go_fast" },
  { patterns: ["साधारण वेग", "normal speed", "normal pace", "regular speed", "नॉर्मल"], command: "normal_speed" },
  { patterns: ["पुढे जा", "पुढील परिच्छेद", "next", "next paragraph", "पुढचा", "next block", "पुढे", "आगे"], command: "next_block" },
  { patterns: ["मागे जा", "मागील परिच्छेद", "previous", "prev", "back", "मागचा", "मागे", "previous paragraph", "पीछे"], command: "prev_block" },
  { patterns: ["पुढील पान", "next page", "pudhil paan", "पुढील पृष्ठ", "अगला पेज"], command: "next_page" },
  { patterns: ["मागील पान", "previous page", "mageel paan", "मागील पृष्ठ", "back page"], command: "prev_page" },
  { patterns: ["tutor mode", "शिक्षक मोड", "tutor on", "tutor", "शिकवा", "ट्युटर", "tutor mode on"], command: "tutor_on" },
  { patterns: ["reading mode", "वाचन मोड", "tutor off", "turn off tutor", "normal mode", "ट्युटर बंद"], command: "tutor_off" },
  { patterns: ["पुन्हा सुरुवात", "restart", "start over", "शुरूवात", "beginning", "पहिल्यापासून"], command: "restart" },
  { patterns: ["help", "मदत", "काय करता येते", "what can you do", "commands", "सांग काय करू"], command: "help" },
  { patterns: ["sleep", "bye", "goodbye", "झोप", "बंद कर", "quiet", "शांत हो", "stop listening", "जा झोप"], command: "sleep" },
];

// ─── Parser ──────────────────────────────────────────────────────────────────

function matchCommand(transcript: string): VAResult | null {
  const t = transcript.trim().toLowerCase();

  // Page jump: "go to page 3" / "पान ३ वर जा"
  const pageMatch = t.match(/(?:page|paan|पान|पृष्ठ)\s*([0-9१२३४५६७८९०]+)/i);
  if (pageMatch) {
    const rawNum = pageMatch[1];
    const devaMap: Record<string, string> = {
      "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
      "५": "5", "६": "6", "७": "7", "८": "8", "९": "9"
    };
    const num = rawNum.split("").map((c) => devaMap[c] || c).join("");
    return { command: "go_to_page", payload: num, confidence: 0.9, rawTranscript: transcript };
  }

  // Question detection → ask_question
  const questionPatterns = [
    "what", "why", "how", "when", "who", "where", "which",
    "काय", "का", "कसे", "कधी", "कोण", "कुठे",
    "explain me", "tell me about", "म्हणजे काय", "what is", "what are"
  ];
  const isQuestion = t.length > 10 && questionPatterns.some((q) =>
    t.startsWith(q) || t.includes(q)
  );
  if (isQuestion) {
    return { command: "ask_question", payload: transcript.trim(), confidence: 0.8, rawTranscript: transcript };
  }

  // Command rules matching
  for (const rule of COMMAND_RULES) {
    for (const pattern of rule.patterns) {
      if (t.includes(pattern.toLowerCase())) {
        return { command: rule.command, confidence: 0.95, rawTranscript: transcript };
      }
    }
  }

  return null;
}

function containsWakeWord(text: string): boolean {
  const t = text.trim().toLowerCase();
  return WAKE_PATTERNS.some((p) => t.includes(p.toLowerCase()));
}

// ─── Natural Responses (Marathi) ─────────────────────────────────────────────

export const VA_RESPONSES: Record<VACommand, string[]> = {
  play:         ["चला, सुरू करूया!", "वाचन सुरू करते.", "आता ऐका."],
  pause:        ["ठीक आहे, थांबते.", "रोखले आहे.", "विराम दिला."],
  repeat:       ["पुन्हा सांगते.", "एकदा परत ऐका.", "पुन्हा वाचते."],
  explain:      ["आता समजावून सांगते.", "चला, नीट समजून घेऊया.", "थांबा, स्पष्टीकरण देते."],
  go_slow:      ["हळू बोलते आता.", "ठीक आहे, आस्ते सांगते.", "वेग कमी केला."],
  go_fast:      ["जलद वाचते.", "ठीक आहे, जलद करते.", "वेग वाढवला."],
  normal_speed: ["साधारण वेगाने वाचते.", "वेग ठीक केला."],
  next_block:   ["पुढे जातो.", "पुढचा भाग."],
  prev_block:   ["मागे जातो.", "मागचा भाग."],
  next_page:    ["पुढील पान उघडते.", "पुढे चलो!"],
  prev_page:    ["मागील पान."],
  tutor_on:     ["शिक्षक मोड चालू! आता स्पष्टीकरण मिळेल.", "ट्युटर मोड सुरू."],
  tutor_off:    ["वाचन मोड सुरू.", "ट्युटर मोड बंद."],
  ask_question: ["चांगला प्रश्न! उत्तर शोधते.", "थांबा, उत्तर सांगते."],
  go_to_page:   ["पान उघडते.", "त्या पानावर जातो."],
  restart:      ["शुरूवातीपासून सुरू करते.", "परत पहिल्यापासून!"],
  stop:         ["ठीक आहे, थांबते."],
  sleep:        ["ठीक आहे, बंद केले."],
  help:         ["मी AksharSetu आहे! थेट बोला: वाचा, थांबा, पुन्हा सांग, समजावून सांग, हळू बोल, जलद बोल, पुढे जा, मागे जा, पुढील पान, मागील पान. एखादा प्रश्न विचारण्यासाठी थेट विचारा!"],
};

export function getVAResponse(command: VACommand): string {
  const list = VA_RESPONSES[command];
  return list[Math.floor(Math.random() * list.length)];
}

// ─── Voice Assistant Class ────────────────────────────────────────────────────

declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}

export class VoiceAssistant {
  config: VAConfig;
  private recognition: SpeechRecognition | null = null;
  private _state: VAState = "listening";
  private isActive = false;
  private restartTimer: ReturnType<typeof setTimeout> | null = null;
  private respondingTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(config: VAConfig) {
    this.config = config;
  }

  setState(state: VAState) {
    this._state = state;
    this.config.onStateChange?.(state);
  }

  get state(): VAState {
    return this._state;
  }

  getState(): VAState {
    return this._state;
  }

  isRunning(): boolean {
    return this.isActive;
  }

  start() {
    if (this.isActive) return;
    if (typeof window === "undefined") return;

    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) {
      this.config.onError?.("Web Speech API not supported in this browser.");
      this.setState("error");
      return;
    }

    this.isActive = true;
    this.setState("listening");
    this._startRecognition();
  }

  stop() {
    this.isActive = false;
    if (this.restartTimer) clearTimeout(this.restartTimer);
    if (this.respondingTimer) clearTimeout(this.respondingTimer);
    this.recognition?.abort();
    this.recognition = null;
    this.setState("idle");
  }

  // Manual activate — no-op in always-on mode (stays listening)
  triggerWake() {
    if (!this.isActive) return;
    this.setState("listening");
  }

  private _startRecognition() {
    if (!this.isActive) return;

    const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognitionAPI) return;

    try {
      const rec = new SpeechRecognitionAPI();
      this.recognition = rec;
      rec.lang = this.config.lang || "hi-IN";
      rec.continuous = true;
      rec.interimResults = true;
      rec.maxAlternatives = 3;

      rec.onresult = (event: SpeechRecognitionEvent) => {
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i];
          const transcript = result[0].transcript;
          const isFinal = result.isFinal;

          // Show live interim transcript always
          this.config.onRawTranscript?.(transcript, isFinal);

          // Only process final results and only when we're in listening state
          if (!isFinal || this._state === "processing" || this._state === "responding") continue;

          // Strip any accidental wake-word prefix from transcript
          let clean = transcript.trim();
          const WAKE_PREFIXES = [
            "hey akshar setu", "hey aksharsetu", "akshar setu", "aksharsetu",
            "hey akshar", "अक्षरसेतू", "हे अक्षरसेतू", "ओ अक्षरसेतू"
          ];
          for (const prefix of WAKE_PREFIXES) {
            const idx = clean.toLowerCase().indexOf(prefix.toLowerCase());
            if (idx !== -1) {
              clean = clean.slice(idx + prefix.length).trim();
            }
          }

          if (clean.length < 2) continue;

          this.setState("processing");
          const matched = matchCommand(clean);

          if (matched) {
            this.setState("responding");
            this.config.onResult?.(matched);
            // Return to listening quickly after response is dispatched
            if (this.respondingTimer) clearTimeout(this.respondingTimer);
            this.respondingTimer = setTimeout(() => {
              if (this._state === "responding") this.setState("listening");
            }, 600);
          } else {
            // Not a recognized command — return to listening immediately
            this.setState("listening");
          }
        }
      };

      rec.onerror = (event: SpeechRecognitionErrorEvent) => {
        if (event.error === "not-allowed" || event.error === "service-not-allowed") {
          this.config.onError?.("Microphone permission denied. Please allow mic access.");
          this.setState("error");
          return;
        }
        // Restart on transient errors (no-speech, network, aborted)
        if (this.isActive) this._scheduleRestart(200);
      };

      rec.onend = () => {
        // Immediately restart to maintain always-on listening
        if (this.isActive) this._scheduleRestart(100);
      };

      rec.start();
    } catch {
      if (this.isActive) this._scheduleRestart(500);
    }
  }

  private _scheduleRestart(delay: number) {
    if (this.restartTimer) clearTimeout(this.restartTimer);
    this.restartTimer = setTimeout(() => {
      if (this.isActive) {
        this.recognition = null;
        this._startRecognition();
      }
    }, delay);
  }
}

// ─── React Hook ──────────────────────────────────────────────────────────────

export interface UseVoiceAssistantOptions {
  enabled: boolean;
  lang?: string;
  onCommand: (result: VAResult) => void;
  onWakeWord?: () => void;
}

export function useVoiceAssistant(options: UseVoiceAssistantOptions) {
  const [vaState, setVaState] = useState<VAState>("idle");
  const [rawTranscript, setRawTranscript] = useState("");
  const [lastCommand, setLastCommand] = useState<VAResult | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const vaRef = useRef<VoiceAssistant | null>(null);

  const onCommandRef = useRef(options.onCommand);
  useEffect(() => { onCommandRef.current = options.onCommand; }, [options.onCommand]);

  const onWakeWordRef = useRef(options.onWakeWord);
  useEffect(() => { onWakeWordRef.current = options.onWakeWord; }, [options.onWakeWord]);

  useEffect(() => {
    if (!options.enabled) {
      vaRef.current?.stop();
      vaRef.current = null;
      setVaState("idle");
      return;
    }

    const va = new VoiceAssistant({
      lang: options.lang || "hi-IN",
      onStateChange: setVaState,
      onResult: (result) => {
        setLastCommand(result);
        onCommandRef.current(result);
      },
      onRawTranscript: (text) => setRawTranscript(text),
      onError: (msg) => {
        setErrorMsg(msg);
        setVaState("error");
      },
      onWakeWord: () => onWakeWordRef.current?.(),
    });

    vaRef.current = va;
    va.start();

    return () => {
      va.stop();
      vaRef.current = null;
    };
  }, [options.enabled, options.lang]);

  const activate = useCallback(() => {
    vaRef.current?.triggerWake();
  }, []);

  return { vaState, rawTranscript, lastCommand, errorMsg, activate };
}
