import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export type TextSize = "sm" | "md" | "lg" | "xl";
export type Lang = "en" | "mr";
const SIZES: Record<TextSize, string> = { sm: "14px", md: "16px", lg: "19px", xl: "22px" };
const ORDER: TextSize[] = ["sm", "md", "lg", "xl"];

type Ctx = {
  size: TextSize;
  setSize: (s: TextSize) => void;
  bump: (d: 1 | -1) => void;
  contrast: boolean;
  setContrast: (v: boolean) => void;
  lang: Lang;
  setLang: (l: Lang) => void;
};
const A11yContext = createContext<Ctx | null>(null);

export function A11yProvider({ children }: { children: ReactNode }) {
  const [size, setSize] = useState<TextSize>("md");
  const [contrast, setContrast] = useState(false);
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    try {
      const s = JSON.parse(localStorage.getItem("aksharsetu:a11y") || "{}");
      if (s.size) setSize(s.size);
      if (typeof s.contrast === "boolean") setContrast(s.contrast);
      if (s.lang) setLang(s.lang);
    } catch {}
  }, []);

  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty("--base-size", SIZES[size]);
    root.classList.toggle("hc", contrast);
    root.lang = lang === "mr" ? "mr" : "en";
    localStorage.setItem("aksharsetu:a11y", JSON.stringify({ size, contrast, lang }));
  }, [size, contrast, lang]);

  const bump = (d: 1 | -1) =>
    setSize((s) => ORDER[Math.min(ORDER.length - 1, Math.max(0, ORDER.indexOf(s) + d))]);

  return (
    <A11yContext.Provider value={{ size, setSize, bump, contrast, setContrast, lang, setLang }}>
      {children}
    </A11yContext.Provider>
  );
}

export function useA11y() {
  const c = useContext(A11yContext);
  if (!c) throw new Error("useA11y must be used inside A11yProvider");
  return c;
}

/** Tiny UI-chrome dictionary. */
const T = {
  home: { en: "Home", mr: "मुख्यपृष्ठ" },
  capture: { en: "Capture", mr: "फोटो घ्या" },
  read: { en: "Read", mr: "वाचा" },
  library: { en: "Library", mr: "ग्रंथालय" },
  review: { en: "Review", mr: "तपासणी" },
  admin: { en: "Metrics", mr: "आकडेवारी" },
  settings: { en: "Settings", mr: "सेटिंग्ज" },
} as const;
export function useT() {
  const { lang } = useA11y();
  return (k: keyof typeof T) => T[k][lang];
}
